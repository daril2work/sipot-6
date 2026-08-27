from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Obat, BatchObat, StokOpname, StokOpnameItem, PenyesuaianStok
from datetime import datetime, date

stok_opname_bp = Blueprint('stok_opname', __name__, url_prefix='/stok-opname')

@stok_opname_bp.route('/')
def list_stok_opname():
    opnames = StokOpname.query.order_by(StokOpname.tanggal_opname.desc(), StokOpname.id.desc()).all()
    return render_template('stok_opname/list.html', opnames=opnames)

@stok_opname_bp.route('/buat', methods=['GET', 'POST'])
def buat_stok_opname():
    if request.method == 'POST':
        tgl_str = request.form.get('tanggal_opname', '').strip()
        petugas = request.form.get('petugas_opname', 'Daril Rahmatullah, S. Farm.').strip()
        penanggung_jawab = request.form.get('penanggung_jawab', 'dr. Durotun Nafisa, M.H').strip()
        keterangan = request.form.get('keterangan', '').strip()

        tgl = date.today()
        if tgl_str:
            try:
                tgl = datetime.strptime(tgl_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        no_opname = f"SO/{tgl.year}/{tgl.month:02d}/{StokOpname.query.count() + 1:03d}"

        opname = StokOpname(
            no_opname=no_opname,
            tanggal_opname=tgl,
            status='Draft',
            petugas_opname=petugas,
            penanggung_jawab=penanggung_jawab,
            keterangan=keterangan
        )
        db.session.add(opname)
        db.session.flush()

        # Otomatis muat seluruh batch obat yang aktif ke dalam lembar opname
        batches = BatchObat.query.join(Obat).order_by(Obat.nama_obat.asc(), BatchObat.expired_date.asc()).all()
        for b in batches:
            item = StokOpnameItem(
                stok_opname_id=opname.id,
                batch_id=b.id,
                obat_id=b.obat_id,
                stok_sistem=b.stok_sekarang,
                stok_fisik=b.stok_sekarang, # Default fisik = sistem
                selisih=0,
                keterangan=''
            )
            db.session.add(item)

        db.session.commit()
        flash(f'Dokumen Stok Opname {no_opname} berhasil dibuat dengan {len(batches)} batch obat.', 'success')
        return redirect(url_for('stok_opname.detail_stok_opname', id=opname.id))

    today_str = date.today().strftime('%Y-%m-%d')
    return render_template('stok_opname/form.html', today_str=today_str)

@stok_opname_bp.route('/<int:id>')
def detail_stok_opname(id):
    opname = StokOpname.query.get_or_404(id)
    items = StokOpnameItem.query.filter_by(stok_opname_id=id).join(Obat).order_by(Obat.nama_obat.asc()).all()
    return render_template('stok_opname/detail.html', opname=opname, items=items)

@stok_opname_bp.route('/<int:id>/update-item', methods=['POST'])
def update_item_opname(id):
    opname = StokOpname.query.get_or_404(id)
    if opname.status == 'Final':
        return jsonify({'status': 'error', 'message': 'Dokumen sudah difinalkan & terkunci.'}), 400

    item_id = request.form.get('item_id', type=int)
    stok_fisik = request.form.get('stok_fisik', type=int, default=0)
    keterangan = request.form.get('keterangan', '').strip()

    item = StokOpnameItem.query.get_or_404(item_id)
    if item.stok_opname_id != opname.id:
        return jsonify({'status': 'error', 'message': 'Item tidak valid.'}), 400

    item.stok_fisik = max(0, stok_fisik)
    item.selisih = item.stok_fisik - item.stok_sistem
    item.keterangan = keterangan
    db.session.commit()

    return jsonify({
        'status': 'success',
        'selisih': item.selisih,
        'stok_fisik': item.stok_fisik
    })

@stok_opname_bp.route('/<int:id>/finalkan', methods=['POST'])
def finalkan_stok_opname(id):
    opname = StokOpname.query.get_or_404(id)
    if opname.status == 'Final':
        flash('Dokumen Stok Opname ini sudah difinalkan sebelumnya.', 'warning')
        return redirect(url_for('stok_opname.detail_stok_opname', id=id))

    # Terapkan penyesuaian fisik ke stok batch sistem
    items = StokOpnameItem.query.filter_by(stok_opname_id=id).all()
    count_adjusted = 0

    for item in items:
        batch = BatchObat.query.get(item.batch_id)
        if batch and item.selisih != 0:
            stok_sebelum = batch.stok_sekarang
            stok_setelah = item.stok_fisik
            batch.stok_sekarang = stok_setelah

            # Log ke PenyesuaianStok
            jenis = 'Penambahan' if item.selisih > 0 else 'Pengurangan'
            record = PenyesuaianStok(
                batch_id=batch.id,
                obat_id=batch.obat_id,
                jenis_penyesuaian=jenis,
                kategori_alasan='Koreksi Fisik',
                stok_sebelum=stok_sebelum,
                jumlah_penyesuaian=abs(item.selisih),
                stok_setelah=stok_setelah,
                tanggal_penyesuaian=opname.tanggal_opname,
                keterangan=f"Hasil Stok Opname {opname.no_opname}. {item.keterangan}".strip(),
                petugas=opname.petugas_opname
            )
            db.session.add(record)
            count_adjusted += 1

    opname.status = 'Final'
    db.session.commit()

    flash(f'Dokumen Stok Opname {opname.no_opname} berhasil difinalkan! {count_adjusted} batch obat disesuaikan stok fisik nya.', 'success')
    return redirect(url_for('stok_opname.detail_stok_opname', id=id))

@stok_opname_bp.route('/<int:id>/print')
def print_stok_opname(id):
    opname = StokOpname.query.get_or_404(id)
    items = StokOpnameItem.query.filter_by(stok_opname_id=id).join(Obat).order_by(Obat.nama_obat.asc()).all()
    return render_template('stok_opname/print.html', opname=opname, items=items)
