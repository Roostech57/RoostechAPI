import os
from flask import current_app
from app.models import Factura, Cliente
import xml.etree.ElementTree as ET
from app import db

def generar_xml_ubl(factura_id):
    factura = Factura.query.get(factura_id)
    if not factura:
        return None

    cliente = Cliente.query.get(factura.cliente_id)
    if not cliente:
        return None

    invoice = ET.Element('Invoice')
    ET.SubElement(invoice, 'ID').text = str(factura.id)
    ET.SubElement(invoice, 'IssueDate').text = factura.fecha_emision.strftime('%Y-%m-%d')

    supplier_party = ET.SubElement(invoice, 'AccountingSupplierParty')
    supplier_party_name = ET.SubElement(supplier_party, 'Party')
    ET.SubElement(supplier_party_name, 'PartyName').text = "Roostech Electronica"

    customer_party = ET.SubElement(invoice, 'AccountingCustomerParty')
    party = ET.SubElement(customer_party, 'Party')
    ET.SubElement(party, 'PartyName').text = cliente.nombre
    party_id = ET.SubElement(party, 'PartyIdentification')
    ET.SubElement(party_id, 'ID').text = cliente.numero_documento

    invoice_lines = ET.SubElement(invoice, 'InvoiceLines')
    for detalle in factura.detalles:
        invoice_line = ET.SubElement(invoice_lines, 'InvoiceLine')
        ET.SubElement(invoice_line, 'ItemName').text = detalle.producto.nombre
        ET.SubElement(invoice_line, 'Quantity').text = str(detalle.cantidad)
        ET.SubElement(invoice_line, 'UnitPrice').text = str(detalle.producto.precio_unitario)
        ET.SubElement(invoice_line, 'Subtotal').text = str(detalle.cantidad * detalle.producto.precio_unitario)

    ET.SubElement(invoice, 'TotalAmount').text = str(factura.total)

    output_dir = os.path.join(current_app.root_path, 'facturas_xml')
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"factura_{factura.id}.xml")

    tree = ET.ElementTree(invoice)
    tree.write(file_path, encoding='utf-8', xml_declaration=True)

    factura.xml_ubl = ET.tostring(invoice, encoding='unicode')
    db.session.commit()

    return file_path