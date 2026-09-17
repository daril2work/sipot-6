from flask import Blueprint, request, jsonify, current_app
from app.models import db, User, Obat, PermintaanObat, PermintaanObatItem, TransaksiKeluar, TransaksiKeluarItem
from app.services.inventory import process_pengeluaran_fefo
import requests
from datetime import date, datetime

webhook_bp = Blueprint('webhook', __name__, url_prefix='/telegram')

def send_telegram_reply(chat_id, text):
    token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

def answer_callback_query(callback_query_id, text, show_alert=False):
    token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id, "text": text, "show_alert": show_alert}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

def edit_message_text(chat_id, message_id, text):
    token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    url = f"https://api.telegram.org/bot{token}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    if not data:
        return jsonify({'status': 'ok'})

    # 1. Handle Callback Query (Inline Buttons)
    if 'callback_query' in data:
        cb = data['callback_query']
        chat_id = str(cb['message']['chat']['id'])
        message_id = cb['message']['message_id']
        cb_id = cb['id']
        cb_data = cb['data']
        
        # Validasi Akses: Harus Admin (atau Grup Admin)
        admin_chat_id = current_app.config.get('TELEGRAM_CHAT_ID')
        if chat_id != admin_chat_id:
            user = User.query.filter_by(telegram_chat_id=chat_id, role='Admin').first()
            if not user:
                answer_callback_query(cb_id, "Anda tidak memiliki akses sebagai Admin.", show_alert=True)
                return jsonify({'status': 'ok'})
                
        if cb_data.startswith('approve_req_'):
            req_id = int(cb_data.split('_')[2])
            permintaan = PermintaanObat.query.get(req_id)
            if not permintaan:
                answer_callback_query(cb_id, "Data permintaan tidak ditemukan.")
                return jsonify({'status': 'ok'})
            
            if permintaan.status != 'Pending':
                answer_callback_query(cb_id, f"Permintaan sudah {permintaan.status}.")
                edit_message_text(chat_id, message_id, cb['message']['text'] + f"\n\n<b>Status:</b> {permintaan.status}")
                return jsonify({'status': 'ok'})
                
            # Proses Approval (Semua disetujui sesuai yang diminta Poli)
            no_penyerahan = f"POS/REQ/{date.today().strftime('%Y%m%d')}/{int(datetime.utcnow().timestamp())}"
            transaksi = TransaksiKeluar(
                no_penyerahan=no_penyerahan,
                subunit_id=permintaan.subunit_id,
                tanggal_keluar=date.today(),
                keterangan=f"Persetujuan via Telegram {permintaan.no_permintaan}"
            )
            db.session.add(transaksi)
            db.session.flush()
            
            try:
                for item in permintaan.items:
                    qty = item.jumlah_diminta
                    if qty > item.obat.total_stok:
                        raise ValueError(f"Stok {item.obat.nama_obat} tidak cukup (Sisa: {item.obat.total_stok}). Silakan ubah/approve via Web.")
                        
                    item.jumlah_disetujui = qty
                    alokasi_fefo = process_pengeluaran_fefo(item.obat_id, qty)
                    for item_alokasi in alokasi_fefo:
                        item_keluar = TransaksiKeluarItem(
                            transaksi_keluar_id=transaksi.id,
                            obat_id=item.obat_id,
                            batch_id=item_alokasi['batch_id'],
                            jumlah=item_alokasi['jumlah']
                        )
                        db.session.add(item_keluar)
                
                permintaan.status = 'Disetujui'
                permintaan.transaksi_keluar_id = transaksi.id
                db.session.commit()
                
                answer_callback_query(cb_id, "Berhasil disetujui dan stok dipotong (FEFO)!", show_alert=True)
                edit_message_text(chat_id, message_id, cb['message']['text'] + f"\n\n✅ <b>Status: Telah Disetujui Penuh (via Telegram)</b>")
                
            except Exception as e:
                db.session.rollback()
                answer_callback_query(cb_id, str(e), show_alert=True)
                
        elif cb_data.startswith('reject_req_'):
            req_id = int(cb_data.split('_')[2])
            permintaan = PermintaanObat.query.get(req_id)
            if permintaan and permintaan.status == 'Pending':
                permintaan.status = 'Ditolak'
                db.session.commit()
                answer_callback_query(cb_id, "Permintaan Ditolak.")
                edit_message_text(chat_id, message_id, cb['message']['text'] + f"\n\n❌ <b>Status: Ditolak (via Telegram)</b>")

        return jsonify({'status': 'ok'})

    # 2. Handle Text Commands
    if 'message' in data and 'text' in data['message']:
        msg = data['message']
        chat_id = str(msg['chat']['id'])
        text = msg['text'].strip()
        
        user = User.query.filter_by(telegram_chat_id=chat_id).first()
        admin_chat_id = current_app.config.get('TELEGRAM_CHAT_ID')
        
        # Jika perintah /start, biarkan siapa saja memakainya untuk mengecek ID
        if text.startswith('/start'):
            send_telegram_reply(chat_id, f"Halo! Chat ID Anda adalah: <code>{chat_id}</code>\nSilakan berikan ID ini ke Administrator SIPOT untuk ditautkan dengan akun Anda.")
            return jsonify({'status': 'ok'})
            
        # Pengecekan Akses: Izinkan jika dia adalah User terdaftar, ATAU jika dia chat di Grup Admin
        if not user and chat_id != admin_chat_id:
            if text.startswith('/'):
                send_telegram_reply(chat_id, "⛔ Akses ditolak. Akun Telegram Anda belum ditautkan dengan SIPOT. Ketik /start untuk melihat Chat ID Anda.")
            return jsonify({'status': 'ok'})
            
        # Fitur cek stok (contoh: /stok paracetamol)
        if text.startswith('/stok'):
            parts = text.split(maxsplit=1)
            if len(parts) > 1:
                keyword = parts[1]
                obats = Obat.query.filter(Obat.nama_obat.ilike(f"%{keyword}%")).limit(10).all()
                if not obats:
                    send_telegram_reply(chat_id, f"Tidak ada obat yang cocok dengan '{keyword}'")
                else:
                    reply = f"🔍 <b>Pencarian: {keyword}</b>\n\n"
                    for o in obats:
                        reply += f"💊 {o.nama_obat}\nStok: <b>{o.total_stok} {o.satuan}</b>\n\n"
                    send_telegram_reply(chat_id, reply)
            else:
                send_telegram_reply(chat_id, "Format salah. Gunakan: <code>/stok [nama_obat]</code>\nContoh: <code>/stok paracetamol</code>")
                
    return jsonify({'status': 'ok'})
