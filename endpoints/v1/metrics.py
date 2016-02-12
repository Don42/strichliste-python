from datetime import datetime, timedelta

from flask_restful import Resource

import strichliste.middleware
from endpoints import make_response
from strichliste import models


class MetricsV1(Resource):

    def get(self):
        today = datetime.utcnow().date()
        data = {'countTransactions': models.Transaction.query.count(),
                'overallBalance': strichliste.middleware.get_global_balance() / 100,
                'countUsers': models.User.query.count(),
                'avgBalance': strichliste.middleware.get_average_balance() / 100,
                'days': [strichliste.middleware.get_day_metrics_float(today - timedelta(days=x)) for x in range(3, -1, -1)]}

        return make_response(data, 200)

