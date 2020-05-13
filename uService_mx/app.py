import os
import json
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

import dill as pickle

app = Flask(__name__)
api = Api(app)



model_0001 = pickle.load(open( "./models/model_0001.mdl", "rb" ))
print(model_0001())




parser = reqparse.RequestParser()
parser.add_argument('dataset_id')
parser.add_argument('inputs')


# curl  -H "Content-Type: application/json" -X POST -d '{"inputs":{"temperature":"20.5", "sonic velosity":"1498"}, "dataset_id":"PUBLISHER"}' http://localhost:5000/calculate
# curl  -X GET http://localhost:5000/get_models

class get_available_models(Resource):
    def get(self):
        list_ = os.listdir('./models')
        list__ = [entry.split('.')[0] for entry in list_]
        return list__

class calculate(Resource):
    def post(self):
        args = parser.parse_args()
        print(args['inputs'])
        return 201

api.add_resource(calculate, '/calculate')

api.add_resource(get_available_models, '/get_models')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

