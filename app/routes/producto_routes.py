from flask import Blueprint, request, jsonify
from app.models import Producto
from app import db

producto_bp = Blueprint('producto_bp', __name__)

@producto_bp.route('/productos', methods=['POST'])
def crear_producto():
    data = request.get_json()

    if not data or 'nombre' not in data or 'precio' not in data:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    nuevo_producto = Producto(
        nombre=data['nombre'],
        precio=data['precio']
    )
    db.session.add(nuevo_producto)
    db.session.commit()
    return jsonify({"mensaje": "Producto creado", "id": nuevo_producto.id})

@producto_bp.route('/productos', methods=['GET'])
def listar_productos():
    productos = Producto.query.all()
    return jsonify([
        {"id": p.id, "nombre": p.nombre, "precio": float(p.precio)}
        for p in productos
    ])
