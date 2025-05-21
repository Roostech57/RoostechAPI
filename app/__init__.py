import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # ✅ Cargar desde variable de entorno
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Registro de rutas
    from app.routes.factura_publica_routes import factura_publica_bp
    app.register_blueprint(factura_publica_bp)

    from app.routes.producto_routes import producto_bp
    app.register_blueprint(producto_bp)

    return app


