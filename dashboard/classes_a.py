import mysql.connector
import pandas as pd
import time
from datetime import datetime, timedelta

MYSQL_HOST='localhost'
MYSQL_USER='root'
MYSQL_PASSWORD='th6nw7hg'
DB_NAME='dash_main'

def msql_dummy():
    connection_flag = False # False if not connected to data base. 
    while connection_flag == False:
        time.sleep(1)
        try:
            connection_flag = True
            mydb = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                auth_plugin='mysql_native_password',
                passwd=MYSQL_PASSWORD,
                database=DB_NAME,
                buffered="True")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            connection_flag = False
    mycursor = mydb.cursor(buffered=True)
    ##### body #####
    mycursor.close()
    mydb.close()
    return 



def get_data_from_db_average(col_a, col_b, date, average_window_min):  
    connection_flag = False # False if not connected to data base. 
    while connection_flag == False:
        time.sleep(0.5)
        try:
            connection_flag = True
            mydb = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                auth_plugin='mysql_native_password',
                passwd=MYSQL_PASSWORD,
                database=DB_NAME,
                buffered="True")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            connection_flag = False
    
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT FROM_UNIXTIME({}*60 * (UNIX_TIMESTAMP(`{}`) DIV ({}*60))) grp_id, AVG({}) FROM `{}` GROUP BY grp_id".format(average_window_min, col_a, average_window_min, col_b, date))
    df = pd.DataFrame(mycursor.fetchall())
    mycursor.close()
    mydb.close()
    return df







def get_tables_list():  # returns list of strings
    connection_flag = False # False if not connected to data base. 
    while connection_flag == False:
        time.sleep(1)
        try:
            connection_flag = True
            mydb = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                auth_plugin='mysql_native_password',
                passwd=MYSQL_PASSWORD,
                database=DB_NAME,
                buffered="True")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            connection_flag = False
    mycursor = mydb.cursor(buffered=True)
    ##### body #####
    mycursor.execute("SHOW TABLES")
    tables_list_from_db =  mycursor.fetchall()
    tables_list = []
    for inx in tables_list_from_db:
        tables_list.append(inx[0].decode('utf-8'))
    
    mycursor.close()
    mydb.close()
    tables_list.reverse()
    return tables_list


# date format: "2020_01_06",  time format "18:00:00"
def get_data_from_db(col_a, col_b, date, start_time, stop_time, fetch_every_n_sec = '15'):  
    start_date_time = date + " " + start_time
    stop_date_time = date + " " + stop_time
    connection_flag = False # False if not connected to data base. 
    while connection_flag == False:
        time.sleep(0.5)
        try:
            connection_flag = True
            mydb = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                auth_plugin='mysql_native_password',
                passwd=MYSQL_PASSWORD,
                database=DB_NAME,
                buffered="True")
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            connection_flag = False
    
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT {}, {} FROM {} WHERE id % {} = 0 AND date_time_utc between '{}' and '{}'".format(col_a, col_b, date, fetch_every_n_sec,  start_date_time, stop_date_time))
    df = pd.DataFrame(mycursor.fetchall())
    mycursor.close()
    mydb.close()
    return df


 
def get_data_generic(col_a, col_b, start_date_time, stop_date_time, fetch_every_n_sec):
    start_date_str = start_date_time.split()[0]
    stop_date_str =stop_date_time.split()[0]
    if start_date_str == stop_date_str:
        df = pd.DataFrame()
        try:
            data_from_db = get_data_from_db(col_a, col_b, start_date_str, '00:00:00', '23:59:59', fetch_every_n_sec)
            df = df.append(data_from_db, ignore_index=True)
        except:
            pass
    else:
        start_date = datetime.strptime(start_date_str, '%Y_%m_%d').date()
        stop_date = datetime.strptime(stop_date_str, '%Y_%m_%d').date()
        
        days_in_range=[]
        date = start_date
        days_in_range.append(date)
        while date + timedelta(days=1) <= stop_date:
            date = date + timedelta(days=1)
            days_in_range.append(date)

        df = pd.DataFrame()
        for day in days_in_range:
            try:
                data_from_db = get_data_from_db(col_a, col_b, day.strftime("%Y_%m_%d"), '00:00:00', '23:59:59', fetch_every_n_sec)
                df = df.append(data_from_db, ignore_index=True)
            except:
                pass
    
    start = datetime.strptime(start_date_time, '%Y_%m_%d %H:%M:%S')
    stop  = datetime.strptime(stop_date_time, '%Y_%m_%d %H:%M:%S')
    df = df[df[0] >= start]
    df = df[df[0] <= stop]
    return df




