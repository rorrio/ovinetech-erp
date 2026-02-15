import sys
import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlmodel import SQLModel 
from pydantic import ValidationError

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ovine_manager.models import Animal, Raza, Sexo, EstadoProductivo, Origen
from ovine_manager.schemas import AnimalCreate
from shared.database import sqlite_url, connect_args # Reusing existing config

# Custom engine for this script, reusing shared config
engine = create_engine(sqlite_url, connect_args=connect_args)

LOG_FILE = "import_errors.log"

def normalize_sexo(val):
    if not val: return None
    val = str(val).strip().upper()
    if val in ["MACHO", "M"]: return Sexo.MACHO
    if val in ["HEMBRA", "F"]: return Sexo.HEMBRA
    return val # Let Pydantic validation fail if invalid

def normalize_raza(val):
    if not val: return None
    # Simple direct mapping or return as is for Pydantic to validate against Enum
    return str(val).strip()

def normalize_estado(val):
    if not val: return None
    # Map common variations if needed, or rely on Pydantic
    return str(val).strip()

def ingest_flock(csv_path: str):
    print(f"Starting ingestion from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found.")
        return

    # Clear previous log
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    # Ensure tables exist
    SQLModel.metadata.create_all(engine)

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    success_count = 0
    error_count = 0
    
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        with Session(engine) as session:
            for index, row in df.iterrows():
                row_num = index + 2 # Header is row 1
                try:
                    # 1. Normalize Data
                    data = {
                        "caravana_visual": str(row['caravana_visual']).strip(),
                        "rfid_tag": str(row['rfid_tag']).strip() if pd.notna(row['rfid_tag']) else None,
                        "raza": normalize_raza(row['raza']),
                        "sexo": normalize_sexo(row['sexo']),
                        "fecha_nacimiento": pd.to_datetime(row['fecha_nacimiento']).date(),
                        "peso_actual": float(row['peso_kg']) if pd.notna(row['peso_kg']) else None,
                        "estado_productivo": normalize_estado(row['estado']),
                        "origen": Origen.PROPIO # Defaulting for now
                    }

                    # 2. Validate with Pydantic
                    # We use AnimalCreate to validate the dict structure and types
                    animal_schema = AnimalCreate(**data)
                    
                    # 3. Check Existence (Idempotency)
                    # Use distinct checks to avoid complex OR logic issues in SQLite if any
                    existing_animal = None
                    if animal_schema.rfid_tag:
                         existing_animal = session.scalar(select(Animal).where(Animal.rfid_tag == animal_schema.rfid_tag))
                    
                    if not existing_animal:
                         existing_animal = session.scalar(select(Animal).where(Animal.caravana_visual == animal_schema.caravana_visual))

                    if existing_animal:
                        print(f"Row {row_num}: Updating existing animal {existing_animal.caravana_visual}")
                        # Update fields
                        existing_animal.raza = animal_schema.raza
                        existing_animal.sexo = animal_schema.sexo
                        existing_animal.fecha_nacimiento = animal_schema.fecha_nacimiento
                        existing_animal.peso_actual = data['peso_actual'] # Not in base schema but in model
                        existing_animal.estado_productivo = animal_schema.estado_productivo
                        # RFID update logic: only if provided and different? 
                        if animal_schema.rfid_tag:
                            existing_animal.rfid_tag = animal_schema.rfid_tag
                    else:
                        print(f"Row {row_num}: Creating new animal {animal_schema.caravana_visual}")
                        # Create new
                        # Mapping schema back to model arguments. 
                        # Note: animal_schema is Pydantic, we need dict for SQLAlchemy model
                        # But Pydantic model might not have all fields if we used a subset schema. 
                        # We constructed AnimalCreate with 'peso_actual' which is not in AnimalBase/Create definition in previous step?
                        # Wait, let's check schemas.py. 
                        # AnimalBase has: rfid_tag, caravana, raza, birth_date, sex, origen.
                        # AnimalCreate is empty subclass.
                        # We need to ensure we pass 'peso_actual' and 'estado_productivo' to the model explicitly if they are not in the schema,
                        # OR update the schema to include them. 
                        # For now, I will map manually to the Model to be safe.
                        
                        new_animal = Animal(
                            caravana_visual=animal_schema.caravana_visual,
                            rfid_tag=animal_schema.rfid_tag,
                            raza=animal_schema.raza,
                            fecha_nacimiento=animal_schema.fecha_nacimiento,
                            sexo=animal_schema.sexo,
                            origen=animal_schema.origen,
                            peso_actual=data['peso_actual'],
                            estado_productivo=data['estado_productivo'] # Assuming Pydantic validated the Enum string
                        )
                        session.add(new_animal)

                    session.commit()
                    success_count += 1

                except ValidationError as ve:
                    error_msg = f"Row {row_num}: Validation Error - {ve}\n"
                    print(error_msg.strip())
                    log.write(error_msg)
                    error_count += 1
                    session.rollback()
                except Exception as e:
                    error_msg = f"Row {row_num}: Processing Error - {e}\n"
                    print(error_msg.strip())
                    log.write(error_msg)
                    error_count += 1
                    session.rollback()

    print(f"\nIngestion Complete.")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
    print(f"See {LOG_FILE} for details.")

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    csv_file = os.path.join(current_dir, "initial_flock.csv")
    ingest_flock(csv_file)
