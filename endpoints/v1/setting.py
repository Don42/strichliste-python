from flask_restful import Resource

from strichliste.config import Config
from endpoints import make_response


class Setting(Resource):

    def get(self):
        config = Config()
        return make_response({'boundaries': {'account': {'upper': config.upper_account_boundary // 100,
                                                         'lower': config.lower_account_boundary // 100},
                                             'transaction': {'upper': config.upper_transaction_boundary // 100,
                                                             'lower': config.lower_transaction_boundary // 100}
                                             }
                              }, 200)

