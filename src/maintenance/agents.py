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