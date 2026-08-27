from flask import Flask
from config import Config
from app.models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Register Blueprints
    from app.routes.dashboard import dashboard_bp
    from app.routes.obat import obat_bp
    from app.routes.subunit import subunit_bp
    from app.routes.transaksi import transaksi_bp
    from app.routes.lplpo import lplpo_bp
    from app.routes.pos import pos_bp
    from app.routes.pegawai import pegawai_bp
    from app.routes.penyesuaian import penyesuaian_bp
    from app.routes.stok_opname import stok_opname_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(obat_bp)
    app.register_blueprint(subunit_bp)
    app.register_blueprint(transaksi_bp)
    app.register_blueprint(lplpo_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(pegawai_bp)
    app.register_blueprint(penyesuaian_bp)
    app.register_blueprint(stok_opname_bp)
    app.register_blueprint(auth_bp)

    @app.before_request
    def check_authentication():
        from flask import request, redirect, url_for, session
        allowed_endpoints = ['auth.login', 'static']
        if not session.get('user_id') and request.endpoint and request.endpoint not in allowed_endpoints:
            return redirect(url_for('auth.login'))

    # Context Processors & Custom Template Filters
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            return f"Rp {float(value):,.0f}".replace(',', '.')
        except (ValueError, TypeError):
            return "Rp 0"

    @app.template_filter('number')
    def number_filter(value):
        try:
            return f"{int(value):,}".replace(',', '.')
        except (ValueError, TypeError):
            return "0"

    @app.context_processor
    def inject_url_for_other_page():
        from flask import request, url_for
        from app.models import User
        def url_for_other_page(page):
            args = request.args.copy()
            args['page'] = page
            return url_for(request.endpoint, **args)
        
        try:
            all_users = User.query.order_by(User.role.asc(), User.id.asc()).all()
        except Exception:
            all_users = []

        return dict(url_for_other_page=url_for_other_page, all_users=all_users)

    with app.app_context():
        db.create_all()

    return app
