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
        current_app.logger.info(f"📥 Datos recibidos: {data}")

        # Validación de token
        if not data or data.get("token") != "SECRETO123":
            return jsonify({"error": "Token inválido o datos incompletos"}), 401

        cliente_data = data.get("cliente")
        productos_data = data.get("productos")
        tipo_factura = data.get("tipo_factura", "electronica")

        current_app.logger.info(f"🧾 Tipo de factura: {tipo_factura}")

        if not cliente_data or not productos_data:
            return jsonify({"error": "Datos de cliente o productos incompletos"}), 400

        if not cliente_data.get("numero_documento"):
            current_app.logger.warning("⚠️ Cliente sin número de documento")

        # Buscar o crear cliente
        cliente = Cliente.query.filter_by(numero_documento=cliente_data["numero_documento"]).first()
        if not cliente:
            cliente = Cliente(**cliente_data)
            db.session.add(cliente)
            db.session.commit()
        current_app.logger.info(f"🧑 Cliente procesado: {cliente.nombre}")

        # Procesar productos
        total = 0
        detalles = []

        for item in productos_data:
            current_app.logger.info(f"🔍 Procesando producto recibido: {item}")
            producto = Producto.query.get(item.get("producto_id"))
            if not producto:
                current_app.logger.warning(f"❌ Producto ID {item.get('producto_id')} no encontrado, creando...")
                try:
                    producto = Producto(
                        id=item.get("producto_id"),
                        nombre=item.get("nombre"),
                        descripcion=item.get("descripcion"),
                        precio_unitario=item.get("precio_unitario", 0)
                    )
                    db.session.add(producto)
                    db.session.commit()
                    current_app.logger.info(f"✅ Producto creado: {producto.nombre}")
                except Exception as e:
                    current_app.logger.error(f"❌ Error al crear producto: {e}")
                    continue
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

        if not detalles:
            return jsonify({"error": "Ningún producto válido en la factura"}), 400

        factura = Factura(cliente_id=cliente.id, total=total)
        factura.detalles = detalles
        db.session.add(factura)
        db.session.commit()

        # Generar documento según tipo
        if tipo_factura == "recibo":
            current_app.logger.info("🧾 Generar recibo - pendiente de implementación")
            factura.xml_ubl = "<recibo>No implementado</recibo>"
        elif tipo_factura == "pos":
            current_app.logger.info("🧾 Generar factura POS - pendiente de implementación")
            factura.xml_ubl = "<pos>No implementado</pos>"
        else:
            ruta_xml = generar_xml_ubl(factura.id)
            factura.xml_ubl = Path(ruta_xml).read_text(encoding="utf-8") if ruta_xml else None

        db.session.commit()

        return jsonify({
            "mensaje": "Factura creada exitosamente",
            "factura_id": factura.id,
            "tipo_factura": tipo_factura
        })

    except Exception as e:
        current_app.logger.error(f"❌ Error en /facturar: {str(e)}")
        return jsonify({"error": str(e)}), 500
