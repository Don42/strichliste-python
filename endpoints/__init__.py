import json

from flask_restful import reqparse
from flask import make_response

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', type=str, location='json')
user_parser.add_argument('mailAddress', type=str, location='json')

transaction_parser = reqparse.RequestParser()
transaction_parser.add_argument('value', location='json')

list_parser = reqparse.RequestParser()
list_parser.add_argument('offset', type=int, location='args')
list_parser.add_argument('limit', type=int, location='args')

HEADERS = {'Content-Type': 'application/json; charset=utf-8'}


def create_error(code: int, msg: str):
    resp = make_response(json.dumps({'message': msg}), code)
    resp.headers.extend(HEADERS)
    return resp
