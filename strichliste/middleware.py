from flask import current_app

from strichliste import models


def get_users_transactions(user_id, limit=None, offset=None):
    user = models.User.query.get(user_id)
    if user is None:
        current_app.logger.warning("User ID not found - user_id='{}'".format(user_id))
        raise KeyError
    count = models.Transaction.query.filter(models.Transaction.userId == user.id).count()
    result = models.Transaction.query.filter(models.Transaction.userId == user.id).offset(offset).limit(limit).all()
    entries = [x.dict() for x in result]
    return {'overallCount': count, 'limit': limit, 'offset': offset, 'entries': entries}


def get_users(limit, offset):
    count = models.User.query.count()
    result = models.User.query.offset(offset).limit(limit).all()
    entries = [x.dict() for x in result]
    users = {'overallCount': count, 'limit': limit, 'offset': offset, 'entries': entries}
    return users