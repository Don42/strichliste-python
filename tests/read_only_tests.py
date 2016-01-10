
import requests
import json

URL = ("http://", "127.0.0.1", ":", "8080", "/")


def test_settings():
    r = requests.get(''.join(URL + ('settings',)))
    assert r.ok
    assert r.encoding == 'utf-8'
    settings = json.loads(r.text)
    assert 'boundaries' in settings
    boundaries = settings['boundaries']
    assert 'upper' in boundaries
    assert 'lower' in boundaries
    assert boundaries['lower'] == -23
    assert boundaries['upper'] == 42


def test_empty_user_list():
    r = requests.get(''.join(URL + ('user', )))
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    users = json.loads(r.text)
    assert {'overallCount', 'limit', 'offset', 'entries'}.issubset(users)
    assert users['overallCount'] == 0
    assert users['limit'] is None
    assert users['offset'] is None
    assert users['entries'] == []


def test_user_not_found():
    r = requests.get(''.join(URL + ('user', '/', '10')))
    assert r.status_code == 404
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "user 10 not found"


def test_user_not_found_transactions():
    r = requests.get(''.join(URL + ('user', '/', '10', '/', 'transaction')))
    assert r.status_code == 404
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "user 10 not found"


def test_empty_transactions():
    r = requests.get(''.join((URL + ('transaction',))))
    assert r.status_code == 200
    assert r.encoding == 'utf-8'
    transactions = json.loads(r.text)
    assert {'overallCount', 'limit', 'offset', 'entries'}.issubset(transactions)
    assert transactions['overallCount'] == 0
    assert transactions['limit'] is None
    assert transactions['offset'] is None
    assert transactions['entries'] == []


def test_fail_without_name():
    r = requests.post(''.join(URL + ('user',)))
    assert r.status_code == 400
    assert r.encoding == 'utf-8'
    result = json.loads(r.text)
    assert 'message' in result
    assert result['message'] == "name missing"
