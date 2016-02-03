import flask

from flask import jsonify
from flask_restful import reqparse

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', type=str, location='json')
user_parser.add_argument('mailAddress', type=str, location='json')

transaction_parser = reqparse.RequestParser()
transaction_parser.add_argument('value', location='json')

list_parser = reqparse.RequestParser()
list_parser.add_argument('offset', type=int, location='args', default=None)
list_parser.add_argument('limit', type=int, location='args', default=None)

HEADERS = {'Content-Type': 'application/json; charset=utf-8'}


def make_error_response(msg: str, code: int = 400):
    return make_response({'message': msg}, code)


def make_response(data, code=200, headers=None):
    resp = flask.make_response(jsonify(data), code)
    resp.headers.extend(HEADERS)
    if headers is not None:
        resp.headers.extend(headers)
    return resp

