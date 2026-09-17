import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'farmasi-puskesmas-lplpo-secret-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(BASE_DIR, 'farmasi_lplpo.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Konfigurasi Telegram Bot
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or '8662797242:AAEZcWIT5XCh0vhNY_vdXtaA2omp0LmvU4M'
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') or '-5521448830'
