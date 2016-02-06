
import requests
import json
import datetime

URL = ("http://", "127.0.0.1", ":", "8080", "/", "v2", "/")

# These tests need to be run in order


def test_01_create_user_1():
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
    params = {'value': 1100}
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
    assert result['value'] == 1100
    create_date = datetime.datetime.strptime(result['createDate'], '%Y-%m-%dT%H:%M:%S.%f')
    assert (now - create_date).total_seconds() < 20


def test_07_create_transaction_2():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Create another transaction
    params = {'value': 1201}
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
    assert result['value'] == 1201
    create_date = datetime.datetime.strptime(result['createDate'], '%Y-%m-%dT%H:%M:%S.%f')
    assert (now - create_date).total_seconds() < 20


def test_08_create_transaction_fail_lower_account_boundary():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction with 403 (lower account boundary)
    params = {'value': -10000}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    assert r.status_code == 403
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == ("transaction value of -10000 leads to an overall account balance "
                                 "of -7699 which goes below the lower account limit of -2300")


def test_09_create_transaction_fail_upper_account_boundary():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction with 403 (lower account boundary)
    params = {'value': 10000}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    assert r.status_code == 403
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == ("transaction value of 10000 leads to an overall account balance of 12301 "
                                 "which goes beyond the upper account limit of 4200")


def test_10_create_transaction_fail_lower_transaction_boundary():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction with 403 (lower account boundary)
    params = {'value': -9999999}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    assert r.status_code == 403
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "transaction value of -9999999 falls below the transaction minimum of -999900"


def test_11_create_transaction_fail_upper_transaction_boundary():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Fail to create transaction with 403 (lower account boundary)
    params = {'value': 9999999}
    r = requests.post(''.join((URL + ('user', '/', '1', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    assert r.status_code == 403
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "transaction value of 9999999 exceeds the transaction maximum of 999900"


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
    assert result['message'] == "Error parsing json"


def test_13_create_user_2():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Create user
    params = {'name': 'bar', 'mailAddress': 'barMail'}
    r = requests.post(''.join(URL + ('user',)), headers=headers, data=json.dumps(params))
    assert r.status_code == 201
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert {'id',
            'name',
            # 'mailAddress',  # appears to not be send
            'balance',
            'lastTransaction'}.issubset(result)
    assert result['name'] == 'bar'
    assert result['id'] == 2
    assert result['balance'] == 0
    assert result['lastTransaction'] is None


def test_14_list_two_users():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('user', )), headers=headers)
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    users = json.loads(r.text)
    assert {'overallCount', 'limit', 'offset', 'entries'}.issubset(users)
    assert users['overallCount'] == 2
    assert users['limit'] is None
    assert users['offset'] is None
    entries = users['entries']
    assert isinstance(entries, list)
    assert len(entries) == 2
    assert {'id', 'name', 'balance', 'lastTransaction'}.issubset(entries[0])
    assert {'id', 'name', 'balance', 'lastTransaction'}.issubset(entries[1])
    assert entries[0]['name'] == 'gert'
    assert entries[0]['id'] == 1
    assert entries[1]['name'] == 'bar'
    assert entries[1]['id'] == 2


def test_15_list_users_empty_offset():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('user', )), headers=headers, params={'offset': 2, 'limit': 1})
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    users = json.loads(r.text)
    assert {'overallCount', 'limit', 'offset', 'entries'}.issubset(users)
    assert users['overallCount'] == 2
    assert users['limit'] == 1
    assert users['offset'] == 2
    assert users['entries'] == []


def test_16_load_user_by_id():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('user', '/', '1')), headers=headers)
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    user = json.loads(r.text)
    print(user)
    assert {'name', 'id', 'balance', 'lastTransaction', 'transactions'}.issubset(user)
    assert user['name'] == 'gert'
    assert user['id'] == 1
    assert user['balance'] == 2301
    assert user['lastTransaction'] is not None
    transactions = user['transactions']
    for entry in transactions:
        assert {'id', 'userId', 'createDate', 'value'}.issubset(entry)
        assert entry['value'] in [1100, 1201]
        assert entry['userId'] == 1


def test_17_load_transactions():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('transaction',)), headers=headers)
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    transactions = json.loads(r.text)
    assert {'overallCount', 'limit', 'offset', 'entries'}.issubset(transactions)
    assert transactions['overallCount'] == 2
    assert transactions['offset'] is None
    assert transactions['limit'] is None
    assert isinstance(transactions['entries'], list)
    entries = transactions['entries']
    for entry in entries:
        assert entry['value'] in [1100, 1201]
        assert entry['userId'] == 1


def test_18_load_transactions():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('transaction',)), headers=headers, params={'offset': 1, 'limit': 1})
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    transactions = json.loads(r.text)
    assert {'overallCount', 'limit', 'offset', 'entries'}.issubset(transactions)
    assert transactions['overallCount'] == 2
    assert transactions['offset'] == 1
    assert transactions['limit'] == 1
    assert isinstance(transactions['entries'], list)
    entries = transactions['entries']
    assert len(entries) == 1
    assert entries[0]['value'] == 1201
    assert entries[0]['userId'] == 1


def test_19_load_user_transactions_1():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('user', '/', '1', '/', 'transaction',)),
                     headers=headers)
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    transactions = json.loads(r.text)
    assert {'overallCount', 'limit', 'offset', 'entries'}.issubset(transactions)
    assert transactions['overallCount'] == 2
    assert transactions['offset'] is None
    assert transactions['limit'] is None
    assert isinstance(transactions['entries'], list)
    entries = transactions['entries']
    assert entries[0]['value'] == 1100
    assert entries[0]['userId'] == 1
    assert entries[1]['value'] == 1201
    assert entries[1]['userId'] == 1


def test_20_load_user_transactions_2():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('user', '/', '2', '/', 'transaction',)),
                     headers=headers)
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    transactions = json.loads(r.text)
    assert {'overallCount', 'limit', 'offset', 'entries'}.issubset(transactions)
    assert transactions['overallCount'] == 0
    assert transactions['offset'] is None
    assert transactions['limit'] is None
    assert transactions['entries'] == []


def test_21_load_user_transactions_offset_1():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('user', '/', '1', '/', 'transaction',)),
                     headers=headers,
                     params={'limit': 1})
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    transactions = json.loads(r.text)
    assert {'overallCount', 'limit', 'offset', 'entries'}.issubset(transactions)
    assert transactions['overallCount'] == 2
    assert transactions['offset'] is None
    assert transactions['limit'] == 1
    assert isinstance(transactions['entries'], list)
    entries = transactions['entries']
    assert len(entries) == 1
    assert entries[0]['value'] == 1100
    assert entries[0]['userId'] == 1


def test_22_load_user_transactions_offset_2():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('user', '/', '1', '/', 'transaction',)),
                     headers=headers,
                     params={'offset': 1, 'limit': 1})
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    transactions = json.loads(r.text)
    assert transactions['overallCount'] == 2
    assert transactions['offset'] == 1
    assert transactions['limit'] == 1
    assert isinstance(transactions['entries'], list)
    entries = transactions['entries']
    assert len(entries) == 1
    assert {'id', 'userId', 'createDate', 'value'}.issubset(entries[0])
    assert entries[0]['value'] == 1201
    assert entries[0]['userId'] == 1


def test_23_load_user_transactions_single():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('user', '/', '1', '/', 'transaction', '/', '1',)),
                     headers=headers)
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    transaction = json.loads(r.text)
    assert {'id', 'userId', 'createDate', 'value'}.issubset(transaction)
    assert transaction['id'] == 1
    assert transaction['userId'] == 1
    assert transaction['value'] == 1100


def test_24_create_transaction_3():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # Create transaction
    params = {'value': -1000}
    r = requests.post(''.join((URL + ('user', '/', '2', '/', 'transaction',))),
                      headers=headers,
                      data=json.dumps(params))
    now = datetime.datetime.utcnow()
    assert r.status_code == 201
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert {'id', 'userId', 'createDate', 'value'}.issubset(result)
    assert result['id'] == 3
    assert result['userId'] == 2
    assert result['value'] == -1000
    create_date = datetime.datetime.strptime(result['createDate'], '%Y-%m-%dT%H:%M:%S.%f')
    assert (now - create_date).total_seconds() < 20


def test_25_metrics():
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    r = requests.get(''.join(URL + ('metrics',)),
                     headers=headers)
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    metrics = json.loads(r.text)
    assert {'overallBalance', 'countTransactions', 'avgBalance', 'countUsers', 'days'}.issubset(metrics)
    assert metrics['overallBalance'] == 1301
    assert metrics['avgBalance'] == 651
    assert metrics['countUsers'] == 2
    assert metrics['countTransactions'] == 3
    assert isinstance(metrics['days'], list)
    assert len(metrics['days']) == 4
    current_day = metrics['days'][3]
    assert current_day['date'] == datetime.datetime.utcnow().date().isoformat()
    assert current_day['dayBalance'] == 1301
    assert current_day['overallNumber'] == 3
    assert current_day['distinctUsers'] == 2

