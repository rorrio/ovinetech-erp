from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class EstadoCiclo(str, Enum):
    GERMINANDO = "GERMINANDO"
    LISTO = "LISTO"
    COSECHADO = "COSECHADO"

class FVHCicloBase(SQLModel):
    fecha_siembra: datetime = Field(default_factory=datetime.utcnow)
    tipo_semilla: str
    peso_semilla_kg: float
    estado: EstadoCiclo = Field(default=EstadoCiclo.GERMINANDO)

class FVHCiclo(FVHCicloBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cosechas: List["FVHCosecha"] = Relationship(back_populates="ciclo")

class FVHCicloCreate(FVHCicloBase):
    pass

class FVHCosechaBase(SQLModel):
    ciclo_id: int = Field(foreign_key="fvhciclo.id")
    fecha_cosecha: datetime = Field(default_factory=datetime.utcnow)
    peso_final_pasto_kg: float

class FVHCosecha(FVHCosechaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ciclo: Optional[FVHCiclo] = Relationship(back_populates="cosechas")

    @property
    def ratio_conversion(self) -> float:
        if self.ciclo and self.ciclo.peso_semilla_kg > 0:
            return self.peso_final_pasto_kg / self.ciclo.peso_semilla_kg
        return 0.0

class FVHCosechaCreate(FVHCosechaBase):
    pass
