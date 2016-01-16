import datetime

from sqlalchemy import Column, ForeignKey, INTEGER, \
    TEXT, DATETIME, DECIMAL
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(TEXT, nullable=False, unique=True)
    createDate = Column(DATETIME, default=datetime.datetime.utcnow())
    active = Column(INTEGER, default=1, nullable=False)
    mailAddress = Column(TEXT)

    def __repr__(self):
        return "User: id: {id}, name: {name}, mailAddress: {mail}, createDate: {date}".format(
            id=self.id, name=self.name, mail=self.mailAddress, date=self.createDate
        )

    def dict(self):
        return {'id': self.id, 'name': self.name, 'createDate': self.createDate.isoformat(),
                'mailAddress': self.mailAddress, 'active': self.active}


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    userId = Column(INTEGER, ForeignKey('users.id'), nullable=False, index=True)
    createDate = Column(DATETIME, default=datetime.datetime.utcnow())
    value = Column(DECIMAL, nullable=False)


class Meta(Base):
    __tablename__ = 'meta'
    key = Column(TEXT, primary_key=True)
    value = Column(TEXT)
