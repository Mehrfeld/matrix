import mysql.connector
import pandas as pd
import time
from datetime import datetime, timedelta

class DB_Reader:

    MYSQL_HOST='localhost'
    MYSQL_USER='root'
    MYSQL_PASSWORD='th6nw7hg'
    DB_NAME='dash_main'
    table_name = 'general_data'

    def __init__(self, MYSQL_HOST=MYSQL_HOST, MYSQL_USER=MYSQL_USER, MYSQL_PASSWORD=MYSQL_PASSWORD, DB_NAME=DB_NAME):
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
                    database=DB_NAME)
            except mysql.connector.Error as err:
                print("Something went wrong: {}".format(err))
                connection_flag = False
        self.mydb = mydb

    def reset(self):
        self.__init__()


    def get_dates_list(self):

        try: mycursor = self.mydb.cursor()   
        except:
            self.reset()
            mycursor = self.mydb.cursor()


        mycursor.execute('SELECT date FROM calendar')
        df = pd.DataFrame(mycursor.fetchall())
        mycursor.close()
        self.mydb.commit()

        list_of_days = []
        for item in df[0].tolist():
            list_of_days.append(item.strftime('%Y_%m_%d'))

        return list_of_days


    
    # date format: "2020_01_06",  time format "18:00:00"

    # def get_data_from_db(self, col_a='date_time_utc', col_b='input_1', date='2020_03_01', start_time='00:00:00', stop_time='23:59:59', fetch_every_n_sec = '10'): 
        
    #     mycursor = self.mydb.cursor()  

    #     start_date_time = date + " " + start_time
    #     stop_date_time = date + " " + stop_time     
    #     mycursor.execute("SELECT SQL_NO_CACHE {}, {} FROM {} WHERE id % {} = 0 AND date_time_utc between '{}' and '{}'".format(col_a, col_b, date, fetch_every_n_sec,  start_date_time, stop_date_time))
    #     df = pd.DataFrame(mycursor.fetchall())
    #     mycursor.close()
    #     self.mydb.commit()
    #     return df




    # date format: "2020_01_06",  time format "18:00:00" / used for reading data collected in one table named "general_data"
    def get_data_generic__(self, col_a='date_time_utc', data_columns=['input_1'], start_date_time='2020_03_01 10:00:00', stop_date_time='2020_03_02 12:00:00', fetch_every_n_sec=10): 
        
        columns = []
        for item in data_columns:
            if item != 'empty':
                columns.append(item)
            else: pass
        data_columns = columns


        if data_columns == []:
            df__ = pd.DataFrame({0:[datetime.strptime(start_date_time, "%Y_%m_%d %H:%M:%S"), datetime.strptime(stop_date_time, "%Y_%m_%d %H:%M:%S")], 1 :[0.0, 0.0]})
            return df__
        else: pass

        try: mycursor = self.mydb.cursor()   
        except:
            self.reset() 
            mycursor = self.mydb.cursor()

        table_name = 'general_data'
        string_of_data_columns = ', '.join(data_columns)
        mycursor.execute("SELECT SQL_NO_CACHE {}, {} FROM {} WHERE id % {} = 0 AND date_time_utc between '{}' and '{}'".format(col_a, string_of_data_columns, table_name, fetch_every_n_sec,  start_date_time, stop_date_time))
        df = pd.DataFrame(mycursor.fetchall())
        mycursor.close()
        self.mydb.commit()
        return df

      
    
    # def get_data_generic(self, col_a='date_time_utc', col_b=['input_1'], start_date_time='2020_03_01 10:00:00', stop_date_time='2020_03_02 12:00:00', fetch_every_n_sec=10):
    #     df_list=[]
    #     for input in col_b:
    #         start_date_str = start_date_time.split()[0]
    #         stop_date_str =stop_date_time.split()[0]
    #         if start_date_str == stop_date_str:
    #             df = pd.DataFrame()
    #             try:
    #                 data_from_db = self.get_data_from_db(col_a, input, start_date_str, '00:00:00', '23:59:59', fetch_every_n_sec)
    #                 df = df.append(data_from_db, ignore_index=True)
    #             except:
    #                 pass
    #         else:
    #             start_date = datetime.strptime(start_date_str, '%Y_%m_%d').date()
    #             stop_date = datetime.strptime(stop_date_str, '%Y_%m_%d').date()
                
    #             days_in_range=[]
    #             date = start_date
    #             days_in_range.append(date)
    #             while date + timedelta(days=1) <= stop_date:
    #                 date = date + timedelta(days=1)
    #                 days_in_range.append(date)

    #             df = pd.DataFrame()
    #             for day in days_in_range:
    #                 try:
    #                     data_from_db = self.get_data_from_db(col_a, input, day.strftime("%Y_%m_%d"), '00:00:00', '23:59:59', fetch_every_n_sec)
    #                     df = df.append(data_from_db, ignore_index=True)
    #                 except:
    #                     pass
            
    #         start = datetime.strptime(start_date_time, '%Y_%m_%d %H:%M:%S')
    #         stop  = datetime.strptime(stop_date_time, '%Y_%m_%d %H:%M:%S')
    #         df = df[df[0] >= start]
    #         df = df[df[0] <= stop]

    #         df_list.append(df)

    #     return df_list

