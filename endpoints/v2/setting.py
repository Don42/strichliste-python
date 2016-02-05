from flask_restful import Resource


class Setting(Resource):

    def get(self):
        return {'boundaries': {'upper': 42, 'lower': -23}}

