
import logging
from odoo_apps.client import OdooClient

def procesar_orden_cocina(odoo_client: OdooClient, payload: dict) -> dict:
    """
    Procesa una orden de cocina, creando un pedido de venta y generando un link de pago.
    :param odoo_client: Instancia de la clase OdooClient.
    :param payload: Diccionario con los datos de la orden de cocina.
    :return: Un diccionario con el resultado del procesamiento de la orden.
    """
    response_data = {
        'status': 'error',
        'message': 'Error al procesar la orden de cocina',
        'data': None
    }
    try:
        orden_data = payload.get('orden_data')
        if not orden_data:
            response_data['message'] = 'Faltan los datos de la orden en el payload'
            return response_data

        cliente_id = orden_data.get('cliente_id')  # Obtener el ID del cliente
        if not cliente_id:
            response_data['message'] = 'Falta el ID del cliente en los datos de la orden'
            return response_data
        
        # Crear la orden de venta en Odoo
        orden_venta_vals = {
            'partner_id': cliente_id,  # Usar el ID del cliente
            'state': 'draft',  # Borrador
            'order_line': [],  # Se agregarán las líneas de la orden más adelante
        }
        
        orden_venta_id = odoo_client.create('sale.order', orden_venta_vals)
        if not orden_venta_id:
            response_data['message'] = 'No se pudo crear la orden de venta en Odoo'
            return response_data
        
        total_orden = 0.0

        # Iterar sobre los platillos de la orden
        for platillo_info in orden_data.get('platillos', []):
            platillo_id = platillo_info.get('platillo_id')
            cantidad = platillo_info.get('cantidad', 1)
            variante_id = platillo_info.get('variante_id')
            extras_ids = platillo_info.get('extras_ids', [])

            # Buscar el platillo en Odoo
            platillo = odoo_client.read('product.product', [platillo_id], ['name', 'price'])
            if not platillo:
                response_data['message'] = f'No se encontró el platillo con ID {platillo_id}'
                return response_data
            
            precio_platillo = platillo[0]['price']
            nombre_platillo = platillo[0]['name']
            
             # Si hay una variante, buscarla y ajustar el precio
            if variante_id:
                variante = odoo_client.read('product.product', [variante_id], ['name', 'price'])
                if variante:
                    precio_platillo = variante[0]['price']
                    nombre_platillo = variante[0]['name'] # agregar el nombre de la variante al nombre del producto
                else:
                    response_data['message'] = f'No se encontró la variante con ID {variante_id}'
                    return response_data
            
            # Calcular el precio de los extras
            precio_extras = 0.0
            if extras_ids:
                extras = odoo_client.read('product.product', extras_ids, ['name', 'price'])
                if extras:
                    for extra in extras:
                        precio_extras += extra['price']
                else:
                     response_data['message'] = 'No se encontraron algunos de los extras'
                     return response_data
            
            # Calcular el precio total de la línea de la orden
            precio_total_linea = (precio_platillo + precio_extras) * cantidad
            total_orden += precio_total_linea
            
            # Crear la línea de la orden de venta
            order_line_vals = {
                'order_id': orden_venta_id,
                'product_id': variante_id if variante_id else platillo_id,  # Usar la variante si existe
                'product_uom_qty': cantidad,
                'price_unit': precio_platillo + precio_extras,  # Precio base + precio de extras
                'name': nombre_platillo,  # Incluir el nombre del platillo
            }
            
            # Crear la línea de la orden de venta en Odoo
            odoo_client.create('sale.order.line', order_line_vals)
        
        # Actualizar el total de la orden de venta
        odoo_client.update('sale.order', [orden_venta_id], {'amount_total': total_orden})
        
        # Confirmar la orden de venta (esto puede generar el link de pago)
        odoo_client.execute_function('sale.order', 'action_confirm', [orden_venta_id])
        
        # Obtener el link de pago (esto depende de la configuración de tu módulo de pagos en Odoo)
        # Aquí se asume que hay un campo 'payment_link' en la orden de venta.  Esto puede variar.
        orden_venta = odoo_client.read('sale.order', [orden_venta_id], ['payment_link'])
        pago_link = orden_venta[0]['payment_link'] if orden_venta else None
        
        if not pago_link:
            response_data['message'] = 'No se pudo generar el link de pago'
            return response_data
        
        # Enviar la orden a la tableta de la cocina (simulado)
        logging.info(f"Enviando orden a la cocina para el platillo: {nombre_platillo}")
        
        response_data['status'] = 'success'
        response_data['message'] = 'Orden de cocina procesada exitosamente'
        response_data['data'] = {
            'orden_venta_id': orden_venta_id,
            'pago_link': pago_link,
            'nombre_platillo': nombre_platillo
        }
        return response_data

    except Exception as e:
        response_data['message'] = f'Error al procesar la orden de cocina: {e}'
        logging.error(response_data['message'])
        return response_data
    
def actualizar_estado_orden(odoo_client: OdooClient, payload: dict) -> dict:
    """
    Actualiza el estado de una orden de venta en Odoo.
    :param odoo_client: Instancia de la clase OdooClient.
    :param payload: Diccionario con los datos para actualizar el estado de la orden.
    :return: Un diccionario con el resultado de la actualización del estado.
    """
    response_data = {
        'status': 'error',
        'message': 'Error al actualizar el estado de la orden',
        'data': None
    }
    try:
        orden_venta_id = payload.get('orden_venta_id')
        nuevo_estado = payload.get('nuevo_estado')

        if not orden_venta_id or not nuevo_estado:
            response_data['message'] = 'Faltan el ID de la orden de venta o el nuevo estado en el payload'
            return response_data

        # Verificar que el nuevo estado sea válido (opcional, según tus estados de Odoo)
        estados_validos = ['por_aceptar', 'en_preparacion', 'listo', 'entregado', 'cancelado']  # Ejemplo
        if nuevo_estado not in estados_validos:
            response_data['message'] = f'Estado de orden inválido: {nuevo_estado}'
            return response_data

        # Mapear el estado de la aplicación al estado de Odoo (esto depende de tus estados en Odoo)
        estado_odoo = {
            'por_aceptar': 'draft',  # Borrador,  ejemplo
            'en_preparacion': 'sale',  # Confirmado, ejemplo
            'listo': 'done',  # Hecho, ejemplo
            'entregado': 'delivered', # Estado personalizado
            'cancelado': 'cancel', # Cancelado
        }.get(nuevo_estado)

        if not estado_odoo:
            response_data['message'] = f'No se pudo mapear el estado {nuevo_estado} al estado de Odoo'
            return response_data

        # Actualizar el estado de la orden de venta en Odoo
        odoo_client.update('sale.order', [orden_venta_id], {'state': estado_odoo})

        response_data['status'] = 'success'
        response_data['message'] = 'Estado de la orden actualizado exitosamente'
        response_data['data'] = {'orden_venta_id': orden_venta_id, 'nuevo_estado': nuevo_estado}
        return response_data

    except Exception as e:
        response_data['message'] = f'Error al actualizar el estado de la orden: {e}'
        logging.error(response_data['message'])
        return response_data
