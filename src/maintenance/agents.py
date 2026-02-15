from datetime import datetime, timedelta
from typing import List
from .models import Equipment, CleaningLog


class MaintenanceAgent:
    def __init__(self, db_connection):
        self.db = db_connection # Simulación de conexión a base de datos

    def _get_last_log(self, equipment_id: str) -> Optional[CleaningLog]:
        # Aquí harías la query real a tu DB ordenando por fecha desc
        # Retorno simulado para el ejemplo:
        return self.db.get_last_log_for(equipment_id)

    def validate_equipment_readiness(self, equipment: Equipment) -> dict:
        """
        Verifica si un equipo está apto para entrar en producción.
        Retorna un diccionario con status y motivo.
        """
        
        # 1. Si el equipo no requiere sanitización (ej. una carretilla externa), pasa.
        if not equipment.requires_sanitization:
            return {"ready": True, "reason": "No requiere sanitización crítica."}

        last_log = self._get_last_log(equipment.id)

        # 2. Verificar existencia de registro
        if not last_log:
            return {
                "ready": False, 
                "reason": "CRÍTICO: No hay registros de limpieza previos."
            }

        # 3. Verificar calidad de la limpieza
        if not last_log.is_successful():
             return {
                "ready": False, 
                "reason": "La última limpieza falló (pH incorrecto o inspección visual rechazada)."
            }

        # 4. Verificar la "Ventana de Esterilidad" (Tiempo)
        time_elapsed = datetime.now() - last_log.timestamp
        if time_elapsed > timedelta(hours=equipment.max_sterile_hours):
            return {
                "ready": False, 
                "reason": f"EXPIRADO: Limpieza realizada hace {time_elapsed}. Límite seguro: {equipment.max_sterile_hours}h."
            }

        # Si pasa todo:
        return {
            "ready": True, 
            "reason": f"OK. Limpio hace {str(time_elapsed).split('.')[0]} horas."
        }

    def register_cleaning(self, log: CleaningLog):
        # Guardar en DB y disparar alertas si falló
        print(f"[{log.timestamp}] Registrando limpieza para {log.equipment_id}...")
        if not log.is_successful():
            print(" ALERTA: Intento de limpieza fallido registrado.")
        self.db.save(log)

    def check_critical_sanitization_status(self) -> List[str]:
        """
        Escanea TODOS los equipos críticos. 
        Retorna una lista de alertas si alguno excedió su ventana de limpieza.
        """
        alerts = []
        # Imaginemos que obtenemos todos los equipos que requieren sanitización
        critical_equipment = self.db.get_all_equipment(requires_sanitization=True)

        for eq in critical_equipment:
            last_log = self._get_last_log(eq.id)
            
            # CASO A: Nunca se ha limpiado (y ya debería estar operativo)
            if not last_log:
                alerts.append(f"URGENTE: {eq.name} nunca ha registrado limpieza.")
                continue

            # CASO B: Se limpió, pero hace demasiado tiempo (Regla de las 12 horas)
            # Nota: Podrías usar eq.max_sterile_hours, o una regla fija de 12h para alertas
            hours_since_cleaning = (datetime.now() - last_log.timestamp).total_seconds() / 3600
            
            # Umbral de alerta: Si pasaron 12 horas desde la última limpieza
            if hours_since_cleaning > 12:
                alerts.append(
                    f"ALERTA SANITARIA: {eq.name} lleva {int(hours_since_cleaning)} horas sin limpieza. "
                    f"Riesgo de contaminación bacteriana."
                )
        
        return alerts
        