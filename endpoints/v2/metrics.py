from datetime import datetime, timedelta

from flask_restful import Resource

import strichliste.middleware
from endpoints import make_response
from strichliste import models


class MetricsV2(Resource):

    def get(self):
        today = datetime.utcnow().date()
        data = dict(today=today.isoformat())

        data['countTransactions'] = models.Transaction.query.count()
        data['overallBalance'] = strichliste.middleware.get_global_balance()
        data['countUsers'] = models.User.query.count()
        data['avgBalance'] = strichliste.middleware.get_average_balance()
        data['days'] = [strichliste.middleware.get_day_metrics(today - timedelta(days=x)) for x in range(3, -1, -1)]
        return make_response(data, 200)

