import os
from lxml import etree

def generar_xml_ubl(factura):
    """
    Genera un archivo XML simple en formato UBL ficticio (puede ajustarse a especificaciones reales).
    """
    root = etree.Element("Factura")
    etree.SubElement(root, "ID").text = str(factura.id)
    etree.SubElement(root, "FechaEmision").text = str(factura.fecha_emision)

    cliente_elem = etree.SubElement(root, "Cliente")
    etree.SubElement(cliente_elem, "Nombre").text = factura.cliente.nombre
    etree.SubElement(cliente_elem, "Documento").text = factura.cliente.numero_documento
    etree.SubElement(cliente_elem, "Direccion").text = factura.cliente.direccion
    etree.SubElement(cliente_elem, "Email").text = factura.cliente.email
    etree.SubElement(cliente_elem, "Telefono").text = factura.cliente.telefono

    detalles_elem = etree.SubElement(root, "Detalles")
    for detalle in factura.detalles:
        item = etree.SubElement(detalles_elem, "Item")
        etree.SubElement(item, "ProductoID").text = str(detalle.producto.id)
        etree.SubElement(item, "Nombre").text = detalle.producto.nombre
        etree.SubElement(item, "Cantidad").text = str(detalle.cantidad)
        etree.SubElement(item, "PrecioUnitario").text = str(detalle.precio_unitario)
        etree.SubElement(item, "Subtotal").text = str(detalle.subtotal)

    etree.SubElement(root, "Total").text = str(factura.total)

    xml_str = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    # Ruta donde se guarda el archivo
    carpeta = "app/facturas_xml"
    os.makedirs(carpeta, exist_ok=True)
    ruta_archivo = os.path.join(carpeta, f"factura_{factura.id}.xml")

    with open(ruta_archivo, "wb") as f:
        f.write(xml_str)

    return ruta_archivo
