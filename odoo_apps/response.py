"""
Standart response
"""

from dataclasses import dataclass
from typing import Literal
from flask import Flask, make_response, jsonify

from .utils.cleaning import generate_dict

meaning = {
    201: 'Succes on creating',
    200: 'Already exist, but ok'
}



@dataclass
class Response:
    """
    Body for response data
    """
    action: Literal['create', 'update', 'delete']
    model: str
    object_id: int | list[int] | list[[int, str]] | bool | None = None
    status: Literal['SUCCESS', 'PASS', 'FAIL'] = 'SUCCESS'
    http_status: Literal[201, 200, 406] = 201
    msg: str | None = None

    def __post_init__(self):
        self.data = generate_dict(self)

    def update_message(self, error_message="") -> str:
        message = ""
        message += f"{self.status} | "
        message += f"Action: {self.action} | "
        message += f"Model: {self.model} | "
        message += f"[ID]: {self.object_id}"

        if self.status != 'FAIL':
            message += f" | Message: {meaning[self.http_status]}"
        else:
            message += f" | Error: {error_message}"

        self.msg = message
    
    def get_data(self):
        self.data = generate_dict(self)
        return {
            "action": self.action,
            "model": self.model,
            "object_id": self.object_id,
            "status": self.status,
            "http_status": self.http_status,
            "msg": self.msg
        }

    def print(self):
        """
        Print the message based on the action and status.
        """
        print(self.msg)

@dataclass
class Request:
    """
    Standarized minimum request data
    """
    odoo_user_id: str
    user_client_id: str
    activity: Literal['CREATE', 'UPDATE', 'DELETE']
    app_body: dict

    def __post_init__(self):
        self.data = generate_dict(self)


def standarize_response(request: Request | dict, response: Response) -> dict:
    """
    Function to simplifys the reponse generation
    """
    app = Flask(__name__)
    data = {
        "message": response.msg,
        "request": request.data if not isinstance(request, dict) else request,
        "response": response.get_data()
    }

    print(type(data['request']))
    print(type(data['response']))
    # print(data)
    with app.app_context():
        response = make_response(
            jsonify(
                data
            ),
            response.status
        )
        response.headers['Content-Type'] = 'application/json'

        return response
