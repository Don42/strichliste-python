def make_float(val):
    return float(val) / 100


def make_transaction_float(transaction):
    ret = transaction.dict()
    ret['value'] = make_float(ret['value'])
    return ret


def make_user_float(user):
    ret = user.dict()
    ret['balance'] = make_float(ret['balance'])
    ret['transactions'] = [make_transaction_float(x) for x in user.transactions]
    return ret