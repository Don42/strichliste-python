from flask import current_app, request
from endpoints import make_error_response


def page_not_found(e):
    current_app.logger.warning("Page not found: '{}'".format(request.path))
    return make_error_response("page not found: '{}'".format(request.path), 404)
