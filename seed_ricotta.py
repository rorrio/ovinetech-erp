from datetime import datetime
from sqlmodel import Session, select
from src.shared.database import engine, create_db_and_tables
from src.cheese_factory.models import LoteQueso

def seed_ricotta():
    print("Seeding Ricotta Batch...")
        
    # Ensure tables exist (including new finance ones if imported in main app, but this script might run standalone)
    # Ideally, we should import all models here to be safe if creating tables, 
    # but strictly we are just inserting into existing or lazily created LoteQueso table.
    create_db_and_tables() 

    with Session(engine) as session:
        # Check if already exists to avoid duplicates
        existing = session.exec(select(LoteQueso).where(LoteQueso.tipo_queso == "Ricotta", LoteQueso.litros_leche_usados == 2.0)).first()
        
        if existing:
            print("Ricotta batch already exists. Skipping.")
            return

        # Create Record
        # Fecha=16/02/2026, Tipo="Ricotta", Litros=2.0, Rendimiento=0.450 Kg
        ricotta = LoteQueso(
            fecha_elaboracion=datetime(2026, 2, 16, 10, 0, 0), # Hora arbitraria
            tipo_queso="Ricotta",
            litros_leche_usados=2.0,
            peso_salida_prensa_kg=0.450,
            # Optional fields left as None/Defaults
        )
        
        session.add(ricotta)
        session.commit()
        print("Ricotta batch created successfully!")

if __name__ == "__main__":
    seed_ricotta()
