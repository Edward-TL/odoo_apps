
import os
import ast
import json
import logging
from typing import Literal
from copy import copy

from dotenv import dotenv_values


EnvFile = Literal["PROJECT_JSON", "WORKSHEETS", "GEMINI"]

ENV_VARS = {
    "PROJECT_JSON" : [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "ODOO"
        ],
    "WORKSHEETS": [
        "WORKSHEET_ID",
        "WORKSHEET_NAME",
        "IDEA_COL",
        "GEMINI_COL"
    ],
    "GEMINI": [
        "GEMINI_API_KEY",
        "MODEL_ID"
    ]
    }

logging.basicConfig(level=logging.INFO)

def ensure_env_vars(env_file: str | EnvFile = "PROJECT_JSON") -> dict:
    """
    Función para cargar las variables de entorno desde un archivo .env o desde el entorno del sistema.
    Si el archivo .env no existe, se cargan las variables de entorno desde el sistema.
    En caso de que las variables sean un diccionario, se deberá de agregar el nombre de la variable,
    a la lista de ENV_VARS para configurarlo, o reemplazarlo por el de GOOGLE_APPLICATION_CREDENTIALS.

    Esta función no está pensada para ser utilizada dentro de una librería, sino para ser utilizada
    dentro de un script de Python. Por lo tanto, no se recomienda su uso en un entorno de producción.
    
    Args:
        env_file (str | EnvFile["PROJECT_JSON", "WORKSHEETS", "GEMINI"]):
            * Nombre del archivo .env o el nombre de la variable de entorno a cargar.
            - Si no se especifica, se buscará el archivo/variable PROJECT_JSON.env por defecto.
            - Si se especifica un nombre de variable de entorno, se cargará el archivo .env con ese nombre.
    """
    env_key = copy(env_file)
    if env_file is None:
        env_file = '.env'

    if env_file in EnvFile.__args__:
        env_file = f"{env_file}.env"

    env_path = os.path.join(os.path.dirname(__file__), env_file)

    if not os.path.exists(env_path):
        log(f"{env_file} file not found. Falling back to environment variables.")
        
        if env_key == "PROJECT_JSON":
            # print(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
            # print(os.getenv('ODOO'))
            return {
                env_var: ast.literal_eval(
                    os.getenv(env_var)
                    ) for env_var in ENV_VARS[env_key]
            }
        return {
            env_var : os.getenv(env_var) for env_var in ENV_VARS[env_key]
            }

    log(f"{env_file}.env file found.")
    env_data = dotenv_values(env_path)
    if env_key == "PROJECT_JSON":
        str_credentias = env_data["GOOGLE_APPLICATION_CREDENTIALS"]
        print("str_credentials: ", str_credentias)
        env_data["GOOGLE_APPLICATION_CREDENTIALS"] = json.loads(str_credentias)

    return env_data



def log(message: str) -> None:
    """
    Función auxiliar para registrar mensajes.
    """
    logging.info(message)

def warning_log(message: str) -> None:
    """
    Función auxiliar para registrar advertencias.
    """
    logging.warning(message)

def error_log(message: str) -> None:
    """
    Función auxiliar para registrar errores.
    """
    logging.error(message)

