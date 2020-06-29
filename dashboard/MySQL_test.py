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
mycursor.execute('SELECT days AS days FROM \
                        (SELECT DATE(date_time_utc) AS days, COUNT(DATE(date_time_utc)) AS counts FROM general_data AS res GROUP BY DATE(date_time_utc) HAVING COUNT(DATE(date_time_utc)) > 1) \
                        AS dayslist')
end = time.time()
print (end - start)

# "SELECT date_time_utc, input_1, input_2 FROM general_data WHERE date_time_utc between '2020_06_09 16:00:00' and '2020_06_10 16:00:00' ORDER BY date_time_utc"
# "CREATE TABLE IF NOT EXISTS Calendar (id INT NOT NULL AUTO_INCREMENT, date DATE, comments TEXT, PRIMARY KEY (id))"

# SELECT days AS days FROM 
# (SELECT DATE(date_time_utc) AS days, COUNT(DATE(date_time_utc)) AS counts FROM general_data AS res WHERE DATE(date_time_utc) BETWEEN '2020-06-01' AND '2020-06-10' GROUP BY DATE(date_time_utc) HAVING COUNT(DATE(date_time_utc)) > 1) 
# AS dayslist


df = pd.DataFrame(mycursor.fetchall())
print (df)
mycursor.close()
mydb.close()




