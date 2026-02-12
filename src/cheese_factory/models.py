from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator

class LoteQuesoBase(SQLModel):
    fecha_elaboracion: datetime = Field(default_factory=datetime.utcnow)
    tipo_queso: str
    litros_leche_usados: float
    
    # Process Phase
    ph_inicial: Optional[float] = None
    ph_corte: Optional[float] = None
    temp_coagulacion: Optional[float] = None
    tiempo_floculacion_min: Optional[int] = None
    
    # Yield Phase
    peso_cuajada_fresca_kg: Optional[float] = None
    peso_salida_prensa_kg: Optional[float] = None

class LoteQueso(LoteQuesoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    maduracion_logs: List["MaduracionLog"] = Relationship(back_populates="lote_queso")

class LoteQuesoCreate(LoteQuesoBase):
    pass


class MaduracionLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lote_queso_id: int = Field(foreign_key="lotequeso.id")
    fecha_control: datetime = Field(default_factory=datetime.utcnow)
    peso_actual_kg: float
    humedad_camara_pct: float
    notas: Optional[str] = None
    
    lote_queso: Optional[LoteQueso] = Relationship(back_populates="maduracion_logs")
