import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # ✅ Configuración desde .env para base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ✅ Opciones de motor para mantener la conexión viva
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 1800
    }

    db.init_app(app)

    # Registro de blueprints de rutas
    from app.routes.factura_publica_routes import factura_publica_bp
    app.register_blueprint(factura_publica_bp)

    from app.routes.producto_routes import producto_bp
    app.register_blueprint(producto_bp)

    from app.routes.factura_routes import factura_bp
    app.register_blueprint(factura_bp)

    from app.routes.cliente_routes import cliente_bp
    app.register_blueprint(cliente_bp)



    return app
