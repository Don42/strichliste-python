
import requests
import json
import datetime

URL = ("http://", "127.0.0.1", ":", "8080", "/")

# These tests need to be run in order


def test_01_create_user():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Create user
    params = {'name': 'gert', 'mailAddress': 'gertMail'}
    r = requests.post(''.join(URL + ('user',)), headers=headers, data=json.dumps(params))
    assert r.status_code == 201
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert {'id',
            'name',
            # 'mailAddress',  # appears to not be send
            'balance',
            'lastTransaction'}.issubset(result)
    assert result['name'] == 'gert'
    assert result['id'] == 1
    assert result['balance'] == 0
    assert result['lastTransaction'] is None


def test_02_create_user_fail_duplicate():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create user with duplicate name
    params = {'name': 'gert', 'mailAddress': 'gertMail'}
    r = requests.post(''.join(URL + ('user',)), headers=headers, data=json.dumps(params))
    assert r.status_code == 409
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "user gert already exists"


def test_03_empty_user_transaction_list():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Show empty transactions list
    r = requests.get(''.join((URL + ('user', '/', '1', '/', 'transaction',))), headers=headers)
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    transactions = json.loads(r.text)
    assert {'overallCount', 'limit', 'offset', 'entries'}.issubset(transactions)
    assert transactions['overallCount'] == 0
    assert transactions['limit'] is None
    assert transactions['offset'] is None
    assert transactions['entries'] == []


def test_04_create_transaction_fail_nan():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction when value is not a number
    params = {'value': 'foo'}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    assert r.status_code == 400
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "not a number: foo"


def test_05_create_transaction_fail_zero():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction when value is zero
    params = {'value': 0}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    assert r.status_code == 400
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "value must not be zero"


def test_06_create_transaction_1():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Create transaction
    params = {'value': 11}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    now = datetime.datetime.utcnow()
    assert r.status_code == 201
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert {'id', 'userId', 'createDate', 'value'}.issubset(result)
    assert result['id'] == 1
    assert result['userId'] == 1
    assert result['value'] == 11
    create_date = datetime.datetime.strptime(result['createDate'], '%Y-%m-%d %H:%M:%S')
    assert (now - create_date).total_seconds() < 20


def test_07_create_transaction_2():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Create another transaction
    params = {'value': 12}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    now = datetime.datetime.utcnow()
    assert r.status_code == 201
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert {'id', 'userId', 'createDate', 'value'}.issubset(result)
    assert result['id'] == 2
    assert result['userId'] == 1
    assert result['value'] == 12
    create_date = datetime.datetime.strptime(result['createDate'], '%Y-%m-%d %H:%M:%S')
    assert (now - create_date).total_seconds() < 20


def test_08_create_transaction_fail_lower_account_boundary():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction with 403 (lower account boundary)
    params = {'value': -100}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    assert r.status_code == 403
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == ("transaction value of -100 leads to an overall account balance "
                                 "of -77 which goes below the lower account limit of -23")


def test_09_create_transaction_fail_upper_account_boundary():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction with 403 (lower account boundary)
    params = {'value': 100}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    assert r.status_code == 403
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == ("transaction value of 100 leads to an overall account balance of 123 "
                                 "which goes beyond the upper account limit of 42")


def test_10_create_transaction_fail_lower_transaction_boundary():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction with 403 (lower account boundary)
    params = {'value': -99999}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    assert r.status_code == 403
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "transaction value of -99999 falls below the transaction minimum of -9999"


def test_11_create_transaction_fail_upper_transaction_boundary():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction with 403 (lower account boundary)
    params = {'value': 99999}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    assert r.status_code == 403
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "transaction value of 99999 exceeds the transaction maximum of 9999"


def test_12_invalid_json():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction with 403 (lower account boundary)
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data='{"name":}')
    assert r.status_code == 400
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "Unexpected token }"
