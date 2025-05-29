"""
Standard response
"""

from dataclasses import dataclass
from typing import Literal, Union
from flask import Flask, make_response, jsonify
from flask import Response as FlaskResponse

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
    200: 'Object already exists',
    400: 'Something went wrong with the request',
    406: 'Server could not produce an acceptable response',
    409: 'Request OK. Not available'
}

http_meaning = {
    201: 'SUCCESS',
    200: 'PASS',
    400: 'BAD REQUEST',
    406: 'NOT ACCEPTABLE',
    409: 'CONFLICT'
}

HttpStatus = Literal[201, 200, 406, 409]
StatusMeaning = Literal['SUCCESS', 'PASS', 'FAIL', 'CONFLICT']
Action = Literal['read', 'search', 'create', 'update', 'delete']

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
    action: Action
    model: str
    object: int | list[int] | list[list[int, str]] | bool | None = None
    status: StatusMeaning = 'SUCCESS'
    http_status: HttpStatus = 201
    msg: str | None = None

    def __post_init__(self):
        self.data = generate_dict(self)

    def update_message(self, error_message="") -> str:
        message = ""
        message += f"{self.status} | "
        if self.status != 'FAIL':
            message += f"Message: {meaning[self.http_status]} | "
        else:
            message += f"Error: {error_message}"
        message += f"Action: {self.action} | "
        message += f"Model: {self.model} | "
        message += f"[ID]: {self.object}"

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

        self.object = obj_id
        self.status = http_meaning[status]
        self.http_status = status
        if msg != "":
            self.msg = msg
        else:
            self.update_message()

        if printer:
            self.print()

    def get_data(self):
        self.data = generate_dict(self)
        return {
            "action": self.action,
            "model": self.model,
            "object": self.object,
            "status": self.status,
            "http_status": self.http_status,
            "msg": self.msg
        }
    

def report_fail(
        action: Action,
        model: str,
        http_status: HttpStatus,
        msg: str) -> Response:
    
    return Response(
        action = action,
        model = model,
        object = None,
        status = http_meaning[http_status],
        http_status = http_status,
        msg = msg
    )

def standarize_response(request: Request, response: Response) -> FlaskResponse:
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
