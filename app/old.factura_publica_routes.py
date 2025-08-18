from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Cliente, Producto, Factura, FacturaDetalle
from app.services.xml_generator import generar_xml_ubl
from pathlib import Path

factura_publica_bp = Blueprint('factura_publica', __name__)

@factura_publica_bp.route('/facturar', methods=['POST'])
def facturar():
    try:
        data = request.get_json()
        current_app.logger.info(f"Datos recibidos: {data}")

        if not data or data.get("token") != "SECRETO123":
            return jsonify({"error": "Token inválido o datos incompletos"}), 401

        cliente_data = data.get("cliente")
        productos_data = data.get("productos")

        if not cliente_data or not productos_data:
            return jsonify({"error": "Datos de cliente o productos incompletos"}), 400

        # Buscar o crear cliente
        cliente = Cliente.query.filter_by(numero_documento=cliente_data["numero_documento"]).first()
        if not cliente:
            cliente = Cliente(**cliente_data)
            db.session.add(cliente)
            db.session.commit()
        current_app.logger.info(f"Cliente procesado: {cliente.nombre}")

        # Calcular total y guardar factura
        total = 0
        detalles = []

        for item in productos_data:
            current_app.logger.info(f"Procesando producto: {item}")
            producto = Producto.query.get(item["producto_id"])
            if not producto:
                return jsonify({"error": f"Producto ID {item['producto_id']} no encontrado"}), 400
            cantidad = item["cantidad"]
            precio_unitario = producto.precio_unitario
            subtotal = cantidad * precio_unitario
            total += subtotal
            detalle = FacturaDetalle(
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )
            detalles.append(detalle)

        factura = Factura(cliente_id=cliente.id, total=total)
        factura.detalles = detalles
        db.session.add(factura)
        db.session.commit()

        # Generar XML y actualizar
        ruta_xml = generar_xml_ubl(factura.id)
        factura.xml_ubl = Path(ruta_xml).read_text(encoding="utf-8") if ruta_xml else None
        db.session.commit()

        return jsonify({
            "mensaje": "Factura creada exitosamente",
            "factura_id": factura.id,
            "ruta_xml": ruta_xml
        })

    except Exception as e:
        current_app.logger.error(f"Error en /facturar: {str(e)}")
        return jsonify({"error": str(e)}), 500
