from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:$hcsr04298N*@localhost/roostechdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from app.routes.cliente_routes import cliente_bp
    app.register_blueprint(cliente_bp)

    # from app.routes.producto_routes import producto_bp
    # app.register_blueprint(producto_bp)

    # from app.routes.factura_routes import factura_bp
    # app.register_blueprint(factura_bp)

    from app.routes.factura_publica_routes import factura_publica_bp
    app.register_blueprint(factura_publica_bp)

    return app
