from typing import Optional
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field

# Enumeración para tipos de acción en saneamiento
class AccionSaneamiento(str, Enum):
    LIMPIEZA = "LIMPIEZA"          # Remoción de suciedad física
    DESINFECCION = "DESINFECCION"  # Eliminación de microorganismos

class RegistroSaneamiento(SQLModel, table=True):
    """Registro de Procedimientos Operativos Estandarizados de Saneamiento (SSOP)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    area_equipo: str = Field(index=True)  # Ej: "Tina Quesera 01", "Paredes Cámara"
    fecha_hora: datetime = Field(default_factory=datetime.now)
    tipo: AccionSaneamiento
    agente_quimico: str                   # Ej: "Soda Cáustica", "Ácido Peracético"
    concentracion: Optional[str] = None    # Ej: "2%", "200ppm"
    responsable: str                      # Nombre del operario
    verificado_por: Optional[str] = None   # Firma/Nombre del supervisor

class ControlAgua(SQLModel, table=True):
    """Monitoreo de potabilidad del agua"""
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=datetime.now)
    cloro_residual_ppm: float             # Rango típico: 0.2 - 2.0 ppm
    ph: float                             # Acidez del agua
    apto_consumo: bool                    # Resultado microbiológico
    nro_informe_laboratorio: str
    adjunto_url: Optional[str] = None     # Link al PDF del informe oficial

class ControlPlagas(SQLModel, table=True):
    """Registro de inspección y cebado de trampas"""
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha_inspeccion: datetime = Field(default_factory=datetime.now)
    trampas_inspeccionadas: int
    trampas_con_actividad: int
    hallazgos: Optional[str] = None
    empresa_servicio: str                 # Empresa habilitada contratada
    nro_registro_empresa: str             # Registro ante MGAP/Intendencia