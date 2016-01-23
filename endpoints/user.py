import decimal
import json
import numbers

from flask_restful import Resource
from flask import make_response
from endpoints import list_parser, user_parser, transaction_parser, create_error, HEADERS

import sqlalchemy.exc

from database import db
import strichliste.models as models


class UserList(Resource):

    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        count = models.User.query.count()
        result = models.User.query.offset(offset).limit(limit).outerjoin(
                models.User.transactions).all()
        entries = [x.dict() for x in result]

        resp = make_response(json.dumps({'overallCount': count, 'limit': limit,
                              'offset': offset, 'entries': entries}), 200)
        resp.headers.extend(HEADERS)
        return resp

    def post(self):
        args = user_parser.parse_args()
        name = args.get('name')
        mail_address = args.get('mailAddress')
        if name is None or mail_address is None:
            return create_error(400, "name missing")

        user = models.User(name=name, mailAddress=mail_address)
        try:
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            # TODO Logging
            return create_error(409, "user {} already exists".format(user.name))

        resp = make_response(json.dumps({'id': user.id, 'name': user.name,
                                         'mailAddress': user.mailAddress,
                                         'balance': 0, 'lastTransaction': None}),
                             201)
        resp.headers.extend(HEADERS)
        return resp


class User(Resource):

    def get(self, user_id):
        try:
            user = models.User.query.get(user_id)
            if user is None:
                return create_error(404, "user {} not found".format(user_id))
            out_dict = user.dict()
            out_dict['transaction'] = [x.dict() for x in user.transactions]
            resp = make_response(json.dumps(out_dict), 200)
            resp.headers.extend(HEADERS)
            return resp
        except sqlalchemy.exc.SQLAlchemyError as e:
            # TODO Logging
            return create_error(500, "Internal Error")


class UserTransactionList(Resource):

    def get(self, user_id):
        user = models.User.query.get(user_id)
        if user is None:
            return create_error(404, "user {} not found".format(user_id))
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        count = models.Transaction.query.filter(models.Transaction.userId == user.id).count()
        result = models.Transaction.query.filter(models.Transaction.userId == user.id).all()
        entries = [x.dict() for x in result]
        resp = make_response(json.dumps({'overallCount': count, 'limit': limit,
                                         'offset': offset, 'entries': entries}),
                             200)
        resp.headers.extend(HEADERS)
        return resp

    def post(self, user_id):
        args = transaction_parser.parse_args()
        if 'value' not in args:
            return create_error(400, "value missing")
        raw_value = args['value']

        try:
            value = int(raw_value)
        except ValueError:
            try:
                value = decimal.Decimal(raw_value)
                value = int(value.quantize(models.TWO_PLACES).shift(2).to_integral_exact())
            except ValueError as e:
                # TODO Logging
                print(e)

        if not isinstance(value, numbers.Number):
            return create_error(400, "not a number: {}".format(raw_value))
        if value == 0:
            return create_error(400, "value must not be zero")

        user = models.User.query.get(user_id)
        if user is None:
            return create_error(404, "user {} not found".format(user_id))

        transaction = models.Transaction(userId=user_id, value=value)
        try:
            db.session.add(transaction)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            # TODO Logging
            return create_error(404, "user {} not found".format(user_id))

        resp = make_response(json.dumps(transaction.dict()), 201)
        resp.headers.extend(HEADERS)
        return resp

