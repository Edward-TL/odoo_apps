import csv
import io
import re
from pathlib import Path

import pandas as pd

from client import OdooClientServer

PROJECT_PATH = str(
    Path(__file__).resolve().parent.parent
    )

TABLES_DIR = 'tables_files'

output = io.StringIO()
DEFAULT_CSV_FILE = f'{PROJECT_PATH}/{TABLES_DIR}/odoo_tables.csv'
DEFAULT_XLSX_FILE = f'{PROJECT_PATH}/{TABLES_DIR}/xodoo_tables.xlsx'


def create_models_file(
    client: OdooClientServer,
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

    models_info = client.search_read("ir.model", fields = ['model', 'name', 'info'])

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

if __name__ == '__main__':
    print(PROJECT_PATH)
    print(DEFAULT_CSV_FILE)
    print(DEFAULT_XLSX_FILE)