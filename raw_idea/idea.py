import json
import logging
from client import OdooClientServer
from .methods.kitchen import procesar_orden_cocina, actualizar_estado_orden

def odoo_api_handler(request):
    """
    Cloud Function para manejar peticiones de la API de Odoo relacionadas con órdenes de cocina.
    """
    response_data = {
        'status': 'error',
        'message': 'Petición inválida',
        'data': None
    }

    if request.method != 'POST' or not request.is_json:
        response_data['message'] = 'Se requiere una petición POST con datos JSON'
        return json.dumps(response_data), 400

    try:
        request_json = request.get_json()
        logging.info(f"Datos de la petición: {request_json}")

        user_info = request_json.get('user_info')
        if not isinstance(user_info, dict):
            response_data['message'] = "Parámetro 'user_info' faltante o inválido (debe ser un diccionario)"
            return json.dumps(response_data), 400

        odoo_client = OdooClientServer(user_info=user_info)

        method = request_json.get('method')
        payload = request_json.get('payload', {})

        if not method:
            response_data['message'] = 'Faltan el modelo o el método'
            return json.dumps(response_data), 400

        if method == 'procesar_orden_cocina':
            response_data = procesar_orden_cocina(odoo_client, payload)
            
        elif method == 'actualizar_estado_orden':
             response_data = actualizar_estado_orden(odoo_client, payload)
        else:
            response_data['message'] = 'Método inválido'
            return json.dumps(response_data), 400

        return json.dumps(response_data), 200

    except Exception as e:
        response_data['message'] = f'Excepción: {e}'
        logging.error(f"Error general: {e}")
        return json.dumps(response_data), 500