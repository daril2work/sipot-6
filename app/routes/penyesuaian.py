from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Obat, BatchObat, PenyesuaianStok
from datetime import datetime, date

penyesuaian_bp = Blueprint('penyesuaian', __name__, url_prefix='/penyesuaian')

@penyesuaian_bp.route('/')
def list_penyesuaian():
    query = request.args.get('q', '').strip()
    alasan_filter = request.args.get('alasan', '').strip()

    penyesuaian_query = PenyesuaianStok.query.join(Obat).join(BatchObat)

    if query:
        penyesuaian_query = penyesuaian_query.filter(
            (Obat.nama_obat.ilike(f'%{query}%')) |
            (Obat.kode_obat.ilike(f'%{query}%')) |
            (BatchObat.no_batch.ilike(f'%{query}%'))
        )

    if alasan_filter:
        penyesuaian_query = penyesuaian_query.filter(PenyesuaianStok.kategori_alasan == alasan_filter)

    records = penyesuaian_query.order_by(PenyesuaianStok.created_at.desc()).all()
    obats = Obat.query.order_by(Obat.nama_obat.asc()).all()

    return render_template('penyesuaian/list.html', records=records, obats=obats, query=query, selected_alasan=alasan_filter)

@penyesuaian_bp.route('/tambah', methods=['GET', 'POST'])
def tambah_penyesuaian():
    if request.method == 'POST':
        batch_id = request.form.get('batch_id', type=int)
        jenis_penyesuaian = request.form.get('jenis_penyesuaian', 'Pengurangan').strip()
        kategori_alasan = request.form.get('kategori_alasan', 'Rusak').strip()
        jumlah = request.form.get('jumlah', type=int, default=0)
        tgl_str = request.form.get('tanggal_penyesuaian', '').strip()
        keterangan = request.form.get('keterangan', '').strip()
        petugas = request.form.get('petugas', 'Daril Rahmatullah, S. Farm.').strip()

        if not batch_id or jumlah <= 0:
            flash('Batch obat dan jumlah penyesuaian wajib diisi dengan benar.', 'danger')
            return redirect(url_for('penyesuaian.tambah_penyesuaian'))

        batch = BatchObat.query.get_or_404(batch_id)
        stok_sebelum = batch.stok_sekarang

        if jenis_penyesuaian == 'Pengurangan':
            if jumlah > stok_sebelum:
                flash(f'Jumlah pengurangan ({jumlah}) melebihi stok batch saat ini ({stok_sebelum}).', 'danger')
                return redirect(url_for('penyesuaian.tambah_penyesuaian'))
            stok_setelah = stok_sebelum - jumlah
        else:
            stok_setelah = stok_sebelum + jumlah

        # Tanggal Penyesuaian
        tgl = date.today()
        if tgl_str:
            try:
                tgl = datetime.strptime(tgl_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Apply update to Batch
        batch.stok_sekarang = stok_setelah

        # Audit Log Record
        record = PenyesuaianStok(
            batch_id=batch.id,
            obat_id=batch.obat_id,
            jenis_penyesuaian=jenis_penyesuaian,
            kategori_alasan=kategori_alasan,
            stok_sebelum=stok_sebelum,
            jumlah_penyesuaian=jumlah,
            stok_setelah=stok_setelah,
            tanggal_penyesuaian=tgl,
            keterangan=keterangan,
            petugas=petugas
        )
        db.session.add(record)
        db.session.commit()

        flash(f'Penyesuaian stok untuk batch {batch.no_batch} ({kategori_alasan}) berhasil disimpan.', 'success')
        return redirect(url_for('penyesuaian.list_penyesuaian'))

    obats = Obat.query.order_by(Obat.nama_obat.asc()).all()
    batches = BatchObat.query.filter(BatchObat.stok_sekarang >= 0).order_by(BatchObat.expired_date.asc()).all()
    return render_template('penyesuaian/form.html', obats=obats, batches=batches)

@penyesuaian_bp.route('/get-batches/<int:obat_id>')
def get_batches_by_obat(obat_id):
    batches = BatchObat.query.filter_by(obat_id=obat_id).order_by(BatchObat.expired_date.asc()).all()
    data = [{
        'id': b.id,
        'no_batch': b.no_batch,
        'expired_date': b.expired_date.strftime('%d-%m-%Y'),
        'stok_sekarang': b.stok_sekarang,
        'sumber_dana': b.sumber_dana
    } for b in batches]
    return jsonify(data)
