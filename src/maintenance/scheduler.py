from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .agents import MaintenanceAgent
from src.core.notifications import send_telegram_alert

def run_sanitization_check():
    """
    Esta función se ejecutará automáticamente en segundo plano.
    """
    print("⏰ [Cron] Iniciando escaneo sanitario programado...")
    
    # Instanciamos el agente (aquí deberías inyectar tu conexión real a DB)
    # db = get_db_connection()
    agent = MaintenanceAgent(db_connection=None) # Mock por ahora
    
    alerts = agent.check_critical_sanitization_status()
    
    if alerts:
        print(f"⚠️ SE DETECTARON {len(alerts)} PROBLEMAS: ENVIANDO A TELEGRAM...")
        # Unimos todas las alertas en un solo mensaje para no saturar tu chat
        mensaje_final = "\n".join([f"• {a}" for a in alerts])
        
        # ¡AQUÍ ESTÁ LA MAGIA!
        send_telegram_alert(mensaje_final)
    else:
        print("✅ [Cron] Todos los equipos están dentro de parámetros sanitarios.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Configurar: Ejecutar cada 1 hora
    scheduler.add_job(
        run_sanitization_check,
        trigger=IntervalTrigger(hours=1), # O minutes=1 para probar rápido
        id='sanitization_check',
        name='Revisar caducidad de limpieza en equipos críticos',
        replace_existing=True
    )
    
    scheduler.start()
    return scheduler