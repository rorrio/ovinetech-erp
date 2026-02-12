from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# We might need to import FVHCosecha for type hinting if we want relationship, 
# but simply having the FK ID is enough for the database schema.
# To keep strictly modular without hard coupling on code level (unless needed), 
# we can just define the field. But for SQLModel to know the table, we might need it.
# Ideally, we just use the table name in the FK string.

class LoteOvejasBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None

class LoteOvejas(LoteOvejasBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    eventos_alimentacion: List["EventoAlimentacion"] = Relationship(back_populates="lote")

class LoteOvejasCreate(LoteOvejasBase):
    pass

class EventoAlimentacionBase(SQLModel):
    fecha: datetime = Field(default_factory=datetime.utcnow)
    lote_id: int = Field(foreign_key="loteovejas.id")
    cosecha_fvh_id: int = Field(foreign_key="fvhcosecha.id")
    kilos_ofrecidos: float

class EventoAlimentacion(EventoAlimentacionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lote: Optional[LoteOvejas] = Relationship(back_populates="eventos_alimentacion")

class EventoAlimentacionCreate(EventoAlimentacionBase):
    pass
    # Relationship to FVHCosecha omitted to avoid circular import complexity for now,
    # unless strictly required. The FK enforces the constraint.

class OrdenieDiario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=datetime.utcnow)
    litros_totales: float
    calidad_grasa: float
    calidad_proteina: float
