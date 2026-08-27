from flask import Blueprint, render_template, request
from app.models import Obat, BatchObat, TransaksiMasuk, TransaksiKeluar, SubUnit, LPLPO
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    active_mode = request.args.get('mode', 'lplpo')  # 'lplpo' atau 'operasional'
    
    total_jenis_obat = Obat.query.count()
    all_obats = Obat.query.all()
    total_stok_obat = sum(o.total_stok for o in all_obats)
    low_stock_obats = [o for o in all_obats if o.total_stok <= o.stok_minimum]
    
    active_batches = BatchObat.query.filter(BatchObat.stok_sekarang > 0).all()
    near_expired_batches = [b for b in active_batches if b.days_until_expired <= 90]
    near_expired_batches.sort(key=lambda b: b.expired_date)
    
    recent_masuk = TransaksiMasuk.query.order_by(TransaksiMasuk.tanggal_terima.desc()).limit(5).all()
    recent_keluar = TransaksiKeluar.query.order_by(TransaksiKeluar.tanggal_keluar.desc()).limit(5).all()

    # Data LPLPO Terbaru (Puskesmas POV)
    latest_lplpo = LPLPO.query.order_by(LPLPO.tahun.desc(), LPLPO.bulan.desc()).first()
    lplpo_items = sorted(latest_lplpo.items, key=lambda x: x.obat.nama_obat) if latest_lplpo else []

    total_lplpo_pemakaian = sum(item.pemakaian for item in lplpo_items) if lplpo_items else 0
    total_lplpo_permintaan = sum(item.permintaan for item in lplpo_items) if lplpo_items else 0
    total_lplpo_persediaan = sum(item.persediaan for item in lplpo_items) if lplpo_items else 0

    return render_template(
        'dashboard.html',
        active_mode=active_mode,
        total_jenis_obat=total_jenis_obat,
        total_stok_obat=total_stok_obat,
        low_stock_count=len(low_stock_obats),
        near_expired_count=len(near_expired_batches),
        low_stock_obats=low_stock_obats[:5],
        near_expired_batches=near_expired_batches[:5],
        recent_masuk=recent_masuk,
        recent_keluar=recent_keluar,
        latest_lplpo=latest_lplpo,
        lplpo_items=lplpo_items[:8],
        total_lplpo_pemakaian=total_lplpo_pemakaian,
        total_lplpo_permintaan=total_lplpo_permintaan,
        total_lplpo_persediaan=total_lplpo_persediaan
    )

