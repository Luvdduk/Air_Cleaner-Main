import serial
import time
import pymysql
import random


power_state=1
fan_speed="MID"


# DB 연결
dust_db = pymysql.connect(
    user='luvdduk', 
    passwd='alrkd4535', 
    host='127.0.0.1', 
    db='air-cleaner', 
    charset='utf8'
)
cursor = dust_db.cursor(pymysql.cursors.DictCursor)
pm1=0
pm25=0
pm10=0
fan_state = "MID"
def loop():
    global pm1, pm25, pm10, power_state
    while True:
        pm1= random.randrange(101)
        pm25= random.randrange(101)
        pm10= random.randrange(101)
        print("================")
        print("pm1: %d\npm2.5: %d\npm10: %d" %(pm1, pm25, pm10))
        print("================")

        # cursor.execute("INSERT INTO status(powerstate, PM1, PM25, PM10) VALUES ('%d', '%d','%d','%d')"%(power_state, pm1, pm25, pm10))
        # dust_db.commit()

        time.sleep(3)



if __name__ == "__main__":
    loop()