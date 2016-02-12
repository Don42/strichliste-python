import datetime
import decimal

from database import db

import sqlalchemy as sa
from sqlalchemy.orm import relationship


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.TEXT, nullable=False, unique=True)
    createDate = db.Column(db.DATETIME, default=datetime.datetime.utcnow())
    active = db.Column(db.INTEGER, default=1, nullable=False)
    mailAddress = db.Column(db.TEXT)
    transactions = relationship('Transaction', back_populates='user')

    @property
    def balance(self) -> int:
        ret = db.session.query(sa.func.sum(Transaction.value)).filter(
                Transaction.userId == self.id).first()
        if ret[0] is None:
            ret = 0
        else:
            ret = ret[0]
        return ret

    @property
    def lastTransaction(self):
        ret = Transaction.query.filter(Transaction.userId == self.id).order_by(
            Transaction.createDate.desc()).first()
        return ret.createDate.isoformat() if ret is not None else None

    def __repr__(self):
        return "<User: id: {id}, name: {name}>".format(id=self.id, name=self.name)

    def dict(self):
        return {'id': self.id, 'name': self.name, 'balance': self.balance,
                'lastTransaction': self.lastTransaction}


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    userId = db.Column(db.INTEGER, db.ForeignKey('users.id'), nullable=False, index=True)
    user = relationship("User", back_populates="transactions")
    createDate = db.Column(db.DATETIME, default=datetime.datetime.utcnow)
    value = db.Column(db.INTEGER, nullable=False)

    def dict(self):
        return {'id': self.id, 'userId': self.userId,
                'value': self.value, 'createDate': self.createDate.isoformat()}

    def __repr__(self):
        return "<Transaction: User: {user}, Value: {value}>".format(user=self.user.name, value=self.value)


class Meta(db.Model):
    __tablename__ = 'meta'
    key = db.Column(db.TEXT, primary_key=True)
    value = db.Column(db.TEXT)


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

