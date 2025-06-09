"""
apps/appointment/appt_manager.py
Appointment Manager file
"""
from dataclasses import dataclass
from datetime import datetime
from pprint import pprint

from flask import Response as FlaskResponse

from odoo_apps.client import OdooClient
from odoo_apps.models import APPOINTMENT, CALENDAR
from odoo_apps.response import Response, standarize_response, report_fail

from odoo_apps.calendar.scheduler import Scheduler
# from odoo_apps.calendar.objects import Event

from odoo_apps.utils.time_management import (
    extract_hour,
    TIME_STR
    )

from .checkers import (
    create_bad_request_response,
    create_busy_response,
    create_error_response
)
from .objects import Appointment


@dataclass
class AppointmentManager:
    """
    Manages interactions with Odoo's appointment.appointment model via RPC.
    """
    client: OdooClient
    request_fields = tuple([
        'start',
        'stop',
        'name',
        'appointment_resource_id',
        'appointment_type_id',
        'timezone_str',
        'partner_id',
        'client_reference_field',
        'client_reference_value'
    ])
    def __post_init__(self):
        self.scheduler = Scheduler(self.client)

    def get_booking_url(self, appointment_type_id: int):
        """
        Returns the webpage url to schedule and appointment by website
        """
        return self.client.search_read(
            model = APPOINTMENT.INVITE,
            domain = [('appointment_type_ids','=', appointment_type_id)],
            fields = ['book_url']
        )[0]['book_url']
    
    def check_slots_available(
            self,
            appointment_type_id: int,
            weekday: int,
            start_hour: int,
            end_hour: int
            ) -> list[int]:
        """
        Check if there's a worktime slot available for the given time
        range. This does not mean that there's a free space on calendar or
        appointments booking line.
        Args:
            - appointment_type_id: int value of the appointment_type required
            - weekday: int value of weekday. Monday is 1.
            - start_hour: INT value
            - end_hour: INT value
        
        Validation:
        domains = [
                ['appointment_type_id', '=', appointment_type_id],
                ['weekday', '=', weekday],
                ['start_hour', '<=', start_hour],
                ['end_hour', '>=', end_hour]
            ]
        Returns:
            A list of slots ids that matches with the given data.
        """
        return self.client.search(
            APPOINTMENT.SLOT,
            domains = [
                ['appointment_type_id', '=', appointment_type_id],
                ['weekday', '=', weekday],
                ['start_hour', '<=', start_hour],
                ['end_hour', '>=', end_hour]
            ]
        )
    
    def weekday_slots(
            self,
            appointment_type_id: int,
            weekday: int) -> dict:
        return self.client.search_read(
            APPOINTMENT.SLOT,
            domain = [
                ['appointment_type_id', '=', appointment_type_id],
                ['weekday', '=', weekday]
            ],
            fields = ['start_hour', 'end_hour']
        )

    def extract_appointment_data(self, request: dict) -> Appointment:
        """
        Generates an Appointment object from a request dictionary.

        Args:
            request (dict): Dictionary containing appointment data.

        Returns:
            Appointment: An Appointment object populated with the provided data.
        """
        # Assuming request contains all necessary fields for Appointment


        if request['appointment_type_id'] is None and request['name_type'] is None:

            return standarize_response(
                request = request,
                response = Response(
                    action = 'create',
                    model = APPOINTMENT.TYPE,
                    http_status = 400,
                    msg = "Neither appointment type nor name type is set."
                )
            )
        if request['appointment_type_id'] is None:
            existing_ids = self.client.search(
                model = APPOINTMENT.TYPE,
                domains = [
                    ('active', '=', True),
                    ('name', '=', request['name_type'])
                ]
            )
            if len(existing_ids) > 1:
                request['appointment_type_id'] = existing_ids
            else:
                request['appointment_type_id'] = existing_ids[0]

        appointment = Appointment(
            start_request = request['start'],
            end_request = request['stop'],
            name = request['name'],
            resource_ids = request['appointment_resource_id'],
            type_id = request['appointment_type_id'],
            timezone_str = request['timezone_str'],
            partner_ids = request['partner_ids']
        )

        if 'calendar_event_id' in request:
            appointment.calendar_event_id = request['calendar_event_id']
            appointment.event.odoo_id = request['calendar_event_id']
            appointment.event.data['calendar_event_id'] = request['calendar_event_id']

        return appointment

    def book_appointment(self, appointment: Appointment, printer=False) -> FlaskResponse:
        """
        Creates a new appointment in Odoo using RPC.

        Args:
            appointment (Appointment): Appointment object containing the data for the new appointment.

        Returns:
            int or list[int] or None: The ID(s) of the created appointment(s) if successful,
                                      or the ID(s) of existing appointment(s) if found (PASS),
                                      or None if an error occurred (FAIL).
        """
        if printer:
            pprint(appointment.extract_booking_data())
        # REVISAR LOS SLOTS
        slot_weekday = datetime.strptime(appointment.start_utc_str, TIME_STR).weekday() + 1
        slots = self.check_slots_available(
            appointment_type_id = appointment.type_id,
            weekday = slot_weekday,
            start_hour = extract_hour(appointment.start_utc_str),
            end_hour = extract_hour(appointment.end_utc_str)
        )

        if slots in ([], [None]):
            # slot_ranges = self.weekday_slots(
            #     appointment_type_id = appointment.type_id,
            #     weekday = slot_weekday
            # )

            # if len(slot_ranges) > 1:
            #     first_slot = slot_ranges[0]['s']
            return standarize_response(
                request = appointment.requested_data(),
                response = Response(
                    action = 'update',
                    model = CALENDAR.EVENT,
                    object = appointment.event.odoo_id,
                    status = 'CONFLICT',
                    http_status = 409,
                    msg = 'There is not Slot available. Try another space.'
                )
            )

        if appointment.calendar_event_id is None:

            if printer:
                print('appointment.event.data')
                pprint(appointment.event.data)

            calendar_response = self.scheduler.create_calendar_event(
                event = appointment.event,
                printer=printer
            )
            if printer:
                print("CALENDAR RESPONSE")
                calendar_response.print()
                print("STATUS = ", calendar_response.status)

            appointment.calendar_event_id = calendar_response.object
    
            if printer:
                pprint(appointment.extract_booking_data())

            if calendar_response.status == 'PASS':

                return standarize_response(
                        request = appointment.requested_data(),
                        response = create_busy_response(calendar_response.object)
                    )

        if calendar_response.status == 'SUCCESS':
            try:
                # Use the client.create method which includes built-in printing
                # We don't need domain_check here because we did the check manually above.
                # Pass printer=True to enable the printing from the client method.
                appt_response = self.client.create(
                    model = APPOINTMENT.BOOKING_LINE,
                    vals = appointment.requested_data(),
                    domains = (
                            ['event_start', '>=', appointment.start_request],
                            ['event_stop', '<=', appointment.end_request],
                    ),
                    printer=printer
                    # domain_check and domain_comp are not needed due to manual check
                )

                if appt_response.status == 'PASS':
                    return standarize_response(
                        request = appointment.requested_data(),
                        response = create_busy_response(appt_response.object)
                    )
                
                return standarize_response(
                    request = appointment.requested_data(),
                    response = appt_response
                )

            except Exception as e:
                # The client.create method should handle printing the error,
                # but we can add an extra layer here if needed, or just return None.
                # Let's rely on client.create's printer.
                error_msg = f"An unexpected error occurred during appointment creation: {e}"
                print(error_msg)
                return standarize_response(
                    request = appointment.requested_data(),
                    response = report_fail(
                        action = 'create',
                        model = APPOINTMENT.BOOKING_LINE,
                        http_status = 400,
                        msg = error_msg
                    )
                )
        
        return standarize_response(
            request = appointment.requested_data(),
            response = calendar_response
        )
    

    def reschedule(self, appointment: Appointment, printer = False, timeoffset = '-0600') -> FlaskResponse:
        """
        Reschedules an existing calendar event after performing validation and conflict checks.
        
        Request Args:
            - appointment_type_id: Int value that represents the type of appointment
            - client_id: Int value of the clients refference.
            - calendar_event_id: Int value of the event that wants to be
            - name: Optional[String] value with that specify that is an Reschedule
            - start: Datetime STRING value with the format `%Y-%m-%d %H:%M %z` of the
                tentative new datetime start schedule. 
            - stop: Datetime STRING value with the format `%Y-%m-%d %H:%M %z` of the
                tentative new datetime stop schedule.

        Returns:
            - response: FlaskResponse, where the response['response'] object contains the data
                of action succes. Remember that does can be (but not exclusively):

                SUCCESS, FAIL, PASS, BAD REQUEST, NOT ACEPTABLE, CONFLICT

                From odoo_apps.response check `meaning` and `http_meaning` for more context.
        """

        # "One" is added because in Odoo Monday is 1, and in .weekday() it's 0
        slot_weekday = datetime.strptime(appointment.start_utc_str, TIME_STR).weekday() + 1
        slots = self.check_slots_available(
            appointment_type_id = appointment.type_id,
            weekday = slot_weekday,
            start_hour = extract_hour(appointment.start_utc_str),
            end_hour = extract_hour(appointment.end_utc_str)
        )

        if slots in ([], [None]):
            return standarize_response(
                request = appointment.requested_data(),
                response = Response(
                    action = 'update',
                    model = APPOINTMENT.BOOKING_LINE,
                    object = appointment.event.odoo_id,
                    status = 'CONFLICT',
                    http_status = 409,
                    msg = 'There is not Slot available. Try another space.'
                )
            )
        
        can_modify = self.client.search(
            model = CALENDAR.EVENT,
            domains = [
                ['id', '=', appointment.calendar_event_id],
                ['partner_ids', '=', appointment.partner_ids]
            ]
        )
        if not can_modify:
            return standarize_response(
                request = appointment.requested_data(),
                response = Response(
                    action = 'update',
                    model = CALENDAR.EVENT,
                    object = appointment.event.odoo_id,
                    status = 'CONFLICT',
                    http_status = 409,
                    msg = 'There is no calendar_event with this partner.'
                )
            )
        try:
            return standarize_response(
                request = appointment.requested_data(),
                response = self.scheduler.move_calendar_event(
                    event_id = appointment.calendar_event_id,
                    new_start = appointment.start_utc_str,
                    new_stop = appointment.end_utc_str,
                    update_name = appointment.name,
                    printer=printer
                )
            )
        
        except Exception as e:
            exception_msg = f"Error al actualizar la cita del calendario '{appointment.name}': {e}"
            print(exception_msg)
            return create_error_response(
                msg = exception_msg,
                action = 'cancel'
            )

    def cancel(self, request_body: dict, printer = FlaskResponse) -> FlaskResponse:
        """
        Cancels (deletes) a calendar event based on its ID.

        This method attempts to delete a calendar event identified by
        `calendar_event_id` via `odoo.client`. It first validates the presence of
        `calendar_event_id` in the event data and checks if the event actually exists
        before attempting deletion.
        Optional debug information can be printed during the process.

        Args:
            calendar_event_id: The Int value of calendar event in odoo db, that is.
                attempt to be deleted. It only requires calendar_event_id because, it's the
                real reference of the appointment. Once is deleted from calendar, the appointment
                it's deleted from appointments.booking_line

        Returns:
            FlaskResponse: An object suitable for an HTTP response in a Flask application.
                - If `calendar_event_id` is missing or the event does not exist,
                it returns a "bad request" response generated by
                `create_bad_request_response`.
                - If the deletion is successful, it returns the response from
                `self.client.delete`.
                - If an error occurs during deletion, it returns an error
                response generated by `create_error_response`.
        """
        if printer:
            print('Checking if `calendar_event_id` was given')

        if 'calendar_event_id' not in request_body:
            return create_bad_request_response(
                msg = f'Missing `calendar_event_id` on request. Keys given: {request_body.keys()}',
                action = 'cancel'
            )
        
        if 'partner_ids' not in request_body:
            return create_bad_request_response(
                msg = f'Missing `calendar_event_id` on request. Keys given: {request_body.keys()}',
                action = 'cancel'
            )
        
        can_cancel = self.client.search(
            model = CALENDAR.EVENT,
            domains = [
                ['id', '=', request_body['calendar_event_id']],
                ['partner_ids', '=', request_body['partner_ids']]
            ]
        )
        if not can_cancel:
            return standarize_response(
                request = request_body,
                response = Response(
                    action = 'update',
                    model = CALENDAR.EVENT,
                    object = request_body['calendar_event_id'],
                    status = 'CONFLICT',
                    http_status = 409,
                    msg = 'There is no calendar_event with this partner.'
                )
            )
        

        # self.client.update_single_record(
        #     model=APPOINTMENT.APPOINTMENT,
        #     record_id=appointment_id,
        #     new_val={'state': 'cancel'},
        #     printer=True
        # )
        try:
            return standarize_response(
                request = request_body,
                response = self.scheduler.cancel(
                    request_body['calendar_event_id']
                    )
            )
        
        except Exception as e:
            ceid = request_body['calendar_event_id']
            exception_msg = f"Error al cancelar la cita del calendario '{ceid}': {e}"
            print(exception_msg)
            return create_error_response(
                msg = exception_msg,
                action = 'cancel'
            )
    # def find_appointments(
    #     self,
    #     domain: List[tuple[str, str, any]] = None,
    #     fields: List[str] = None
    # ) -> List[dict]:
    #     """
    #     Searches and reads appointments from Odoo.

    #     Args:
    #         domain (List[tuple[str, str, any]], optional): Odoo domain for searching. Defaults to [].
    #         fields (List[str], optional): List of fields to read. Defaults to ['name'].

    #     Returns:
    #         List[dict]: A list of dictionaries, each representing an appointment record.
    #     """
    #     print("Searching for appointments...")
    #     # Use the client.search_read method
    #     appointments_data = self.client.search_read(
    #         model=APPOINTMENT.APPOINTMENT,
    #         domain=domain,
    #         fields=fields
    #     )
    #     print(f"Found {len(appointments_data)} appointments.")
    #     # pprint(appointments_data) # Uncomment for debugging
    #     return appointments_data

    # def get_appointment_details(self, appointment_id: int, fields: List[str] = None) -> Optional[dict]:
    #     """
    #     Reads details of a specific appointment by ID.

    #     Args:
    #         appointment_id (int): The ID of the appointment to read.
    #         fields (List[str], optional): List of fields to read. Defaults to ['name'].

    #     Returns:
    #         Optional[dict]: A dictionary representing the appointment record, or None if not found.
    #     """
    #     print(f"Reading details for appointment ID: {appointment_id}")
    #     # Use the client.read method
    #     appointments_data = self.client.read(
    #         model=APPOINTMENT.APPOINTMENT,
    #         ids=[appointment_id],
    #         fields=fields if fields is not None else ['name'] # Ensure fields is a list
    #     )
    #     if appointments_data:
    #         # read returns a list, even for a single ID
    #         return appointments_data[0]
    #     return None # Appointment not found

    # def cancel_appointment(self, appointment_id: int) -> bool:
    #     """
    #     Cancels an appointment by setting its state (assuming 'cancel' state exists).
    #     Note: Odoo appointment models might have specific methods for cancellation
    #     or rely on state changes. This is a generic update example.
    #     A more robust approach might call a specific Odoo method like 'action_cancel'.

    #     Args:
    #         appointment_id (int): The ID of the appointment to cancel.

    #     Returns:
    #         bool: True if the update was successful, False otherwise.
    #     """
    #     print(f"Attempting to cancel appointment ID: {appointment_id}")
    #     # This assumes there's a 'state' field and a 'cancel' value.
    #     # Check Odoo's model definition for the correct state field and value.
    #     # A safer way is often to call a specific Odoo method if available.
    #     # Example using update_single_record:
    #     # update_success = self.client.update_single_record(
    #     #     model=APPOINTMENT.APPOINTMENT,
    #     #     record_id=appointment_id,
    #     #     new_val={'state': 'cancel'}, # Replace 'state' and 'cancel' with actual field/value
    #     #     printer=True
    #     # )
    #     # return update_success is not False # update_single_record returns True/False or other values

    #     # Example using delete (if cancellation means deletion)
    #     delete_success = self.client.delete(
    #         model=APPOINTMENT.APPOINTMENT,
    #         ids=appointment_id,
    #         printer=True
    #     )
    #     return delete_success is not False # delete returns True/False

    # # Add other methods as needed (e.g., update_appointment, reschedule_appointment)
    # # These would typically use self.client.update_single_record or specific Odoo methods.