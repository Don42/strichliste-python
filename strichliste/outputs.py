import flask


HEADERS_JSON = {'Content-Type': 'application/json'}


def output_json(data, code, headers=None):
    resp = flask.make_response(flask.jsonify(data), code)
    resp.headers.extend(HEADERS_JSON)
    if headers is not None:
        resp.headers.extend(headers)
    return resp


