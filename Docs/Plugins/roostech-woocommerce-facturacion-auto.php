<?php
/*
Plugin Name: Roostech WooCommerce Facturación
Description: Permite seleccionar el tipo de factura (electrónica, POS o recibo) y envía automáticamente los datos a la API Roostech.
Version: 1.1
Author: Wilson Gallo
*/

add_action('add_meta_boxes', 'roostech_agregar_metabox_facturacion');
add_action('save_post_shop_order', 'roostech_procesar_factura_roostech');

function roostech_agregar_metabox_facturacion() {
    add_meta_box(
        'roostech_tipo_factura',
        'Tipo de Factura Roostech',
        'roostech_mostrar_metabox_factura',
        'shop_order',
        'side',
        'default'
    );
}

function roostech_mostrar_metabox_factura($post) {
    $valor = get_post_meta($post->ID, '_roostech_tipo_factura', true);
    ?>
    <label for="roostech_tipo_factura">Seleccione el tipo de factura:</label>
    <select name="roostech_tipo_factura" id="roostech_tipo_factura" class="widefat">
        <option value="">-- Elegir --</option>
        <option value="electronica" <?php selected($valor, 'electronica'); ?>>Factura Electrónica (XML)</option>
        <option value="pos" <?php selected($valor, 'pos'); ?>>Factura POS</option>
        <option value="recibo" <?php selected($valor, 'recibo'); ?>>Recibo de Caja</option>
    </select>
    <?php
}

function roostech_procesar_factura_roostech($post_id) {
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;

    if (isset($_POST['roostech_tipo_factura'])) {
        $tipo_factura = sanitize_text_field($_POST['roostech_tipo_factura']);
        update_post_meta($post_id, '_roostech_tipo_factura', $tipo_factura);

        if (empty($tipo_factura)) return;

        $order = wc_get_order($post_id);
        if (!$order) return;

        $cliente = array(
            'nombre' => $order->get_billing_first_name() . ' ' . $order->get_billing_last_name(),
            'tipo_documento' => 'CC',
            'numero_documento' => $order->get_meta('_billing_dni') ?: '00000000',
            'email' => $order->get_billing_email(),
            'telefono' => $order->get_billing_phone(),
            'direccion' => $order->get_billing_address_1()
        );

        $productos = array();
        foreach ($order->get_items() as $item) {
            $product = $item->get_product();
            if ($product) {
                $productos[] = array(
                    'producto_id' => $product->get_id(),
                    'cantidad' => $item->get_quantity()
                );
            }
        }

        $data = array(
            'token' => 'SECRETO123',
            'tipo_documento' => $tipo_factura,
            'cliente' => $cliente,
            'productos' => $productos
        );

        $response = wp_remote_post('https://aaa9-167-0-187-141.ngrok-free.app/facturar', array(
            'method' => 'POST',
            'headers' => array('Content-Type' => 'application/json'),
            'body' => json_encode($data),
            'timeout' => 5
        ));

        if (is_wp_error($response)) {
            error_log('[Roostech] Error al enviar factura: ' . $response->get_error_message());
        } else {
            error_log('[Roostech] Factura enviada exitosamente: ' . wp_remote_retrieve_body($response));
        }
    }
}
?>
