"""
# odoo_rpc.py
This module provides a class to interact with Odoo's XML-RPC API.
It allows for searching, reading, creating, updating, and deleting records in Odoo models.
It also provides a function to create a CSV file with the models and their descriptions.
It uses the xmlrpc.client library to communicate with the Odoo server.

Author: EdwardTL
"""
import csv
import io
import re
from pathlib import Path
from dataclasses import dataclass
from typing import OrderedDict
import xmlrpc.client
from pprint import pprint

import pandas as pd

from .response import Response
from .utils.cleaning import check_domains, CompDomain

InterestFields = ['string', 'help', 'type', 'selection']

PROJECT_PATH = str(
    Path(__file__).resolve().parent.parent
    )

TABLES_DIR = 'tables_files'

output = io.StringIO()
DEFAULT_CSV_FILE = f'{PROJECT_PATH}/{TABLES_DIR}/odoo_tables.csv'
DEFAULT_XLSX_FILE = f'{PROJECT_PATH}/{TABLES_DIR}/xodoo_tables.xlsx'


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
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search', [domain])

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

    def create(
        self, model: str, vals: dict | list[dict],
        domain_check: str | list[str] = 'name',
        domain_comp: CompDomain | list[CompDomain] = '=', printer = False
        ) -> Response:
        '''
        Create a new record in the specified model.
        :param model: The name of the model to create a record in.
        :param vals: A dictionary of field names and values for the new record.
        :return: The ID of the newly created record.
        '''

        domains = check_domains(
            domain_check = domain_check,
            domain_comp = domain_comp,
            vals = vals
        )

        if printer:
            print("DOMAINS: ", domains)
        response = Response(
            action = 'create',
            model = model
            )

        exists = self.search(model, domains)
        if printer:
            print(exists)

        if not exists:
            try:
                object_id = self.models.execute(
                    self.db, self.uid, self.password, model,
                    'create', vals
                )
                
                response.object_id = object_id
                response.status = 'SUCCESS'
                response.update_message()
                if printer:
                    print(object_id)
                    print('success creating')
                    response.print()

                return response

            except Exception as e:
                response.status = 'FAIL'
                response.update_message(error_message=str(e))
                if printer:
                    response.print()

                return response

        else:
            if isinstance(exists,list):
                response.object_id = exists[0]
            else:
                response.object_id = exists

            response.status = 'PASS'
            response.update_message()
            if printer:
                print('passing')
                response.print()

        return response

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

        update_printer = Response(
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


        delete_printer = Response(
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

    def read_fields(self, model,
        domain: list[tuple[str, str, str]] = None, fields: list[str] = None) -> list[dict]:
        """
        Combine functions read and search for special fields or
        models that does not have a field called 'name'
        """

        return self.read(
            model = model,
            ids = self.search(
                model = model,
                domain = domain
            ),
            fields = fields
        )

    def print_fields(self, model,
    interest_fields: set | list = InterestFields, get_values=False) -> None | list:
        """
        Print fields from a model
        :param model: Model name
        :param fields: Fields to get
        :return: Dictionary of fields
        """
        attribute_fields = self.get_models_fields(
            model,
            {
                'attributes': ['string', 'help', 'type']
                }
                )
        clean_fields = {}
        for field, props in attribute_fields.items():
            # print(props)
            # print(field)
            if field not in clean_fields:
                clean_fields[field] = {}
            for k, v in props.items():
                if k in interest_fields:
                    clean_fields[field][k] = v
        pprint(
            clean_fields
        )
        if get_values:
            return list(clean_fields.keys())


def create_models_file(
    self,
    csv_file = DEFAULT_CSV_FILE,
    xlsx_file = DEFAULT_XLSX_FILE) -> None:
    """
    Create a CSV file with the models and their descriptions.
    :param client: OdooClientServer instance
    :return: None
    """

    odoo_tables_file = open(csv_file, 'w', encoding='utf-8')
    writer = csv.writer(odoo_tables_file)
    writer.writerow(['app', 'module', 'component', 'model_name', 'description'])

    models_info = self.search_read("ir.model", fields = ['model', 'name', 'info'])

    for model_info in models_info:
        model_name = model_info.get('model', 'N/A')
        # Odoo nombra las tablas de la base de datos a partir del nombre técnico del modelo,
        # reemplazando los puntos por guiones bajos.
        # Ej: res.partner -> res_partner
        model_comp = model_name.split('.')
        app = model_comp[0]
        if len(model_comp) == 1:
            module = ''
            component = ''
        elif len(model_comp) == 2:
            module = model_comp[1]
            component = ''
        else:
            module = model_comp[1]
            component = '.'.join(model_comp[2:])

        # table_name = model_name.replace('.', '_') if model_name != 'N/A' else 'N/A'

        description = model_info.get('name', 'Sin descripción') # 'name' es el nombre visible
        # 'info' a veces contiene una descripción más detallada, podemos usarla si está disponible
        detailed_info = model_info.get('info', '').strip()
        if detailed_info:
            description += f" ({detailed_info})"


        # Limpiar la descripción para evitar problemas con caracteres especiales en CSV
        description = description.replace('"', '""').replace('\n', ' ').replace('\r', '')
        description = re.sub(r'\s+', ' ', description)  # Eliminar espacios adicionales
        description = re.sub(r'=+', ' ', description)  # Eliminar espacios adicionales
        writer.writerow([app, module, component, model_name, description])

    odoo_tables_file.close()

    pd.read_csv(csv_file, encoding='utf-8').to_excel(xlsx_file, index=False)
