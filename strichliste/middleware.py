import datetime
import decimal

import sqlalchemy as sa
from flask import current_app

import sqlalchemy.exc

from strichliste.models import User, Transaction
from strichliste.database import db


class DuplicateUser(Exception):
    def __init__(self, user_name):
        self.user_name = user_name


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
        raise


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