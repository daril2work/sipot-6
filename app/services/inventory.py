from app.models import db, BatchObat, Obat
from datetime import date

def process_pengeluaran_fefo(obat_id, jumlah_dibutuhkan):
    """
    Mengeluarkan stok obat berdasarkan prinsip FEFO (First Expired First Out).
    Mengembalikan list of dict [{'batch': batch_obj, 'jumlah': qty_diambil}]
    """
    obat = Obat.query.get(obat_id)
    if not obat:
        raise ValueError(f"Obat dengan ID {obat_id} tidak ditemukan.")

    if obat.total_stok < jumlah_dibutuhkan:
        raise ValueError(f"Stok obat '{obat.nama_obat}' tidak mencukupi. Tersedia: {obat.total_stok}, Dibutuhkan: {jumlah_dibutuhkan}")

    # Ambil batch aktif yang memiliki stok > 0, diurutkan dari Expired Date terdekat
    batches = BatchObat.query.filter(
        BatchObat.obat_id == obat_id,
        BatchObat.stok_sekarang > 0
    ).order_by(BatchObat.expired_date.asc()).all()

    sisa_kebutuhan = jumlah_dibutuhkan
    alokasi = []

    for batch in batches:
        if sisa_kebutuhan <= 0:
            break

        if batch.stok_sekarang >= sisa_kebutuhan:
            batch.stok_sekarang -= sisa_kebutuhan
            alokasi.append({
                'batch_id': batch.id,
                'batch': batch,
                'jumlah': sisa_kebutuhan
            })
            sisa_kebutuhan = 0
        else:
            diambil = batch.stok_sekarang
            sisa_kebutuhan -= diambil
            batch.stok_sekarang = 0
            alokasi.append({
                'batch_id': batch.id,
                'batch': batch,
                'jumlah': diambil
            })

    return alokasi

def tambah_stok_batch(obat_id, no_batch, expired_date, jumlah, harga=0.0, sumber_dana='APBD'):
    """
    Menambah stok batch obat baru atau memperbarui batch yang sudah ada.
    """
    batch = BatchObat.query.filter_by(obat_id=obat_id, no_batch=no_batch).first()
    
    if batch:
        batch.stok_sekarang += jumlah
        batch.stok_awal += jumlah
        if expired_date:
            batch.expired_date = expired_date
    else:
        batch = BatchObat(
            obat_id=obat_id,
            no_batch=no_batch,
            expired_date=expired_date,
            stok_awal=jumlah,
            stok_sekarang=jumlah,
            harga_batch=harga,
            sumber_dana=sumber_dana
        )
        db.session.add(batch)

    return batch
