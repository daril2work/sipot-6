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

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(obat_bp)
    app.register_blueprint(subunit_bp)
    app.register_blueprint(transaksi_bp)
    app.register_blueprint(lplpo_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(pegawai_bp)

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

    with app.app_context():
        db.create_all()

    return app
