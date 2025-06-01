
from flask import Blueprint, request, jsonify
from app import db
from app.models import Cliente, Producto, Factura, FacturaDetalle
from app.services.xml_generator import generar_xml_ubl
from pathlib import Path

factura_publica_bp = Blueprint('factura_publica', __name__)

@factura_publica_bp.route('/facturar', methods=['POST'])
def facturar():
    try:
        print("➡️ Iniciando proceso de facturación...")
        data = request.get_json()
        print("📦 Datos recibidos:", data)

        if not data or data.get("token") != "SECRETO123":
            print("❌ Token inválido o datos incompletos.")
            return jsonify({"error": "Token inválido o datos incompletos"}), 401

        cliente_data = data.get("cliente")
        productos_data = data.get("productos")

        if not cliente_data or not productos_data:
            print("❌ Datos de cliente o productos incompletos.")
            return jsonify({"error": "Datos de cliente o productos incompletos"}), 400

        # Buscar o crear cliente
        print("🔍 Buscando cliente por documento:", cliente_data["numero_documento"])
        cliente = Cliente.query.filter_by(numero_documento=cliente_data["numero_documento"]).first()
        if not cliente:
            print("👤 Cliente no existe, creando nuevo.")
            cliente = Cliente(**cliente_data)
            db.session.add(cliente)
            db.session.commit()
        else:
            print("✅ Cliente encontrado:", cliente.nombre)

        # Calcular total y preparar detalles
        total = 0
        detalles = []

        for item in productos_data:
            print("🔍 Buscando producto ID:", item["producto_id"])
            producto = Producto.query.get(item["producto_id"])
            if not producto:
                print(f"❌ Producto ID {item['producto_id']} no encontrado.")
                return jsonify({"error": f"Producto ID {item['producto_id']} no encontrado"}), 400

            cantidad = item["cantidad"]
            precio_unitario = producto.precio_unitario
            subtotal = cantidad * precio_unitario
            total += subtotal

            print(f"🧾 Producto: {producto.nombre}, Cantidad: {cantidad}, Subtotal: {subtotal}")

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

        # Generar XML
        print("🛠 Generando XML UBL para factura ID:", factura.id)
        ruta_xml = generar_xml_ubl(factura.id)
        factura.xml_ubl = Path(ruta_xml).read_text(encoding="utf-8") if ruta_xml else None
        db.session.commit()

        print("✅ Factura creada exitosamente.")
        return jsonify({
            "mensaje": "Factura creada exitosamente",
            "factura_id": factura.id,
            "ruta_xml": ruta_xml
        })

    except Exception as e:
        print("💥 Error inesperado:", str(e))
        return jsonify({"error": str(e)}), 500
