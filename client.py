"""
# odoo_rpc.py
This module provides a class to interact with Odoo's XML-RPC API.
It allows for searching, reading, creating, updating, and deleting records in Odoo models.
It also provides a function to create a CSV file with the models and their descriptions.
It uses the xmlrpc.client library to communicate with the Odoo server.

Author: EdwardTL
"""

from dataclasses import dataclass

from typing import OrderedDict, Literal
import xmlrpc.client

COMP_DOMAIN = Literal['=', '<', '>', '<=', '>=', '!=']

@dataclass
class Printer:
    """
    Printer class to handle printing messages.
    """
    action: Literal['create', 'update', 'delete']
    model: str
    object_id: int | list[int] | list[[int, str]] | bool | None = None
    status: Literal['SUCCESS', 'FAIL', 'PASS'] = 'SUCCESS'
    error_message: str | None = None

    def print(self):
        """
        Print the message based on the action and status.
        """
        message = f"{self.status} | Action: {self.action} | Model: {self.model} | [ID]: {self.object_id}"
        if self.error_message is not None:
            message += f" | Error: {self.error_message}"

        print(message)


@dataclass
class OdooClientServer:
    """
    Odoo client server class to interact with Odoo XML-RPC API.
    """

    user_info: OrderedDict[str, str]

    def __post_init__(self):
        self.url = self.user_info['HOST']
        self.db = self.user_info['DB']
        self.username = self.user_info['USER']
        self.password = self.user_info['PASSWORD']

        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

    def search(self, model: str, domain: list[tuple[str, str, str]]):
        '''
        Search for records in the specified model that match the given domain.
        :param model: The name of the model to search in.
        :param domain: A list of tuples representing the search criteria.
                       Each tuple should be in the format (field_name, operator, value).
        :return: A list of record IDs that match the search criteria.
        '''
        # ids = models.execute_kw(
        #               db, uid, password, 'res.partner', 'search',
        #               [
        #                   [('is_company', '=', True)] <- domain example
        #               ]  
        #)
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'search', [domain])

    def read(self, model: str, ids: list[int], fields: list[str]):
        '''
        Read records from the specified model.
        :param model: The name of the model to read from.
        :param ids: A list of record IDs to read.
        :param fields: A list of field names to retrieve.
        :return: A list of dictionaries representing the records.
        '''

        # data = models.execute_kw(
        #           db, uid, password, 'res.partner', 'read',
        #           [ids],
        #           {'fields': ['name', 'email']}
        # )

        return self.models.execute_kw(
            self.db, self.uid, self.password, model, 'read', [ids], {'fields': fields}
            )
        # Esto es de Gemini
        # data = models.execute_kw(
        #   db, uid, password, 'res.partner', 'read', [ids, ['name', 'email']]
        #)

    def search_read(self, model: str,
        domain: list[tuple[str, str, str]] = None, fields: list[str] = None):
        '''
        Search and read records from the specified model.
        :param model: The name of the model to search and read from.
        :param domain: A list of tuples representing the search criteria.
                       Each tuple should be in the format (field_name, operator, value).
        :param fields: A list of field names to retrieve.
        :return: A list of dictionaries representing the records that match the search criteria.
        '''
        # Ejemplo de Gemini:
        # partners = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
        #     [[('customer_rank', '>', 0)]],
        #     {'fields': ['name', 'phone'], 'limit': 10, 'order': 'name asc'}
        # )
        if domain is None:
            domain = []

        if fields is None:
            fields = ['name']

        return self.models.execute_kw(
            self.db, self.uid, self.password, model, 'search_read', [domain], {'fields': fields}
            )

    def create(self, model: str, vals: dict | list[dict],
        domain_check: str | list[str] = 'name', domain_comp: COMP_DOMAIN = '=', printer = False):
        '''
        Create a new record in the specified model.
        :param model: The name of the model to create a record in.
        :param vals: A dictionary of field names and values for the new record.
        :return: The ID of the newly created record.
        '''
        
        domains = []
        if isinstance(vals, list):
            # print(f"Vals: {vals} are List")
            if isinstance(domain_check, str):
                for value in vals:
                    for k, v in value.items():
                        if k == domain_check:
                            domains.append((domain_check, domain_comp, v))
                            break

            if isinstance(domain_check, list):
                for domain in domain_check:
                    for value in vals:
                        for k, v in value.items():
                            if k == domain:
                                domains.append((domain_check, domain_comp, v))
                    
        if isinstance(vals, dict):
            # print(f"Vals: {vals} are Dictionary")
            domains.append((domain_check, domain_comp, vals[domain_check]))
        
        creation_printer = Printer(
            action = 'create',
            model = model,
            )

        exists = self.search(model, domains)
        
        if not exists:
            try:
                object_id = self.models.execute(
                    self.db, self.uid, self.password, model,
                    'create', vals
                )

                if printer:
                    creation_printer.object_id = object_id
                    creation_printer.status = 'SUCCESS'
                    creation_printer.print()

                return object_id 
            except Exception as e:
                    creation_printer.error_message = str(e)
                    creation_printer.status = 'FAIL'
                    creation_printer.print()

                    return False
        else:
            creation_printer.object_id = exists
            creation_printer.status = 'PASS'
            creation_printer.print()
        
        return exists[0]

    def update_single_record(self, model: str, record_id: int | list[int], new_val: dict, printer = False):
        '''
        Update existing records in the specified model.
        :param model: The name of the model to update records in.
        :param record_id:
            if int: The ID of the record to update.
            if list: A list of record IDs to update with the given value.
        :param vals: A dictionary of field names and values to update.
        :return: List like [[id, new_val]].
        '''
        if isinstance(record_id, int):
            record_id = [record_id]

        update_printer = Printer(
            action = 'update',
            model = model,
            )
        try: 
            object_vals = self.models.execute_kw(
                self.db, self.uid, self.password, model,
                'write',
                [record_id, new_val]
            )
            if printer:
                update_printer.object_id = object_vals
                update_printer.status = 'SUCCESS'
                update_printer.print()

            return object_vals

        except Exception as e:
                update_printer.error_message = str(e)
                update_printer.status = 'FAIL'
                update_printer.print()

                return False
        

    def delete(self, model: str, ids: int | list[int], printer = False) -> None:
        '''
        Delete records from the specified model.
        :param model: The name of the model to delete records from.
        :param ids: A list of record IDs to delete.
        :return: True if the deletion was successful, False otherwise.
        '''
        if isinstance(ids, int):
            ids = [ids]
        
            
        delete_printer = Printer(
            action = 'update',
            model = model,
            )
        try: 
            delete_status = self.models.execute_kw(
            self.db, self.uid, self.password,
            model,
            'unlink',
            [ids]
        )
            if printer:
                delete_printer.object_id = delete_status
                delete_printer.status = 'SUCCESS'
                delete_printer.print()

            return delete_status

        except Exception as e:
                delete_printer.error_message = str(e)
                delete_printer.status = 'FAIL'
                delete_printer.print()

                return False
        

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model,
            'unlink',
            [ids]
        )

    def get_record_names(self, model: str, ids: list[int]):
        '''
        Get the names (textual representation) of records in the specified model.
        :param model: The name of the model to get names from.
        :param ids: A list of record IDs to get names for.
        :return: A list of tuples containing record IDs and their corresponding names.
        '''
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'name_get', [ids])

    def get_models_fields(self, model: str, attributes = False) -> tuple | dict:
        '''
        Get the fields of a specified model.
        :param model: The name of the model to get fields from.
        :return: A dictionary of field names and their corresponding attributes.
        '''
        # fields_info = models.execute_kw(
        #   db, uid, password, 'res.partner', 'fields_get', [], 
        # {'attributes': ['string', 'type']}
        #)
        fields_data = self.models.execute_kw(self.db, self.uid, self.password, model, 'fields_get', [])
        if not attributes:
            fields = [field for field in fields_data.keys()]
            return tuple(fields)
            
        return fields_data


