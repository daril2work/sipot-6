from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models import db, Obat, SubUnit, TransaksiKeluar, TransaksiKeluarItem, BatchObat
from app.services.inventory import process_pengeluaran_fefo
from datetime import datetime, date

pos_bp = Blueprint('pos', __name__, url_prefix='/pos')

@pos_bp.route('/')
def pos_index():
    subunits = SubUnit.query.order_by(SubUnit.nama_subunit.asc()).all()
    obats = Obat.query.filter(Obat.id.in_(
        db.session.query(BatchObat.obat_id).filter(BatchObat.stok_sekarang > 0)
    )).order_by(Obat.nama_obat.asc()).all()

    # Sertakan detail obat dalam format serializable untuk Alpine.js
    obats_data = []
    for o in obats:
        batch_ed = o.batch_terdekat_ed
        obats_data.append({
            'id': o.id,
            'kode_obat': o.kode_obat,
            'nama_obat': o.nama_obat,
            'bentuk_sediaan': o.bentuk_sediaan,
            'satuan': o.satuan,
            'kategori': o.kategori,
            'harga_satuan': o.harga_satuan,
            'total_stok': o.total_stok,
            'ed_terdekat': batch_ed.expired_date.strftime('%d-%m-%Y') if batch_ed else '-'
        })

    return render_template('pos.html', subunits=subunits, obats_json=obats_data)

@pos_bp.route('/checkout', methods=['POST'])
def pos_checkout():
    data = request.get_json() or request.form
    subunit_id = data.get('subunit_id')
    keterangan = data.get('keterangan', 'Pelayanan POS Obat / Distribusi').strip()
    items = data.get('items', [])

    if not subunit_id or not items:
        return jsonify({'status': 'error', 'message': 'Sub-Unit dan minimal 1 item obat wajib dipilih.'}), 400

    try:
        no_penyerahan = f"POS/{date.today().strftime('%Y%m%d')}/{int(datetime.utcnow().timestamp())}"
        transaksi = TransaksiKeluar(
            no_penyerahan=no_penyerahan,
            subunit_id=int(subunit_id),
            tanggal_keluar=date.today(),
            keterangan=keterangan
        )
        db.session.add(transaksi)
        db.session.flush()

        for item_req in items:
            o_id = int(item_req.get('obat_id'))
            qty = int(item_req.get('jumlah'))
            if qty <= 0:
                continue

            # Jalankan alokasi FEFO
            alokasi_fefo = process_pengeluaran_fefo(o_id, qty)
            for alok in alokasi_fefo:
                k_item = TransaksiKeluarItem(
                    transaksi_keluar_id=transaksi.id,
                    obat_id=o_id,
                    batch_id=alok['batch_id'],
                    jumlah=alok['jumlah']
                )
                db.session.add(k_item)

        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Transaksi POS penyerahan obat berhasil disimpan.',
            'transaksi_id': transaksi.id
        })
    except ValueError as err:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(err)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f"Terjadi kesalahan server: {str(e)}"}), 500

@pos_bp.route('/receipt/<int:id>')
def pos_receipt(id):
    transaksi = TransaksiKeluar.query.get_or_404(id)
    return render_template('pos_receipt.html', transaksi=transaksi)
