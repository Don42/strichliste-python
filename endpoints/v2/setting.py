from flask_restful import Resource

from strichliste.config import Config
from endpoints import make_response


class SettingV2(Resource):

    def get(self):
        config = Config()
        return make_response({'boundaries': {'account': {'upper': config.upper_account_boundary,
                                                         'lower': config.lower_account_boundary},
                                             'transaction': {'upper': config.upper_transaction_boundary,
                                                             'lower': config.lower_transaction_boundary}
                                             }
                              }, 200)
