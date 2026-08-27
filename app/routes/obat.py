from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Obat, BatchObat
from datetime import datetime

obat_bp = Blueprint('obat', __name__, url_prefix='/obat')

@obat_bp.route('/')
def list_obat():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '').strip()
    kategori_filter = request.args.get('kategori', '').strip()

    obats_query = Obat.query

    if query:
        obats_query = obats_query.filter(
            (Obat.nama_obat.ilike(f'%{query}%')) | 
            (Obat.kode_obat.ilike(f'%{query}%'))
        )
    
    if kategori_filter:
        obats_query = obats_query.filter(Obat.kategori == kategori_filter)

    pagination = obats_query.order_by(Obat.nama_obat.asc()).paginate(page=page, per_page=15, error_out=False)
    obats = pagination.items
    
    kategori_list = db.session.query(Obat.kategori).distinct().all()
    kategori_list = [k[0] for k in kategori_list if k[0]]

    return render_template('obat/list.html', obats=obats, pagination=pagination, query=query, kategori_list=kategori_list, selected_kategori=kategori_filter)

@obat_bp.route('/tambah', methods=['GET', 'POST'])
def tambah_obat():
    if request.method == 'POST':
        kode_obat = request.form.get('kode_obat', '').strip()
        nama_obat = request.form.get('nama_obat', '').strip()
        bentuk_sediaan = request.form.get('bentuk_sediaan', 'Tablet').strip()
        satuan = request.form.get('satuan', 'Tablet').strip()
        kategori = request.form.get('kategori', 'Generik').strip()
        harga_satuan = float(request.form.get('harga_satuan', 0))
        stok_minimum = int(request.form.get('stok_minimum', 10))

        if not kode_obat or not nama_obat:
            flash('Kode obat dan nama obat wajib diisi.', 'danger')
            return redirect(url_for('obat.tambah_obat'))

        if Obat.query.filter_by(kode_obat=kode_obat).first():
            flash(f'Kode obat "{kode_obat}" sudah terdaftar.', 'warning')
            return redirect(url_for('obat.tambah_obat'))

        obat = Obat(
            kode_obat=kode_obat,
            nama_obat=nama_obat,
            bentuk_sediaan=bentuk_sediaan,
            satuan=satuan,
            kategori=kategori,
            harga_satuan=harga_satuan,
            stok_minimum=stok_minimum
        )
        db.session.add(obat)
        db.session.commit()
        flash(f'Obat "{nama_obat}" berhasil ditambahkan.', 'success')
        return redirect(url_for('obat.list_obat'))

    return render_template('obat/form.html', obat=None)

@obat_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_obat(id):
    obat = Obat.query.get_or_404(id)
    
    if request.method == 'POST':
        obat.kode_obat = request.form.get('kode_obat', '').strip()
        obat.nama_obat = request.form.get('nama_obat', '').strip()
        obat.bentuk_sediaan = request.form.get('bentuk_sediaan', 'Tablet').strip()
        obat.satuan = request.form.get('satuan', 'Tablet').strip()
        obat.kategori = request.form.get('kategori', 'Generik').strip()
        obat.harga_satuan = float(request.form.get('harga_satuan', 0))
        obat.stok_minimum = int(request.form.get('stok_minimum', 10))

        db.session.commit()
        flash(f'Data obat "{obat.nama_obat}" berhasil diperbarui.', 'success')
        return redirect(url_for('obat.list_obat'))

    return render_template('obat/form.html', obat=obat)

@obat_bp.route('/<int:id>')
def detail_obat(id):
    obat = Obat.query.get_or_404(id)
    batches = BatchObat.query.filter_by(obat_id=id).order_by(BatchObat.expired_date.asc()).all()
    return render_template('obat/detail.html', obat=obat, batches=batches)

import json
import csv
import io

@obat_bp.route('/import', methods=['GET', 'POST'])
def import_obat_bulk():
    if request.method == 'POST':
        raw_text = request.form.get('raw_data', '').strip()
        uploaded_file = request.files.get('file')

        content = ""
        if uploaded_file and uploaded_file.filename != '':
            content = uploaded_file.read().decode('utf-8', errors='ignore')
        elif raw_text:
            content = raw_text

        if not content:
            flash('Harap masukkan teks CSV/JSON atau unggah file data obat.', 'danger')
            return redirect(url_for('obat.import_obat_bulk'))

        count = 0
        try:
            # Coba parse JSON terlebih dahulu
            if content.strip().startswith('[') or content.strip().startswith('{'):
                items = json.loads(content)
                if isinstance(items, dict):
                    items = [items]
                for idx, item in enumerate(items, 1):
                    kode = item.get('kode') or item.get('kode_obat') or f"OBT-{idx:03d}"
                    nama = item.get('nama') or item.get('nama_obat')
                    if not nama:
                        continue
                    
                    existing = Obat.query.filter_by(kode_obat=kode).first()
                    if not existing:
                        obat = Obat(
                            kode_obat=kode,
                            nama_obat=nama,
                            bentuk_sediaan=item.get('sediaan', item.get('bentuk_sediaan', 'Tablet')),
                            satuan=item.get('satuan', 'Tablet'),
                            kategori=item.get('kategori', 'Obat Oral'),
                            harga_satuan=float(item.get('harga', item.get('harga_satuan', 0))),
                            stok_minimum=int(item.get('min', item.get('stok_minimum', 10)))
                        )
                        db.session.add(obat)
                        count += 1
            else:
                # Fallback parse CSV (delimiter koma atau titik koma)
                delimiter = ';' if ';' in content else ','
                reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
                for idx, row in enumerate(reader, 1):
                    kode = row.get('kode') or row.get('kode_obat') or f"OBT-IMP-{idx:03d}"
                    nama = row.get('nama') or row.get('nama_obat')
                    if not nama:
                        continue

                    existing = Obat.query.filter_by(kode_obat=kode).first()
                    if not existing:
                        obat = Obat(
                            kode_obat=kode,
                            nama_obat=nama,
                            bentuk_sediaan=row.get('sediaan', row.get('bentuk_sediaan', 'Tablet')),
                            satuan=row.get('satuan', 'Tablet'),
                            kategori=row.get('kategori', 'Obat Oral'),
                            harga_satuan=float(row.get('harga', row.get('harga_satuan', 0)) or 0),
                            stok_minimum=int(row.get('min', row.get('stok_minimum', 10)) or 10)
                        )
                        db.session.add(obat)
                        count += 1

            db.session.commit()
            flash(f'Berhasil mengimpor {count} item obat baru secara masal!', 'success')
            return redirect(url_for('obat.list_obat'))
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengimpor data: {str(e)}', 'danger')
            return redirect(url_for('obat.import_obat_bulk'))

    return render_template('obat/import.html')

@obat_bp.route('/<int:id>/hapus', methods=['POST'])
def hapus_obat(id):
    obat = Obat.query.get_or_404(id)
    nama = obat.nama_obat
    db.session.delete(obat)
    db.session.commit()
    flash(f'Obat "{nama}" berhasil dihapus.', 'success')
    return redirect(url_for('obat.list_obat'))

