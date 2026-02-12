from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from src.main import app
from src.shared.database import get_session
import os

# Use an in-memory database for testing or a separate file
# For this verification, let's use the actual file to match the user's request of checking ovinetech.db
# but TestClient usually works best with dependency overrides.

client = TestClient(app)

def test_api_workflows():
    # Remove existing db if any to start fresh
    if os.path.exists("ovinetech.db"):
        try:
            os.remove("ovinetech.db")
        except PermissionError:
            pass 

    with TestClient(app) as client:
        # 1. Cheese Factory
        print("Testing Cheese Factory...")
        response = client.post(
            "/cheese-factory/batches/",
            json={
                "fecha_elaboracion": "2023-10-27T10:00:00",
                "tipo_queso": "Manchego",
                "litros_leche_usados": 500.5,
                "ph_inicial": 6.5
            },
        )
        assert response.status_code == 200, f"Cheese Batch failed: {response.text}"
        
        # 2. GreenHouse
        print("Testing GreenHouse...")
        # Create Cycle
        res_cycle = client.post(
            "/greenhouse/cycles/",
            json={
                "tipo_semilla": "Cebada",
                "peso_semilla_kg": 10.0
            }
        )
        assert res_cycle.status_code == 200, f"Cycle failed: {res_cycle.text}"
        cycle_id = res_cycle.json()["id"]
        
        # Create Harvest
        res_harvest = client.post(
            "/greenhouse/harvests/",
            json={
                "ciclo_id": cycle_id,
                "peso_final_pasto_kg": 65.0
            }
        )
        assert res_harvest.status_code == 200, f"Harvest failed: {res_harvest.text}"
        
        # 3. Ovine Manager
        print("Testing Ovine Manager...")
        # Create Sheep Batch
        res_batch = client.post(
            "/ovine-manager/batches/",
            json={
                "nombre": "Lote Principal",
                "descripcion": "Ovejas en lactancia"
            }
        )
        assert res_batch.status_code == 200, f"Sheep Batch failed: {res_batch.text}"
        batch_id = res_batch.json()["id"]
        
        print("All verification tests passed successfully!")

if __name__ == "__main__":
    test_api_workflows()
