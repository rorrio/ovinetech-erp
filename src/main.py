from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel

from src.shared.database import create_db_and_tables
# Import models to register them with SQLModel metadata
from src.greenhouse import models as greenhouse_models
from src.ovine_manager import models as ovine_models
from src.cheese_factory import models as cheese_models

from src.greenhouse.router import router as greenhouse_router
from src.ovine_manager.router import router as ovine_manager_router
from src.cheese_factory.router import router as cheese_factory_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="OvineTech ERP", lifespan=lifespan)

app.include_router(greenhouse_router)
app.include_router(ovine_manager_router)
app.include_router(cheese_factory_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to OvineTech ERP"}


# 1. Definimos la estructura del mensaje de Alerta
class AlertaIoT(BaseModel):
    sensor_id: str
    tipo_alerta: str  # Ej: "TEMPERATURA_ALTA"
    valor: float
    mensaje: str

# 2. Creamos el Endpoint (El Buzón de Entrada)
@app.post("/api/alertas/")
def recibir_alerta(alerta: AlertaIoT):
    print(f"🚨 [ALERTA RECIBIDA] {alerta.tipo_alerta}: {alerta.mensaje} (Valor: {alerta.valor})")
    # Aquí en el futuro guardaremos en la base de datos
    return {"status": "recibido", "alerta": alerta.tipo_alerta}
