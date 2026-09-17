#!/bin/bash
# Script untuk update/pull kode dari GitHub di PythonAnywhere

echo "=== Memulai proses update SIPOT ==="

# Pindah ke direktori aplikasi (Ganti 'sipot-6-flask' dengan nama folder Anda di PythonAnywhere jika berbeda)
cd ~/sipot-6-flask || { echo "Gagal masuk ke direktori aplikasi. Periksa nama foldernya."; exit 1; }

# 1. Menarik perubahan terbaru dari branch main (atau master)
echo "📥 Pulling perubahan terbaru dari GitHub..."
git pull origin main

# 2. Mengaktifkan virtual environment (Opsional, hapus tanda '#' di bawah jika Anda menggunakan venv)
# source ~/.virtualenvs/my-virtualenv/bin/activate

# 3. Menginstall/update dependensi jika ada perubahan di requirements.txt
echo "📦 Memeriksa dependensi Python (requirements.txt)..."
pip install -r requirements.txt

# 4. Patching / Migrasi Database (Jika ada pembaruan seperti kolom telegram_chat_id)
# Jika tidak diperlukan setiap saat, Anda bisa menonaktifkannya
echo "🗄️ Menjalankan patch database (jika ada)..."
python patch_db.py

echo "✅ Proses update selesai!"
echo "⚠️  PENTING: Jangan lupa klik tombol 'Reload' pada tab Web di dashboard PythonAnywhere agar perubahan berlaku."
