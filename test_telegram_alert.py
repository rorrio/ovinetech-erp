# test_telegram.py
from src.core.notifications import send_telegram_alert

print("Probando envío...")
send_telegram_alert("Prueba de integración. Si lees esto, OvineTech está conectado a tu bolsillo.")