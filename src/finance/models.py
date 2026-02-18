from datetime import datetime, date
from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field

class TipoTransaccion(str, Enum):
    INGRESO = "INGRESO"
    GASTO = "GASTO"

class TransaccionBase(SQLModel):
    fecha: datetime = Field(default_factory=datetime.now)
    tipo: TipoTransaccion
    categoria: str # Ej: "Venta Queso", "Compra Insumos", "Pago Servicios"
    monto: float
    descripcion: Optional[str] = None

class Transaccion(TransaccionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class TransaccionCreate(TransaccionBase):
    pass

class MetaCapitalBase(SQLModel):
    nombre_objetivo: str
    monto_objetivo: float
    fecha_limite: date

class MetaCapital(MetaCapitalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class MetaCapitalCreate(MetaCapitalBase):
    pass
