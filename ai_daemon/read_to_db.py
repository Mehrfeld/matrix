#!/usr/bin/python3.6

import signal
import sys
import os
import threading
import datetime
import time

import mysql.connector
import configparser
import logging

import random
from dash_classes import RandomWalker


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

logging.basicConfig(filename='ai_daemon.log', filemode = 'w', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.debug('Starting AI_Service')


def sigterm_handler(signal, frame):
    global exit_flag
    exit_flag = True
    # save the state here or do whatever you want
    print('\n', 'bye bye...')
    time.sleep(0)

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
writing_to_db_flag = True # writing to data base is possible if True
WAIT_SECONDS = 1                                                        # sampling rate in secinds
def analog_input_reader():
    global exit_flag
    global config_messages
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
    print(list_of_inputs)
    print(list_of_inputs_calculated)
    
    input_1, input_2, input_3, input_4, input_5, input_6, input_7, input_8 = list_of_inputs
    in_1_calculated, in_2_calculated, in_3_calculated, in_4_calculated, in_5_calculated, in_6_calculated, in_7_calculated, in_8_calculated = list_of_inputs_calculated


    comments = '...'                                                    # data to db

    current_time = datetime.datetime.utcnow()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]      # data to db
    global current_table
    global writing_to_db_flag
    if current_table != current_time.strftime("%Y_%m_%d"):
        current_table = current_time.strftime("%Y_%m_%d")
        print('Creating tabele...')
        if writing_to_db_flag == True:
            writing_to_db_flag = False
            mycursor.execute("CREATE TABLE IF NOT EXISTS {} (id INT NOT NULL AUTO_INCREMENT,\
                            date_time_utc DATETIME(0), \
                            temperature_1 FLOAT, temperature_2 FLOAT,\
                            input_1 FLOAT, input_2 FLOAT, input_3 FLOAT, input_4 FLOAT, input_5 FLOAT, input_6 FLOAT, input_7 FLOAT, input_8 FLOAT,\
                            in_1_calculated FLOAT, in_2_calculated FLOAT, in_3_calculated FLOAT, in_4_calculated FLOAT, in_5_calculated FLOAT, in_6_calculated FLOAT, in_7_calculated FLOAT, in_8_calculated FLOAT,\
                            comments TEXT, PRIMARY KEY (id))".format(current_table))
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
                                comments)\
            VALUES ('{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, '{}')".format(current_table, timestamp, temperature_1, temperature_2, 
                                                                                input_1, input_2, input_3, input_4, input_5, input_6, input_7, input_8, 
                                                                                in_1_calculated, in_2_calculated, in_3_calculated, in_4_calculated, in_5_calculated, in_6_calculated, in_7_calculated, in_8_calculated,
                                                                                comments))
        mydb.commit()
        writing_to_db_flag = True
        #print('\r', timestamp, '***', temperature, '***', input_1,
        #      '***', input_2, '***', input_3, '***', input_4, end = '')
    else:
        print('\n', 'pass...')

WAIT_FOR_RELOAD_SECONDS = 10
def reload_config():
    threading.Timer(WAIT_FOR_RELOAD_SECONDS, reload_config).start()
    config.read('../dashboard/matrix.ini')
    print('Reload config ok')


analog_input_reader() 
reload_config()
