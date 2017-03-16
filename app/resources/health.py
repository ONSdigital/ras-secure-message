from flask_restful import Resource


class Health(Resource):

    """Rest endpoint to provide health monitoring statistics"""

    @staticmethod
    def get():
        return "{status : healthy}"
