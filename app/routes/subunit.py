from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, SubUnit

subunit_bp = Blueprint('subunit', __name__, url_prefix='/subunit')

@subunit_bp.route('/')
def list_subunit():
    subunits = SubUnit.query.order_by(SubUnit.nama_subunit.asc()).all()
    return render_template('subunit/list.html', subunits=subunits)

@subunit_bp.route('/tambah', methods=['POST'])
def tambah_subunit():
    nama_subunit = request.form.get('nama_subunit', '').strip()
    penanggung_jawab = request.form.get('penanggung_jawab', '').strip()
    keterangan = request.form.get('keterangan', '').strip()

    if not nama_subunit:
        flash('Nama Sub-Unit/Poli wajib diisi.', 'danger')
        return redirect(url_for('subunit.list_subunit'))

    if SubUnit.query.filter_by(nama_subunit=nama_subunit).first():
        flash(f'Sub-Unit "{nama_subunit}" sudah ada.', 'warning')
        return redirect(url_for('subunit.list_subunit'))

    subunit = SubUnit(
        nama_subunit=nama_subunit,
        penanggung_jawab=penanggung_jawab,
        keterangan=keterangan
    )
    db.session.add(subunit)
    db.session.commit()
    flash(f'Sub-Unit "{nama_subunit}" berhasil ditambahkan.', 'success')
    return redirect(url_for('subunit.list_subunit'))

@subunit_bp.route('/<int:id>/edit', methods=['POST'])
def edit_subunit(id):
    subunit = SubUnit.query.get_or_404(id)
    subunit.nama_subunit = request.form.get('nama_subunit', '').strip()
    subunit.penanggung_jawab = request.form.get('penanggung_jawab', '').strip()
    subunit.keterangan = request.form.get('keterangan', '').strip()

    db.session.commit()
    flash(f'Sub-Unit "{subunit.nama_subunit}" berhasil diperbarui.', 'success')
    return redirect(url_for('subunit.list_subunit'))

@subunit_bp.route('/<int:id>/hapus', methods=['POST'])
def hapus_subunit(id):
    subunit = SubUnit.query.get_or_404(id)
    nama = subunit.nama_subunit
    db.session.delete(subunit)
    db.session.commit()
    flash(f'Sub-Unit "{nama}" berhasil dihapus.', 'success')
    return redirect(url_for('subunit.list_subunit'))
