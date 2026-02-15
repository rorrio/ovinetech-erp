from fastapi import APIRouter, Depends
from .models import CleaningLog
from .agents import MaintenanceAgent

router = APIRouter()

# Dependencia para obtener el agente (simplificado)
def get_maintenance_agent():
    # Aquí inyectarías tu conexión real a DB
    return MaintenanceAgent(db_connection=MockDB()) 

@router.post("/logs")
def create_cleaning_log(log_data: CleaningLog, agent: MaintenanceAgent = Depends(get_maintenance_agent)):
    """
    Este endpoint recibe el JSON de la Raspberry Pi.
    """
    # 1. El Agente valida y registra
    agent.register_cleaning(log_data)
    
    return {"status": "success", "message": "Limpieza registrada correctamente"}