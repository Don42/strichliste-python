import datetime
import decimal

import sqlalchemy as sa
from flask import current_app

import sqlalchemy.exc

from strichliste.config import Config
from strichliste.models import User, Transaction
from strichliste.database import db


class DuplicateUser(Exception):
    def __init__(self, user_name):
        self.user_name = user_name


class DatabaseError(Exception):
    pass


class TransactionValue(Exception):
    pass


class TransactionValueZero(TransactionValue):
    pass


class TransactionValueLimit(TransactionValue):
    def __init__(self, value, limit):
        self.value = value
        self.limit = limit


class TransactionValueHigh(TransactionValueLimit):
    def __str__(self):
        return "transaction value of {} exceeds the transaction maximum of {}".format(self.value, self.limit)


class TransactionValueLow(TransactionValueLimit):
    def __str__(self):
        return "transaction value of {} falls below the transaction minimum of {}".format(self.value, self.limit)


class TransactionResultLimit(TransactionValue):
    def __init__(self, value, limit, result):
        self.value = value
        self.limit = limit
        self.result = result


class TransactionResultHigh(TransactionResultLimit):
    def __str__(self):
        return ("transaction value of {trans_val} leads to an overall account balance of {new} "
                "which goes beyond the upper account limit of {limit}").format(trans_val=self.value,
                                                                               new=self.result,
                                                                               limit=self.limit)


class TransactionResultLow(TransactionResultLimit):
    def __str__(self):
        return ("transaction value of {trans_val} leads to an overall account balance of {new} "
                "which goes below the lower account limit of {limit}").format(trans_val=self.value,
                                                                              new=self.result,
                                                                              limit=self.limit)


def insert_transaction(user_id: int, value: int) -> Transaction:
    config = Config()
    max_transaction = config.upper_transaction_boundary
    min_transaction = config.lower_transaction_boundary
    if value == 0:
        raise TransactionValueZero("value must not be zero")
    elif value > max_transaction:
        raise TransactionValueHigh(value, max_transaction)
    elif value < min_transaction:
        raise TransactionValueLow(value, min_transaction)

    user = User.query.get(user_id)
    if user is None:
        raise KeyError

    max_account = config.upper_account_boundary
    min_account = config.lower_account_boundary
    new_balance = user.balance + value
    if new_balance > max_account:
        raise TransactionResultHigh(value, max_account, new_balance)
    elif new_balance < min_account:
        raise TransactionResultLow(value, min_account, new_balance)

    transaction = Transaction(userId=user_id, value=value)
    try:
        db.session.add(transaction)
        db.session.commit()
    except sqlalchemy.exc.DatabaseError as e:
        raise DatabaseError
    return transaction


def get_users_transactions(user_id, limit=None, offset=None):
    user = User.query.get(user_id)
    if user is None:
        raise KeyError
    count = Transaction.query.filter(Transaction.userId == user.id).count()
    result = Transaction.query.filter(Transaction.userId == user.id).offset(offset).limit(limit).all()
    entries = [x.dict() for x in result]
    return {'overallCount': count, 'limit': limit, 'offset': offset, 'entries': entries}


def get_users(limit, offset):
    count = User.query.count()
    result = User.query.offset(offset).limit(limit).all()
    entries = [x.dict() for x in result]
    users = {'overallCount': count, 'limit': limit, 'offset': offset, 'entries': entries}
    return users


def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if user is None:
            current_app.logger.warning("Could not find user: User ID not found - user_id='{}'".format(user_id))
            raise KeyError
        out_dict = user.dict()
        out_dict['transactions'] = [x.dict() for x in user.transactions]
        return out_dict
    except sqlalchemy.exc.SQLAlchemyError as e:
        current_app.logger.error("Unexpected SQLAlchemyError: {error} - user_id='{user_id}".format(error=e,
                                                                                                   user_id=user_id))
        raise DatabaseError("SQLAlchemyError: {error}".format(error=e))


def insert_user(name, email=''):
    try:
        user = User(name=name, mailAddress=email)
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise DuplicateUser(user.name)
    return user


def get_global_balance():
    ret = db.session.query(sa.func.sum(Transaction.value)).first()
    if ret[0] is None:
        ret = 0
    else:
        ret = ret[0]
    return ret


def get_average_balance():
    user_count = User.query.count()
    if user_count <= 0:
        return 0
    global_balance = decimal.Decimal(get_global_balance())
    avg = decimal.Decimal(global_balance / user_count)
    return int(avg.to_integral_value(decimal.ROUND_05UP))


def get_day_metrics(date: datetime.date):
    daily_transactions = Transaction.query.filter(Transaction.createDate >= date,
                                                  Transaction.createDate <= date + datetime.timedelta(days=1)).all()
    ret = {'date': date.isoformat(),
           'overallNumber': len(daily_transactions),
           'distinctUsers': len(set((x.userId for x in daily_transactions))),
           'dayBalance': sum((x.value for x in daily_transactions)),
           'dayBalancePositive': sum((x.value if x.value > 0 else 0 for x in daily_transactions)),
           'dayBalanceNegative': sum((x.value if x.value < 0 else 0 for x in daily_transactions))
           }
    return ret


def get_day_metrics_float(date: datetime.date):
    daily_transactions = Transaction.query.filter(Transaction.createDate >= date,
                                                  Transaction.createDate <= date + datetime.timedelta(days=1)).all()
    ret = {'date': date.isoformat(),
           'overallNumber': len(daily_transactions),
           'distinctUsers': len(set((x.userId for x in daily_transactions))),
           'dayBalance': sum((x.value for x in daily_transactions)) / 100,
           'dayBalancePositive': sum((x.value if x.value > 0 else 0 for x in daily_transactions)) / 100,
           'dayBalanceNegative': sum((x.value if x.value < 0 else 0 for x in daily_transactions)) / 100
           }
    return ret

