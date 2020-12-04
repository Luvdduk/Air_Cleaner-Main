import pymysql
import datetime
import json
from random import randrange as rd

dust_db = pymysql.connect(
    user='luvdduk', 
    passwd='qazwsxedc123', 
    host='aircleaner.software', 
    db='air-cleaner', 
    charset='utf8'
)

def dummy_week():
    cursor = dust_db.cursor(pymysql.cursors.DictCursor)
    a = 0
    while a<8:
        start_date = datetime.datetime.now() - datetime.timedelta(days=a)
        try:
            cursor.execute("INSERT INTO status(timestamp, powerstate, PM1, PM25, PM10) VALUES ('%s','%d','%d','%d','%d')"%(start_date, 1, rd(1,8), rd(1,16), rd(1,36)))
            dust_db.commit()
        except KeyError:
            pass
        a += 1

def dummy_day():
    cursor = dust_db.cursor(pymysql.cursors.DictCursor)
    a = 1
    while a<24:
        start_date = datetime.datetime.now() - datetime.timedelta(hours=a)
        try: 
            cursor.execute("INSERT INTO status(timestamp, powerstate, PM1, PM25, PM10) VALUES ('%s','%d','%d','%d','%d')"%(start_date, 1, rd(1,8), rd(1,16), rd(1,36)))
            dust_db.commit()
        except KeyError:
            pass
        a += 1



if __name__ == "__main__":
    dummy_day()
    dummy_week()
