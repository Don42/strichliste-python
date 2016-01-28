import decimal

from flask import current_app
from flask_restful import Resource
from endpoints import list_parser, user_parser, transaction_parser, make_error_response, make_response

import sqlalchemy.exc

from database import db
import strichliste.models as models
from werkzeug.exceptions import BadRequest


class UserList(Resource):

    def get(self):
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        count = models.User.query.count()
        result = models.User.query.offset(offset).limit(limit).all()
        entries = [x.dict() for x in result]

        return make_response({'overallCount': count, 'limit': limit,
                              'offset': offset, 'entries': entries}, 200)

    def post(self):
        args = user_parser.parse_args()
        name = args.get('name')
        mail_address = args.get('mailAddress')
        if name is None or mail_address is None:
            return make_error_response("name missing", 400)

        user = models.User(name=name, mailAddress=mail_address)
        try:
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            # TODO Logging
            return make_error_response("user {} already exists".format(user.name), 409)

        return make_response({'id': user.id, 'name': user.name,
                              'mailAddress': user.mailAddress,
                              'balance': 0, 'lastTransaction': None},
                             201)


class User(Resource):

    def get(self, user_id):
        try:
            user = models.User.query.get(user_id)
            if user is None:
                return make_error_response("user {} not found".format(user_id), 404)
            out_dict = user.dict()
            out_dict['transactions'] = [x.dict() for x in user.transactions]
            return make_response(out_dict, 200)
        except sqlalchemy.exc.SQLAlchemyError as e:
            # TODO Logging
            return make_error_response("Internal Error", 500)


class UserTransactionList(Resource):

    def get(self, user_id):
        user = models.User.query.get(user_id)
        if user is None:
            return make_error_response("user {} not found".format(user_id), 404)
        args = list_parser.parse_args()
        limit = args.get('limit', None)
        offset = args.get('offset', None)
        count = models.Transaction.query.filter(models.Transaction.userId == user.id).count()
        result = models.Transaction.query.filter(models.Transaction.userId == user.id).all()
        entries = [x.dict() for x in result]
        return make_response({'overallCount': count, 'limit': limit,
                              'offset': offset, 'entries': entries},
                             200)

    def post(self, user_id):
        try:
            args = transaction_parser.parse_args()
        except BadRequest:
            # TODO Logging
            return make_error_response("Error parsing json", 400)
        if 'value' not in args:
            return make_error_response("value missing", 400)
        raw_value = args['value']

        try:
            value = int(raw_value)
        except ValueError:
            try:
                value = decimal.Decimal(raw_value)
                value = int(value.quantize(models.TWO_PLACES).shift(2).to_integral_exact())
            except decimal.InvalidOperation as e:
                # TODO Logging
                return make_error_response("not a number: {}".format(raw_value), 400)

        config = current_app.config['app_config']
        max_transaction = config.upper_transaction_boundary
        min_transaction = config.lower_transaction_boundary
        if value == 0:
            return make_error_response("value must not be zero", 400)
        elif value > max_transaction:
            return make_error_response(
                    "transaction value of {} exceeds the transaction maximum of {}".format(value, max_transaction),
                    403)
        elif value < min_transaction:
            return make_error_response(
                    "transaction value of {} falls below the transaction minimum of {}".format(value, min_transaction),
                    403)

        user = models.User.query.get(user_id)
        if user is None:
            return make_error_response("user {} not found".format(user_id), 404)

        max_account = config.upper_account_boundary
        min_account = config.lower_account_boundary
        new_balance = user.balance_cent + value
        if new_balance > max_account:
            return make_error_response(
                    ("transaction value of {trans_val} leads to an overall account balance of {new} "
                     "which goes beyond the upper account limit of {limit}".format(trans_val=value,
                                                                                   new=new_balance,
                                                                                   limit=max_account)),
                    403
            )
        elif new_balance < min_account:
            return make_error_response(
                    ("transaction value of {trans_val} leads to an overall account balance of {new} "
                     "which goes below the lower account limit of {limit}").format(trans_val=value,
                                                                                   new=new_balance,
                                                                                   limit=min_account),
                    403
            )

        transaction = models.Transaction(userId=user_id, value=value)
        try:
            db.session.add(transaction)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            # TODO Logging
            return make_error_response("user {} not found".format(user_id), 404)

        return make_response(transaction.dict(), 201)

