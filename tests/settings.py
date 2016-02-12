import json

import requests

URL_V2 = ("http://", "127.0.0.1", ":", "8080", "/")


def test_settings_v2():
    r = requests.get(''.join(URL_V2 + ('settings',)))
    assert r.ok
    assert r.encoding == 'utf-8'
    settings = json.loads(r.text)
    assert 'boundaries' in settings
    boundaries = settings['boundaries']
    assert 'account' in boundaries
    assert 'transaction' in boundaries
    assert boundaries['account']['lower'] == -2300
    assert boundaries['account']['upper'] == 4200
    assert boundaries['transaction']['lower'] == -999900
    assert boundaries['transaction']['upper'] == 999900
