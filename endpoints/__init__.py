from flask_restful import reqparse

user_parser = reqparse.RequestParser()
user_parser.add_argument('name')
user_parser.add_argument('mailAddress')

transaction_parser = reqparse.RequestParser()
user_parser.add_argument('value')

list_parser = reqparse.RequestParser()
user_parser.add_argument('offset')
user_parser.add_argument('limit')


def create_error(code: int, msg: str):
    return {'message': msg}, code
