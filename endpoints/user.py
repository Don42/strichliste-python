import numbers

from flask_restful import Resource
from strichliste import list_parser, user_parser
from endpoints import create_error


class UserList(Resource):

    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        return {'overallCount': 0, 'limit': limit, 'offset': offset, 'entries': []}

    def post(self):
        args = user_parser.parse_args()
        name = args.get('name')
        mail_address = args.get('mailAddress')
        if name is None or mail_address is None:
            return create_error(400, "name missing")

        return {'id': 1, 'name': name, 'mailAddress': mail_address,
                'balance': 0, 'lastTransaction': None}


class User(Resource):

    def get(self, user_id):
        return create_error(404, "user {} not found".format(user_id))


class UserTransactionList(Resource):

    def get(self, user_id):
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        return create_error(404, "user {} not found".format(user_id))

    def post(self, user_id):
        args = user_parser.parse_args()
        if not {'value'}.issubset():
            return create_error(400, "value missing")
        value = args['value']
        if not isinstance(value, numbers.Number):
            return create_error(400, "not a number: {}".format(value))
        if value == 0:
            return create_error(400, "value must not be zero")
        return create_error(404, "user {} not found".format(user_id))