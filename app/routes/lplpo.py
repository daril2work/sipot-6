from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from app.models import db, LPLPO, LPLPOItem
from app.services.lplpo_engine import generate_lplpo_periode, get_subunit_usage_breakdown
from app.utils.excel_exporter import export_lplpo_to_excel
from datetime import date

lplpo_bp = Blueprint('lplpo', __name__, url_prefix='/lplpo')

@lplpo_bp.route('/')
def list_lplpo():
    page = request.args.get('page', 1, type=int)
    pagination = LPLPO.query.order_by(LPLPO.tahun.desc(), LPLPO.bulan.desc()).paginate(page=page, per_page=15, error_out=False)
    lplpo_list = pagination.items
    return render_template('lplpo/list.html', lplpo_list=lplpo_list, pagination=pagination)

@lplpo_bp.route('/generate', methods=['GET', 'POST'])
def generate_lplpo():
    if request.method == 'POST':
        bulan = int(request.form.get('bulan', date.today().month))
        tahun = int(request.form.get('tahun', date.today().year))
        nama_puskesmas = request.form.get('nama_puskesmas', 'Puskesmas Sehat Utama').strip()

        lplpo = generate_lplpo_periode(bulan, tahun, nama_puskesmas)
        flash(f'Dokumen LPLPO Periode {lplpo.nama_bulan} {lplpo.tahun} berhasil diproses.', 'success')
        return redirect(url_for('lplpo.detail_lplpo', id=lplpo.id))

    current_month = date.today().month
    current_year = date.today().year
    return render_template('lplpo/generate.html', current_month=current_month, current_year=current_year)

@lplpo_bp.route('/<int:id>')
def detail_lplpo(id):
    lplpo = LPLPO.query.get_or_404(id)
    items = sorted(lplpo.items, key=lambda x: x.obat.nama_obat)
    return render_template('lplpo/detail.html', lplpo=lplpo, items=items)

@lplpo_bp.route('/<int:id>/item-breakdown/<int:obat_id>')
def item_breakdown(id, obat_id):
    lplpo = LPLPO.query.get_or_404(id)
    breakdown = get_subunit_usage_breakdown(lplpo.bulan, lplpo.tahun, obat_id)
    return jsonify({
        'status': 'success',
        'bulan': lplpo.nama_bulan,
        'tahun': lplpo.tahun,
        'breakdown': breakdown
    })

@lplpo_bp.route('/<int:id>/toggle-status', methods=['POST'])
def toggle_status(id):
    lplpo = LPLPO.query.get_or_404(id)
    if lplpo.status == 'Draft':
        lplpo.status = 'Final'
        flash(f'Dokumen LPLPO Periode {lplpo.nama_bulan} {lplpo.tahun} telah DIKUNCI (Final).', 'success')
    else:
        lplpo.status = 'Draft'
        flash(f'Status Dokumen LPLPO dikembalikan ke DRAFT.', 'warning')
    
    db.session.commit()
    return redirect(url_for('lplpo.detail_lplpo', id=id))

@lplpo_bp.route('/<int:id>/print')
def print_lplpo(id):
    lplpo = LPLPO.query.get_or_404(id)
    items = sorted(lplpo.items, key=lambda x: x.obat.nama_obat)
    return render_template('lplpo/print.html', lplpo=lplpo, items=items)

@lplpo_bp.route('/<int:id>/update-item', methods=['POST'])
def update_lplpo_item(id):
    item_id = request.form.get('item_id')
    field = request.form.get('field')
    value = int(request.form.get('value', 0))

    item = LPLPOItem.query.get_or_404(item_id)
    
    if field == 'stok_optimum':
        item.stok_optimum = value
        item.permintaan = max(0, item.stok_optimum - item.sisa_stok)
    elif field == 'permintaan':
        item.permintaan = value
    elif field == 'pemberian':
        item.pemberian = value
    
    db.session.commit()
    return jsonify({
        'status': 'success',
        'item_id': item.id,
        'stok_optimum': item.stok_optimum,
        'permintaan': item.permintaan,
        'pemberian': item.pemberian
    })

@lplpo_bp.route('/<int:id>/excel')
def download_excel(id):
    lplpo = LPLPO.query.get_or_404(id)
    try:
        buffer = export_lplpo_to_excel(id)
        filename = f"LPLPO_{lplpo.nama_puskesmas.replace(' ', '_')}_{lplpo.nama_bulan}_{lplpo.tahun}.xlsx"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'Gagal mengunduh Excel: {str(e)}', 'danger')
        return redirect(url_for('lplpo.detail_lplpo', id=id))

