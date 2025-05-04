from app import db

class Empresa(db.Model):
    __tablename__ = 'empresa'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nit = db.Column(db.String(20), unique=True, nullable=False)
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_documento = db.Column(db.String(10), nullable=False)
    numero_documento = db.Column(db.String(30), unique=True, nullable=False)
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    referencia = db.Column(db.String(50), unique=True, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

from datetime import datetime

class Factura(db.Model):
    __tablename__ = 'facturas'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    xml_ubl = db.Column(db.Text)  # ✅ Aquí se guarda el XML como texto plano

    cliente = db.relationship('Cliente', backref='facturas')
    detalles = db.relationship('FacturaDetalle', backref='factura', cascade="all, delete-orphan")


class FacturaDetalle(db.Model):
    __tablename__ = 'factura_detalle'

    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    producto = db.relationship('Producto')
