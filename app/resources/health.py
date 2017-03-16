from flask_restful import Resource


class Health(Resource):

    """Rest endpoint to provide health monitoring statistics"""

    def get(self):
        return "{status : healthy}"
