from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Mengeksekusi Server Farmasi Puskesmas (LPLPO)...")
    app.run(host='0.0.0.0', port=5000, debug=True)
