import requests
import os

# Ganti dengan token bot Anda
TOKEN = "8662797242:AAEZcWIT5XCh0vhNY_vdXtaA2omp0LmvU4M"

# Ganti dengan URL domain PythonAnywhere Anda
# HARUS HTTPS
DOMAIN = "https://yourusername.pythonanywhere.com"

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
payload = {
    "url": f"{DOMAIN}/telegram/webhook"
}

print(f"Setting webhook to {payload['url']} ...")
response = requests.post(url, json=payload)
print(response.json())
