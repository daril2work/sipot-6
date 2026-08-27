from datetime import date
from sqlalchemy import extract
from app.models import (
    db, Obat, LPLPO, LPLPOItem, TransaksiMasuk, TransaksiMasukItem,
    TransaksiKeluar, TransaksiKeluarItem
)

def generate_lplpo_periode(bulan, tahun, nama_puskesmas='Puskesmas Sehat Utama'):
    """
    Menghasilkan dokumen LPLPO otomatis untuk periode bulan & tahun tertentu.
    Jika LPLPO untuk periode tersebut sudah ada, akan diperbarui (recalculate).
    """
    lplpo = LPLPO.query.filter_by(bulan=bulan, tahun=tahun).first()
    
    if not lplpo:
        lplpo = LPLPO(
            bulan=bulan,
            tahun=tahun,
            nama_puskesmas=nama_puskesmas,
            tanggal_laporan=date.today(),
            status='Draft'
        )
        db.session.add(lplpo)
        db.session.flush()
    else:
        # Hapus item lama untuk di-recalculate
        LPLPOItem.query.filter_by(lplpo_id=lplpo.id).delete()

    # Cari LPLPO bulan sebelumnya untuk menentukan Stok Awal otomatis
    prev_bulan = 12 if bulan == 1 else bulan - 1
    prev_tahun = tahun - 1 if bulan == 1 else tahun
    prev_lplpo = LPLPO.query.filter_by(bulan=prev_bulan, tahun=prev_tahun).first()
    
    prev_sisa_map = {}
    if prev_lplpo:
        for item in prev_lplpo.items:
            prev_sisa_map[item.obat_id] = item.sisa_stok

    semua_obat = Obat.query.order_by(Obat.nama_obat.asc()).all()

    for obat in semua_obat:
        # 1. Stok Awal
        if obat.id in prev_sisa_map:
            stok_awal = prev_sisa_map[obat.id]
        else:
            # Jika tidak ada LPLPO bulan lalu, gunakan estimasi total stok saat ini minus transaksi bulan ini
            stok_awal = max(0, obat.total_stok)

        # 2. Penerimaan Bulan Ini
        penerimaan_item = db.session.query(db.func.sum(TransaksiMasukItem.jumlah)).join(
            TransaksiMasuk, TransaksiMasukItem.transaksi_masuk_id == TransaksiMasuk.id
        ).filter(
            TransaksiMasukItem.obat_id == obat.id,
            extract('month', TransaksiMasuk.tanggal_terima) == bulan,
            extract('year', TransaksiMasuk.tanggal_terima) == tahun
        ).scalar() or 0

        penerimaan = int(penerimaan_item)

        # 3. Total Persediaan
        persediaan = stok_awal + penerimaan

        # 4. Pemakaian Bulan Ini
        pemakaian_item = db.session.query(db.func.sum(TransaksiKeluarItem.jumlah)).join(
            TransaksiKeluar, TransaksiKeluarItem.transaksi_keluar_id == TransaksiKeluar.id
        ).filter(
            TransaksiKeluarItem.obat_id == obat.id,
            extract('month', TransaksiKeluar.tanggal_keluar) == bulan,
            extract('year', TransaksiKeluar.tanggal_keluar) == tahun
        ).scalar() or 0

        pemakaian = int(pemakaian_item)

        # 5. Sisa Stok
        sisa_stok = max(0, persediaan - pemakaian)

        # 6. Stok Optimum (Standard Kemenkes: 1.5 * Pemakaian atau Pemakaian + Buffer)
        stok_optimum = round(pemakaian * (1.0 + (obat.buffer_percent or 0.20)) + obat.stok_minimum)

        # 7. Permintaan
        permintaan = max(0, stok_optimum - sisa_stok)

        # 8. Pemberian (default disamakan dengan Permintaan)
        pemberian = permintaan

        lplpo_item = LPLPOItem(
            lplpo_id=lplpo.id,
            obat_id=obat.id,
            stok_awal=stok_awal,
            penerimaan=penerimaan,
            persediaan=persediaan,
            pemakaian=pemakaian,
            sisa_stok=sisa_stok,
            stok_optimum=stok_optimum,
            permintaan=permintaan,
            pemberian=pemberian
        )
        db.session.add(lplpo_item)

    db.session.commit()
    return lplpo

def get_subunit_usage_breakdown(bulan, tahun, obat_id):
    """
    Mengambil rincian jumlah pemakaian obat tertentu per Sub-Unit / Poli pada bulan & tahun tertentu.
    """
    from app.models import SubUnit

    results = db.session.query(
        SubUnit.nama_subunit,
        db.func.sum(TransaksiKeluarItem.jumlah).label('total_pemakaian')
    ).join(
        TransaksiKeluar, TransaksiKeluarItem.transaksi_keluar_id == TransaksiKeluar.id
    ).join(
        SubUnit, TransaksiKeluar.subunit_id == SubUnit.id
    ).filter(
        TransaksiKeluarItem.obat_id == obat_id,
        extract('month', TransaksiKeluar.tanggal_keluar) == bulan,
        extract('year', TransaksiKeluar.tanggal_keluar) == tahun
    ).group_by(SubUnit.nama_subunit).order_by(db.func.sum(TransaksiKeluarItem.jumlah).desc()).all()

    return [{'nama_subunit': r[0], 'jumlah': int(r[1])} for r in results]

