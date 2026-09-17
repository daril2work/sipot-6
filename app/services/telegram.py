import requests
from flask import current_app

def send_telegram_notification(message, reply_markup=None):
    token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    chat_id = current_app.config.get('TELEGRAM_CHAT_ID')

    if not token or not chat_id or 'REPLACE_WITH_FULL_TOKEN' in token:
        # Jangan kirim jika token belum lengkap
        print("Telegram notification skipped: Token not configured.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram notification error: {e}")
        return False
