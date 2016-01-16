import datetime

from strichliste.flask import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.TEXT, nullable=False, unique=True)
    createDate = db.Column(db.DATETIME, default=datetime.datetime.utcnow())
    active = db.Column(db.INTEGER, default=1, nullable=False)
    mailAddress = db.Column(db.TEXT)

    def __repr__(self):
        return "User: id: {id}, name: {name}, mailAddress: {mail}, createDate: {date}".format(
                id=self.id, name=self.name, mail=self.mailAddress, date=self.createDate
        )

    def dict(self):
        return {'id': self.id, 'name': self.name, 'createDate': self.createDate.isoformat(),
                'mailAddress': self.mailAddress, 'active': self.active}


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    userId = db.Column(db.INTEGER, db.ForeignKey('users.id'), nullable=False, index=True)
    createDate = db.Column(db.DATETIME, default=datetime.datetime.utcnow())
    value = db.Column(db.DECIMAL, nullable=False)


class Meta(db.Model):
    __tablename__ = 'meta'
    key = db.Column(db.TEXT, primary_key=True)
    value = db.Column(db.TEXT)
