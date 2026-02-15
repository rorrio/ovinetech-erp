import requests
import os

# Idealmente, estos valores vienen de variables de entorno (.env)
# Pero puedes pegarlos aquí temporalmente para probar.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN", ")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "2105670102")

def send_telegram_alert(message: str):
    """
    Envía un mensaje urgente a tu celular vía Telegram.
    """
    if "PEGAR_TU" in TELEGRAM_BOT_TOKEN:
        print("❌ Error: Faltan configurar las credenciales de Telegram.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Formato del mensaje (Markdown para negritas)
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🚨 *ALERTA OvineTech* 🚨\n\n{message}",
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            print(f"⚠️ Error Telegram: {response.text}")
        else:
            print(f"✅ Notificación enviada: {message}")
    except Exception as e:
        print(f"❌ Error de conexión con Telegram: {e}")