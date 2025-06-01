
# app/routes/cliente_routes.py

from flask import Blueprint, request, jsonify
from app import db
from app.models import Cliente

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/clientes', methods=['GET'])
def listar_clientes():
    clientes = Cliente.query.all()
    resultado = []
    for c in clientes:
        resultado.append({
            "id": c.id,
            "nombre": c.nombre,
            "tipo_documento": c.tipo_documento,
            "numero_documento": c.numero_documento,
            "direccion": c.direccion,
            "telefono": c.telefono,
            "email": c.email
        })
    return jsonify(resultado)

@cliente_bp.route('/clientes', methods=['POST'])
def crear_cliente():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400

    campos_obligatorios = ["nombre", "tipo_documento", "numero_documento"]
    for campo in campos_obligatorios:
        if campo not in data:
            return jsonify({"error": f"Falta el campo obligatorio: {campo}"}), 400

    cliente_existente = Cliente.query.filter_by(numero_documento=data["numero_documento"]).first()
    if cliente_existente:
        return jsonify({"mensaje": "Cliente ya existe", "cliente_id": cliente_existente.id}), 200

    nuevo_cliente = Cliente(
        nombre=data["nombre"],
        tipo_documento=data["tipo_documento"],
        numero_documento=data["numero_documento"],
        direccion=data.get("direccion"),
        telefono=data.get("telefono"),
        email=data.get("email")
    )

    db.session.add(nuevo_cliente)
    db.session.commit()

    return jsonify({
        "mensaje": "Cliente creado exitosamente",
        "cliente_id": nuevo_cliente.id
    }), 201
