from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)



parser = reqparse.RequestParser()
parser.add_argument('dataset')
parser.add_argument('inputs')


# curl  -H "Content-Type: application/json" -X POST -d '{"inputs":{"temperature":"20.5", "sonic velosity":"1498"}, "dataset":"PUBLISHER"}' http://localhost:5000/calculate

class calculate(Resource):
    def post(self):
        args = parser.parse_args()
        print(args)
        return 201

api.add_resource(calculate, '/calculate')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

