from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from app.models import db, Obat, SubUnit, PermintaanObat, PermintaanObatItem, TransaksiKeluar, TransaksiKeluarItem, BatchObat
from app.services.inventory import process_pengeluaran_fefo
from app.services.telegram import send_telegram_notification
from datetime import datetime, date

permintaan_bp = Blueprint('permintaan', __name__, url_prefix='/permintaan')

# ---- SUB-UNIT ROUTES ----
@permintaan_bp.route('/saya')
def list_saya():
    if session.get('role') != 'SubUnit':
        return redirect(url_for('dashboard.index'))
    
    subunit_id = session.get('subunit_id')
    page = request.args.get('page', 1, type=int)
    pagination = PermintaanObat.query.filter_by(subunit_id=subunit_id).order_by(PermintaanObat.tanggal_permintaan.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('permintaan/list.html', permintaan_list=pagination.items, pagination=pagination)

@permintaan_bp.route('/buat', methods=['GET', 'POST'])
def buat_permintaan():
    if session.get('role') != 'SubUnit':
        return redirect(url_for('dashboard.index'))
    
    subunit_id = session.get('subunit_id')
    subunit = SubUnit.query.get(subunit_id)
    
    if request.method == 'POST':
        keterangan = request.form.get('keterangan', '').strip()
        obat_ids = request.form.getlist('obat_id[]')
        jumlahs = request.form.getlist('jumlah[]')

        if not obat_ids:
            flash('Minimal 1 item obat wajib dipilih.', 'danger')
            return redirect(url_for('permintaan.buat_permintaan'))

        no_permintaan = f"REQ/{date.today().strftime('%Y%m%d')}/{int(datetime.utcnow().timestamp())}"
        permintaan = PermintaanObat(
            no_permintaan=no_permintaan,
            subunit_id=subunit_id,
            keterangan=keterangan
        )
        db.session.add(permintaan)
        db.session.flush()

        item_names = []
        
        for idx in range(len(obat_ids)):
            if not obat_ids[idx] or not jumlahs[idx]:
                continue
            qty = int(jumlahs[idx])
            if qty <= 0:
                continue
                
            o_id = int(obat_ids[idx])
            item = PermintaanObatItem(
                permintaan_id=permintaan.id,
                obat_id=o_id,
                jumlah_diminta=qty
            )
            db.session.add(item)
            
            obat = Obat.query.get(o_id)
            if obat:
                item_names.append(f"- {obat.nama_obat} ({qty} {obat.satuan})")

        db.session.commit()
        
        # Kirim notifikasi Telegram
        nama_poli = subunit.nama_subunit if subunit else "Poli/Sub-Unit"
        pesan_tele = f"🔔 <b>Permintaan Obat Baru!</b>\n\n<b>Dari:</b> {nama_poli}\n<b>Nomor:</b> {no_permintaan}\n<b>Ket:</b> {keterangan}\n\n<b>Item Diminta:</b>\n"
        pesan_tele += "\n".join(item_names)
        pesan_tele += "\n\nMohon segera diperiksa di sistem SIPOT atau klik tombol di bawah ini."
        
        # Buat Inline Keyboard
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ Setujui Semua", "callback_data": f"approve_req_{permintaan.id}"},
                    {"text": "❌ Tolak", "callback_data": f"reject_req_{permintaan.id}"}
                ]
            ]
        }
        
        send_telegram_notification(pesan_tele, reply_markup=reply_markup)

        flash('Permintaan obat berhasil dikirim ke Gudang Farmasi.', 'success')
        return redirect(url_for('permintaan.list_saya'))

    obats = Obat.query.order_by(Obat.nama_obat.asc()).all()
    return render_template('permintaan/form.html', obats=obats)

# ---- ADMIN ROUTES ----
@permintaan_bp.route('/masuk')
def list_masuk():
    if session.get('role') != 'Admin':
        return redirect(url_for('dashboard.index'))
        
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = PermintaanObat.query
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    pagination = query.order_by(
        db.case(
            (PermintaanObat.status == 'Pending', 1),
            else_=2
        ),
        PermintaanObat.tanggal_permintaan.desc()
    ).paginate(page=page, per_page=15, error_out=False)
    
    return render_template('permintaan/admin_list.html', permintaan_list=pagination.items, pagination=pagination, status_filter=status_filter)

@permintaan_bp.route('/approve/<int:id>', methods=['GET', 'POST'])
def approve_permintaan(id):
    if session.get('role') != 'Admin':
        return redirect(url_for('dashboard.index'))
        
    permintaan = PermintaanObat.query.get_or_404(id)
    
    if request.method == 'POST':
        if permintaan.status != 'Pending':
            flash('Permintaan ini sudah diproses.', 'warning')
            return redirect(url_for('permintaan.list_masuk'))
            
        action = request.form.get('action')
        
        if action == 'reject':
            permintaan.status = 'Ditolak'
            db.session.commit()
            flash(f'Permintaan {permintaan.no_permintaan} telah ditolak.', 'danger')
            return redirect(url_for('permintaan.list_masuk'))
            
        # Approval
        jumlah_disetujui_list = request.form.getlist('jumlah_disetujui[]')
        item_ids = request.form.getlist('item_id[]')
        
        no_penyerahan = f"POS/REQ/{date.today().strftime('%Y%m%d')}/{int(datetime.utcnow().timestamp())}"
        transaksi = TransaksiKeluar(
            no_penyerahan=no_penyerahan,
            subunit_id=permintaan.subunit_id,
            tanggal_keluar=date.today(),
            keterangan=f"Persetujuan Permintaan {permintaan.no_permintaan}"
        )
        db.session.add(transaksi)
        db.session.flush()
        
        try:
            for idx in range(len(item_ids)):
                item = PermintaanObatItem.query.get(int(item_ids[idx]))
                if not item or item.permintaan_id != permintaan.id:
                    continue
                    
                qty_setuju = int(jumlah_disetujui_list[idx])
                item.jumlah_disetujui = qty_setuju
                
                if qty_setuju <= 0:
                    continue
                    
                alokasi_fefo = process_pengeluaran_fefo(item.obat_id, qty_setuju)
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
            
            # Notifikasi ke subunit (opsional) atau selesai
            flash(f'Permintaan {permintaan.no_permintaan} disetujui. Bukti distribusi dibuat.', 'success')
            return redirect(url_for('permintaan.list_masuk'))
            
        except ValueError as err:
            db.session.rollback()
            flash(str(err), 'danger')
            return redirect(url_for('permintaan.approve_permintaan', id=id))

    return render_template('permintaan/admin_approval.html', permintaan=permintaan)
