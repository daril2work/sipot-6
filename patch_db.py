import sqlite3

def patch_db():
    conn = sqlite3.connect('farmasi_lplpo.db')
    try:
        conn.execute('ALTER TABLE user ADD COLUMN telegram_chat_id VARCHAR(50);')
        print("Column telegram_chat_id added successfully.")
    except Exception as e:
        print(f"Error (maybe already exists): {e}")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    patch_db()
