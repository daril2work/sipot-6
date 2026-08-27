from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Pegawai
import json
import csv
import io

pegawai_bp = Blueprint('pegawai', __name__, url_prefix='/pegawai')

@pegawai_bp.route('/')
def list_pegawai():
    query = request.args.get('q', '').strip()
    pegawai_query = Pegawai.query

    if query:
        pegawai_query = pegawai_query.filter(
            (Pegawai.nama_pegawai.ilike(f'%{query}%')) |
            (Pegawai.nip.ilike(f'%{query}%')) |
            (Pegawai.jabatan.ilike(f'%{query}%'))
        )

    pegawai_list = pegawai_query.order_by(Pegawai.nama_pegawai.asc()).all()
    return render_template('pegawai/list.html', pegawai_list=pegawai_list, query=query)

@pegawai_bp.route('/tambah', methods=['POST'])
def tambah_pegawai():
    nip = request.form.get('nip', '').strip()
    nama_pegawai = request.form.get('nama_pegawai', '').strip()
    jabatan = request.form.get('jabatan', 'Staf Farmasi').strip()
    unit_tugas = request.form.get('unit_tugas', 'Gudang Farmasi').strip()
    no_hp = request.form.get('no_hp', '').strip()

    if not nip or not nama_pegawai:
        flash('NIP dan Nama Pegawai wajib diisi.', 'danger')
        return redirect(url_for('pegawai.list_pegawai'))

    if Pegawai.query.filter_by(nip=nip).first():
        flash(f'NIP "{nip}" sudah terdaftar.', 'warning')
        return redirect(url_for('pegawai.list_pegawai'))

    pegawai = Pegawai(
        nip=nip,
        nama_pegawai=nama_pegawai,
        jabatan=jabatan,
        unit_tugas=unit_tugas,
        no_hp=no_hp
    )
    db.session.add(pegawai)
    db.session.commit()
    flash(f'Pegawai "{nama_pegawai}" berhasil ditambahkan.', 'success')
    return redirect(url_for('pegawai.list_pegawai'))

@pegawai_bp.route('/<int:id>/edit', methods=['POST'])
def edit_pegawai(id):
    pegawai = Pegawai.query.get_or_404(id)
    pegawai.nip = request.form.get('nip', '').strip()
    pegawai.nama_pegawai = request.form.get('nama_pegawai', '').strip()
    pegawai.jabatan = request.form.get('jabatan', '').strip()
    pegawai.unit_tugas = request.form.get('unit_tugas', '').strip()
    pegawai.no_hp = request.form.get('no_hp', '').strip()

    db.session.commit()
    flash(f'Data pegawai "{pegawai.nama_pegawai}" berhasil diperbarui.', 'success')
    return redirect(url_for('pegawai.list_pegawai'))

@pegawai_bp.route('/<int:id>/hapus', methods=['POST'])
def hapus_pegawai(id):
    pegawai = Pegawai.query.get_or_404(id)
    nama = pegawai.nama_pegawai
    db.session.delete(pegawai)
    db.session.commit()
    flash(f'Pegawai "{nama}" berhasil dihapus.', 'success')
    return redirect(url_for('pegawai.list_pegawai'))

@pegawai_bp.route('/hapus-semua', methods=['POST'])
def hapus_semua_pegawai():
    count = Pegawai.query.delete()
    db.session.commit()
    flash(f'Seluruh data master pegawai ({count} pegawai) berhasil dihapus.', 'success')
    return redirect(url_for('pegawai.list_pegawai'))


@pegawai_bp.route('/import', methods=['POST'])
def import_pegawai_bulk():
    raw_text = request.form.get('raw_data', '').strip()
    uploaded_file = request.files.get('file')

    content = ""
    if uploaded_file and uploaded_file.filename != '':
        content = uploaded_file.read().decode('utf-8', errors='ignore')
    elif raw_text:
        content = raw_text

    if not content:
        flash('Harap masukkan teks CSV/JSON atau unggah file data pegawai.', 'danger')
        return redirect(url_for('pegawai.list_pegawai'))

    count = 0
    try:
        if content.strip().startswith('[') or content.strip().startswith('{'):
            items = json.loads(content)
            if isinstance(items, dict):
                items = [items]
            for idx, item in enumerate(items, 1):
                nip = item.get('nip') or f"198001012010011{idx:03d}"
                nama = item.get('nama') or item.get('nama_pegawai')
                if not nama:
                    continue
                if not Pegawai.query.filter_by(nip=nip).first():
                    p = Pegawai(
                        nip=nip,
                        nama_pegawai=nama,
                        jabatan=item.get('jabatan', 'Staf Farmasi'),
                        unit_tugas=item.get('unit_tugas', 'Gudang Farmasi'),
                        no_hp=item.get('no_hp', '')
                    )
                    db.session.add(p)
                    count += 1
        else:
            delimiter = ';' if ';' in content else ','
            reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
            for idx, row in enumerate(reader, 1):
                nip = row.get('nip') or f"198001012010011{idx:03d}"
                nama = row.get('nama') or row.get('nama_pegawai')
                if not nama:
                    continue
                if not Pegawai.query.filter_by(nip=nip).first():
                    p = Pegawai(
                        nip=nip,
                        nama_pegawai=nama,
                        jabatan=row.get('jabatan', 'Staf Farmasi'),
                        unit_tugas=row.get('unit_tugas', 'Gudang Farmasi'),
                        no_hp=row.get('no_hp', '')
                    )
                    db.session.add(p)
                    count += 1

        db.session.commit()
        flash(f'Berhasil mengimpor {count} data pegawai baru!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal mengimpor data pegawai: {str(e)}', 'danger')

    return redirect(url_for('pegawai.list_pegawai'))
