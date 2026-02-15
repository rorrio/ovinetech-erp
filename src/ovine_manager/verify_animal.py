import sys
import os
from datetime import date, timedelta
from typing import Optional

# Add src to python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel import SQLModel

from ovine_manager.models import Animal, Raza, Sexo, Origen, EstadoProductivo
from ovine_manager.schemas import AnimalCreate, AnimalRead
from greenhouse.models import FVHCosecha # Needed for EventoAlimentacion FK resolution

def verify_animal_implementation():
    print("--- Verifying Animal Implementation ---")

    # 1. Setup In-Memory Database
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    print("Database initialized.")

    # 2. Test Animal Creation via SQLAlchemy
    today = date.today()
    birth_date = today - timedelta(days=365 + 180) # Approx 1.5 years old
    
    with Session(engine) as session:
        animal = Animal(
            caravana_visual="ARG-001",
            raza=Raza.TEXEL,
            fecha_nacimiento=birth_date,
            sexo=Sexo.HEMBRA,
            origen=Origen.PROPIO,
            estado_productivo=EstadoProductivo.GESTACION
        )
        session.add(animal)
        session.commit()
        session.refresh(animal)
        animal_id = animal.id
        print(f"Animal created with ID: {animal.id}")
        
        # 3. Test Age Calculation
        print(f"Age in months: {animal.edad_meses}")
        assert animal.edad_meses >= 17.0, f"Expected age approx 18 months, got {animal.edad_meses}"
        
        # 4. Test Pydantic Schema Validation (Read)
        # Convert ORM object to Pydantic model
        animal_dto = AnimalRead.model_validate(animal)
        print(f"Pydantic DTO created: {animal_dto.model_dump_json()}")
        
        assert animal_dto.caravana_visual == "ARG-001"
        assert animal_dto.raza == Raza.TEXEL
        assert animal_dto.edad_meses == animal.edad_meses
        print("Pydantic validation passed.")

    # 5. Test Pydantic Schema Validation (Create)
    new_animal_data = {
        "caravana_visual": "ARG-002",
        "raza": "Friesian",
        "fecha_nacimiento": "2024-01-01",
        "sexo": "M",
        "origen": "Compra Externa"
    }
    animal_create = AnimalCreate(**new_animal_data)
    print(f"AnimalCreate schema validated: {animal_create}")
    
    print("--- Verification Completed Successfully ---")

if __name__ == "__main__":
    try:
        verify_animal_implementation()
    except Exception as e:
        print(f"Verification FAILED: {e}")
        import traceback
        traceback.print_exc()
