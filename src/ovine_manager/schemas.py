from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .models import Raza, Sexo, Origen, EstadoProductivo

class AnimalBase(BaseModel):
    """Esquema base con campos comunes para crear y leer."""
    rfid_tag: Optional[str] = Field(default=None, description="Tag RFID único")
    caravana_visual: str = Field(..., description="Identificador visual", min_length=1)
    raza: Raza
    fecha_nacimiento: date
    sexo: Sexo
    origen: Origen = Origen.PROPIO
    madre_id: Optional[UUID] = None
    padre_id: Optional[UUID] = None
    lote_actual_id: Optional[int] = None

class AnimalCreate(AnimalBase):
    """Esquema para la creación de un nuevo animal."""
    pass

class AnimalRead(AnimalBase):
    """Esquema para la lectura (DTO) de un animal, incluyendo campos calculados."""
    id: UUID
    estado_productivo: EstadoProductivo
    peso_actual: Optional[float] = None
    fecha_ultima_pesada: Optional[datetime] = None
    edad_meses: float = Field(..., description="Edad calculada en meses")

    model_config = ConfigDict(from_attributes=True)
