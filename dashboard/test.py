import mysql.connector
import pandas as pd
import time
from datetime import datetime, timedelta

MYSQL_HOST='localhost'
MYSQL_USER='root'
MYSQL_PASSWORD='th6nw7hg'
DB_NAME='dash_main'


connection_flag = True
mydb = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    auth_plugin='mysql_native_password',
    passwd=MYSQL_PASSWORD,
    database=DB_NAME,
    buffered="True")

    
mycursor = mydb.cursor(buffered=True)
start = time.time()
mycursor.execute("SELECT date_time_utc, input_1, input_2 FROM 2020_05_29 WHERE date_time_utc between '2020_05_29 00:00:00' and '2020_05_29 23:59:59' ORDER BY date_time_utc")
end = time.time()
print (end - start)

df = pd.DataFrame(mycursor.fetchall())
print (df)
mycursor.close()
mydb.close()




