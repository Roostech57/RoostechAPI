from flask import Blueprint, request, jsonify
from app import db
from app.models import Cliente, Producto, Factura, FacturaDetalle
from app.services.xml_generator import generar_xml_ubl

factura_publica_bp = Blueprint('factura_publica', __name__)

@factura_publica_bp.route('/facturar', methods=['POST'])
def facturar():
    try:
        data = request.get_json()
        tipo = data.get("tipo_documento")
        cliente_data = data.get("cliente")
        productos_data = data.get("productos")

        if not cliente_data or not productos_data:
            return jsonify({"error": "Datos incompletos"}), 400

        # Verificar si el cliente ya existe
        cliente = Cliente.query.filter_by(numero_documento=cliente_data["numero_documento"]).first()
        if not cliente:
            cliente = Cliente(
                nombre=cliente_data["nombre"],
                numero_documento=cliente_data["numero_documento"],
                tipo_documento=cliente_data.get("tipo_documento", "CC"),
                email=cliente_data.get("email"),
                telefono=cliente_data.get("telefono"),
                direccion=cliente_data.get("direccion"),
            )
            db.session.add(cliente)
            db.session.commit()

        # Crear la factura
        factura = Factura(cliente_id=cliente.id, total=0)
        db.session.add(factura)
        db.session.flush()

        total = 0
        for item in productos_data:
            producto = Producto.query.get(item["producto_id"])
            if not producto:
                return jsonify({"error": f"Producto ID {item['producto_id']} no encontrado"}), 404

            cantidad = item["cantidad"]
            subtotal = cantidad * producto.precio
            detalle = FacturaDetalle(
                factura_id=factura.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=subtotal
            )
            db.session.add(detalle)
            total += subtotal

        factura.total = total
        db.session.commit()

        # Generar XML si aplica
        if tipo != "recibo":
            ruta = generar_xml_ubl(factura.id)
        else:
            ruta = None

        return jsonify({
            "mensaje": "Factura creada exitosamente",
            "factura_id": factura.id,
            "ruta_xml": ruta
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
