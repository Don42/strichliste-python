from flask_restful import reqparse

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', type=str, location='json')
user_parser.add_argument('mailAddress', type=str, location='json')

transaction_parser = reqparse.RequestParser()
transaction_parser.add_argument('value', location='json')

list_parser = reqparse.RequestParser()
list_parser.add_argument('offset', type=int, location='args')
list_parser.add_argument('limit', type=int, location='args')


def create_error(code: int, msg: str):
    return {'message': msg}, code
