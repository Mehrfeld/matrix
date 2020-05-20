import os
import json
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

import dill as pickle

app = Flask(__name__)
api = Api(app)

model = pickle.load(open( "./models/model_0000.mdl", 'rb'))
active_model = 'model_0000'

parser = reqparse.RequestParser()
parser.add_argument('dataset_id')
parser.add_argument('inputs')


# curl  -H "Content-Type: application/json" -X POST -d '{"inputs":{"model_input_a":"20", "model_input_b":"1498", "model_input_c":"1" }, "dataset_id":"model_0000"}' http://localhost:5000/calculate
# curl  -X GET http://localhost:5000/get_models

class get_available_models(Resource):
    def get(self):
        list_ = os.listdir('./models')
        list__ = [entry.split('.')[0] for entry in list_]
        return list__

class calculate(Resource):
    def post(self):

        global model, active_model

        args = parser.parse_args()
        
        dataset_id = args['dataset_id']
        if dataset_id != active_model:
            try:
                model =  pickle.load(open( f"./models/{dataset_id}.mdl", "rb" ))
                active_model = dataset_id
            except:
                return 'Error: check the dataset_id'
        else:
            pass

        inputs = json.loads(args['inputs'].replace("\'", "\""))
        try: model_input_a = float(inputs['model_input_a'])
        except: model_input_a = 1

        try: model_input_b = float(inputs['model_input_b'])
        except: model_input_b = 1

        try: model_input_c = float(inputs['model_input_c'])
        except: model_input_c = 1

        try: model_input_d = float(inputs['model_input_d'])
        except: model_input_d = 1

        try: model_input_e = float(inputs['model_input_e'])
        except: model_input_e = 1

        try: model_input_f = float(inputs['model_input_f'])
        except: model_input_f = 1

        try: model_input_g = float(inputs['model_input_g'])
        except: model_input_g = 1

        try: model_input_h = float(inputs['model_input_h'])
        except: model_input_h = 1

        return model(   model_input_a, model_input_b, model_input_c, model_input_d,
                        model_input_e, model_input_f, model_input_g, model_input_h)

api.add_resource(calculate, '/calculate')
api.add_resource(get_available_models, '/get_models')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

