#!/usr/bin/python3.6

import signal
import sys
import os
import threading
import datetime
import time
import pandas as pd

import mysql.connector
import configparser
import logging

import random
from dash_classes import RandomWalker

import requests

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)


print('My PID is:', os.getpid())
exit_flag = False  # SIGTERM signal from OS is received if True


config = configparser.ConfigParser()
config.read('../dashboard/matrix.ini')

config_messages = configparser.ConfigParser()
config_messages.read('./ai_messages.conf')
def write_config_messages():
    with open('./ai_messages.conf', 'w') as configfile:
        #fcntl.flock(configfile, fcntl.LOCK_EX)
        config.write(configfile)
        #fcntl.flock(configfile, fcntl.LOCK_UN)

logging.basicConfig(filename='ai_daemon.log', filemode = 'w', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.info('Starting AI_Service')


def sigterm_handler(signal, frame):
    global exit_flag
    exit_flag = True
    # save the state here or do whatever you want
    print('\n', 'bye bye...')
    time.sleep(5)
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)


connection_flag = False # False if no connection to data base. 
while connection_flag == False:
    time.sleep(1)
    try:
        connection_flag = True
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            auth_plugin='mysql_native_password',
            passwd="th6nw7hg",
            database="dash_main",
            buffered="True")
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        connection_flag = False
mycursor = mydb.cursor(buffered=True)

rw_1 = RandomWalker()
rw_2 = RandomWalker()
rw_3 = RandomWalker()
rw_4 = RandomWalker()
rw_5 = RandomWalker()
rw_6 = RandomWalker()
rw_7 = RandomWalker()

current_table = ''
current_date = ''

writing_to_db_flag = True # writing to data base is possible if True
WAIT_SECONDS = 1                                                        # sampling rate in secinds
def analog_input_reader():
    global exit_flag
    global config_messages
    global last_measurements
    if exit_flag == False:
        threading.Timer(WAIT_SECONDS, analog_input_reader).start()
    else:
        pass
    temperature_1 = 'NULL'                                               # data to db   / 'NULL' or float number
    temperature_2 = 'NULL'                                               # data to db   / 'NULL' or float number


    input_1 = round(rw_1.get_single_value(),3)
    input_2 = round(rw_2.get_single_value(),3)
    input_3 = round(rw_3.get_single_value(),3)
    input_4 = round(rw_4.get_single_value(),3)
    input_5 = round(rw_5.get_single_value(),3)
    input_6 = round(rw_6.get_single_value(),3)
    input_7 = round(rw_7.get_single_value(),3)
    input_8 = round(random.uniform(5, 9), 3)
    
    list_of_inputs = [input_1, input_2, input_3, input_4, input_5, input_6, input_7, input_8]

    list_of_inputs_calculated = ['NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL']
    for n in range(1,9):
        if config['AI'][f'ai_{n}_active'] == 'True':                           # data to db
            try:                                             
                x1 = float(config['AI'][f'ai_{n}_source_low'])
                y1 = float(config['AI'][f'ai_{n}_target_low'])
                x2 = float(config['AI'][f'ai_{n}_source_high'])
                y2 = float(config['AI'][f'ai_{n}_target_high'])
                k = (y1 - y2) / (x1 - x2)
                b = y2 - k*x2
                in_calculated = k * list_of_inputs[n-1] + b
            except:
                in_calculated = 'NULL'
        else:
            list_of_inputs[n-1] = 'NULL'
            in_calculated = 'NULL'
        list_of_inputs_calculated[n-1] = in_calculated   

  

    url = 'http://localhost:5000/calculate'
    json = {"inputs":{"model_input_a":"20", "model_input_b":"1498.3", "model_input_c":"8",  "model_input_d":"NULL" }, "dataset_id":"model_0000"}
    try: 
        x = requests.post(url, json = json)
        list_of_model_outputs = x.json()
    except: 
        list_of_model_outputs = ['NULL', 'NULL', 'NULL', 'NULL']
        print ('Error: Check if MATRIX daemon is running.')


    
    input_1, input_2, input_3, input_4, input_5, input_6, input_7, input_8 = list_of_inputs
    in_1_calculated, in_2_calculated, in_3_calculated, in_4_calculated, in_5_calculated, in_6_calculated, in_7_calculated, in_8_calculated = list_of_inputs_calculated

    j = [config['model']['model_output_a'], config['model']['model_output_b'], config['model']['model_output_c'],config['model']['model_output_d']]
    try: output_1 = list_of_model_outputs[j.index('output_1')] 
    except: output_1 = 'NULL'
    try: output_2 = list_of_model_outputs[j.index('output_2')] 
    except: output_2 = 'NULL'
    try: output_3 = list_of_model_outputs[j.index('output_3')] 
    except: output_3 = 'NULL' 
    try: output_4 = list_of_model_outputs[j.index('output_4')] 
    except: output_4 = 'NULL' 

    print(list_of_inputs)
    print(list_of_inputs_calculated)
    print(output_1, output_2, output_3, output_4)
    print('----')

    last_measurements = list_of_inputs + list_of_inputs_calculated + [output_1, output_2, output_3, output_4]


    comments = '...'                                                    # data to db

    current_time = datetime.datetime.utcnow()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]      # data to db
    
    global current_table
    global current_date
    global writing_to_db_flag
    current_table = 'general_data' 



    if current_date != current_time.strftime("%Y-%m-%d"):
        current_date = current_time.strftime("%Y-%m-%d")
        print('Inserting date in Calendar...')
        print(current_date)
        if writing_to_db_flag == True:
            writing_to_db_flag = False
            mycursor.execute('REPLACE INTO calendar SET date = "{}"'.format(current_date))
            mydb.commit()
            writing_to_db_flag = True
        else: 
            pass
    else:
        pass

 
    if writing_to_db_flag == True:
        writing_to_db_flag = False
        mycursor.execute(
            "INSERT INTO {} (   date_time_utc, temperature_1, temperature_2, \
                                input_1, input_2, input_3, input_4, input_5, input_6, input_7, input_8,\
                                in_1_calculated, in_2_calculated, in_3_calculated, in_4_calculated, in_5_calculated, in_6_calculated, in_7_calculated, in_8_calculated,\
                                output_1, output_2, output_3, output_4,\
                                comments)\
            VALUES ('{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, '{}')".format(current_table,
                                                timestamp, temperature_1, temperature_2, 
                                                input_1, input_2, input_3, input_4, input_5, input_6, input_7, input_8, 
                                                in_1_calculated, in_2_calculated, in_3_calculated, in_4_calculated, in_5_calculated, in_6_calculated, in_7_calculated, in_8_calculated,
                                                output_1, output_2, output_3, output_4,
                                                comments))
        mydb.commit()
        writing_to_db_flag = True
        #print('\r', timestamp, '***', temperature, '***', input_1,
        #      '***', input_2, '***', input_3, '***', input_4, end = '')
    else:
        print('\n', 'pass...')

WAIT_FOR_RELOAD_SECONDS = 10
def reload_config():
    global exit_flag
    if exit_flag == False:
        threading.Timer(WAIT_FOR_RELOAD_SECONDS, reload_config).start()
    else:
        pass  
    config.read('../dashboard/matrix.ini')
    print('Reload config ok')

analog_input_reader() 
reload_config()


class get_last_measurement(Resource):
    def get(self):
        global last_measurements
        return last_measurements


api.add_resource(get_last_measurement, '/get_last_measurement')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

