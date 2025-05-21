"""
Standard response
"""

from dataclasses import dataclass
from typing import Literal, Union
from flask import Flask, make_response, jsonify

from .request import (
    SearchRequest,
    ReadRequest,
    SearchReadRequest,
    CreateRequest,
    UpdateRequest,
    DeleteRequest
    )
from .utils.cleaning import generate_dict

meaning = {
    201: 'Succes on creating',
    200: 'Object already exists'
}

http_meaning = {
    201: 'SUCCESS',
    200: 'PASS',
    406: 'FAIL'
}

HttpStatus = Literal[201, 200, 406]
StatusMeaning = Literal['SUCCESS', 'PASS', 'FAIL']


# Just an Idea, that will evolve
Request = Union[
    dict,
    SearchRequest,
    ReadRequest,
    SearchReadRequest,
    CreateRequest,
    UpdateRequest,
    DeleteRequest
]

@dataclass
class Response:
    """
    Body for response data
    """
    action: Literal['create', 'update', 'delete']
    model: str
    object_id: int | list[int] | list[[int, str]] | bool | None = None
    status: StatusMeaning = 'SUCCESS'
    http_status: HttpStatus = 201
    msg: str | None = None

    def __post_init__(self):
        self.data = generate_dict(self)

    def update_message(self, error_message="") -> str:
        message = ""
        message += f"{self.status} | "
        if self.status != 'FAIL':
            message += f" | Message: {meaning[self.http_status]}"
        else:
            message += f" | Error: {error_message}"
        message += f"Action: {self.action} | "
        message += f"Model: {self.model} | "
        message += f"[ID]: {self.object_id}"

        self.msg = message

    def print(self):
        """
        Print the message based on the action and status.
        """
        print(self.msg)

    def complete_response(
        self, obj_id: int | bool, status: HttpStatus, msg = "",
        printer = False
        ):

        self.object_id = obj_id
        self.status = http_meaning[status]
        self.http_status = status
        if msg != "":
            self.msg = msg
        else:
            self.msg = meaning[status]
        self.update_message()

        if printer:
            self.print()

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


def standarize_response(request: Request, response: Response) -> dict:
    """
    Function to simplifys the reponse generation
    """
    app = Flask(__name__)
    response_status = int(response.http_status)

    data = {
        "message": response.msg,
        "success": response_status in {200, 201},
        "status": response_status, 
        "request": request.data if not isinstance(request, dict) else request,
        "response": response.get_data()
    }

    # print(type(data['request']))
    # print(type(data['response']))
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
