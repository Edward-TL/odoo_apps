"""
Google API Authentication and Connection
"""

from dataclasses import dataclass

import gspread
from google.oauth2 import service_account

from utils.helpers import ensure_env_vars

GOOGLE_CREDENTIALS = ensure_env_vars("PROJECT_JSON")['GOOGLE_APPLICATION_CREDENTIALS']

@dataclass
class GoogleEnv:
    """
    Clase para manejar la autenticación y conexión a Google Sheets API.
    """
    env_vals = GOOGLE_CREDENTIALS
    scopes: tuple = tuple(
        [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    "https://www.googleapis.com/auth/spreadsheets.readonly"
    ]
    )

    def __post_init__(self):
        self.credentials = (
            service_account
            .Credentials
            .from_service_account_info(
                self.env_vals)
                )
        # Set scopes
        self.creds_with_scope = self.credentials.with_scopes(self.scopes)
        self.sheets = gspread.authorize(self.creds_with_scope)
    
    # def sheets_client(self):
    #     """Get client for Google Spread Sheet"""
    #     self.sheets = gspread.authorize(self.creds_with_scope)
    #     return self.sheets
