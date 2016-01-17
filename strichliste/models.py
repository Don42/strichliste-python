import decimal
import datetime

from database import db
from sqlalchemy.orm import relationship

TWO_PLACES = decimal.Decimal("0.01")
CONTEXT = decimal.getcontext()
CONTEXT.rounding = decimal.ROUND_HALF_UP


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.TEXT, nullable=False, unique=True)
    createDate = db.Column(db.DATETIME, default=datetime.datetime.utcnow())
    active = db.Column(db.INTEGER, default=1, nullable=False)
    mailAddress = db.Column(db.TEXT)

    def __repr__(self):
        return "User: id: {id}, name: {name}".format(id=self.id, name=self.name)

    def dict(self):
        transactions = [x.dict() for x in self.transactions]
        return {'id': self.id, 'name': self.name, 'createDate': self.createDate.isoformat(),
                'mailAddress': self.mailAddress, 'active': self.active, 'transactions': transactions}


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    userId = db.Column(db.INTEGER, db.ForeignKey('users.id'), nullable=False, index=True)
    user = relationship("User", back_populates="transactions")
    createDate = db.Column(db.DATETIME, default=datetime.datetime.utcnow())
    value = db.Column(db.INTEGER, nullable=False)

    @property
    def value_dec(self) -> decimal.Decimal:
        return round(decimal.Decimal(self.value) / 100, 2)

    @value_dec.setter
    def value_dec(self, value: decimal.Decimal):
        self.value = value.quantize(TWO_PLACES).shift(2).to_integral_exact()

    def dict(self):
        return {'id': self.id, 'userId': self.userId,
                'value': "{}".format(self.value_dec.quantize(TWO_PLACES)),
                'createDate': self.createDate.isoformat()}

    def get_decimal(self) -> decimal.Decimal:
        return decimal.Decimal(self.value) / 100


User.transactions = relationship('Transaction', order_by=Transaction.id, back_populates='user')


class Meta(db.Model):
    __tablename__ = 'meta'
    key = db.Column(db.TEXT, primary_key=True)
    value = db.Column(db.TEXT)
