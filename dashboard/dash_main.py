import os
from flask import send_file
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output, State
from classes_a import get_data_generic, get_tables_list, get_data_from_db_average

import plotly.graph_objects as go
import numpy as np
import pandas as pd
import datetime
import time

from pytz import timezone
import pytz

import configparser
# import fcntl # locking access to a file for different applications/processes
from threading import Lock

from db_connector import DB_Reader

lock = Lock() 

db_reader_a = DB_Reader()
#db_reader_b = DB_Reader()

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


#-----------tab_0_content (Cockpit)-------------------
def tab0_content():
    global last_point_in_chart
    global df
    global fig
    current_time = datetime.datetime.utcnow()
    last_point_in_chart = current_time
    lock.acquire()
    df_a = db_reader_a.get_data_generic('date_time_utc', ['input_1'], (current_time - datetime.timedelta(hours=1)).strftime("%Y_%m_%d %H:%M:%S"), current_time.strftime("%Y_%m_%d %H:%M:%S"), fetch_every_n_sec = '10')
    lock.release()
    df = df_a[0]
    fig = go.Figure(data=go.Scattergl(mode='lines+markers', line=dict(color='#1E90FF', width=4, dash='dot'), x=df[0], y=df[1])) # use Scattergl for large data
    fig['layout']['xaxis'].update(title='111', autorange=True)
    fig['layout']['yaxis'].update(title='111', range=[0, 25], autorange=True)
    fig['layout'].update(autosize = True)

    z1 = np.array([
        [8.83,8.89,8.81,8.87,8.9,8.87],
        [8.89,8.94,8.85,8.94,8.96,8.92],
        [8.84,8.9,8.82,8.92,8.93,8.91],
        [8.79,8.85,8.79,8.9,8.94,8.92],
        [8.79,8.88,8.81,8.9,8.95,8.92],
        [8.8,8.82,8.78,8.91,8.94,8.92],
        [8.75,8.78,8.77,8.91,8.95,8.92],
        [8.8,8.8,8.77,8.91,8.95,8.94],
        [8.74,8.81,8.76,8.93,8.98,8.99],
        [8.89,8.99,8.92,9.1,9.13,9.11],
        [8.97,8.97,8.91,9.09,9.11,9.11],
        [9.04,9.08,9.05,9.25,9.28,9.27],
        [9,9.01,9,9.2,9.23,9.2],
        [8.99,8.99,8.98,9.18,9.2,9.19],
        [8.93,8.97,8.97,9.18,9.2,9.18]
    ])
    z2 = z1 + 1

    fig_dataset = go.Figure(data=[
        go.Surface(z=z1, showscale=False),
        go.Surface(z=z2, showscale=False)
    ])

    tab1_content = dbc.Card(
        dbc.CardBody(children=[
            dbc.Row(no_gutters=True, children=[ dbc.Col(width=1, children=['----1-----']),
                                                dbc.Col(width=6, children=[ dbc.Row(dcc.Graph(id='live-chart', figure=fig, config={"displaylogo": False,'modeBarButtonsToRemove': ['lasso2d']}, style={'height': 600, 'width': '100%'})),
                                                                            dbc.Row(html.Div(id='input1_last_value', children=['-----!!!!-----'], style={'margin-left':100}))
                                                                                    ]),   
                                                dbc.Col(width=5, children=[dcc.Graph(id='fig_dataset', figure=fig_dataset, config={"displaylogo": False,'modeBarButtonsToRemove': ['lasso2d']}, style={'height': 600, 'width': '100%'})])
                                                        ]),
            dbc.Row(dbc.Col(html.Div("----------------------hello world!--------------------")), justify="center")
                                ]                               
                                                        
                    ),className="mt-3")

    return tab1_content

#-----------tab_1_content (Level 1)-------------------
def tab1_content():


    tab2_content = dbc.Card(
        dbc.CardBody(
            [
                html.P("This is tab 2!", className="card-text")
            ]), className="mt-3",)




    
    return tab2_content

#-----------db_browser_content (Level 2)--------------
def db_browser_content():
    channels =[ {'label': 'Empty', 'value': 'empty'},
                {'label': 'Analog Input 1 (calculated)', 'value': 'in_1_calculated'},
                {'label': 'Analog Input 2 (calculated)', 'value': 'in_2_calculated'},
                {'label': 'Analog Input 3 (calculated)', 'value': 'in_3_calculated'},
                {'label': 'Analog Input 4 (calculated)', 'value': 'in_4_calculated'},
                {'label': 'Analog Input 5 (calculated)', 'value': 'in_5_calculated'},
                {'label': 'Analog Input 6 (calculated)', 'value': 'in_6_calculated'},
                {'label': 'Analog Input 7 (calculated)', 'value': 'in_7_calculated'},
                {'label': 'Analog Input 8 (calculated)', 'value': 'in_8_calculated'},
                {'label': 'Analog Input 1 (raw signal)', 'value': 'input_1'},
                {'label': 'Analog Input 2 (raw signal)', 'value': 'input_2'},
                {'label': 'Analog Input 3 (raw signal)', 'value': 'input_3'},
                {'label': 'Analog Input 4 (raw signal)', 'value': 'input_4'},
                {'label': 'Analog Input 5 (raw signal)', 'value': 'input_5'},
                {'label': 'Analog Input 6 (raw signal)', 'value': 'input_6'},
                {'label': 'Analog Input 7 (raw signal)', 'value': 'input_7'},
                {'label': 'Analog Input 8 (raw signal)', 'value': 'input_8'} ]
    global fig
    browser_content = dbc.Card(
        dcc.Loading(dbc.CardBody(children = [
                    dbc.Row(dbc.Col(html.Div(children=[ html.A("Download selected data", id = 'download_selected_data', href = 'download/2020_02_15.csv'),
                                                        dbc.Tooltip("Noun: rare, the action or habit of estimating something as worthless.", target="download_selected_data", hide_arrow=False),
                    
                                                    ]))),
                    dbc.Row(no_gutters=False,
                            children=[
                            dbc.Col(html.Div(className="mt-3", children = [
                                dbc.Button(className="mb-3", id = 'button_reload_tables', children=["Reload", html.Br(),"data base"], color="primary", size="sm", style={'min-width': '90px'}),
                                dbc.Button(className="mb-3 ml-1", id = 'button_delete_selected', children=["Delete", html.Br(),"selected"], color="danger", size="sm", style={'min-width': '90px'}),
                                html.Div(dash_table.DataTable(id='table', columns=[{"name": "Day Tables in db:", "id": "tabels_in_db"}], 
                                        selected_cells = [{'row': 0, 'column': 0, 'column_id': 'tabels_in_db'}],
                                        data=[{"tabels_in_db": i} for i in get_tables_list()],
                                        fixed_rows={ 'headers': True, 'data': 0 },
                                        style_table={'maxHeight': '450px', 'cursor':'auto'},
                                        style_cell={'textAlign': 'center', 'font-size':'140%'},
                                        style_as_list_view=True), className="pl-0 pr-0")],
                            ), width=3),
                            dbc.Col(html.Div(children = [
                                            html.Div(dcc.Graph(id='day_chart', figure=fig, config={"displaylogo": False,'modeBarButtonsToRemove': ['lasso2d']}, style={'height': '100%', 'width': '100%'}), style={'height': 500 }),

                                            dbc.Row(children=[
                                            dbc.Col(children=[

                                            dbc.Row([html.Div(  dcc.Dropdown(options=channels,                                                                                      #channel_to_show_a 
                                                                        value='empty', style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False,
                                                                        id='channel_to_show_a'), style={'margin-left': 16, 'margin-right': 10}),
                                                                dcc.Dropdown(options=channels, 
                                                                            value='empty',
                                                                            style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False, id='channel_to_show_b')], className='mb-2'),

                                            dbc.Row([html.Div(  dcc.Dropdown(options=channels, 
                                                                        value='empty', style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False,
                                                                        id='channel_to_show_c'), style={'margin-left': 16, 'margin-right': 10}),
                                                                dcc.Dropdown(options=channels, 
                                                                            value='empty',
                                                                            style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False, id='channel_to_show_d')], className='mb-2'),                                          
                                            
                                            dbc.Row(dcc.Checklist(options=[
                                                                            {'label': 'Analog Input 1', 'value': 'input_1'},
                                                                            {'label': 'Analog Input 2', 'value': 'input_2'},
                                                                            {'label': 'Analog Input 3', 'value': 'input_3'},
                                                                            {'label': 'Analog Input 4', 'value': 'input_4'}
                                                                        ],
                                                                        value=[ chunk.strip(None) for chunk in config['db_browser']['list_of_inputs'].split(',') ],
                                                                        labelStyle={'display': 'inline-block', 'margin-right':12, 'font-size':'16px'},
                                                                        inputStyle={'margin-right':23, 'margin-left':20, 'transform':'scale(1.6)'},
                                                                        id='list_of_inputs')),

                                            dbc.Row(dcc.Checklist(options=[
                                                                            {'label': 'Analog Input 5', 'value': 'input_5'},
                                                                            {'label': 'Analog Input 6', 'value': 'input_6'},
                                                                            {'label': 'Analog Input 7', 'value': 'input_7'},
                                                                            {'label': 'Analog Input 8', 'value': 'input_8'}
                                                                        ],
                                                                        value=[ chunk.strip(None) for chunk in config['db_browser']['list_of_inputs'].split(',') ],
                                                                        labelStyle={'display': 'inline-block', 'margin-right':12, 'font-size':'16px'},
                                                                        inputStyle={'margin-right':23, 'margin-left':20, 'transform':'scale(1.6)'},
                                                                        id='list_of_inputs_b')),
                                       
                                            dbc.Row(dcc.Checklist(options=[
                                                                            {'label': 'Analog Output 1', 'value': 'output_1'},
                                                                            {'label': 'Analog Output 2', 'value': 'output_2'},
                                                                            {'label': 'Analog Output 3', 'value': 'output_3'},
                                                                            {'label': 'Analog Output 4', 'value': 'output_4'}],
                                                                        value=[ chunk.strip(None) for chunk in config['db_browser']['list_of_outputs'].split(',') ],
                                                                        labelStyle={'display': 'inline-block', 'margin-right':0, 'font-size':'16px'},
                                                                        inputStyle={'margin-right':22, 'margin-left':20, 'transform':'scale(1.6)'},
                                                                        id='list_of_outputs'))
                                                ], width=9),
                                            
                                            dbc.Col(html.Div(dbc.Button(className="mb-3", id = 'button_load_curves', children=["Load", html.Br(),"curves"], color="primary", size="sm", style={'min-width': '90px'}), style={'text-align': 'left'}),
                                            width=3)
                                            ], justify="start"),

                                            dbc.Row([html.Div(dcc.Dropdown(options=[ 
                                                                            {'label': 'One day / 180 sec.',     'value': 'one_180'},
                                                                            {'label': 'One day / 60 sec.',      'value': 'one_60'},
                                                                            {'label': 'One day / 30 sec.',      'value': 'one_30'},
                                                                            {'label': 'Three days / 180 sec.',  'value': 'three_180'},
                                                                            ], 
                                                                        value=config['db_browser']['days_and_points_in_chart'], style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False,
                                                                        id='days_and_points_in_chart'), style={'margin-left': 16, 'margin-right': 10}),
                                                    dcc.Dropdown(options=[  {'label': 'Lines+markers', 'value': 'lines+markers'},
                                                                            {'label': 'Lines', 'value': 'lines'},
                                                                            {'label': 'Markers', 'value': 'markers'}], 
                                                                            value=config['db_browser']['lines_markers'],
                                                                            style={'min-width': '330px', 'margin-left':0}, clearable=False, searchable=False, id='lines_markers')]
                                                    )  
                                            ]), width=9, align='center')
                        ],
                    ), 
                      
                    ],
                    className=""), type = 'cube', fullscreen=True),
            className="mt-3"
        )
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
                                    dbc.Col(dbc.Input(id=f"AI_{n}_description", value=config['AI'][f'AI_{n}_description'].replace('%%', '%'), placeholder="Enter channel name ... ", type="text",  className="mb-2"), width=9),
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
                                                            style={'min-width': '0', 'margin-left':0}, className="mb-2 mt-2", clearable=False, searchable=False, id=f'AI_{n}_mode')), width=7),]),

                                    dbc.Row(no_gutters=True, children=[
                                    dbc.Col(html.Div(children=['Target units:'],style={'font-size': '15px', 'text-align':'right'}, className='mr-2 mt-2'), width=5),
                                    dbc.Col(dbc.Input(id=f"AI_{n}_units", placeholder="Enter units", value=config['AI'][f'AI_{n}_units'].replace('%%', '%'), type="text"), width=7)]), # AI units
                                    

                                ], body=True, style={'min-height': '250px'})])
    content_1 = html.Div(children=[ dbc.Row(no_gutters=True, className='mt-3', children=[dbc.Button(className="", id=f'save_AI_settings', children=["SAVE"], color="primary", outline=True,  size="sm", style={'min-width': '100%'})]),
                                    dbc.Row(no_gutters=True, className='mt-3', children=[ai_n_settings_block(1), ai_n_settings_block(2), ai_n_settings_block(3), ai_n_settings_block(4)]),
                                    dbc.Row(no_gutters=True, className='mt-3', children=[ai_n_settings_block(5), ai_n_settings_block(6), ai_n_settings_block(7), ai_n_settings_block(8)])                   
                                ])


    tab1_content = [    html.Div(id='hidden-div-1', style={'display':'none'}), # used for callbacks without any output
                        html.Div(id='hidden-div-2', style={'display':'none'}), # used for callbacks without any output
                        html.Div(id='hidden-div-3', style={'display':'none'}), # used for callbacks without any output
                        content_1]


    # Content of 'MATRIX'.
    content_mx = html.Div(children=["-----CONTENT Matrix------"], style={'min-height': '300px'}, className='mt-3')
       
    # Content of 'Analog Outputs'.
    content_ao = html.Div(children=["-----CONTENT AO------"], style={'min-height': '300px'}, className='mt-3')
 
    # Content of 'Date and Time'
    dropdown_zime_zone =  dcc.Dropdown(
        options=[{'label': f"{i}", 'value': f"{i}"} for i in pytz.all_timezones],
        value=config['db_browser']['local_time_zone'], clearable=False, id = 'dropdown_zime_zone') 
    content_date_time = html.Div(dropdown_zime_zone, style={'min-height': '300px'}, className='mt-3')


    tab_settings_label_style = {"color": "#007bff", "cursor": "pointer", "font-size": "large"} 
    settings_content = dbc.Card(
        dbc.CardBody(dbc.Tabs(style={'margin-top':'0px'}, id='setting_tabs', children=[
                                    dbc.Tab(tab1_content, label="Analog Inputs", tab_id='tab_ai', label_style=tab_settings_label_style),
                                    dbc.Tab(content_mx, label="MATRIX", tab_id='tab_mx', label_style=tab_settings_label_style),
                                    dbc.Tab(content_ao, label="Analog Outputs", tab_id='tab_ao', label_style=tab_settings_label_style),
                                    dbc.Tab(content_date_time, label="Date and Time", tab_id='tab_dt', label_style=tab_settings_label_style, disabled=False)
                                ])), className="mt-3", style={'padding-top':'0px'})

    return settings_content 




#---------------------------------------------
app = dash.Dash(__name__)
app.title='Matrix'

def serve_layout():
    tab_label_style = {"color": "#00AEF9", "cursor": "pointer", "font-size": "large"} 
    return html.Div(html.Div(className="ml-2 mr-2 mt-2 mb-2", children=[
        html.Div(children=[dbc.Row(justify="between", align="center",className="pt-2 ml-0 mr-0", style={'background-color':'LightSkyBlue', 'border-radius':'5px'}, children=[
                                dbc.Col(children=[html.H6(html.Div(children = ["L O G O"], className="pt-2 pb-2 pl-2 pr-2", style={'text-align': 'left'}), style={'text-align': 'left'})], width=2),
                                dbc.Col(html.Div("One of three columns", className="mb-2"), width=4),
                                dbc.Col(children=[html.H6(html.Div(id="date_time_notification", children = ["Date and Time"], className="pt-2 pb-2 pl-2 pr-2", style={'text-align': 'left'}))], style={ 'max-width': '170px', 'min-width': '170px'})
                                ])], className="mb-2 ml-0 mr-0"),
        dbc.Tabs(id='main_tabs', children=[
            dbc.Tab(tab_id="tab-0", label='Cockpit', children=[tab0_content()], label_style=tab_label_style), 
            dbc.Tab(tab_id="tab-1", label='Level 1', children=[tab1_content()], label_style=tab_label_style),
            dbc.Tab(tab_id="db_browser", label='Level 2', children=[db_browser_content()], label_style=tab_label_style),
            dbc.Tab(tab_id="tab-3", label='Level 3', children=[''], label_style=tab_label_style),
            dbc.Tab(tab_id="tab-4", label='Level 4', children=[''], label_style=tab_label_style),
            dbc.Tab(tab_id="tab-5", label='Level 5', children=[''], label_style=tab_label_style),
            dbc.Tab(tab_id="tab-settings", label='Settings', children=[settings_content()], label_style=tab_label_style),
            dcc.Interval(id='interval-component_60', interval=60*1000, n_intervals=0),  # Inreval triggers every 60 seconds. Used for the date and time notification
            dcc.Interval(id='interval-component_20', interval=20*1000, n_intervals=0),  # Inreval triggers every 20 seconds
            dcc.Interval(id='interval-component_10', interval=10*1000, n_intervals=0),  # Inreval triggers every 10 seconds
            dcc.Interval(id='interval-component_5', interval=5*1000, n_intervals=0),    # Inreval triggers every 5 seconds
            dcc.Interval(id='interval-component_1', interval=1*1000, n_intervals=0)     # Inreval triggers every 1 second
                ])]), className='', style={"min-width": "1000px"})

app.layout = serve_layout
# Heads up! You need to write app.layout = serve_layout not app.layout = serve_layout(). That is, define app.layout to the actual function instance.


#---------------------
@app.server.route('/download/<path:path>')
def download(path):
    """Serve a file from the upload directory."""
    return send_file(f'download/{path}', mimetype='text/csv', attachment_filename=f'{path}', as_attachment=True)



#-----------CALLBACKS---------------------                              

#----------updates date and time notification in status bar------------
@app.callback(  Output("date_time_notification", "children"), 
                [Input('interval-component_1', 'n_intervals')]) 
def update_date_time(n):
    global config
    current_time = timezone('UTC').localize(datetime.datetime.utcnow())
    current_time = current_time.astimezone(timezone(config['db_browser']['local_time_zone']))
    return [dbc.Row(dbc.Col(current_time.strftime("%d %B %Y"), width=12)),
            dbc.Row([   dbc.Col(current_time.strftime("%H:%M:%S"), width=5), dbc.Col(current_time.strftime("%Z"), width=7)], justify="start")]


#----------updates live chart in Cockpit------------
@app.callback(  [Output("live-chart", "figure"), Output('input1_last_value', 'children')],
                [Input('interval-component_10', 'n_intervals')],
                [State('main_tabs', 'active_tab'), State('live-chart', 'figure'), State('input1_last_value', 'children')]) 
def update_graph_live(n, active_tab, figure_state, input1_last_value_state):
    if active_tab == 'tab-0':
        print ('updating live chart...')
        global last_point_in_chart
        global df
        current_time = datetime.datetime.utcnow()
        lock.acquire()
        df_append_a = db_reader_a.get_data_generic('date_time_utc', ['input_1'], (last_point_in_chart + datetime.timedelta(seconds=1)).strftime("%Y_%m_%d %H:%M:%S"), current_time.strftime("%Y_%m_%d %H:%M:%S"), fetch_every_n_sec = '10')
        lock.release()
        df_append = df_append_a[0]
        last_average_value = str(np.average(df_append[1].values))

        df = df.append(df_append, ignore_index=True) 
        df = df[df_append.shape[0]:]    # deletes first rows

        df_utc = []
        for i in df.index:
            df_utc.append(timezone('UTC').localize(df[0][i]))  
        df_local_time = []
        for i in df_utc:
            df_local_time.append(i.astimezone(timezone(config['db_browser']['local_time_zone'])))

        last_point_in_chart = current_time
        fig = go.Figure(data=go.Scattergl(mode='lines+markers', line=dict(color='#1E90FF', width=4, dash='dot'), x=df_local_time, y=df[1]))
        return fig, last_average_value
    else:
        return figure_state, input1_last_value_state
        


#--------This loads day chart in the db_browser
@app.callback(  [Output("day_chart", "figure"), Output('download_selected_data', 'href'), Output('download_selected_data', 'children')], 
                [Input("table", "selected_cells"), Input('button_load_curves', 'n_clicks')], 
                [State("table", "data"), State('list_of_inputs', 'value'), State('days_and_points_in_chart', 'value'), State('lines_markers', 'value'),
                State('channel_to_show_a', 'value'), State('channel_to_show_b', 'value'), State('channel_to_show_c', 'value'), State('channel_to_show_d', 'value')])
def current_cell(   selected_cell, button_load_curves_input, data, list_of_inputs_state, days_and_points_in_chart_state, lines_markers_state,
                    channel_to_show_a_state, channel_to_show_b_state, channel_to_show_c_state, channel_to_show_d_state):
    
    
    
    
    dropdowns_list = [channel_to_show_a_state, channel_to_show_b_state, channel_to_show_c_state, channel_to_show_d_state]
    print(dropdowns_list)
    # Remove all 'empty' elements
    l = []
    for elem in dropdowns_list:
        if elem != 'empty':
            l.append(elem)
    print(l)

    list_of_inputs_state = list_of_inputs_state +l

    print(list_of_inputs_state)





    

    current_cell = data[selected_cell[0]['row']]['tabels_in_db'] # current cell as string formated as "2020_01_21"
    date_in_cell = datetime.datetime.strptime(current_cell, '%Y_%m_%d')
    days_in_chart_state = days_and_points_in_chart_state.split('_')[0]
    fetch_sec_state = days_and_points_in_chart_state.split('_')[1]
    
    if days_in_chart_state=='one':
        start_time = date_in_cell - datetime.timedelta(hours=12)
        end_time = date_in_cell + datetime.timedelta(hours=36)
    else:
        start_time = date_in_cell - datetime.timedelta(hours=36)
        end_time = date_in_cell + datetime.timedelta(hours=60)

    list_of_inputs_state.sort(reverse=True)
    lock.acquire()
    try: 
        df_b = db_reader_a.get_data_generic('date_time_utc', list_of_inputs_state, start_time.strftime('%Y_%m_%d %H:%M:%S') , end_time.strftime('%Y_%m_%d %H:%M:%S'), fetch_every_n_sec = fetch_sec_state) # df_b is list of pandas frames
        lock.release()
    except:
        lock.release()
    
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
    #trace_colors = {'input_1':'#119DFF', 'input_2':'#EA11FF','input_3':'#FF7311', 'input_4':'#26FF11'}
    #line=dict(color=trace_colors[list_of_inputs_state[k]])
    k = 0
    for i in df_b: # überarbeiten mit "list_of_inputs_state"
        fig.add_trace(go.Scattergl(mode=lines_markers_state, name=list_of_inputs_state[k], x=df_local_time, y=i[1]))
        df_merged[list_of_inputs_state[k]] = i[1].reset_index(drop=True)
        k = k +1
    fig.add_trace(go.Scatter(x=[date_in_cell, date_in_cell], y=[0, 22], mode="lines", showlegend = False, line=dict(color='royalblue', width=2, dash='dot')))
    fig.add_trace(go.Scatter(x=[date_in_cell + datetime.timedelta(hours=24), date_in_cell + datetime.timedelta(hours=24)], y=[0, 22], mode="lines", showlegend = False, line=dict(color='royalblue', width=2, dash='dot')))
    input_list = ''.join(list_of_inputs_state).replace('input_','')
    file_name = f"{current_cell[2:10].replace('_', '')}_{fetch_sec_state}_{days_in_chart_state}_{input_list}.csv"
    df_merged.to_csv(work_dir + '/download/' + file_name, sep=',', index=False)
    link_to_file = 'download/' + file_name

    return fig, link_to_file, f'Download selected data: ' + file_name


#--------Reload tables from db (tab_3)
@app.callback(                                         
    dash.dependencies.Output('table', 'data'),
    [dash.dependencies.Input('button_reload_tables', 'n_clicks')])
def update_output(n_clicks):
    list_of_tables = get_tables_list()
    data=[{"tabels_in_db": i} for i in list_of_tables]
    return data



#-------Settings---------------------------------------------------
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


#------------Update Config / Analog Input Settings------------------------
@app.callback(      Output("hidden-div-2", "children"),
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

    config['AI']['AI_1_description'] = AI_1_description.replace('%', '%%') # Configparser does not accept '%', use '%%' instead
    config['AI']['AI_2_description'] = AI_2_description.replace('%', '%%')
    config['AI']['AI_3_description'] = AI_3_description.replace('%', '%%')
    config['AI']['AI_4_description'] = AI_4_description.replace('%', '%%')
    config['AI']['AI_5_description'] = AI_5_description.replace('%', '%%')
    config['AI']['AI_6_description'] = AI_6_description.replace('%', '%%')
    config['AI']['AI_7_description'] = AI_7_description.replace('%', '%%')
    config['AI']['AI_8_description'] = AI_8_description.replace('%', '%%')

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


#------Switch between Setting Tabs------------------------------------------
@app.callback(Output('hidden-div-3', 'children'), [Input('setting_tabs', 'active_tab')])
def switch_tab(ac):
    if ac == 'tab_mx':
        print(config['AI']['AI_1_active'])
        print(config['AI']['AI_2_active'])
        print(config['AI']['AI_3_active'])
        print(config['AI']['AI_4_active'])


#------------Update Config / db_broweser------------------------
@app.callback(  Output("hidden-div-1", "children"),
                [Input("dropdown_zime_zone", "value"),
                 Input('days_and_points_in_chart', 'value'),
                 Input('list_of_inputs', 'value'),
                 Input('list_of_outputs', 'value'),
                 Input('lines_markers', 'value')])
def update_config(time_zone, days_and_points_in_chart, list_of_inputs, list_of_outputs, lines_markers):
    global config

    #--Settings
    config['db_browser']['local_time_zone'] = time_zone

    #--Day chart
    config['db_browser']['days_and_points_in_chart'] = days_and_points_in_chart
    config['db_browser']['lines_markers'] = lines_markers


    list_of_inputs.sort(reverse=False)
    config['db_browser']['list_of_inputs'] = ', '.join(list_of_inputs)
    list_of_outputs.sort(reverse=False)
    config['db_browser']['list_of_outputs']= ', '.join(list_of_outputs)


    write_config()



#------------------------------------
#-----------------------------------



if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)

