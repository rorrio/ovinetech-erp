from datetime import date, datetime
from typing import Optional, List
from enum import Enum
import uuid

from sqlalchemy import ForeignKey, String, Date, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlmodel import SQLModel, Field, Relationship

# --- Shared Base for SQLAlchemy 2.0 Models ---
# We use SQLModel.metadata ensuring compatibility with the existing alembic/database setup
class Base(DeclarativeBase):
    metadata = SQLModel.metadata

# --- Enums for Animal Entity ---
class Raza(str, Enum):
    FRIESIAN = "Friesian"
    TEXEL = "Texel"
    PAMPINTA = "Pampinta"
    CRUZA = "Cruza"
    CORRIEDALE = "Corriedale"
    OTRA = "Otra"

class Sexo(str, Enum):
    MACHO = "M"
    HEMBRA = "F"

class Origen(str, Enum):
    PROPIO = "Propio"
    COMPRA_EXTERNA = "Compra Externa"

class EstadoProductivo(str, Enum):
    CRECIMIENTO = "Crecimiento"
    SERVICIO = "Servicio"
    GESTACION = "Gestación"
    LACTANCIA = "Lactancia"
    SECA = "Seca"
    ENGORDE = "Engorde"

# --- Main Entity: Animal (Oveja) ---
class Animal(Base):
    """
    Representa una oveja individual dentro del sistema OvineTech.
    Utiliza SQLAlchemy 2.0 imperative mapping style.
    """
    __tablename__ = "animal"

    # Identificadores
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    rfid_tag: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True, comment="Tag RFID único para trazabilidad electrónica")
    caravana_visual: Mapped[str] = mapped_column(String, index=True, comment="Identificador visual (areta) para manejo en campo")

    # Datos Fijos
    raza: Mapped[Raza] = mapped_column(comment="Raza principal del animal")
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    sexo: Mapped[Sexo] = mapped_column(comment="Sexo del animal (M/F)")
    origen: Mapped[Origen] = mapped_column(default=Origen.PROPIO)

    # Estado Dinámico
    estado_productivo: Mapped[EstadoProductivo] = mapped_column(default=EstadoProductivo.CRECIMIENTO, comment="Estado actual en el ciclo productivo")
    peso_actual: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="Ültimo peso registrado en kg")
    fecha_ultima_pesada: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relaciones
    # Self-referential relationships for genealogy
    madre_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("animal.id"), nullable=True)
    padre_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("animal.id"), nullable=True)

    # Relationship to Lote (using the existing SQLModel LoteOvejas table name 'loteovejas')
    # Note: LoteOvejas uses SQLModel which defaults table name to class name lowercased or snake_cased?
    # SQLModel defaults to class name. Let's assume 'loteovejas' based on previous context or standard SQLModel behavior.
    # We will use string reference 'loteovejas.id' assuming the table name.
    lote_actual_id: Mapped[Optional[int]] = mapped_column(ForeignKey("loteovejas.id"), nullable=True)

    # ORM Relationships
    madre: Mapped[Optional["Animal"]] = relationship("Animal", remote_side=[id], foreign_keys=[madre_id], backref="hijos_madre")
    padre: Mapped[Optional["Animal"]] = relationship("Animal", remote_side=[id], foreign_keys=[padre_id], backref="hijos_padre")
    
    # We can define relationship to Lote if needed, but since Lote is SQLModel, we might need a wrapper or just rely on ID for now logic-wise.
    # To keep it simple and strictly following "SQLAlchemy 2.0" request for this class:
    # lote: Mapped[Optional["LoteOvejas"]] = relationship("LoteOvejas", back_populates="animales") # Requires import

    @property
    def edad_meses(self) -> float:
        """Calcula la edad actual en meses."""
        today = date.today()
        # Calculate difference in months
        age_months = (today.year - self.fecha_nacimiento.year) * 12 + (today.month - self.fecha_nacimiento.month)
        # Adjust for day
        if today.day < self.fecha_nacimiento.day:
            age_months -= 1
        
        # If less than 1 month, return explicit 0 or decimal fraction? 
        # Requirement says "Edad en Meses". Integer or Float? 
        # Let's return a float for precision if needed, or int. 
        # Standard logic usually returns int months.
        # But for "Corderos" days matter.
        # Let's keep it simple: approximate months.
        
        delta = today - self.fecha_nacimiento
        return round(delta.days / 30.44, 1) # 30.44 is avg days in month


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
