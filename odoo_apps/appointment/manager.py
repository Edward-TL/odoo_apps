"""
apps/appointment/appt_manager.py
Appointment Manager file
"""
from dataclasses import dataclass
from pprint import pprint

from flask import Response as FlaskResponse

from odoo_apps.client import OdooClient
from odoo_apps.models import APPOINTMENT, CALENDAR
from odoo_apps.response import Response, standarize_response, report_fail

from odoo_apps.calendar.scheduler import Scheduler
from .objects import Appointment

def create_busy_response(object_id) -> Response:
    return Response(
        action = 'create',
        model = CALENDAR.EVENT,
        object = object_id,
        status = 'PASS',
        http_status = 409,
        msg = "User is busy. Request is OK. Try other time"
    )

@dataclass
class AppointmentManager:
    """
    Manages interactions with Odoo's appointment.appointment model via RPC.
    """
    client: OdooClient
    request_fields = tuple([
        'event_start',
        'event_stop',
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

    def extract_appointment_data(self, request: dict) -> Appointment:
        """
        Generates an Appointment object from a request dictionary.

        Args:
            request (dict): Dictionary containing appointment data.

        Returns:
            Appointment: An Appointment object populated with the provided data.
        """
        # Assuming request contains all necessary fields for Appointment


        if request['appointment_type_id'] is None and request['name_type'] is not None:

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
            start_datetime = request['event_start'],
            end_datetime = request['event_stop'],
            name = request['name'],
            resource_ids = request['appointment_resource_id'],
            type_id = request['appointment_type_id'],
            timezone_str = request['timezone_str'],
            partner_ids = request['partner_ids']
        )


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

        if appointment.calendar_event_id is None:

            if printer:
                print('appointment.event.data')
                print(appointment.event.data)

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
                        request = appointment.extract_booking_data(),
                        response = create_busy_response(calendar_response.object)
                    )

        if calendar_response.status == 'SUCCESS':
            try:
                # Use the client.create method which includes built-in printing
                # We don't need domain_check here because we did the check manually above.
                # Pass printer=True to enable the printing from the client method.
                appt_response = self.client.create(
                    model = APPOINTMENT.BOOKING_LINE,
                    vals = appointment.extract_booking_data(),
                    domains = (
                            ['event_start', '>=', appointment.start_datetime],
                            ['event_stop', '<=', appointment.end_datetime],
                    ),
                    printer=printer
                    # domain_check and domain_comp are not needed due to manual check
                )

                if appt_response.status == 'PASS':
                    return standarize_response(
                        request = appointment.extract_booking_data(),
                        response = create_busy_response(appt_response.object)
                    )
                
                return standarize_response(
                    request = appointment.extract_booking_data(),
                    response = appt_response
                )

            except Exception as e:
                # The client.create method should handle printing the error,
                # but we can add an extra layer here if needed, or just return None.
                # Let's rely on client.create's printer.
                error_msg = f"An unexpected error occurred during appointment creation: {e}"
                print(error_msg)
                return standarize_response(
                    request = appointment.extract_booking_data(),
                    response = report_fail(
                        action = 'create',
                        model = APPOINTMENT.BOOKING_LINE,
                        http_status = 400,
                        msg = error_msg
                    )
                )
        
        return standarize_response(
            request = appointment.extract_booking_data(),
            response = calendar_response
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