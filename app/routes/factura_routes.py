from flask import Blueprint, jsonify
from app.models import Factura

factura_bp = Blueprint('factura', __name__)

@factura_bp.route('/factura/<int:factura_id>', methods=['GET'])
def obtener_factura(factura_id):
    factura = Factura.query.get(factura_id)
    if not factura:
        return jsonify({"error": "Factura no encontrada"}), 404

    detalles = [
        {
            "producto_id": d.producto_id,
            "producto_nombre": d.producto.nombre,
            "cantidad": d.cantidad,
            "precio_unitario": d.precio_unitario,
            "subtotal": d.subtotal
        } for d in factura.detalles
    ]

    return jsonify({
        "factura_id": factura.id,
        "fecha_emision": factura.fecha_emision.strftime("%Y-%m-%d %H:%M:%S"),
        "total": factura.total,
        "cliente": {
            "id": factura.cliente.id,
            "nombre": factura.cliente.nombre,
            "numero_documento": factura.cliente.numero_documento
        },
        "detalles": detalles
    })

@factura_bp.route('/facturas', methods=['GET'])
def listar_facturas():
    facturas = Factura.query.all()
    resultado = []

    for factura in facturas:
        resultado.append({
            "factura_id": factura.id,
            "fecha_emision": factura.fecha_emision.strftime("%Y-%m-%d %H:%M:%S"),
            "total": factura.total,
            "cliente": {
                "id": factura.cliente.id,
                "nombre": factura.cliente.nombre,
                "numero_documento": factura.cliente.numero_documento
            }
        })

    return jsonify(resultado)
