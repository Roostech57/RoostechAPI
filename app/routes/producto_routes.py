from flask import Blueprint, request, jsonify
from app import db

producto_bp = Blueprint('producto_bp', __name__)

@producto_bp.route('/productos', methods=['GET'])
def listar_productos():
    from app.models import Producto  # Importación dentro del endpoint para evitar import circular

    productos = Producto.query.all()
    resultado = []
    for p in productos:
        resultado.append({
            "id": p.id,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "referencia": p.referencia,
            "precio_unitario": p.precio_unitario,
            "stock": p.stock
        })
    return jsonify(resultado), 200

@producto_bp.route('/productos', methods=['POST'])
def crear_producto():
    from app.models import Producto  # Importación dentro del endpoint

    data = request.get_json()

    if not data:
        return jsonify({"error": "No se recibieron datos"}), 400

    campos_requeridos = ['nombre', 'descripcion', 'referencia', 'precio_unitario', 'stock']
    if not all(campo in data for campo in campos_requeridos):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        nuevo_producto = Producto(
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            referencia=data['referencia'],
            precio_unitario=float(data['precio_unitario']),
            stock=int(data['stock'])
        )
        db.session.add(nuevo_producto)
        db.session.commit()

        return jsonify({"mensaje": "Producto creado exitosamente", "producto_id": nuevo_producto.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
