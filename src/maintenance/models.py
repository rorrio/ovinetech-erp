from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
import uuid

# Tipos de limpieza para estandarizar
class CleaningType(str, Enum):
    CIP = "CIP_AUTOMATICO"      # Clean In Place (Sistemas de tuberías/bombas)
    MANUAL = "MANUAL_PROFUNDO"  # Desarme y cepillado (Válvulas, moldes)
    RINSING = "ENJUAGUE"        # Solo agua (entre lotes rápidos)

# Modelo del Equipo (Simplificado para este contexto)
class Equipment(BaseModel):
    id: str
    name: str
    requires_sanitization: bool = True # Si toca leche/queso, es True. Si es un motor, False.
    max_sterile_hours: int = 4  # Tiempo máx que aguanta limpio sin usar (Regla sanitaria)

# El Log de Limpieza (La evidencia)
class CleaningLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    equipment_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    performed_by: str  # ID del usuario o "SYSTEM_AUTO"
    cleaning_type: CleaningType
    chemicals_used: List[str]  # Ej: ["Cloro", "Ácido Peracético"]
    ph_check: Optional[float] = None  # Dato de sensor (crítico para CIP)
    visual_check_passed: bool = True  # Verificación humana o por cámara
    
    # Propiedad calculada para saber si el log es válido sanitariamente
    def is_successful(self) -> bool:
        # Lógica: Debe pasar inspección visual y, si hay pH, estar en rango seguro
        if not self.visual_check_passed:
            return False
        if self.ph_check is not None and (self.ph_check < 6.0 or self.ph_check > 8.0):
             # Ejemplo: Si quedó ácido residual, falla.
            return False
        return True