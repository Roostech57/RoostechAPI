from flask import Blueprint, request, jsonify
from app import db
from app.models import Cliente, Producto, Factura, FacturaDetalle
from app.services.xml_generator import generar_xml_ubl
from datetime import datetime

factura_publica_bp = Blueprint('factura_publica_bp', __name__)

@factura_publica_bp.route('/facturar', methods=['POST'])
def facturar():
    try:
        data = request.get_json()
        print("📌 Datos recibidos:", data)

        if data.get("token") != "SECRETO123":
            return jsonify({"error": "Token inválido"}), 403

        cliente_data = data.get("cliente")
        print("🧩 Cliente recibido:", cliente_data)

        cliente = Cliente.query.filter_by(numero_documento=cliente_data.get("numero_documento")).first()
        if not cliente:
            cliente = Cliente(
                nombre=cliente_data.get("nombre"),
                tipo_documento=cliente_data.get("tipo_documento"),
                numero_documento=cliente_data.get("numero_documento"),
                email=cliente_data.get("email"),
                telefono=cliente_data.get("telefono"),
                direccion=cliente_data.get("direccion")
            )
            db.session.add(cliente)
            db.session.commit()
            print("➕ Cliente nuevo creado:", cliente.nombre)
        else:
            print("✅ Cliente ya existe:", cliente.nombre)

        factura = Factura(
            cliente_id=cliente.id,
            fecha_emision=datetime.now(),
            total=0.0
        )
        db.session.add(factura)
        db.session.flush()

        total_factura = 0.0

        for item in data.get("productos", []):
            print("🔍 Revisando producto:", item)

            producto = Producto.query.get(item.get("producto_id"))
            if not producto:
                producto = Producto(
                    id=item.get("producto_id"),
                    nombre=item.get("nombre"),
                    descripcion=item.get("descripcion", ""),
                    referencia="",
                    precio_unitario=item.get("precio_unitario", 0.0),
                    stock=0
                )
                db.session.add(producto)
                db.session.flush()
                print("➕ Producto creado automáticamente:", producto.nombre)

            cantidad = item.get("cantidad", 1)
            subtotal = cantidad * producto.precio_unitario
            detalle = FacturaDetalle(
                factura_id=factura.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=producto.precio_unitario,
                subtotal=subtotal
            )
            db.session.add(detalle)
            total_factura += subtotal
            print("🧾 Producto agregado:", producto.nombre, "Cantidad:", cantidad, "Subtotal:", subtotal)

        factura.total = total_factura
        db.session.commit()

        print("💾 Factura creada con ID:", factura.id)

        ruta_xml = generar_xml_ubl(factura)
        print("📄 XML generado y guardado:", ruta_xml)

        return jsonify({"mensaje": "Factura generada exitosamente", "factura_id": factura.id}), 200

    except Exception as e:
        print("🔥 Error inesperado:", str(e))
        return jsonify({"error": "Error interno del servidor"}), 500

