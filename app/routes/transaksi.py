from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import (
    db, Obat, SubUnit, TransaksiMasuk, TransaksiMasukItem,
    TransaksiKeluar, TransaksiKeluarItem, BatchObat
)
from app.services.inventory import process_pengeluaran_fefo, tambah_stok_batch
from datetime import datetime, date

transaksi_bp = Blueprint('transaksi', __name__, url_prefix='/transaksi')

@transaksi_bp.route('/masuk')
def list_masuk():
    transaksi_list = TransaksiMasuk.query.order_by(TransaksiMasuk.tanggal_terima.desc()).all()
    return render_template('transaksi/masuk_list.html', transaksi_list=transaksi_list)

@transaksi_bp.route('/masuk/tambah', methods=['GET', 'POST'])
def tambah_masuk():
    if request.method == 'POST':
        no_sbbk = request.form.get('no_sbbk', '').strip()
        sumber_penerimaan = request.form.get('sumber_penerimaan', 'Gudang Farmasi Kabupaten').strip()
        tgl_str = request.form.get('tanggal_terima', str(date.today()))
        keterangan = request.form.get('keterangan', '').strip()

        obat_ids = request.form.getlist('obat_id[]')
        no_batches = request.form.getlist('no_batch[]')
        expired_dates = request.form.getlist('expired_date[]')
        jumlahs = request.form.getlist('jumlah[]')
        hargas = request.form.getlist('harga_satuan[]')

        if not no_sbbk or not obat_ids:
            flash('No SBBK dan minimal 1 item obat wajib diisi.', 'danger')
            return redirect(url_for('transaksi.tambah_masuk'))

        try:
            tgl_terima = datetime.strptime(tgl_str, '%Y-%m-%d').date()
        except ValueError:
            tgl_terima = date.today()

        transaksi = TransaksiMasuk(
            no_sbbk=no_sbbk,
            sumber_penerimaan=sumber_penerimaan,
            tanggal_terima=tgl_terima,
            keterangan=keterangan
        )
        db.session.add(transaksi)
        db.session.flush()

        for idx in range(len(obat_ids)):
            if not obat_ids[idx] or not jumlahs[idx]:
                continue
            
            o_id = int(obat_ids[idx])
            n_batch = no_batches[idx].strip() if idx < len(no_batches) and no_batches[idx] else f"BATCH-{date.today().strftime('%Y%m')}"
            
            try:
                ed_date = datetime.strptime(expired_dates[idx], '%Y-%m-%d').date() if idx < len(expired_dates) and expired_dates[idx] else date(date.today().year + 2, 12, 31)
            except ValueError:
                ed_date = date(date.today().year + 2, 12, 31)

            qty = int(jumlahs[idx])
            hrg = float(hargas[idx]) if idx < len(hargas) and hargas[idx] else 0.0

            # Update / Tambah Batch
            batch = tambah_stok_batch(
                obat_id=o_id,
                no_batch=n_batch,
                expired_date=ed_date,
                jumlah=qty,
                harga=hrg,
                sumber_dana=sumber_penerimaan
            )
            db.session.flush()

            item = TransaksiMasukItem(
                transaksi_masuk_id=transaksi.id,
                obat_id=o_id,
                batch_id=batch.id,
                jumlah=qty,
                harga_satuan=hrg
            )
            db.session.add(item)

        db.session.commit()
        flash(f'Penerimaan barang SBBK {no_sbbk} berhasil disimpan.', 'success')
        return redirect(url_for('transaksi.list_masuk'))

    obats = Obat.query.order_by(Obat.nama_obat.asc()).all()
    return render_template('transaksi/masuk_form.html', obats=obats, today=str(date.today()))

@transaksi_bp.route('/keluar')
def list_keluar():
    transaksi_list = TransaksiKeluar.query.order_by(TransaksiKeluar.tanggal_keluar.desc()).all()
    return render_template('transaksi/keluar_list.html', transaksi_list=transaksi_list)

@transaksi_bp.route('/keluar/tambah', methods=['GET', 'POST'])
def tambah_keluar():
    if request.method == 'POST':
        no_penyerahan = request.form.get('no_penyerahan', '').strip()
        subunit_id = request.form.get('subunit_id')
        tgl_str = request.form.get('tanggal_keluar', str(date.today()))
        keterangan = request.form.get('keterangan', '').strip()

        obat_ids = request.form.getlist('obat_id[]')
        jumlahs = request.form.getlist('jumlah[]')

        if not no_penyerahan or not subunit_id or not obat_ids:
            flash('Nomor Penyerahan, Sub-Unit, dan item obat wajib diisi.', 'danger')
            return redirect(url_for('transaksi.tambah_keluar'))

        try:
            tgl_keluar = datetime.strptime(tgl_str, '%Y-%m-%d').date()
        except ValueError:
            tgl_keluar = date.today()

        transaksi = TransaksiKeluar(
            no_penyerahan=no_penyerahan,
            subunit_id=int(subunit_id),
            tanggal_keluar=tgl_keluar,
            keterangan=keterangan
        )
        db.session.add(transaksi)
        db.session.flush()

        try:
            for idx in range(len(obat_ids)):
                if not obat_ids[idx] or not jumlahs[idx]:
                    continue
                
                o_id = int(obat_ids[idx])
                qty_minta = int(jumlahs[idx])

                if qty_minta <= 0:
                    continue

                # Jalankan logika FEFO otomatis untuk pengurangan batch
                alokasi_fefo = process_pengeluaran_fefo(o_id, qty_minta)

                for item_alokasi in alokasi_fefo:
                    item_keluar = TransaksiKeluarItem(
                        transaksi_keluar_id=transaksi.id,
                        obat_id=o_id,
                        batch_id=item_alokasi['batch_id'],
                        jumlah=item_alokasi['jumlah']
                    )
                    db.session.add(item_keluar)

            db.session.commit()
            flash(f'Pengeluaran obat ke sub-unit berhasil disimpan (Metode FEFO).', 'success')
            return redirect(url_for('transaksi.list_keluar'))
        except ValueError as err:
            db.session.rollback()
            flash(str(err), 'danger')
            return redirect(url_for('transaksi.tambah_keluar'))

    subunits = SubUnit.query.order_by(SubUnit.nama_subunit.asc()).all()
    obats = Obat.query.order_by(Obat.nama_obat.asc()).all()
    return render_template('transaksi/keluar_form.html', subunits=subunits, obats=obats, today=str(date.today()))
