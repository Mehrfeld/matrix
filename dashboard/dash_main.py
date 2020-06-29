#!/usr/bin/python3.6

import os, sys, signal
from flask import send_file
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output, State
#from classes_a import get_tables_list, get_data_from_db_average

import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime
import time
import requests
from pytz import timezone
import pytz

import logging
import configparser
# import fcntl # locking access to a file for different applications/processes
from threading import Lock

from db_connector import DB_Reader


def sigterm_handler(signal, frame):
    global exit_flag
    exit_flag = True
    # save the state here or do whatever you want
    print('\n', 'bye bye...')
    time.sleep(5)
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

lock = Lock()

logging.basicConfig(filename='dashboard.log', filemode = 'w', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.info('Starting Dashboard')


db_reader_a = DB_Reader() # used for db_browser
db_reader_b = DB_Reader() # used for cockpit



work_dir = os.path.abspath(os.path.dirname(__file__))

config = configparser.ConfigParser()
config.read(work_dir + '/matrix.ini')
print(os.path.abspath(os.path.dirname(__file__)))






def write_config():
    with open(work_dir + '/matrix.ini', 'w') as configfile:
        #fcntl.flock(configfile, fcntl.LOCK_EX)
        config.write(configfile)
        #fcntl.flock(configfile, fcntl.LOCK_UN)

fmt = '%Y-%m-%d %H:%M:%S %Z%z'
current_time_test = datetime.datetime.utcnow()
now_utc = timezone('UTC').localize(current_time_test)
now_berlin = now_utc.astimezone(timezone('Europe/Berlin'))
print (now_berlin.strftime(fmt))
print (now_utc.strftime(fmt))

def channels():
    channels =[ {'label': 'Empty', 'value': 'empty'},
                {'label': f'Analog Input 1 ({config["AI"]["AI_1_description"].replace("%%", "%")})', 'value': 'in_1_calculated'},
                {'label': f'Analog Input 2 ({config["AI"]["AI_2_description"].replace("%%", "%")})', 'value': 'in_2_calculated'},
                {'label': f'Analog Input 3 ({config["AI"]["AI_3_description"].replace("%%", "%")})', 'value': 'in_3_calculated'},
                {'label': f'Analog Input 4 ({config["AI"]["AI_4_description"].replace("%%", "%")})', 'value': 'in_4_calculated'},
                {'label': f'Analog Input 5 ({config["AI"]["AI_5_description"].replace("%%", "%")})', 'value': 'in_5_calculated'},
                {'label': f'Analog Input 6 ({config["AI"]["AI_6_description"].replace("%%", "%")})', 'value': 'in_6_calculated'},
                {'label': f'Analog Input 7 ({config["AI"]["AI_7_description"].replace("%%", "%")})', 'value': 'in_7_calculated'},
                {'label': f'Analog Input 8 ({config["AI"]["AI_8_description"].replace("%%", "%")})', 'value': 'in_8_calculated'},
                {'label': 'Analog Input 1 (raw signal)', 'value': 'input_1'},
                {'label': 'Analog Input 2 (raw signal)', 'value': 'input_2'},
                {'label': 'Analog Input 3 (raw signal)', 'value': 'input_3'},
                {'label': 'Analog Input 4 (raw signal)', 'value': 'input_4'},
                {'label': 'Analog Input 5 (raw signal)', 'value': 'input_5'},
                {'label': 'Analog Input 6 (raw signal)', 'value': 'input_6'},
                {'label': 'Analog Input 7 (raw signal)', 'value': 'input_7'},
                {'label': 'Analog Input 8 (raw signal)', 'value': 'input_8'},
                {'label': f'Analog Output 1 ({config["AO"]["ao_1_description"].replace("%%", "%")})', 'value': 'output_1'},
                {'label': f'Analog Output 2 ({config["AO"]["ao_2_description"].replace("%%", "%")})', 'value': 'output_2'},
                {'label': f'Analog Output 3 ({config["AO"]["ao_3_description"].replace("%%", "%")})', 'value': 'output_3'},
                {'label': f'Analog Output 4 ({config["AO"]["ao_4_description"].replace("%%", "%")})', 'value': 'output_4'} ]
    return channels

def channels_calс_inputs():
    channels_calс_inputs = [ 
                {'label': 'Empty', 'value': 'empty'},
                {'label': f'Analog Input 1 ({config["AI"]["AI_1_description"].replace("%%", "%")})', 'value': 'in_1_calculated', 'disabled': False},
                {'label': f'Analog Input 2 ({config["AI"]["AI_2_description"].replace("%%", "%")})', 'value': 'in_2_calculated', 'disabled': False},
                {'label': f'Analog Input 3 ({config["AI"]["AI_3_description"].replace("%%", "%")})', 'value': 'in_3_calculated', 'disabled': False},
                {'label': f'Analog Input 4 ({config["AI"]["AI_4_description"].replace("%%", "%")})', 'value': 'in_4_calculated', 'disabled': False},
                {'label': f'Analog Input 5 ({config["AI"]["AI_5_description"].replace("%%", "%")})', 'value': 'in_5_calculated', 'disabled': False},
                {'label': f'Analog Input 6 ({config["AI"]["AI_6_description"].replace("%%", "%")})', 'value': 'in_6_calculated', 'disabled': False},
                {'label': f'Analog Input 7 ({config["AI"]["AI_7_description"].replace("%%", "%")})', 'value': 'in_7_calculated', 'disabled': False},
                {'label': f'Analog Input 8 ({config["AI"]["AI_8_description"].replace("%%", "%")})', 'value': 'in_8_calculated', 'disabled': False} ]
    return channels_calс_inputs

def channels_output():
    channels_output =[  
                {'label': 'Not active', 'value': 'empty'},
                {'label': 'Analog Output 1', 'value': 'output_1', 'disabled': False},
                {'label': 'Analog Output 2', 'value': 'output_2', 'disabled': False},
                {'label': 'Analog Output 3', 'value': 'output_3', 'disabled': False},
                {'label': 'Analog Output 4', 'value': 'output_4', 'disabled': False}  ]
    return channels_output


#-----------tab_0_content (Cockpit)-------------------
def tab0_content():

    logging.info('Redrowing Cockpit content')
    print('Redrowing Cockpit content')

    global time_of_last_point_in_chart_a_graph
    #global df_a_graph, df_b_graph
    global fig
    global data_to_show_a_graph, data_to_show_b_graph, period_to_monitor_a_graph, period_to_monitor_b_graph

    data_to_show_a_graph = config['cockpit']['data_to_show_a_graph']
    data_to_show_b_graph = config['cockpit']['data_to_show_b_graph']
    period_to_monitor_a_graph = 'start value'
    period_to_monitor_b_graph = 'start value'

    current_time = datetime.datetime.utcnow()
    time_of_last_point_in_chart_a_graph = current_time

    # start_date_time='2020_01_01 10:00:00'
    # stop_date_time='2020_01_01 12:00:00'
    # df_a_graph = pd.DataFrame({0:[datetime.datetime.strptime(start_date_time, "%Y_%m_%d %H:%M:%S"), datetime.datetime.strptime(stop_date_time, "%Y_%m_%d %H:%M:%S")], 1 :[0.0, 0.0]})
    # df_b_graph = pd.DataFrame({0:[datetime.datetime.strptime(start_date_time, "%Y_%m_%d %H:%M:%S"), datetime.datetime.strptime(stop_date_time, "%Y_%m_%d %H:%M:%S")], 1 :[0.0, 0.0]})

    fig = go.Figure(data=go.Scattergl(mode='lines+markers', line=dict(color='#1E90FF', width=4, dash='dot'), x=[0], y=[0])) # use Scattergl for large data
    fig['layout']['xaxis'].update(title='Date and Time', type='date', tickformat='%H:%M\n%b %d, %Y',  autorange=True)
    fig['layout']['yaxis'].update(title='...', autorange=True)
    #fig['layout'].update(autosize = True)
    fig.update_layout(margin=dict(t=50), autosize = True)

    tab0_content = dbc.Card(html.Div(children=[
        dcc.Store(id='memory_a_graph'),
        dcc.Store(id='store_to_append_a_graph'),
        dcc.Store(id='state_a_graph'),
        dcc.Store(id='memory_b_graph'),
        dcc.Store(id='data_to_append_b_graph'), 
        dcc.Store(id='state_b_graph'),
        dbc.CardBody(children=[
            dbc.Row(no_gutters=True, children=[ 
                
                dbc.Col(width=3, style={'text-align':'left'}, children=[  
                        html.Div(style={'margin-top':30, 'padding':15}, children=[      
                            dbc.Row(style={'margin-top':0}, no_gutters=True, children=[
                                        dbc.Col(width=12, children=[
                                                            dcc.Dropdown(   options=[{ **item, 'label': item['label'].replace('Analog Input', 'AI').replace('Analog Output', 'AO').replace('(', '- ').replace(')', '')} for item in channels()[1:21]]      , 
                                                                            value=config['cockpit']['data_to_show_a'], style={'width': '100%', 'margin-left':0, 'margin-top':0, 'margin-bottom':0, 'font-weight':'bold'}, clearable=False, searchable=False,
                                                                            id='channel_to_monitor_a')])    ]),
                            html.Div('--,--', id='last_value_to_indicate_a', style={    'height': '60px', 'width': '100%', 'margin-bottom':10, 'margin-top':10,
                                                                                        'border-style': 'double', 'border-color': 'Gainsboro', 'border-width': '4px',
                                                                                        'font-weight':'bold','font-size':'xx-large', 'text-align':'center'}),               
                            html.Div(dcc.Slider(id='slider_a', min=0, max=100, step=0.5, value=10, included=False, disabled=False, vertical=False, marks={
                                        0: {'label': '0 °C', 'style': {'color': '#77b0b1', 'font-size':'large', 'white-space': 'nowrap', 'font-weight':'bold'}},
                                        100: {'label': '2000 °C', 'style': {'color': '#f50', 'font-size':'large', 'white-space': 'nowrap', 'font-weight':'bold'}}}  ), style={'pointer-events':'none'})]),  ]),

                
                dbc.Col(width=3, style={'text-align':'left'}, children=[   
                        html.Div(style={'margin-top':30, 'padding':15}, children=[
                            dbc.Row(style={'margin-top':0}, no_gutters=True, children=[
                                        dbc.Col(width=12, children=[
                                                            dcc.Dropdown(   options=[{ **item, 'label': item['label'].replace('Analog Input', 'AI').replace('Analog Output', 'AO').replace('(', '- ').replace(')', '')} for item in channels()[0:21]], 
                                                                            value=config['cockpit']['data_to_show_b'], style={'width': '100%', 'margin-left':0, 'margin-top':0, 'margin-bottom':0, 'font-weight':'bold'}, clearable=False, searchable=False,
                                                                            id='channel_to_monitor_b')])]),
                            html.Div('--,--', id='last_value_to_indicate_b', style={    'height': '60px', 'width': '100%', 'margin-bottom':10, 'margin-top':10,
                                                                                        'border-style': 'double', 'border-color': 'Gainsboro', 'border-width': '4px',
                                                                                        'font-weight':'bold','font-size':'xx-large', 'text-align':'center'}),               
                            html.Div(dcc.Slider(id='slider_b', min=0, max=100, step=0.5, value=10, included=False, disabled=False, marks={
                                        0: {'label': '0 °C', 'style': {'color': '#77b0b1', 'font-size':'large', 'white-space': 'nowrap', 'font-weight':'bold'}},
                                        100: {'label': '2000 °C', 'style': {'color': '#f50', 'font-size':'large', 'white-space': 'nowrap', 'font-weight':'bold'}}}  ), style={'pointer-events':'none'})]),  ]),

                dbc.Col(width=3, style={'text-align':'left'}, children=[   
                        html.Div(style={'margin-top':30, 'padding':15}, children=[
                            dbc.Row(style={'margin-top':0}, no_gutters=True, children=[
                                        dbc.Col(width=12, children=[
                                                            dcc.Dropdown(   options=[{ **item, 'label': item['label'].replace('Analog Input', 'AI').replace('Analog Output', 'AO').replace('(', '- ').replace(')', '')} for item in channels()[0:21]], 
                                                                            value=config['cockpit']['data_to_show_c'], style={'width': '100%', 'margin-left':0, 'margin-top':0, 'margin-bottom':0, 'font-weight':'bold'}, clearable=False, searchable=False,
                                                                            id='channel_to_monitor_c')])]),
                            html.Div('--,--', id='last_value_to_indicate_c', style={    'height': '60px', 'width': '100%', 'margin-bottom':10, 'margin-top':10,
                                                                                        'border-style': 'double', 'border-color': 'Gainsboro', 'border-width': '4px',
                                                                                        'font-weight':'bold','font-size':'xx-large', 'text-align':'center'}),               
                            html.Div(dcc.Slider(id='slider_c', min=0, max=100, step=0.5, value=10, included=False, disabled=False, marks={
                                        0: {'label': '0 °C', 'style': {'color': '#77b0b1', 'font-size':'large', 'white-space': 'nowrap', 'font-weight':'bold'}},
                                        100: {'label': '2000 °C', 'style': {'color': '#f50', 'font-size':'large', 'white-space': 'nowrap', 'font-weight':'bold'}}}  ), style={'pointer-events':'none'})]),   ]),
                
                
                dbc.Col(width=3, style={'text-align':'left'}, children=[   
                        html.Div(style={'margin-top':30, 'padding':15}, children=[
                            dbc.Row(style={'margin-top':0}, no_gutters=True, children=[
                                        dbc.Col(width=12, children=[
                                                            dcc.Dropdown(   options=[{ **item, 'label': item['label'].replace('Analog Input', 'AI').replace('Analog Output', 'AO').replace('(', '- ').replace(')', '')} for item in channels()[0:21]], 
                                                                            value=config['cockpit']['data_to_show_d'], style={'width': '100%', 'margin-left':0, 'margin-top':0, 'margin-bottom':0, 'font-weight':'bold'}, clearable=False, searchable=False,
                                                                            id='channel_to_monitor_d')])]),
                            html.Div('--,--', id='last_value_to_indicate_d', style={    'height': '60px', 'width': '100%', 'margin-bottom':10, 'margin-top':10,
                                                                                        'border-style': 'double', 'border-color': 'Gainsboro', 'border-width': '4px',
                                                                                        'font-weight':'bold','font-size':'xx-large', 'text-align':'center'}),               
                            html.Div(dcc.Slider(id='slider_d', min=0, max=100, step=0.5, value=10, included=False, disabled=False, marks={
                                        0: {'label': '0 °C', 'style': {'color': '#77b0b1', 'font-size':'large', 'white-space': 'nowrap', 'font-weight':'bold'}},
                                        100: {'label': '2000 °C', 'style': {'color': '#f50', 'font-size':'large', 'white-space': 'nowrap', 'font-weight':'bold'}}}  ), style={'pointer-events':'none'})]),   ]),

                ]),

            dbc.Row(style={'min-height':60}, no_gutters=True ,children=[  
                dbc.Col(

                    html.Div(style={ 'position': 'relative', 'display': 'inline-block', 'width': '100%'}, children=[
                        html.Div(dcc.Graph(id='live-chart-a', figure=fig, config={'displayModeBar': False, "displaylogo": False,'modeBarButtonsToRemove': ['lasso2d']}, style={'height': 300, 'margin-top':3, 'width': '100%'})), 
                        html.Div(dcc.Dropdown(   options=[{ **item, 'label': item['label'].replace('Analog Input', 'AI').replace('Analog Output', 'AO').replace('(', '- ').replace(')', '')} for item in channels()[0:21]], 
                                    value=config['cockpit']['data_to_show_a_graph'], clearable=False, searchable=False,
                                    id='channel_to_monitor_a_graph'), style={'text-align':'left', 'font-weight':'bold', 'width': 450 , 'position': 'absolute', 'left':80, 'top':3} )
                                    
                                    ]), 

                    width=6),
                
                dbc.Col(

                    html.Div(style={ 'position': 'relative', 'display': 'inline-block', 'width': '100%'}, children=[
                        html.Div(dcc.Graph(id='live-chart-b', figure=fig, config={'displayModeBar': False, "displaylogo": False,'modeBarButtonsToRemove': ['lasso2d']}, style={'height': 300, 'margin-top':3, 'width': '100%'})),
                        html.Div(dcc.Dropdown(   options=[{ **item, 'label': item['label'].replace('Analog Input', 'AI').replace('Analog Output', 'AO').replace('(', '- ').replace(')', '')} for item in channels()[0:21]], 
                                    value=config['cockpit']['data_to_show_b_graph'], clearable=False, searchable=False,
                                    id='channel_to_monitor_b_graph'), style={'text-align':'left', 'font-weight':'bold', 'width': 450 , 'position': 'absolute', 'left':80, 'top':3})
                                    
                                    ]), 

                    width=6)    ]),

                                ]),
        
        

        html.Div('Period of time to monitor (graphs): ', style={'position': 'absolute', 'left':690, 'top':15}),
        html.Div(children=[
            dcc.Dropdown(   options=[ 
                                    {'label': 'One hour',   'value': '1_hour'},
                                    {'label': 'Three hours','value': '3_hours'},
                                    {'label': '12 hours',   'value': '12_hours'},
                                    {'label': '24 hours',   'value': '24_hours'},
                                    {'label': 'Three days', 'value': '3_days'},
                                    {'label': 'Seven days', 'value': '7_days'}
                                    ], value=config['cockpit']['period_to_monitor_a_graph'], style={'width': 273}, clearable=False, searchable=False, id='period_to_monitor'),
            ], style={'margin-left':0, 'position': 'absolute', 'left':953, 'top':15}),
        html.Div('APPLICATION', style={'font-weight':'bold','font-size':'x-large', 'position': 'absolute', 'left':25, 'top':13})

            ], style={'position': 'relative', 'display': 'inline-block'}), className="mt-3")

    return tab0_content



#-----------tab_1_content (Level 1)-------------------
def tab1_content():


    tab_content = dbc.Card(
        dbc.CardBody(
            [
                html.P("This is tab 2!", style={'text-align':'left'}, className="card-text"),
                html.Div(html.Img(src="./assets/model_0000.jpg", style={'max-width':'100%'}))
            ]), className="mt-3",)

    return tab_content

#-----------db_browser_content (Level 2)--------------  

def db_browser_content():
    inputs_to_show_list = [chunk.strip(None) for chunk in config['db_browser']['list_of_inputs'].split(',')]
    
    lock.acquire()
    list_of_dates_in_db = db_reader_a.get_dates_list()
    lock.release()


    global fig
    browser_content = dbc.Card(
        dcc.Loading(dbc.CardBody(children = [
                    dbc.Row(html.Div(children=[ dcc.Graph(id='day_chart', figure=fig, config={'displayModeBar': True, "displaylogo": False,'modeBarButtonsToRemove': ['lasso2d']}, style={'height': '100%', 'width': '100%'}),
                                                html.Div(   html.Div(children=[ html.A("Download selected data", id = 'download_selected_data', href = 'download/2020_02_15.csv'),
                                                                                dbc.Tooltip("Noun: rare, the action or habit of estimating something as worthless.", target="download_selected_data", hide_arrow=False)]), 
                                                            style={'position': 'absolute', 'left':25, 'top':0})], # Div for the any elemets on top of Graph layer - left top corner.
                                    style={'height': 500, 'width':'100%',  'position': 'relative', 'display': 'inline-block'})),
                    
                    dbc.Row(no_gutters=False,
                            children=[
                            dbc.Col(html.Div(children = [
                                #dbc.Button(className="mb-3", id = 'button_reload_tables', children=["Reload", html.Br(),"data base"], color="primary", size="sm", style={'min-width': '90px'}),
                                #dbc.Button(className="mb-3 ml-1", id = 'button_delete_selected', children=["Delete", html.Br(),"selected"], color="danger", size="sm", style={'min-width': '90px'}),
                                html.Div(dash_table.DataTable(id='table_list_of_days', columns=[{"name": "Day Tables in db:", "id": "tabels_in_db"}], 
                                        selected_cells = [{'row': 0, 'column': 0, 'column_id': 'tabels_in_db'}],
                                        data=[{"tabels_in_db": i} for i in reversed(list_of_dates_in_db)],
                                        fixed_rows={ 'headers': True, 'data': 0 },
                                        style_table={'maxHeight': '200px', 'cursor':'auto'},
                                        style_cell={'textAlign': 'center', 'font-size':'140%'},
                                        style_as_list_view=True), className="pl-0 pr-0")
                                        
                                        
                                        
                                        ]), width=3),      
                            dbc.Col(html.Div(style={'margin-left':16}, children = [
                                            dbc.Row(children=[
                                                dbc.Col(children=[                                                    
                                                    dbc.Row([html.Div(  dcc.Dropdown(options=channels()[1:21], 
                                                                                value=inputs_to_show_list[0], 
                                                                                style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False,
                                                                                id='channel_to_show_a'), style={'margin-left': 0, 'margin-right': 10}),
                                                                        dcc.Dropdown(options=channels(), 
                                                                                value=inputs_to_show_list[1],
                                                                                style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False, 
                                                                                id='channel_to_show_b')], className='mb-2'),                                                    
                                                    
                                                    
                                                    dbc.Row([html.Div(  dcc.Dropdown(options=channels(), 
                                                                                value=inputs_to_show_list[2], 
                                                                                style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False,
                                                                                id='channel_to_show_c'), style={'margin-left': 0, 'margin-right': 10}),
                                                                        dcc.Dropdown(options=channels(), 
                                                                                value=inputs_to_show_list[3],
                                                                                style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False, 
                                                                                id='channel_to_show_d')], className='mb-2'),                                          
                                                                                        
                                                    dbc.Row(html.Div('',style={'width':'670px','margin-top':4, 'margin-bottom':12, 'border-top-style': 'double', 'border-top-color': 'Gainsboro', 'border-top-width': '4px'})),

                                                    dbc.Row([html.Div(
                                                                    dcc.Dropdown(options=[ 
                                                                                    {'label': 'One day / 180 sec.',     'value': 'one_180'},
                                                                                    {'label': 'One day / 60 sec.',      'value': 'one_60'},
                                                                                    {'label': 'One day / 30 sec.',      'value': 'one_30'},
                                                                                    {'label': 'Three days / 180 sec.',  'value': 'three_180'},
                                                                                    ], 
                                                                                value=config['db_browser']['days_and_points_in_chart'], style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False,
                                                                                id='days_and_points_in_chart'), style={'margin-left': 0, 'margin-right': 10}),
                                                                    dcc.Dropdown(options=[  {'label': 'Lines+markers', 'value': 'lines+markers'},
                                                                                    {'label': 'Lines', 'value': 'lines'},
                                                                                    {'label': 'Markers', 'value': 'markers'}], 
                                                                                    value=config['db_browser']['lines_markers'],
                                                                                    style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False, id='lines_markers')], style={})  
                                                        ], width=9),
                                                
                                                dbc.Col(html.Div(dbc.Button(className="mb-3", id = 'button_load_curves', children=["Load", html.Br(),"curves"], color="primary", size="sm", style={'min-width': '90px'}), style={'text-align': 'left'}),
                                                width=3)
                                                ], justify="start"),
                                            ]), width=9, align='start')      
                        ],
                    )], className=""), type = 'cube', fullscreen=True),
                    className="mt-3")
    return browser_content    

#-----------settings_content--------------------------
def settings_content():

    # Content of 'Analog Inputs'
    def ai_n_settings_block(n):
        if config['AI'][f'ai_{n}_active']=='True':
            value_active = ['True']
        else:
            value_active = []
        return dbc.Col(className='pr-2', children=[   
                                dbc.Card(color='light', outline=True, inverse=False, id=f'AI_{n}_card', children=[

                                    dbc.Row(no_gutters=True, children=[
                                    dbc.Col(dbc.Input(id=f"AI_{n}_description", value=config['AI'][f'AI_{n}_description'].replace('%%', '%'), placeholder=" ... ", type="text",  className="mb-2"), width=9),
                                    dbc.Col(dcc.Checklist(options=[{'label': f' AI {n}', 'value': 'True'}], value=value_active, id=f'AI_{n}_active'), style={'text-align': 'right', 'font-weight': 'bold'}, width=3)]),
  

                                    dbc.Row(children=[  dbc.Col(dbc.Input(id=f"AI_{n}_source_low", placeholder="...", value=config['AI'][f'AI_{n}_source_low'], inputMode='numeric', type='text'), width=3), # AI source low
                                                        dbc.Col(html.Div('mA', className="ml-2 mt-3"), width=2),       
                                                        dbc.Col(dbc.Input(id=f"AI_{n}_target_low", placeholder="...", value=config['AI'][f'AI_{n}_target_low'], inputMode='numeric', type='text'), width=3), # AI target low
                                                        dbc.Col(html.Div('a.u.', id=f'AI_{n}_units_a',  className="ml-2 mt-3"), width=4)], no_gutters=True, className="mb-2"),
                                    
                                    dbc.Row(children=[  dbc.Col(dbc.Input(id=f"AI_{n}_source_high", placeholder="...", value=config['AI'][f'AI_{n}_source_high'], inputMode='numeric', type='text'), width=3), # AI source high
                                                        dbc.Col(html.Div('mA', className="ml-2 mt-3"), width=2),       
                                                        dbc.Col(dbc.Input(id=f"AI_{n}_target_high", placeholder="...", value=config['AI'][f'AI_{n}_target_high'], inputMode='numeric', type='text'), width=3), # AI terget high
                                                        dbc.Col(html.Div('a.u.', id=f'AI_{n}_units_b', className="ml-2 mt-3"), width=4)], no_gutters=True, className="mb-2"),
                                    
                                    dbc.Row(no_gutters=True, children=[
                                    dbc.Col(html.Div(children=['Analog input', html.Br(), 'mode:'],style={'font-size': '15px', 'text-align':'right'}, className='mr-2 mt-1'), width=5),
                                    dbc.Col(html.Div(dcc.Dropdown(options=[  {'label': '0...20 mA', 'value': '0...20'},
                                                            {'label': '4...20 mA', 'value': '4...20'},
                                                            {'label': '0...10 V', 'value': '0...10'}], 
                                                            value=config['AI'][f'AI_{n}_mode'], # AI mode
                                                            disabled=True,
                                                            style={'min-width': '0', 'margin-left':0}, className="mb-2 mt-2", clearable=False, searchable=False, id=f'AI_{n}_mode')), width=7),]),

                                    dbc.Row(no_gutters=True, children=[
                                    dbc.Col(html.Div(children=['Target units:'],style={'font-size': '15px', 'text-align':'right'}, className='mr-2 mt-2'), width=5),
                                    dbc.Col(dbc.Input(id=f"AI_{n}_units", placeholder="Enter units", value=config['AI'][f'AI_{n}_units'].replace('%%', '%'), type="text"), width=7)]), # AI units
                                ], body=True, style={'min-height': '250px'})])
    
    content_1 = html.Div(children=[ dbc.Row(no_gutters=True, className='mt-3', children=[dbc.Button(className="", id=f'save_AI_settings', children=["SAVE ANALOG INPUT SETTINGS"], color="primary", outline=True,  size="sm", style={'min-width': '100%'})]),
                                    dbc.Row(no_gutters=True, className='mt-3', children=[ai_n_settings_block(1), ai_n_settings_block(2), ai_n_settings_block(3), ai_n_settings_block(4)]),
                                    dbc.Row(no_gutters=True, className='mt-3', children=[ai_n_settings_block(5), ai_n_settings_block(6), ai_n_settings_block(7), ai_n_settings_block(8)])                   
                                ], style={'text-align': 'left'})

    content_ai = [    html.Div(id='hidden-div-1', style={'display':'none'}), # used for callbacks without any output
                        html.Div(id='hidden-div-2', style={'display':'none'}), # used for callbacks without any output
                        html.Div(id='hidden-div-3', style={'display':'none'}),
                        html.Div(id='hidden-div-4', style={'display':'none'}), # used for callbacks without any output
                        html.Div(id='hidden-div-5', style={'display':'none'}),
                        content_1]

    # Content of 'MATRIX'. 
    models_list =[ 
            {'label': 'Not active', 'value': 'empty'},
            {'label': 'Model 1', 'value': 'model_1'},
            {'label': 'Model 2', 'value': 'model_2'},
            {'label': 'Model 3', 'value': 'model_3'},
            {'label': 'Model 4', 'value': 'model_4'},]

    content_mx = html.Div(children=[dbc.Row(children=[
            dbc.Col(html.Div(children=  [
                    html.Div('Inputs', style={'font-weight': 'bold'}),
                    dcc.Dropdown(options=channels_calс_inputs(), value=config['model']['model_input_a'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'60px'}, clearable=False, searchable=False, id='model_input_a'),
                    dcc.Dropdown(options=channels_calс_inputs(), value=config['model']['model_input_b'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'20px'}, clearable=False, searchable=False, id='model_input_b'),
                    dcc.Dropdown(options=channels_calс_inputs(), value=config['model']['model_input_c'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'20px'}, clearable=False, searchable=False, id='model_input_c'),
                    dcc.Dropdown(options=channels_calс_inputs(), value=config['model']['model_input_d'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'20px'}, clearable=False, searchable=False, id='model_input_d'),
                    dcc.Dropdown(options=channels_calс_inputs(), value=config['model']['model_input_e'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'20px'}, clearable=False, searchable=False, id='model_input_e'),
                    dcc.Dropdown(options=channels_calс_inputs(), value=config['model']['model_input_f'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'20px'}, clearable=False, searchable=False, id='model_input_f'),
                    dcc.Dropdown(options=channels_calс_inputs(), value=config['model']['model_input_g'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'20px'}, clearable=False, searchable=False, id='model_input_g'),
                    dcc.Dropdown(options=channels_calс_inputs(), value=config['model']['model_input_h'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'20px'}, clearable=False, searchable=False, id='model_input_h'),
                                        ]), width=3),

            dbc.Col(html.Div(children=[ 
                    dbc.Row(no_gutters=True, children=[
                    dbc.Col(dcc.Dropdown(options=models_list, value='model_1', style={'width': '100%','padding-left':'10px', 'padding-right':'10px', 'font-weight': 'bold'}, clearable=False, searchable=False, id='models_list_a'))]),
                    html.Img(src="./assets/model_0000.jpg", style={'max-width':'100%', 'margin-top':'5px', 'padding-left':'10px', 'padding-right':'10px'})],
                    style={ 'border-right-style': 'double', 'border-right-color': 'Gainsboro', 'border-right-width': '4px',
                            'border-left-style': 'double', 'border-left-color': 'Gainsboro', 'border-left-width': '4px'})),

            dbc.Col(html.Div(children=  [
                html.Div('Outputs', style={'font-weight': 'bold'}),
                dcc.Dropdown(options=channels_output(), value=config['model']['model_output_a'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'60px'}, clearable=False, searchable=False, id='model_output_a'),
                dbc.Row(no_gutters=True, style={'margin-top':'5px'},children=[
                    dbc.Col(dbc.Input(id="AO_1_description_", value=config['AO']['AO_1_description'].replace('%%', '%'), placeholder="Enter channel name ... ", type="text",  className=""), style={'padding-right':'5px'}, width=8),
                    dbc.Col(dbc.Input(id="AO_1_units_", placeholder="Enter units", value=config['AO'][f'AO_1_units'].replace('%%', '%'), type="text"), style={'text-align': 'right', 'font-weight': 'bold'}, width=4)]),

                dcc.Dropdown(options=channels_output(), value=config['model']['model_output_b'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'20px'}, clearable=False, searchable=False, id='model_output_b'),
                dbc.Row(no_gutters=True, style={'margin-top':'5px'},children=[
                    dbc.Col(dbc.Input(id="AO_2_description_", value=config['AO']['AO_2_description'].replace('%%', '%'), placeholder="Enter channel name ... ", type="text",  className=""), style={'padding-right':'5px'}, width=8),
                    dbc.Col(dbc.Input(id="AO_2_units_", placeholder="Enter units", value=config['AO'][f'AO_2_units'].replace('%%', '%'), type="text"), style={'text-align': 'right', 'font-weight': 'bold'}, width=4)]),

                dcc.Dropdown(options=channels_output(), value=config['model']['model_output_c'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'20px'}, clearable=False, searchable=False, id='model_output_c'),
                dbc.Row(no_gutters=True, style={'margin-top':'5px'},children=[
                    dbc.Col(dbc.Input(id="AO_3_description_", value=config['AO']['AO_3_description'].replace('%%', '%'), placeholder="Enter channel name ... ", type="text",  className=""), style={'padding-right':'5px'}, width=8),
                    dbc.Col(dbc.Input(id="AO_3_units_", placeholder="Enter units", value=config['AO'][f'AO_3_units'].replace('%%', '%'), type="text"), style={'text-align': 'right', 'font-weight': 'bold'}, width=4)]),

                dcc.Dropdown(options=channels_output(), value=config['model']['model_output_d'], style={'padding-left':'0px', 'padding-right':'0px', 'font-weight': 'normal', 'margin-top':'20px'}, clearable=False, searchable=False, id='model_output_d'),
                dbc.Row(no_gutters=True, style={'margin-top':'5px'},children=[
                    dbc.Col(dbc.Input(id="AO_4_description_", value=config['AO']['AO_4_description'].replace('%%', '%'), placeholder="Enter channel name ... ", type="text",  className=""), style={'padding-right':'5px'}, width=8),
                    dbc.Col(dbc.Input(id="AO_4_units_", placeholder="Enter units", value=config['AO'][f'AO_4_units'].replace('%%', '%'), type="text"), style={'text-align': 'right', 'font-weight': 'bold'}, width=4)]),
                dbc.Button(className="", id='save_AO_settings_', children=["SAVE ANALOG OUTPUT SETTINGS"], color="primary", outline=True,  size="sm", style={'min-width': '100%', 'margin-top':'20px'})

                    ]), width=3)

            ])], style={'min-height': '300px'}, className='mt-3')
       
    # Content of 'Analog Outputs'.
    def ao_n_settings_block(n):
        # if config['AO'][f'ao_{n}_active']=='True':
        #     value_active = ['True']
        # else:
        #     value_active = []
        return dbc.Col(className='pr-2', children=[   
                    dbc.Card(color='light', outline=True, inverse=False, id=f'AO_{n}_card', children=[

                        dbc.Row(no_gutters=True, children=[
                            dbc.Col(dbc.Input(id=f"AO_{n}_description", value=config['AO'][f'AO_{n}_description'].replace('%%', '%'), placeholder="Enter channel name ... ", type="text", disabled=True,  className="mb-2"), width=9),
                            dbc.Col(html.Div(f'AI {n}', id=f'AO_{n}_active'), style={'text-align': 'right', 'font-weight': 'bold'}, width=3)]),
                            #dbc.Col(dcc.Checklist(options=[{'label': f' AO {n}', 'value': 'True', 'disabled':True}], value=value_active, id=f'AO_{n}_active'), style={'text-align': 'right', 'font-weight': 'bold'}, width=3)]),

                        dbc.Row(children=[  
                            dbc.Col(dbc.Input(id=f"AO_{n}_source_low", placeholder="...", value=config['AO'][f'AO_{n}_target_low'], inputMode='numeric', type='text'), width=3), # AO sourse low
                            dbc.Col(html.Div('a.u.', id=f'AO_{n}_units_a',  className="ml-2 mt-3"), width=4),

                            dbc.Col(dbc.Input(id=f"AO_{n}_target_low", placeholder="...", value=config['AO'][f'AO_{n}_source_low'], inputMode='numeric', type='text'), width=3), # AO target low
                            dbc.Col(html.Div('mA', className="ml-2 mt-3"), width=2)], no_gutters=True, className="mb-2"),  
                                            
                        dbc.Row(children=[  
                            dbc.Col(dbc.Input(id=f"AO_{n}_source_high", placeholder="...", value=config['AO'][f'AO_{n}_target_high'], inputMode='numeric', type='text'), width=3), # AO sourse high
                            dbc.Col(html.Div('a.u.', id=f'AO_{n}_units_b', className="ml-2 mt-3"), width=4),
                                            
                            dbc.Col(dbc.Input(id=f"AO_{n}_target_high", placeholder="...", value=config['AO'][f'AO_{n}_source_high'], inputMode='numeric', type='text'), width=3), # AO target high
                            dbc.Col(html.Div('mA', className="ml-2 mt-3"), width=2)], no_gutters=True, className="mb-2"),
                        
                        dbc.Row(no_gutters=True, children=[
                            dbc.Col(html.Div(children=['Analog output', html.Br(), 'mode:'],style={'font-size': '15px', 'text-align':'right'}, className='mr-2 mt-1'), width=5),
                            dbc.Col(html.Div(dcc.Dropdown(options=[  {'label': '0...20 mA', 'value': '0...20'},
                                                {'label': '4...20 mA', 'value': '4...20'},
                                                {'label': '0...10 V', 'value': '0...10'}], 
                                                value=config['AO'][f'AO_{n}_mode'],                                                                                                   # AO mode
                                                disabled=True,                                                                                                            
                                                style={'min-width': '0', 'margin-left':0}, className="mb-2 mt-2", clearable=False, searchable=False, id=f'AO_{n}_mode')), width=7),]),

                        # dbc.Row(no_gutters=True, children=[
                        #     dbc.Col(html.Div(children=['Target units:'],style={'font-size': '15px', 'text-align':'right'}, className='mr-2 mt-2'), width=5),
                        #     dbc.Col(dbc.Input(id=f"AO_{n}_units", placeholder="Enter units", value=config['AO'][f'AO_{n}_units'].replace('%%', '%'), type="text"), width=7)]),        # AO units
                    ], body=True, style={'min-height': '250px'})])
                                
    content = html.Div(children=[   dbc.Row(no_gutters=True, className='mt-3', children=[ao_n_settings_block(1), ao_n_settings_block(2), ao_n_settings_block(3), ao_n_settings_block(4)]),
                                    dbc.Row(no_gutters=True, className='mt-3', children=[dbc.Button(className="", id=f'save_AO_settings', children=["SAVE ANALOG OUTPUT SETTINGS"], color="primary", outline=True,  size="sm", style={'min-width': '100%'})]),             
                                ], style={'text-align': 'left'})

    content_ao = html.Div(children=[content], style={'min-height': '300px'}, className='mt-3')
 
    # Content of 'Date and Time'
    dropdown_zime_zone =  dcc.Dropdown(
        options=[{'label': f"{i}", 'value': f"{i}"} for i in pytz.all_timezones],
        value=config['db_browser']['local_time_zone'], clearable=False, id = 'dropdown_zime_zone') 
    content_date_time = html.Div(dropdown_zime_zone, style={'min-height': '300px', 'text-align':'left'}, className='mt-3')

    # Content of 'General Info'
    content_info = html.Div('Contennt of General Information', id='cpu_temp')


    tab_settings_label_style = {"color": "#007bff", "cursor": "pointer", "font-size": "large"} 
    settings_content = dbc.Card(
        dbc.CardBody(dbc.Tabs(style={'margin-top':'0px'}, id='setting_tabs', children=[
                                    dbc.Tab(content_ai, label="Analog Inputs", tab_id='tab_ai', label_style=tab_settings_label_style),
                                    dbc.Tab(content_mx, label="MATRIX", tab_id='tab_mx', label_style=tab_settings_label_style),
                                    dbc.Tab(content_ao, label="Analog Outputs", tab_id='tab_ao', label_style=tab_settings_label_style),
                                    dbc.Tab(content_date_time, label="Date and Time", tab_id='tab_dt', label_style=tab_settings_label_style, disabled=False),
                                    dbc.Tab(content_info, label='General information', tab_id='tab_info', label_style=tab_settings_label_style, disabled=False)
                                ])), className="mt-3", style={'padding-top':'0px'})

    return settings_content 


#---------------------------------------------
app = dash.Dash(__name__)
app.title='Matrix'
server = app.server #### used for Gunicorn / run from command line: gunicorn -w 1 --threads 9 -b 0.0.0.0:5002 dash_main:server / number of threads is = number of CPU * 2 + 1

def serve_layout():

    tab_label_style = {"color": "#00AEF9", "cursor": "pointer", "font-size": "large"}   
    return html.Div(html.Div(className="pl-2 pr-2 pt-2 pb-2", children=[
        html.Div(children=[dbc.Row(justify="between", align="center",className="pt-2 ml-0 mr-0", style={'background-color':'LightSkyBlue', 'border-radius':'5px'}, children=[
                                dbc.Col(children=[html.H6(html.Div(children = ["L O G O"], className="pt-2 pb-2 pl-2 pr-2", style={'text-align': 'left'}), style={'text-align': 'left'})], width=2),
                                dbc.Col(html.Div("One of three columns", className="mb-2", id='top_bar', tabIndex='-1', style={'outline': 'none'}), width=4),
                                dbc.Col(children=[html.H6(html.Div(id="date_time_notification", children = ["Date and Time"], className="pt-2 pb-2 pl-2 pr-2", style={'text-align': 'left'}))], style={ 'max-width': '170px', 'min-width': '170px'})
                                ])], className="mb-2 ml-0 mr-0"),
        dbc.Tabs(id='main_tabs', active_tab='tab-0' , children=[   
            dbc.Tab(tab_id="tab-0", label='Cockpit', children=[tab0_content()], label_style=tab_label_style), 
            #dbc.Tab(tab_id="tab-1", label='Level 1', children=[tab1_content()], label_style=tab_label_style),
            dbc.Tab(tab_id="db_browser", label='Data browser', children=[db_browser_content()], label_style=tab_label_style),
            #dbc.Tab(tab_id="tab-3", label='Level 3', children=[''], label_style=tab_label_style),
            #dbc.Tab(tab_id="tab-4", label='Level 4', children=[''], label_style=tab_label_style),
            #dbc.Tab(tab_id="tab-5", label='Level 5', children=[''], label_style=tab_label_style),
            dbc.Tab(tab_id="tab-settings", label='Settings', children=[settings_content()], label_style=tab_label_style),
            dcc.Interval(id='interval-component_60', interval=60*1000, n_intervals=0),  # Inreval triggers every 60 seconds. Used for the date and time notification
            dcc.Interval(id='interval-component_20', interval=20*1000, n_intervals=0),  # Inreval triggers every 20 seconds
            dcc.Interval(id='interval-component_10', interval=10*1000, n_intervals=0),  # Inreval triggers every 10 seconds
            dcc.Interval(id='interval-component_5', interval=5*1000, n_intervals=0),    # Inreval triggers every 5 seconds
            dcc.Interval(id='interval-component_1', interval=1*1000, n_intervals=0)     # Inreval triggers every 1 second
                ])], style={"width": "1280px", 'display': 'inline-block'}), style={"width": "100%", 'text-align': 'center'})

app.layout = serve_layout
#### Heads up! You need to write app.layout = serve_layout not app.layout = serve_layout(). That is, define app.layout to the actual function instance.



#-----------CALLBACKS---------------------  
                         
#---Status Bar--------------------------------------------------------
#----------updates date and time notification in status bar------------
@app.callback(  Output("date_time_notification", "children"), 
                [Input('interval-component_1', 'n_intervals')]) 
def update_date_time(n):
    global config
    current_time = timezone('UTC').localize(datetime.datetime.utcnow())
    current_time = current_time.astimezone(timezone(config['db_browser']['local_time_zone']))
    return [dbc.Row(dbc.Col(current_time.strftime("%d %B %Y"), width=12)),
            dbc.Row([   dbc.Col(current_time.strftime("%H:%M:%S"), width=5), dbc.Col(current_time.strftime("%Z"), width=7)], justify="start")]


#---Cockpit------------------------------------------------------
@app.callback(  Output('slider_a', 'value'),
                [Input('slider_b', 'value')]) 
def set_slider_value_a(value_b):
    return value_b


#----------updates last values in Cockpit-------------------------
@app.callback(  [Output('last_value_to_indicate_a', 'children'), Output('last_value_to_indicate_b', 'children'), Output('last_value_to_indicate_c', 'children'), Output('last_value_to_indicate_d', 'children')],
                [Input('interval-component_1', 'n_intervals')],
                [State('channel_to_monitor_a', 'value'), State('channel_to_monitor_b', 'value'), State('channel_to_monitor_c', 'value'), State('channel_to_monitor_d', 'value')]) 
def update_last_values(n, channel_to_monitor_a, channel_to_monitor_b, channel_to_monitor_c, channel_to_monitor_d):
    # last_average_value = str(round((np.average(df_append[1].values)),2))
    url = 'http://localhost:5001/get_last_measurement'
    x = requests.get(url)
    
    last_values = x.json()
    values_names = ['input_1', 'input_2', 'input_3', 'input_4', 'input_5', 'input_6', 'input_7', 'input_8',
                    'in_1_calculated', 'in_2_calculated', 'in_3_calculated', 'in_4_calculated', 'in_5_calculated', 'in_6_calculated', 'in_7_calculated', 'in_8_calculated',
                    'output_1', 'output_2', 'output_3', 'output_4']
    
    units_list = {  'input_1':'mA', 'input_2':'mA', 'input_3':'mA', 'input_4':'mA', 'input_5':'mA', 'input_6':'mA', 'input_7':'mA', 'input_8':'mA',
                    'in_1_calculated': config['AI']['ai_1_units'], 'in_2_calculated': config['AI']['ai_2_units'], 'in_3_calculated': config['AI']['ai_3_units'], 'in_4_calculated': config['AI']['ai_4_units'],
                    'in_5_calculated': config['AI']['ai_5_units'], 'in_6_calculated': config['AI']['ai_6_units'], 'in_7_calculated': config['AI']['ai_7_units'], 'in_8_calculated': config['AI']['ai_8_units'],
                    'output_1':config['AO']['ao_1_units'], 'output_2':config['AO']['ao_2_units'], 'output_3':config['AO']['ao_3_units'], 'output_4':config['AO']['ao_4_units']}
   
    if last_values[values_names.index(config['cockpit']['data_to_show_a'])] != 'NULL':
        units_a = units_list[config['cockpit']['data_to_show_a']]
        last_value_a = dbc.Row(no_gutters=True, children=[
            dbc.Col('%.2f' % round(last_values[values_names.index(config['cockpit']['data_to_show_a'])], 2), width=9),
            dbc.Col(units_a, width=3, style={'font-size':'large', 'text-align':'left'} )
            ])
    else: last_value_a = 'No data'
    
    
    if config['cockpit']['data_to_show_b'] != 'empty' and last_values[values_names.index(config['cockpit']['data_to_show_b'])] != 'NULL':
        units_b = units_list[config['cockpit']['data_to_show_b']]
        last_value_b = dbc.Row(no_gutters=True, children=[
            dbc.Col('%.2f' % round(last_values[values_names.index(config['cockpit']['data_to_show_b'])], 2), width=9),
            dbc.Col(units_b, width=3, style={'font-size':'large', 'text-align':'left'} )
            ])
    else: last_value_b = '--,--'

    if config['cockpit']['data_to_show_c'] != 'empty' and last_values[values_names.index(config['cockpit']['data_to_show_c'])] != 'NULL':
        units_c = units_list[config['cockpit']['data_to_show_c']]
        last_value_c = dbc.Row(no_gutters=True, children=[
            dbc.Col('%.2f' % round(last_values[values_names.index(config['cockpit']['data_to_show_c'])], 2), width=9),
            dbc.Col(units_c, width=3, style={'font-size':'large', 'text-align':'left'} )
            ])
    else: last_value_c = '--,--'

    if config['cockpit']['data_to_show_d'] != 'empty' and last_values[values_names.index(config['cockpit']['data_to_show_d'])] != 'NULL':
        units_d = units_list[config['cockpit']['data_to_show_d']]
        last_value_d = dbc.Row(no_gutters=True, children=[
            dbc.Col('%.2f' % round(last_values[values_names.index(config['cockpit']['data_to_show_d'])], 2), width=9),
            dbc.Col(units_d, width=3, style={'font-size':'large', 'text-align':'left'} )
            ])
    else: last_value_d = '--,--'


    return [last_value_a, last_value_b, last_value_c, last_value_d]



#--A------update live chart A in Cockpit, Store + client side calback-------

@app.callback(  Output('store_to_append_a_graph', 'data'),
                [Input('interval-component_60', 'n_intervals')],
                [State('main_tabs', 'active_tab'), State('state_a_graph', 'data')]) 
def update_graph_live(n, active_tab, state_a_graph):  
    
 
    if active_tab == 'tab-0':

        #global time_of_last_point_in_chart_a_graph
        global data_to_show_a_graph, period_to_monitor_a_graph

        

        dict_of_periods =        {'1_hour':1, '3_hours':3, '12_hours':12, '24_hours':24, '3_days':72, '7_days':168}         # hours
        dict_of_smapling_times = {'1_hour':1, '3_hours':3, '12_hours':10, '24_hours':25, '3_days':60, '7_days':160}         # seconds

        hours = int(dict_of_periods[config['cockpit']['period_to_monitor_a_graph']])
        period = dict_of_smapling_times[config['cockpit']['period_to_monitor_a_graph']]


        logging.info(state_a_graph)

        current_time_a = datetime.datetime.utcnow()
        if state_a_graph == None:
            time_of_last_point_in_chart_a_graph = current_time_a - datetime.timedelta(hours=hours)
        else: time_of_last_point_in_chart_a_graph = (datetime.datetime.strptime(state_a_graph[1], '%Y-%m-%d %H:%M:%S'))  


        
        if config['cockpit']['data_to_show_a_graph'] != data_to_show_a_graph or config['cockpit']['period_to_monitor_a_graph'] != period_to_monitor_a_graph or state_a_graph == None:
            lock.acquire()
            print ('updating live chart a...')
            df_to_append_a = db_reader_b.get_data_generic__('date_time_utc', [config['cockpit']['data_to_show_a_graph']], (current_time_a - datetime.timedelta(hours=hours)).strftime("%Y_%m_%d %H:%M:%S"), current_time_a.strftime("%Y_%m_%d %H:%M:%S"), fetch_every_n_sec = period)
            lock.release()
            data_to_show_a_graph = config['cockpit']['data_to_show_a_graph']
            period_to_monitor_a_graph = config['cockpit']['period_to_monitor_a_graph']
            new_data_falg = 'True'
            
            
        else: 
            lock.acquire()
            print ('updating live chart a...')
            df_to_append_a = db_reader_b.get_data_generic__('date_time_utc', [config['cockpit']['data_to_show_a_graph']], (time_of_last_point_in_chart_a_graph + datetime.timedelta(seconds=1)).strftime("%Y_%m_%d %H:%M:%S"), current_time_a.strftime("%Y_%m_%d %H:%M:%S"), fetch_every_n_sec = period)
            lock.release()
            new_data_falg = 'False'
            
            


        # time_of_last_point_in_chart_a_graph = current_time_a

        if df_to_append_a.empty:
            fig = go.Figure(data=go.Scattergl(mode='lines+markers', line=dict(color='#1E90FF', width=4, dash='dot'), x=[], y=[]))
        else:
            fig = go.Figure(data=go.Scattergl(mode='lines+markers', line=dict(color='#1E90FF', width=4, dash='dot'), x=df_to_append_a[0], y=df_to_append_a[1]))
        

        datetime_list_of_strings = []
        for item in fig['data'][0]['x']:
            datetime_list_of_strings.append(item.strftime("%Y-%m-%d %H:%M:%S"))

        logging.info([ datetime_list_of_strings, fig['data'][0]['y'], new_data_falg ])
        return [ datetime_list_of_strings, fig['data'][0]['y'], new_data_falg ]

    else: 
        new_data_falg = 'False'
        fig = go.Figure(data=go.Scattergl(mode='lines+markers', line=dict(color='#1E90FF', width=4, dash='dot'), x=[], y=[]))
        datetime_list_of_strings = []
        for item in fig['data'][0]['x']:
            datetime_list_of_strings.append(item.strftime("%Y-%m-%d %H:%M:%S"))
        
        logging.info([ datetime_list_of_strings, fig['data'][0]['y'], new_data_falg ])
        return  [ datetime_list_of_strings, fig['data'][0]['y'], new_data_falg ]

#--B--- clientside -----  

app.clientside_callback(
    """
    function(data_to_append, data_in_memory) { 


        if (data_to_append[2] === 'True' || data_in_memory === undefined) {
            data_x = data_to_append[0];
            data_y = data_to_append[1];
        } else {
            data_x = data_in_memory[0].concat(data_to_append[0]);
            data_x = data_x.slice(data_to_append[0].length, data_x.length)

            data_y = data_in_memory[1].concat(data_to_append[1]);
            data_y = data_y.slice(data_to_append[0].length, data_y.length)
        } ;


        return [data_x, data_y, data_to_append[2]]
    }

    """,
    Output('memory_a_graph', 'data'),
    [Input('store_to_append_a_graph', 'data')],
    [State('memory_a_graph', 'data')]

)

#--C--- clientside -----  

app.clientside_callback(
    """
    function(data, figure) { 
 
        data_fig = figure['data'];
        data_fig[0]['x'] = data[0];
        data_fig[0]['y'] = data[1];

        first_datetime = data[0][0];
        last_datetime = data[0][data[0].length - 1];
        state_a_graph = [first_datetime, last_datetime];
                
        console.log(state_a_graph); 

        fig = {
            'data': data_fig,
            'layout': figure['layout']
        }
        
        return [fig, state_a_graph]
    }
    """,
    [Output('live-chart-a', "figure"), Output('state_a_graph', 'data')],
    [Input('memory_a_graph', 'data')],
    [State('live-chart-a', 'figure')]

)












#----------updates live charts in Cockpit-------------------------

# @app.callback(  [Output("live-chart-a", "figure")],
#                 [Input('interval-component_20', 'n_intervals')],            
#                 [State('main_tabs', 'active_tab'), State('live-chart-a', 'figure')]) 
# def update_graph_live(n, active_tab, figure_state):                         
#     if active_tab == 'tab-0':
        
#         global time_of_last_point_in_chart_a_graph
#         global df_a_graph
#         global data_to_show_a_graph, period_to_monitor_a_graph

#         current_time_a = datetime.datetime.utcnow()

#         dict_of_periods =        {'1_hour':1, '3_hours':3, '12_hours':12, '24_hours':24, '3_days':72, '7_days':168}         # hours
#         dict_of_smapling_times = {'1_hour':1, '3_hours':3, '12_hours':10, '24_hours':25, '3_days':60, '7_days':160}         # seconds

#         hours = int(dict_of_periods[config['cockpit']['period_to_monitor_a_graph']])
#         period = dict_of_smapling_times[config['cockpit']['period_to_monitor_a_graph']]
        
#         if config['cockpit']['data_to_show_a_graph'] != data_to_show_a_graph or config['cockpit']['period_to_monitor_a_graph'] != period_to_monitor_a_graph:
#             df_a_graph = df_a_graph[df_a_graph.shape[0]:] 
#             lock.acquire()
#             print ('updating live chart a...')
#             df_append_a = db_reader_b.get_data_generic__('date_time_utc', [config['cockpit']['data_to_show_a_graph']], (current_time_a - datetime.timedelta(hours=hours)).strftime("%Y_%m_%d %H:%M:%S"), current_time_a.strftime("%Y_%m_%d %H:%M:%S"), fetch_every_n_sec = period)
#             lock.release()
#             data_to_show_a_graph = config['cockpit']['data_to_show_a_graph']
#             period_to_monitor_a_graph = config['cockpit']['period_to_monitor_a_graph']
#         else: 
#             lock.acquire()
#             print ('updating live chart a...')
#             df_append_a = db_reader_b.get_data_generic__('date_time_utc', [config['cockpit']['data_to_show_a_graph']], (time_of_last_point_in_chart_a_graph + datetime.timedelta(seconds=1)).strftime("%Y_%m_%d %H:%M:%S"), current_time_a.strftime("%Y_%m_%d %H:%M:%S"), fetch_every_n_sec = period)
#             lock.release()
        
#         df_append = df_append_a
#         df_a_graph = df_a_graph.append(df_append, ignore_index=True) 
        
#         time_filter_mask = df_a_graph[0] > datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
#         df_a_graph = df_a_graph[time_filter_mask]


#         df_utc = []
#         for i in df_a_graph.index:
#             df_utc.append(timezone('UTC').localize(df_a_graph[0][i]))  
#         df_local_time = []
#         for i in df_utc:
#             df_local_time.append(i.astimezone(timezone(config['db_browser']['local_time_zone'])))

        
#         descr_list = {  'empty':'...',
#                         'input_1':'Raw input', 'input_2':'Raw input', 'input_3':'Raw input', 'input_4':'Raw input', 'input_5':'Raw input', 'input_6':'Raw input', 'input_7':'Raw input', 'input_8':'Raw input',
#                         'in_1_calculated': config['AI']['ai_1_description'], 'in_2_calculated': config['AI']['ai_2_description'], 'in_3_calculated': config['AI']['ai_3_description'], 'in_4_calculated': config['AI']['ai_4_description'],
#                         'in_5_calculated': config['AI']['ai_5_description'], 'in_6_calculated': config['AI']['ai_6_description'], 'in_7_calculated': config['AI']['ai_7_description'], 'in_8_calculated': config['AI']['ai_8_description'],
#                         'output_1':config['AO']['ao_1_description'], 'output_2':config['AO']['ao_2_description'], 'output_3':config['AO']['ao_3_description'], 'output_4':config['AO']['ao_4_description']}
        
#         units_list = {  'empty':'...',
#                         'input_1':'mA', 'input_2':'mA', 'input_3':'mA', 'input_4':'mA', 'input_5':'mA', 'input_6':'mA', 'input_7':'mA', 'input_8':'mA',
#                         'in_1_calculated': config['AI']['ai_1_units'], 'in_2_calculated': config['AI']['ai_2_units'], 'in_3_calculated': config['AI']['ai_3_units'], 'in_4_calculated': config['AI']['ai_4_units'],
#                         'in_5_calculated': config['AI']['ai_5_units'], 'in_6_calculated': config['AI']['ai_6_units'], 'in_7_calculated': config['AI']['ai_7_units'], 'in_8_calculated': config['AI']['ai_8_units'],
#                         'output_1':config['AO']['ao_1_units'], 'output_2':config['AO']['ao_2_units'], 'output_3':config['AO']['ao_3_units'], 'output_4':config['AO']['ao_4_units']}

#         yaxix_name = descr_list[config['cockpit']['data_to_show_a_graph']] + ', ' + units_list[config['cockpit']['data_to_show_a_graph']]
        
#         time_of_last_point_in_chart_a_graph = current_time_a

#         fig = go.Figure(data=go.Scattergl(mode='lines+markers', line=dict(color='#1E90FF', width=4, dash='dot'), x=df_local_time, y=df_a_graph[1]))
#         fig.update_layout(margin=dict(t=50))
#         fig['layout']['xaxis'].update(title='Date and Time', autorange=True)
#         fig['layout']['yaxis'].update(title=yaxix_name, autorange=True)

#         if config['cockpit']['data_to_show_a_graph'] == 'empty':
#             fig = go.Figure(data=go.Scattergl(mode='lines+markers', line=dict(color='#1E90FF', width=4, dash='dot'), x=[0], y=[0]))
#             fig.update_layout(margin=dict(t=50))
#             fig['layout']['xaxis'].update(title='Not active', autorange=True)
#             fig['layout']['yaxis'].update(title='Not active', autorange=True)
#         else: pass


#         return [fig]
#     else:
#         return [figure_state]



# @app.callback(  [Output("live-chart-b", "figure")],
#                 [Input('interval-component_20', 'n_intervals')],            
#                 [State('main_tabs', 'active_tab'), State('live-chart-b', 'figure')]) 
# def update_graph_live_b(n, active_tab, figure_state):                         
#     if active_tab == 'tab-0':
        
#         global time_of_last_point_in_chart_b_graph
#         global df_b_graph
#         global data_to_show_b_graph, period_to_monitor_b_graph

#         current_time_b = datetime.datetime.utcnow()

#         dict_of_periods =        {'1_hour':1, '3_hours':3, '12_hours':12, '24_hours':24, '3_days':72, '7_days':168}         # hours
#         dict_of_smapling_times = {'1_hour':1, '3_hours':3, '12_hours':10, '24_hours':25, '3_days':60, '7_days':160}         # seconds

#         hours = int(dict_of_periods[config['cockpit']['period_to_monitor_b_graph']])
#         period = dict_of_smapling_times[config['cockpit']['period_to_monitor_b_graph']]
        
#         if config['cockpit']['data_to_show_b_graph'] != data_to_show_b_graph or config['cockpit']['period_to_monitor_b_graph'] != period_to_monitor_b_graph:
#             df_b_graph = df_b_graph[df_b_graph.shape[0]:] 
#             lock.acquire()
#             print ('updating live chart b...')
#             df_append_a = db_reader_b.get_data_generic__('date_time_utc', [config['cockpit']['data_to_show_b_graph']], (current_time_b - datetime.timedelta(hours=hours)).strftime("%Y_%m_%d %H:%M:%S"), current_time_b.strftime("%Y_%m_%d %H:%M:%S"), fetch_every_n_sec = period)
#             lock.release()
#             data_to_show_b_graph = config['cockpit']['data_to_show_b_graph']
#             period_to_monitor_b_graph = config['cockpit']['period_to_monitor_b_graph']
#         else: 
#             lock.acquire()
#             print ('updating live chart b...')
#             df_append_a = db_reader_b.get_data_generic__('date_time_utc', [config['cockpit']['data_to_show_b_graph']], (time_of_last_point_in_chart_b_graph + datetime.timedelta(seconds=1)).strftime("%Y_%m_%d %H:%M:%S"), current_time_b.strftime("%Y_%m_%d %H:%M:%S"), fetch_every_n_sec = period)
#             lock.release()
        
#         df_append = df_append_a
#         df_b_graph = df_b_graph.append(df_append, ignore_index=True) 
        
#         time_filter_mask = df_b_graph[0] > datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
#         df_b_graph = df_b_graph[time_filter_mask]


#         df_utc = []
#         for i in df_b_graph.index:
#             df_utc.append(timezone('UTC').localize(df_b_graph[0][i]))  
#         df_local_time = []
#         for i in df_utc:
#             df_local_time.append(i.astimezone(timezone(config['db_browser']['local_time_zone'])))

        
#         descr_list = {  'empty':'...',
#                         'input_1':'Raw input', 'input_2':'Raw input', 'input_3':'Raw input', 'input_4':'Raw input', 'input_5':'Raw input', 'input_6':'Raw input', 'input_7':'Raw input', 'input_8':'Raw input',
#                         'in_1_calculated': config['AI']['ai_1_description'], 'in_2_calculated': config['AI']['ai_2_description'], 'in_3_calculated': config['AI']['ai_3_description'], 'in_4_calculated': config['AI']['ai_4_description'],
#                         'in_5_calculated': config['AI']['ai_5_description'], 'in_6_calculated': config['AI']['ai_6_description'], 'in_7_calculated': config['AI']['ai_7_description'], 'in_8_calculated': config['AI']['ai_8_description'],
#                         'output_1':config['AO']['ao_1_description'], 'output_2':config['AO']['ao_2_description'], 'output_3':config['AO']['ao_3_description'], 'output_4':config['AO']['ao_4_description']}
        
#         units_list = {  'empty':'...',
#                         'input_1':'mA', 'input_2':'mA', 'input_3':'mA', 'input_4':'mA', 'input_5':'mA', 'input_6':'mA', 'input_7':'mA', 'input_8':'mA',
#                         'in_1_calculated': config['AI']['ai_1_units'], 'in_2_calculated': config['AI']['ai_2_units'], 'in_3_calculated': config['AI']['ai_3_units'], 'in_4_calculated': config['AI']['ai_4_units'],
#                         'in_5_calculated': config['AI']['ai_5_units'], 'in_6_calculated': config['AI']['ai_6_units'], 'in_7_calculated': config['AI']['ai_7_units'], 'in_8_calculated': config['AI']['ai_8_units'],
#                         'output_1':config['AO']['ao_1_units'], 'output_2':config['AO']['ao_2_units'], 'output_3':config['AO']['ao_3_units'], 'output_4':config['AO']['ao_4_units']}

#         yaxix_name = descr_list[config['cockpit']['data_to_show_b_graph']] + ', ' + units_list[config['cockpit']['data_to_show_b_graph']]
        
#         time_of_last_point_in_chart_b_graph = current_time_b
#         fig = go.Figure(data=go.Scattergl(mode='lines+markers', line=dict(color='#1E90FF', width=4, dash='dot'), x=df_local_time, y=df_b_graph[1]))
#         fig.update_layout(margin=dict(t=50))
#         fig['layout']['xaxis'].update(title='Date and Time', autorange=True)
#         fig['layout']['yaxis'].update(title=yaxix_name, autorange=True)

#         if config['cockpit']['data_to_show_b_graph'] == 'empty':
#             fig = go.Figure(data=go.Scattergl(mode='lines+markers', line=dict(color='#1E90FF', width=4, dash='dot'), x=[0], y=[0]))
#             fig.update_layout(margin=dict(t=50))
#             fig['layout']['xaxis'].update(title='Not active', autorange=True)
#             fig['layout']['yaxis'].update(title='Not active', autorange=True)
#         else: pass


#         return [fig]
#     else:
#         return [figure_state]





#--- Cockpit Settings-------------------------------------------
@app.callback(  Output('hidden-div-4', 'children'),
                [Input('channel_to_monitor_a', 'value'), Input('channel_to_monitor_b', 'value'), Input('channel_to_monitor_c', 'value'), Input('channel_to_monitor_d', 'value'),
                Input('channel_to_monitor_a_graph', 'value'), Input('channel_to_monitor_b_graph', 'value'),
                Input('period_to_monitor', 'value')])   
def cockpit_settings(channel_to_monitor_a, channel_to_monitor_b, channel_to_monitor_c, channel_to_monitor_d,
                       channel_to_monitor_a_graph, channel_to_monitor_b_graph,
                       period_to_monitor):
    config['cockpit']['data_to_show_a'] = channel_to_monitor_a
    config['cockpit']['data_to_show_b'] = channel_to_monitor_b
    config['cockpit']['data_to_show_c'] = channel_to_monitor_c
    config['cockpit']['data_to_show_d'] = channel_to_monitor_d
    config['cockpit']['data_to_show_a_graph'] = channel_to_monitor_a_graph
    config['cockpit']['data_to_show_b_graph'] = channel_to_monitor_b_graph
    config['cockpit']['period_to_monitor_a_graph'] = period_to_monitor
    config['cockpit']['period_to_monitor_b_graph'] = period_to_monitor
    write_config()


# Browser-------------------------------------
#--------This loads day chart in the db_browser

@app.callback(  [Output("day_chart", "figure"), Output('download_selected_data', 'href'), Output('download_selected_data', 'children')], 
                [Input("table_list_of_days", "selected_cells"), Input('button_load_curves', 'n_clicks')], 
                [State("table_list_of_days", "data"), State('days_and_points_in_chart', 'value'), State('lines_markers', 'value'),
                State('channel_to_show_a', 'value'), State('channel_to_show_b', 'value'), State('channel_to_show_c', 'value'), State('channel_to_show_d', 'value'),
                State('channel_to_show_a', 'options')])
def current_cell(   selected_cell, button_load_curves_input, data, days_and_points_in_chart_state, lines_markers_state,
                    channel_to_show_a_state, channel_to_show_b_state, channel_to_show_c_state, channel_to_show_d_state,
                    channel_to_show_a_options):
    
    
    
    dropdowns_list = [channel_to_show_a_state, channel_to_show_b_state, channel_to_show_c_state, channel_to_show_d_state]
    # Remove all 'empty' elements
    l = []
    list_of_channels = []
    channel_index = 0
    for elem in dropdowns_list:
        if elem != 'empty':
            l.append(elem)
            list_of_channels.append(channel_index)
        channel_index = channel_index + 1
    list_of_inputs_state = l
  
 
    current_cell = data[selected_cell[0]['row']]['tabels_in_db'] # current cell as string formated as "2020_01_21"
    date_in_cell = datetime.datetime.strptime(current_cell, '%Y_%m_%d')
    days_in_chart_state = days_and_points_in_chart_state.split('_')[0]
    fetch_sec_state = days_and_points_in_chart_state.split('_')[1]
    
    if days_in_chart_state=='one':
        start_time = date_in_cell - datetime.timedelta(hours=12)
        end_time = date_in_cell + datetime.timedelta(hours=36)
    else:
        start_time = date_in_cell - datetime.timedelta(hours=60)
        end_time = date_in_cell + datetime.timedelta(hours=36)

    #-----------------
    lock.acquire()
    print ('updating day chart in browser...')
    try: 
        df_bbb = db_reader_a.get_data_generic__('date_time_utc', list_of_inputs_state, start_time.strftime('%Y_%m_%d %H:%M:%S'), end_time.strftime('%Y_%m_%d %H:%M:%S'), fetch_every_n_sec = fetch_sec_state) # df_b is list of pandas frames
        lock.release()
    except:
        lock.release()

    df_1 = [df_bbb[[0,1]]]
    try:df_2 = [df_bbb[[0,2]].rename(columns={2:1})] 
    except: df_2 = []
    try: df_3 = [df_bbb[[0,3]].rename(columns={3:1})] 
    except: df_3 = []
    try: df_4 = [df_bbb[[0,4]].rename(columns={4:1})] 
    except: df_4 = []  

    df_b = df_1 + df_2 + df_3 + df_4
    #----------------- 

    df = df_b[0]
    df_utc = []
    for i in df.index:
        df_utc.append(timezone('UTC').localize(df[0][i]))  
    df_local_time = []
    for i in df_utc:
        df_local_time.append(i.astimezone(timezone(config['db_browser']['local_time_zone'])))
    
    fig = go.Figure()
    fig['layout']['xaxis'].update(title='Time', autorange=True)
    fig['layout']['yaxis'].update(title='Value', range=[0, 25], autorange=True)
    fig['layout'].update(autosize = True)
    
    data = {'Date and Time': df_local_time} 
    df_merged = pd.DataFrame(data) 
    trace_colors = ['#119DFF', '#EA11FF', '#FF7311', '#46cc37']    #26FF11
 
    yaxis_names = []
    for i in range (0, 4):
        try:
            yaxis_names.append(list_of_inputs_state[i])
        except:
            yaxis_names.append('***')  
    yaxis_labels = []
    for j in yaxis_names:
        if j == '***':
            yaxis_labels.append('***')
        else:
            for i in channel_to_show_a_options:
                if i['value'] == j:
                    yaxis_labels.append(i['label'])
                else:
                    pass

    yaxis_labels = [label.replace('Analog Input','AI')  for label in yaxis_labels]
    yaxis_labels = [label.replace('Analog Output','AO')  for label in yaxis_labels]
    
    ai_1_units = config['AI']['ai_1_units']
    ai_2_units = config['AI']['ai_2_units']
    ai_3_units = config['AI']['ai_3_units']
    ai_4_units = config['AI']['ai_4_units']
    ai_5_units = config['AI']['ai_5_units']
    ai_6_units = config['AI']['ai_6_units']
    ai_7_units = config['AI']['ai_7_units']
    ai_8_units = config['AI']['ai_8_units']
    ao_1_units = config['AO']['ao_1_units']
    ao_2_units = config['AO']['ao_2_units']
    ao_3_units = config['AO']['ao_3_units']
    ao_4_units = config['AO']['ao_4_units']

    units_id = ['in_1_calculated', 'in_2_calculated', 'in_3_calculated', 'in_4_calculated', 'in_5_calculated', 'in_6_calculated', 'in_7_calculated', 'in_1_calculated', 'output_1', 'output_2', 'output_3', 'output_4']
    units_list = [ai_1_units, ai_2_units, ai_3_units, ai_4_units, ai_5_units, ai_6_units, ai_7_units, ai_8_units, ao_1_units, ao_2_units, ao_3_units, ao_4_units ]

    yaxis_units = []
    for item in yaxis_names:
        try: yaxis_units.append(units_list[units_id.index(item)])
        except: yaxis_units.append('...')

    k = 0
    for i in df_b:     
        fig.add_trace(go.Scattergl(line=dict(color=trace_colors[list_of_channels[k]]), mode=lines_markers_state, yaxis=f"y{k+1}", name=list_of_inputs_state[k], x=df_local_time, y=i[1]))
        df_merged[yaxis_labels[k]] = i[1].reset_index(drop=True)
        k = k +1
    # fig.add_trace(go.Scatter(x=[date_in_cell, date_in_cell], y=[0, 22], yaxis='y1', mode="lines", showlegend = False, line=dict(color='royalblue', width=2, dash='dot')))
    # fig.add_trace(go.Scatter(x=[date_in_cell + datetime.timedelta(hours=24), date_in_cell + datetime.timedelta(hours=24)], y=[0, 22], yaxis='y1', mode="lines", showlegend = False, line=dict(color='royalblue', width=2, dash='dot')))
    
    list_of_channels.extend([0] * (4 - len(list_of_channels)))
    fig.update_layout(  
                        yaxis =dict(title=yaxis_labels[0] +', '+ yaxis_units[0], titlefont=dict(color=trace_colors[list_of_channels[0]]), tickfont=dict(color=trace_colors[list_of_channels[0]]), anchor="free", side="left", position=0),
                        yaxis2=dict(title=yaxis_labels[1] +', '+ yaxis_units[1], titlefont=dict(color=trace_colors[list_of_channels[1]]), tickfont=dict(color=trace_colors[list_of_channels[1]]), anchor="free", side="left", position=0.07),
                        yaxis3=dict(title=yaxis_labels[2] +', '+ yaxis_units[2], titlefont=dict(color=trace_colors[list_of_channels[2]]), tickfont=dict(color=trace_colors[list_of_channels[2]]), anchor="free", side="left", position=0.14),
                        yaxis4=dict(title=yaxis_labels[3] +', '+ yaxis_units[3], titlefont=dict(color=trace_colors[list_of_channels[3]]), tickfont=dict(color=trace_colors[list_of_channels[3]]), anchor="free", side="left", position=0.21))
    x_domain_list = [0, 0.07, 0.14, 0.21]
    fig.update_layout(xaxis=dict(domain=[x_domain_list[k-1], 1]))
    fig.update_layout(margin=dict(t=50))
       
    input_list = ''.join(list_of_inputs_state).replace('input_','_raw').replace('_calculated','').replace('in_','_in').replace('output_','_out')
    file_name = f"{current_cell[2:10].replace('_', '')}_{fetch_sec_state}_{days_in_chart_state}{input_list}.csv"
    df_merged.to_csv(work_dir + '/download/' + file_name, sep=',', index=False)
    link_to_file = 'download/' + file_name

    return fig, link_to_file, f'Download selected data: ' + file_name


#------Link for download---------------
@app.server.route('/download/<path:path>')
def download(path):
    """Serve a file from the upload directory."""
    return send_file(f'download/{path}', mimetype='text/csv', attachment_filename=f'{path}', as_attachment=True)



#-------Analog Inputs--------------------------------------------------
#-------Set target units of Analog Inputs -------------------------
@app.callback(  [Output("AI_1_units_a", "children"), Output('AI_1_units_b', 'children')],
                [Input("AI_1_units", "value")])
def update_units_1(units):
    return units, units

@app.callback(  [Output("AI_2_units_a", "children"), Output('AI_2_units_b', 'children')],
                [Input("AI_2_units", "value")])
def update_units_2(units):
    return units, units

@app.callback(  [Output("AI_3_units_a", "children"), Output('AI_3_units_b', 'children')],
                [Input("AI_3_units", "value")])
def update_units_3(units):
    return units, units

@app.callback(  [Output("AI_4_units_a", "children"), Output('AI_4_units_b', 'children')],
                [Input("AI_4_units", "value")])
def update_units_4(units):
    return units, units

@app.callback(  [Output("AI_5_units_a", "children"), Output('AI_5_units_b', 'children')],
                [Input("AI_5_units", "value")])
def update_units_5(units):
    return units, units

@app.callback(  [Output("AI_6_units_a", "children"), Output('AI_6_units_b', 'children')],
                [Input("AI_6_units", "value")])
def update_units_6(units):
    return units, units

@app.callback(  [Output("AI_7_units_a", "children"), Output('AI_7_units_b', 'children')],
                [Input("AI_7_units", "value")])
def update_units_7(units):
    return units, units

@app.callback(  [Output("AI_8_units_a", "children"), Output('AI_8_units_b', 'children')],
                [Input("AI_8_units", "value")])
def update_units_8(units):
    return units, units


#------Update Config / Analog Input Settings------------------------
@app.callback(      Output('hidden-div-2', 'children'),
                [   Input('save_AI_settings', 'n_clicks')], 
                [   State("AI_1_units", "value"), State("AI_2_units", "value"), State("AI_3_units", "value"), State("AI_4_units", "value"), State("AI_5_units", "value"), State("AI_6_units", "value"), State("AI_7_units", "value"), State("AI_8_units", "value"),
                    State('AI_1_mode', 'value'), State('AI_2_mode', 'value'), State('AI_3_mode', 'value'), State('AI_4_mode', 'value'), State('AI_5_mode', 'value'), State('AI_6_mode', 'value'), State('AI_7_mode', 'value'), State('AI_8_mode', 'value'),
                    
                    State('AI_1_source_low', 'value'), State('AI_1_target_low', 'value'), State('AI_1_source_high', 'value'), State('AI_1_target_high', 'value'),
                    State('AI_2_source_low', 'value'), State('AI_2_target_low', 'value'), State('AI_2_source_high', 'value'), State('AI_2_target_high', 'value'),
                    State('AI_3_source_low', 'value'), State('AI_3_target_low', 'value'), State('AI_3_source_high', 'value'), State('AI_3_target_high', 'value'),
                    State('AI_4_source_low', 'value'), State('AI_4_target_low', 'value'), State('AI_4_source_high', 'value'), State('AI_4_target_high', 'value'),
                    State('AI_5_source_low', 'value'), State('AI_5_target_low', 'value'), State('AI_5_source_high', 'value'), State('AI_5_target_high', 'value'),
                    State('AI_6_source_low', 'value'), State('AI_6_target_low', 'value'), State('AI_6_source_high', 'value'), State('AI_6_target_high', 'value'),
                    State('AI_7_source_low', 'value'), State('AI_7_target_low', 'value'), State('AI_7_source_high', 'value'), State('AI_7_target_high', 'value'),
                    
                    State('AI_8_source_low', 'value'), State('AI_8_target_low', 'value'), State('AI_8_source_high', 'value'), State('AI_8_target_high', 'value'),
                    
                    State('AI_1_description', 'value'), State('AI_2_description', 'value'), State('AI_3_description', 'value'), State('AI_4_description', 'value'), State('AI_5_description', 'value'), State('AI_6_description', 'value'), State('AI_7_description', 'value'), State('AI_8_description', 'value')])
def update_config_AI(   AI_1_n_clicks, 
                        AI_1_units, AI_2_units, AI_3_units, AI_4_units, AI_5_units, AI_6_units, AI_7_units, AI_8_units, 
                        AI_1_mode, AI_2_mode, AI_3_mode, AI_4_mode, AI_5_mode, AI_6_mode, AI_7_mode, AI_8_mode,
                        AI_1_source_low, AI_1_target_low, AI_1_source_high, AI_1_target_high,
                        AI_2_source_low, AI_2_target_low, AI_2_source_high, AI_2_target_high,
                        AI_3_source_low, AI_3_target_low, AI_3_source_high, AI_3_target_high,
                        AI_4_source_low, AI_4_target_low, AI_4_source_high, AI_4_target_high,
                        AI_5_source_low, AI_5_target_low, AI_5_source_high, AI_5_target_high,
                        AI_6_source_low, AI_6_target_low, AI_6_source_high, AI_6_target_high,
                        AI_7_source_low, AI_7_target_low, AI_7_source_high, AI_7_target_high,
                        AI_8_source_low, AI_8_target_low, AI_8_source_high, AI_8_target_high,  
                        AI_1_description, AI_2_description, AI_3_description, AI_4_description, AI_5_description, AI_6_description, AI_7_description, AI_8_description):

     
    config['AI']['AI_1_description'] = '...' if AI_1_description == '' else AI_1_description.replace('%', '%%')       # Configparser does not accept '%', use '%%' instead
    config['AI']['AI_2_description'] = '...' if AI_2_description == '' else AI_2_description.replace('%', '%%')
    config['AI']['AI_3_description'] = '...' if AI_3_description == '' else AI_3_description.replace('%', '%%')
    config['AI']['AI_4_description'] = '...' if AI_4_description == '' else AI_4_description.replace('%', '%%')
    config['AI']['AI_5_description'] = '...' if AI_5_description == '' else AI_5_description.replace('%', '%%')
    config['AI']['AI_6_description'] = '...' if AI_6_description == '' else AI_6_description.replace('%', '%%')
    config['AI']['AI_7_description'] = '...' if AI_7_description == '' else AI_7_description.replace('%', '%%')
    config['AI']['AI_8_description'] = '...' if AI_8_description == '' else AI_8_description.replace('%', '%%')

    config['AI']['AI_1_units'] = AI_1_units.replace('%', '%%')
    config['AI']['AI_2_units'] = AI_2_units.replace('%', '%%')
    config['AI']['AI_3_units'] = AI_3_units.replace('%', '%%')
    config['AI']['AI_4_units'] = AI_4_units.replace('%', '%%')
    config['AI']['AI_5_units'] = AI_5_units.replace('%', '%%')
    config['AI']['AI_6_units'] = AI_6_units.replace('%', '%%')
    config['AI']['AI_7_units'] = AI_7_units.replace('%', '%%')
    config['AI']['AI_8_units'] = AI_8_units.replace('%', '%%')

    config['AI']['AI_1_mode'] = AI_1_mode
    config['AI']['AI_2_mode'] = AI_2_mode
    config['AI']['AI_3_mode'] = AI_3_mode
    config['AI']['AI_4_mode'] = AI_4_mode
    config['AI']['AI_5_mode'] = AI_5_mode
    config['AI']['AI_6_mode'] = AI_6_mode
    config['AI']['AI_7_mode'] = AI_7_mode
    config['AI']['AI_8_mode'] = AI_8_mode

    config['AI']['AI_1_source_low'] = AI_1_source_low
    config['AI']['AI_1_target_low'] = AI_1_target_low
    config['AI']['AI_1_source_high'] = AI_1_source_high
    config['AI']['AI_1_target_high'] = AI_1_target_high 

    config['AI']['AI_2_source_low'] = AI_2_source_low
    config['AI']['AI_2_target_low'] = AI_2_target_low
    config['AI']['AI_2_source_high'] = AI_2_source_high
    config['AI']['AI_2_target_high'] = AI_2_target_high 

    config['AI']['AI_3_source_low'] = AI_3_source_low
    config['AI']['AI_3_target_low'] = AI_3_target_low
    config['AI']['AI_3_source_high'] = AI_3_source_high
    config['AI']['AI_3_target_high'] = AI_3_target_high 

    config['AI']['AI_4_source_low'] = AI_4_source_low
    config['AI']['AI_4_target_low'] = AI_4_target_low
    config['AI']['AI_4_source_high'] = AI_4_source_high
    config['AI']['AI_4_target_high'] = AI_4_target_high 

    config['AI']['AI_5_source_low'] = AI_5_source_low
    config['AI']['AI_5_target_low'] = AI_5_target_low
    config['AI']['AI_5_source_high'] = AI_5_source_high
    config['AI']['AI_5_target_high'] = AI_5_target_high 

    config['AI']['AI_6_source_low'] = AI_6_source_low
    config['AI']['AI_6_target_low'] = AI_6_target_low
    config['AI']['AI_6_source_high'] = AI_6_source_high
    config['AI']['AI_6_target_high'] = AI_6_target_high 

    config['AI']['AI_7_source_low'] = AI_7_source_low
    config['AI']['AI_7_target_low'] = AI_7_target_low
    config['AI']['AI_7_source_high'] = AI_7_source_high
    config['AI']['AI_7_target_high'] = AI_7_target_high 

    config['AI']['AI_8_source_low'] = AI_8_source_low
    config['AI']['AI_8_target_low'] = AI_8_target_low
    config['AI']['AI_8_source_high'] = AI_8_source_high
    config['AI']['AI_8_target_high'] = AI_8_target_high 

    write_config()


#------Set Analog Inputs active/disabled--------
color = 'AliceBlue'
@app.callback(  [Output('AI_1_card', 'color'), Output('AI_1_card', 'style')],  # AI 1 active/disabled
                [Input('AI_1_active', 'value')])
def set_active_1(active_value):
    if active_value == ['True']:
        config['AI']['AI_1_active'] = 'True'
        write_config()
        return ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AI']['AI_1_active'] = 'Flase'
        write_config()
        return ['', {'min-height': '250px'}]

@app.callback(  [Output('AI_2_card', 'color'), Output('AI_2_card', 'style')],  # AI 2 active/disabled
                [Input('AI_2_active', 'value')])
def set_active_2(active_value):
    if active_value == ['True']:
        config['AI']['AI_2_active'] = 'True'
        write_config()
        return ['primary', {'min-height': '250px', 'background-color':color}] 
    else:
        config['AI']['AI_2_active'] = 'Flase'
        write_config()
        return ['', {'min-height': '250px'}]

@app.callback(  [Output('AI_3_card', 'color'), Output('AI_3_card', 'style')],  # AI 3 active/disabled
                [Input('AI_3_active', 'value')])
def set_active_3(active_value):
    if active_value == ['True']:
        config['AI']['AI_3_active'] = 'True'
        write_config()
        return ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AI']['AI_3_active'] = 'Flase'
        write_config()
        return ['', {'min-height': '250px'}]

@app.callback(  [Output('AI_4_card', 'color'), Output('AI_4_card', 'style')],  # AI 4 active/disabled
                [Input('AI_4_active', 'value')])
def set_active_4(active_value):
    if active_value == ['True']:
        config['AI']['AI_4_active'] = 'True'
        write_config()
        return ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AI']['AI_4_active'] = 'Flase'
        write_config()
        return ['', {'min-height': '250px'}]

@app.callback(  [Output('AI_5_card', 'color'), Output('AI_5_card', 'style')],  # AI 5 active/disabled
                [Input('AI_5_active', 'value')])
def set_active_5(active_value):
    if active_value == ['True']:
        config['AI']['AI_5_active'] = 'True'
        write_config()
        return ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AI']['AI_5_active'] = 'Flase'
        write_config()
        return ['', {'min-height': '250px'}]

@app.callback(  [Output('AI_6_card', 'color'), Output('AI_6_card', 'style')],  # AI 6 active/disabled
                [Input('AI_6_active', 'value')])
def set_active_6(active_value):
    if active_value == ['True']:
        config['AI']['AI_6_active'] = 'True'
        write_config()
        return ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AI']['AI_6_active'] = 'Flase'
        write_config()
        return ['', {'min-height': '250px'}]

@app.callback(  [Output('AI_7_card', 'color'), Output('AI_7_card', 'style')],  # AI 7 active/disabled
                [Input('AI_7_active', 'value')])
def set_active_7(active_value):
    if active_value == ['True']:
        config['AI']['AI_7_active'] = 'True'
        write_config()
        return ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AI']['AI_7_active'] = 'Flase'
        write_config()
        return ['', {'min-height': '250px'}]

@app.callback(  [Output('AI_8_card', 'color'), Output('AI_8_card', 'style')],  # AI 8 active/disabled
                [Input('AI_8_active', 'value')])
def set_active_8(active_value):
    if active_value == ['True']:
        config['AI']['AI_8_active'] = 'True'
        write_config()
        return ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AI']['AI_8_active'] = 'Flase'
        write_config()
        return ['', {'min-height': '250px'}]




#------Analog Outputs------------------------------------------------
#------Update Config / Analog Output Settings------------------------
@app.callback(  Output('hidden-div-3', 'children'),
                [Input('save_AO_settings', 'n_clicks'), Input('save_AO_settings_', 'n_clicks')], 
                [State('AO_1_description_', 'value'), State('AO_2_description_', 'value'), State('AO_3_description_', 'value'), State('AO_4_description_', 'value'),
                State("AO_1_units_", "value"), State("AO_2_units_", "value"), State("AO_3_units_", "value"), State("AO_4_units_", "value"),
                State('AO_1_source_low', 'value'), State('AO_1_target_low', 'value'), State('AO_1_source_high', 'value'), State('AO_1_target_high', 'value'),
                State('AO_2_source_low', 'value'), State('AO_2_target_low', 'value'), State('AO_2_source_high', 'value'), State('AO_2_target_high', 'value'),
                State('AO_3_source_low', 'value'), State('AO_3_target_low', 'value'), State('AO_3_source_high', 'value'), State('AO_3_target_high', 'value'),
                State('AO_4_source_low', 'value'), State('AO_4_target_low', 'value'), State('AO_4_source_high', 'value'), State('AO_4_target_high', 'value')])
def update_config_AO(   AO_n_clicks, AO_n_clicks_,
                        AO_1_description, AO_2_description, AO_3_description, AO_4_description,
                        AO_1_units, AO_2_units, AO_3_units, AO_4_units,

                        AO_1_source_low, AO_1_target_low, AO_1_source_high, AO_1_target_high,
                        AO_2_source_low, AO_2_target_low, AO_2_source_high, AO_2_target_high,
                        AO_3_source_low, AO_3_target_low, AO_3_source_high, AO_3_target_high,
                        AO_4_source_low, AO_4_target_low, AO_4_source_high, AO_4_target_high):

    config['AO']['AO_1_description'] = '...' if AO_1_description == '' else AO_1_description.replace('%', '%%')       # Configparser does not accept '%', use '%%' instead
    config['AO']['AO_2_description'] = '...' if AO_2_description == '' else AO_2_description.replace('%', '%%')
    config['AO']['AO_3_description'] = '...' if AO_3_description == '' else AO_3_description.replace('%', '%%')
    config['AO']['AO_4_description'] = '...' if AO_4_description == '' else AO_4_description.replace('%', '%%')

    config['AO']['AO_1_units'] = AO_1_units.replace('%', '%%')
    config['AO']['AO_2_units'] = AO_2_units.replace('%', '%%')
    config['AO']['AO_3_units'] = AO_3_units.replace('%', '%%')
    config['AO']['AO_4_units'] = AO_4_units.replace('%', '%%')

    config['AO']['AO_1_source_low'] = AO_1_source_low
    config['AO']['AO_1_target_low'] = AO_1_target_low
    config['AO']['AO_1_source_high'] = AO_1_source_high
    config['AO']['AO_1_target_high'] = AO_1_target_high 

    config['AO']['AO_2_source_low'] = AO_2_source_low
    config['AO']['AO_2_target_low'] = AO_2_target_low
    config['AO']['AO_2_source_high'] = AO_2_source_high
    config['AO']['AO_2_target_high'] = AO_2_target_high 

    config['AO']['AO_3_source_low'] = AO_3_source_low
    config['AO']['AO_3_target_low'] = AO_3_target_low
    config['AO']['AO_3_source_high'] = AO_3_source_high
    config['AO']['AO_3_target_high'] = AO_3_target_high 

    config['AO']['AO_4_source_low'] = AO_4_source_low
    config['AO']['AO_4_target_low'] = AO_4_target_low
    config['AO']['AO_4_source_high'] = AO_4_source_high
    config['AO']['AO_4_target_high'] = AO_4_target_high 

    write_config()



#-------Set source units and descriptions of Analog Outputs -------------------------
@app.callback(  [Output('AO_1_description', 'value'), Output('AO_2_description', 'value'), Output('AO_3_description', 'value'), Output('AO_4_description', 'value'),
                
                Output("AO_1_units_a", "children"), Output('AO_1_units_b', 'children'), Output("AO_2_units_a", "children"), Output('AO_2_units_b', 'children'),
                Output("AO_3_units_a", "children"), Output('AO_3_units_b', 'children'), Output("AO_4_units_a", "children"), Output('AO_4_units_b', 'children')],


                [Input('AO_1_description_', 'value'), Input('AO_2_description_', 'value'), Input('AO_3_description_', 'value'), Input('AO_4_description_', 'value'),
                Input('model_output_a', 'value'), Input('model_output_b', 'value'), Input('model_output_c', 'value'), Input('model_output_d', 'value'),
                Input("AO_1_units_", "value"), Input("AO_2_units_", "value"),Input("AO_3_units_", "value"),Input("AO_4_units_", "value")])
def update_output_units_1(  description_1_, description_2_, description_3_, description_4_,
                            model_output_a, model_output_b, model_output_c, model_output_d,
                            AO_1_units_, AO_2_units_, AO_3_units_, AO_4_units_):
    

    
    j = [model_output_a, model_output_b, model_output_c, model_output_d]
    k = [description_1_, description_2_, description_3_, description_4_]
    l = [AO_1_units_, AO_2_units_, AO_3_units_, AO_4_units_]
    
    try: 
        description_1 = k[j.index('output_1')]
        AO_1_units = l[j.index('output_1')]

    except: 
        description_1 = 'Not active'
        AO_1_units = '...'
    
    try: 
        description_2 = k[j.index('output_2')]
        AO_2_units = l[j.index('output_2')]
    except: 
        description_2 = 'Not active'
        AO_2_units = '...'
    
    try: 
        description_3 = k[j.index('output_3')]
        AO_3_units = l[j.index('output_3')]
    except: 
        description_3 = 'Not active'
        AO_3_units = '...'
    
    try: 
        description_4 = k[j.index('output_4')]
        AO_4_units = l[j.index('output_4')]
    except: 
        description_4 = 'Not active'
        AO_4_units = '...'


    out =  [description_1, description_2, description_3, description_4, 
            AO_1_units, AO_1_units, AO_2_units, AO_2_units,
            AO_3_units, AO_3_units, AO_4_units, AO_4_units]

    return out



#-------Model------------------------------------------------------------
#------Set Analog Outputs of the MODEL - channel to be output to --------
@app.callback(  [Output('model_output_a', 'options'), Output('model_output_b', 'options'), Output('model_output_c', 'options'), Output('model_output_d', 'options'),
                Output('AO_1_card', 'color'), Output('AO_1_card', 'style'), Output('AO_2_card', 'color'), Output('AO_2_card', 'style'), 
                Output('AO_3_card', 'color'), Output('AO_3_card', 'style'), Output('AO_4_card', 'color'), Output('AO_4_card', 'style') ], 
                [Input('model_output_a', 'value'), Input('model_output_b', 'value'), Input('model_output_c', 'value'), Input('model_output_d', 'value'),
                Input('model_input_a', 'value'), Input('model_input_b', 'value'), Input('model_input_c', 'value'), Input('model_input_d', 'value'),
                Input('model_input_e', 'value'), Input('model_input_f', 'value'), Input('model_input_g', 'value'), Input('model_input_h', 'value') ])
def set_model_output_list_a(value_a, value_b, value_c, value_d, 
                            value_input_a, value_input_b, value_input_c, value_input_d, value_input_e, value_input_f, value_input_g, value_input_h):
    config['model']['model_output_a'] = value_a
    config['model']['model_output_b'] = value_b
    config['model']['model_output_c'] = value_c
    config['model']['model_output_d'] = value_d

    config['model']['model_input_a'] = value_input_a
    config['model']['model_input_b'] = value_input_b
    config['model']['model_input_c'] = value_input_c
    config['model']['model_input_d'] = value_input_d
    config['model']['model_input_e'] = value_input_e
    config['model']['model_input_f'] = value_input_f
    config['model']['model_input_g'] = value_input_g
    config['model']['model_input_h'] = value_input_h

    channels_output_a =[  
            {'label': 'Not active', 'value': 'empty'},
            {'label': 'Analog Output 1', 'value': 'output_1', 'disabled': True if value_b == 'output_1' or value_c == 'output_1' or value_d == 'output_1' else False},
            {'label': 'Analog Output 2', 'value': 'output_2', 'disabled': True if value_b == 'output_2' or value_c == 'output_2' or value_d == 'output_2' else False},
            {'label': 'Analog Output 3', 'value': 'output_3', 'disabled': True if value_b == 'output_3' or value_c == 'output_3' or value_d == 'output_3' else False},
            {'label': 'Analog Output 4', 'value': 'output_4', 'disabled': True if value_b == 'output_4' or value_c == 'output_4' or value_d == 'output_4' else False}  ]
    channels_output_b =[  
            {'label': 'Not active', 'value': 'empty'},
            {'label': 'Analog Output 1', 'value': 'output_1', 'disabled': True if value_a == 'output_1' or value_c == 'output_1' or value_d == 'output_1' else False},
            {'label': 'Analog Output 2', 'value': 'output_2', 'disabled': True if value_a == 'output_2' or value_c == 'output_2' or value_d == 'output_2' else False},
            {'label': 'Analog Output 3', 'value': 'output_3', 'disabled': True if value_a == 'output_3' or value_c == 'output_3' or value_d == 'output_3' else False},
            {'label': 'Analog Output 4', 'value': 'output_4', 'disabled': True if value_a == 'output_4' or value_c == 'output_4' or value_d == 'output_4' else False}  ]
    channels_output_c =[  
            {'label': 'Not active', 'value': 'empty'},
            {'label': 'Analog Output 1', 'value': 'output_1', 'disabled': True if value_b == 'output_1' or value_a == 'output_1' or value_d == 'output_1' else False},
            {'label': 'Analog Output 2', 'value': 'output_2', 'disabled': True if value_b == 'output_2' or value_a == 'output_2' or value_d == 'output_2' else False},
            {'label': 'Analog Output 3', 'value': 'output_3', 'disabled': True if value_b == 'output_3' or value_a == 'output_3' or value_d == 'output_3' else False},
            {'label': 'Analog Output 4', 'value': 'output_4', 'disabled': True if value_b == 'output_4' or value_a == 'output_4' or value_d == 'output_4' else False}  ]       
    channels_output_d =[  
            {'label': 'Not active', 'value': 'empty'},
            {'label': 'Analog Output 1', 'value': 'output_1', 'disabled': True if value_b == 'output_1' or value_c == 'output_1' or value_a == 'output_1' else False},
            {'label': 'Analog Output 2', 'value': 'output_2', 'disabled': True if value_b == 'output_2' or value_c == 'output_2' or value_a == 'output_2' else False},
            {'label': 'Analog Output 3', 'value': 'output_3', 'disabled': True if value_b == 'output_3' or value_c == 'output_3' or value_a == 'output_3' else False},
            {'label': 'Analog Output 4', 'value': 'output_4', 'disabled': True if value_b == 'output_4' or value_c == 'output_4' or value_a == 'output_4' else False}  ]
 
    j = [value_a, value_b, value_c, value_d]  #  'AO_1_active'  ['True']

    if 'output_1' in j:
        config['AO']['AO_1_active'] = 'True'
        active_marker_1 = ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AO']['AO_1_active'] = 'Flase'
        active_marker_1 = ['', {'min-height': '250px'}]

    if 'output_2' in j:
        config['AO']['AO_2_active'] = 'True'
        active_marker_2 = ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AO']['AO_2_active'] = 'Flase'
        active_marker_2 = ['', {'min-height': '250px'}]

    if 'output_3' in j:
        config['AO']['AO_3_active'] = 'True'
        active_marker_3 = ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AO']['AO_3_active'] = 'Flase'
        active_marker_3 = ['', {'min-height': '250px'}]

    if 'output_4' in j:
        config['AO']['AO_4_active'] = 'True'
        active_marker_4 = ['primary', {'min-height': '250px', 'background-color':color}]
    else:
        config['AO']['AO_4_active'] = 'Flase'
        active_marker_4 = ['', {'min-height': '250px'}]

    write_config()
    
    return [channels_output_a, channels_output_b, channels_output_c, channels_output_d]  + active_marker_1  + active_marker_2 + active_marker_3 + active_marker_4


#-----General Information------------------------
@app.callback(  Output('cpu_temp', 'children'),
                [Input('interval-component_5', 'n_intervals')]) 
def update__gen_info(n):

    stream = os.popen('cat /sys/class/thermal/thermal_zone0/temp')
    output = stream.read()
    stream.close()

    return  'CPU temperature: ' + "{:.2f}".format(int(output)/1000) + ' °C'



#------------Update Config / db_browser------------------------
@app.callback(   Output("hidden-div-1", "children"),     
                [Input("dropdown_zime_zone", "value"), Input('days_and_points_in_chart', 'value'),
                 Input('channel_to_show_a', 'value'), Input('channel_to_show_b', 'value'), Input('channel_to_show_c', 'value'), Input('channel_to_show_d', 'value'),
                 Input('lines_markers', 'value')])
def update_config(time_zone, days_and_points_in_chart, channel_to_show_a, channel_to_show_b, channel_to_show_c, channel_to_show_d, lines_markers):

    #--Settings
    config['db_browser']['local_time_zone'] = time_zone

    #--Day chart
    config['db_browser']['days_and_points_in_chart'] = days_and_points_in_chart
    config['db_browser']['lines_markers'] = lines_markers

    config['db_browser']['list_of_inputs'] = channel_to_show_a +', '+ channel_to_show_b +', '+ channel_to_show_c +', '+ channel_to_show_d
    
    # list_of_outputs.sort(reverse=False)
    # config['db_browser']['list_of_outputs'] = ', '.join(list_of_outputs)

    write_config()



#----- Removes focus from all Dropdowns in Cockpit after changing the value -----
app.clientside_callback(
    """
    function(v1, v2, v3, v4, v5, v6, period) {
        element = document.getElementById('top_bar');
        element.focus();
    }
    """,
    Output('hidden-div-5', 'children'),
    [   Input('channel_to_monitor_a_graph', 'value'), Input('channel_to_monitor_b_graph', 'value'),
        Input('channel_to_monitor_a', 'value'), Input('channel_to_monitor_b', 'value'), Input('channel_to_monitor_c', 'value'), Input('channel_to_monitor_d', 'value'),
        Input('period_to_monitor', 'value') ]     
)



#-----------------------------------
#-----------------------------------



if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=5002, threaded = True)

