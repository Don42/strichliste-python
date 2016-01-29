import datetime

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
        return "User: id: {id}, name: {name}".format(id=self.id, name=self.name)

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


class Meta(db.Model):
    __tablename__ = 'meta'
    key = db.Column(db.TEXT, primary_key=True)
    value = db.Column(db.TEXT)
