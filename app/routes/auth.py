from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, User, SubUnit, TransaksiKeluar, TransaksiKeluarItem, Obat
from datetime import date

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'Admin':
            return redirect(url_for('dashboard.index'))
        else:
            return redirect(url_for('auth.unit_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['nama_lengkap'] = user.nama_lengkap or user.username
            session['subunit_id'] = user.subunit_id
            session['subunit_nama'] = user.subunit.nama_subunit if user.subunit else 'Gudang Farmasi Utama'

            flash(f'Selamat datang kembali, {session["nama_lengkap"]}!', 'success')
            
            if user.role == 'Admin':
                return redirect(url_for('dashboard.index'))
            else:
                return redirect(url_for('auth.unit_dashboard'))
        else:
            flash('Username atau password salah. Silakan coba lagi.', 'danger')

    subunits = SubUnit.query.order_by(SubUnit.nama_subunit.asc()).all()
    return render_template('auth/login.html', subunits=subunits)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Anda telah berhasil keluar dari sistem.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/switch-account/<username>')
def switch_account(username):
    user = User.query.filter_by(username=username).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['nama_lengkap'] = user.nama_lengkap or user.username
        session['subunit_id'] = user.subunit_id
        session['subunit_nama'] = user.subunit.nama_subunit if user.subunit else 'Gudang Farmasi Utama'

        flash(f'⚡ Berhasil beralih ke akun {session["nama_lengkap"]} ({session["subunit_nama"]})', 'info')

        if user.role == 'Admin':
            return redirect(url_for('dashboard.index'))
        else:
            return redirect(url_for('auth.unit_dashboard'))
    
    flash('Akun pengguna tidak ditemukan.', 'danger')
    return redirect(request.referrer or url_for('auth.login'))

@auth_bp.route('/unit-dashboard')
def unit_dashboard():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('auth.login'))

    role = session.get('role')
    subunit_id = session.get('subunit_id')

    if role == 'Admin':
        return redirect(url_for('dashboard.index'))

    subunit = SubUnit.query.get_or_404(subunit_id)

    # Ambil riwayat penyerahan obat khusus untuk sub-unit ini
    transaksi_list = TransaksiKeluar.query.filter_by(subunit_id=subunit_id).order_by(TransaksiKeluar.tanggal_keluar.desc()).all()

    # Hitung ringkasan penerimaan obat sub-unit
    total_transaksi = len(transaksi_list)
    total_item_diterima = sum(len(t.items) for t in transaksi_list)

    return render_template('auth/unit_dashboard.html', subunit=subunit, transaksi_list=transaksi_list, total_transaksi=total_transaksi, total_item_diterima=total_item_diterima)
