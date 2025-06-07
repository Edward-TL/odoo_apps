"""
Helper functions to keep code cleaner
"""
# from pprint import pprint
from typing import Literal

# from odoo_apps.client import OdooClient
from odoo_apps.models import CALENDAR#, APPOINTMENT
from odoo_apps.response import Response

# from odoo_apps.utils.cleaning import replace_values

# from .objects import Event, Appointment

def create_busy_response(object_id) -> Response:
    return Response(
        action = 'create',
        model = CALENDAR.EVENT,
        object = object_id,
        status = 'PASS',
        http_status = 409,
        msg = "User is busy. Request is OK. Try other time"
    )

def create_bad_request_response(
        msg: str, action: Literal['update', 'cancel', 'create'] = 'update'
        ) -> Response:
    return Response(
        action = action,
        model = CALENDAR.EVENT,
        object = None,
        status = 'BAD REQUEST',
        http_status = 400,
        msg = msg
    )

def create_error_response(
    msg: str, action: Literal['update', 'cancel', 'create'] = 'update'
    ) -> Response:
    return Response(
        action = action,
        model = CALENDAR.EVENT,
        object = None,
        status = 'NOT ACCEPTABLE',
        http_status = 406,
        msg = msg
    )



# def check_event(appointment:Appointment, client: OdooClient, printer = False) -> dict:
#     event = appointment.event
#     if printer:
#         print('Checking if `calendar_event_id` was given')
#         pprint(event.data)

#     if 'calendar_event_id' not in event.data and appointment.odoo_id is None:
#         reference_error = 'Missing `calendar_event_id` on `event.data` '
#         reference_error += "and not `appointment_id` assigned on `appointment.odoo_id`. "
#         reference_error += "Please assign one."
#         return create_bad_request_response(
#             msg = reference_error
#         )
    
#     if printer:
#         print('Checking if event exists')

#     domain_check = None
#     missing = None
#     field_check = None
#     if 'calendar_event_id' not in event.data:
#         if printer:
#             print('Missing Calendar Event ID')
#         domain_check = appointment.odoo_id
#         missing = 'calendar_event_id'
#         field_check = 'id'

#     if appointment.odoo_id is not None:
#         if printer:
#             print('Missing Appointment ID')
#         domain_check = appointment.event.odoo_id
#         missing = 'id'
#         field_check = 'calendar_event_id'

#     if printer:
#         print('Checking domain:')
#         print([field_check, '=', domain_check])

#     event_fields = list(event.data.keys())
#     ids = ['id', 'calendar_event_id']
#     for key in ids:
#         if key not in event_fields:
#             event_fields.append(key)

#     replacer = {
#         'name': 'display_name',
#         'start': 'event_start',
#         'stop': 'event_stop'
#     }
#     for old, new in replacer.items():
#         replace_values(
#             old_val = old,
#             new_val = new,
#             array = event_fields
#         )

#     appt_fields = set(client.get_models_fields(APPOINTMENT.BOOKING_LINE))
#     common_fields = [
#         field for field in event_fields if field in appt_fields
#     ]

#     searched_appointment = client.search_read(
#         model = APPOINTMENT.BOOKING_LINE,
#         domain = [
#             [field_check, '=', domain_check]
#         ],
#         fields = common_fields
#     )
    

#     if printer:
#         print('searched appointment')
    
#     if searched_appointment in ([], [None]): # Event DOES NOT exist
#         return create_bad_request_response(
#             msg = 'Missing `calendar_event_id` HAS NEVER BEEN SCHEDULED.'
#         )
    
#     if isinstance(searched_appointment, list):
#         searched_appointment = searched_appointment[0]
#         pprint(searched_appointment)

#     if missing == 'calendar_event_id':
#         if printer:
#             print('Extracting `calendar_event_id`')
#         calendar_event_id = searched_appointment['calendar_event_id'][0]
#         appointment.event.odoo_id = calendar_event_id
#         appointment.event.data['id'] = calendar_event_id
#     else:
#         print('`calendar_event_id` was given')
#         calendar_event_id = event.data['calendar_event_id']

#     # Here is just ID 
#     event_fields.remove('calendar_event_id')
#     replacer = {
#         'event_start': 'start',
#         'event_stop': 'stop'
#     }
#     for old, new in replacer.items():
#         replace_values(
#             old_val = old,
#             new_val = new,
#             array = event_fields
#         )
        
#     searched_event = client.search_read(
#         model = CALENDAR.EVENT,
#         domain = [
#             ['id', '=', calendar_event_id]
#         ],
#         fields = event_fields
#     )

#     if isinstance(searched_event, list):
#         searched_event = searched_event[0]
#         pprint(searched_event)

#     if missing == 'appointment_id':
#         if printer:
#             print('Extracting appointment `id`')
#         appointment_id = searched_appointment[0]['id'][0]
#         appointment.odoo_id = appointment_id

#     return event, searched_appointment, searched_event
    
    # if printer:
    #     print('Checking if there is no conflict with other event')

    # busy_check = self.client.search_read(
    #     model = CALENDAR.EVENT,
    #     domain = [
    #         ['start', '>=', event.data['start']],
    #         ['stop', '<=', event.data['stop']],
    #         # ['partner_ids', 'in', [event.data['partner_ids']]]
    #         # ['resource_ids', 'in', event.data['resource_ids']]
    #     ],
    #     fields = ['start', 'stop', 'partner_ids', 'resource_ids']
    # )

    # if printer:
    #     print('Busy check')
    #     print(busy_check)

    # if busy_check not in ([], [None]):
    #     busy_msg = f"There's a conflict with the this/these event(s): {busy_check}"
    #     busy_msg += '\n. Please, free space in the calendars involved.'

    #     return create_bad_request_response(
    #         msg = busy_msg
    #     )
    # if printer:
    #     print('Everyone is available')

