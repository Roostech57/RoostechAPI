from flask import Blueprint, jsonify
from app import db
from app.models import Factura, FacturaDetalle, Cliente, Producto

factura_bp = Blueprint('factura', __name__)

@factura_bp.route('/factura/<int:factura_id>', methods=['GET'])
def obtener_factura(factura_id):
    factura = Factura.query.get(factura_id)
    if not factura:
        return jsonify({"error": "Factura no encontrada"}), 404

    detalles = []
    for detalle in factura.detalles:
        detalles.append({
            "producto_id": detalle.producto_id,
            "producto_nombre": detalle.producto.nombre,
            "cantidad": detalle.cantidad,
            "precio_unitario": detalle.precio_unitario,
            "subtotal": detalle.subtotal
        })

    return jsonify({
        "factura_id": factura.id,
        "cliente": {
            "id": factura.cliente.id,
            "nombre": factura.cliente.nombre,
            "numero_documento": factura.cliente.numero_documento
        },
        "fecha_emision": factura.fecha_emision.strftime("%Y-%m-%d %H:%M:%S"),
        "total": factura.total,
        "detalles": detalles
    })
