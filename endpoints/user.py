import numbers

from flask_restful import Resource
from endpoints import list_parser, user_parser, create_error

import database.sqlalchemy_declarative as mapping
import sqlalchemy.exc


class UserList(Resource):

    def __init__(self, **kwargs):
        self.session = kwargs['db']

    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        count = self.session.query(mapping.User).count()
        result = self.session.query(mapping.User).offset(offset).limit(limit).all()
        entries = [x.dict() for x in result]

        return {'overallCount': count, 'limit': limit,
                'offset': offset, 'entries': entries}

    def post(self):
        args = user_parser.parse_args()
        name = args.get('name')
        mail_address = args.get('mailAddress')
        if name is None or mail_address is None:
            return create_error(400, "name missing")

        user = mapping.User(name=name, mailAddress=mail_address)
        try:
            self.session.add(user)
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            # TODO Logging
            return create_error(409, "user {} already exists".format(user.name))

        return {'id': user.id, 'name': user.name,
                'mailAddress': user.mailAddress,
                'balance': 0, 'lastTransaction': None}, 201


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