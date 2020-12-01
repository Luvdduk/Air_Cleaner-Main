import pymysql
import datetime
import json
import pandas as pd
from random import randrange as rd


# DB 연결, DB참조 오류로 인해 각각 지정
dust_db = pymysql.connect(
    user='luvdduk', 
    passwd='alrkd4535', 
    host='127.0.0.1', 
    db='air-cleaner', 
    charset='utf8'
)
dust_db2 = pymysql.connect(
    user='luvdduk', 
    passwd='alrkd4535', 
    host='127.0.0.1', 
    db='air-cleaner', 
    charset='utf8'
)


def oneday_hours_mean():
    cursor1 = dust_db.cursor(pymysql.cursors.DictCursor) # DB커서 지정
    NowDate = datetime.datetime.now() # 현재시간
    left24h = NowDate - datetime.timedelta(days=1) # 24시간전
    cursor1.execute("SELECT * FROM status WHERE TIMESTAMP(timestamp) BETWEEN '%s' AND '%s';"%(left24h, NowDate)) # DB 데이터 선택
    df = cursor1.fetchall() # 변수에 데이터 저장
    df = pd.DataFrame(df) # 데이터프레임으로 변경
    hour = 1
    hours_mean = list() # 반환타입 리스트 변수로 지정
    while hour <= 24:
        if hour > 0:
            start_time = datetime.datetime.now() - datetime.timedelta(hours=hour) # 시작시간 부터
            end_time = start_time + datetime.timedelta(hours=1) # 끝나는시간까지
            one_hour = (df['timestamp']>= start_time) & (df['timestamp']< end_time) # 데이터 추출
            df_1h = df.loc[one_hour]
            mean_1h = { "hours" : hour, "time": start_time.strftime("%Y-%m-%d %H:%M:%S"), "pm1": df_1h['PM1'].mean(), "pm25": df_1h['PM25'].mean(), "pm10": df_1h['PM10'].mean()} # 데이터별 평균을 구해서, dict형식으로 저장
        hours_mean.append(mean_1h) # dict변수 mean1_h를 list변수 hours_mean에 추가
        hour += 1
    return hours_mean # list변수 리턴


def oneweek_days_mean():
    cursor = dust_db2.cursor(pymysql.cursors.DictCursor) # DB커서 지정
    NowDate = datetime.datetime.now() # 현재시간
    left7d = NowDate - datetime.timedelta(days=8) # 24시간전
    cursor.execute("SELECT * FROM status WHERE TIMESTAMP(timestamp) BETWEEN '%s' AND '%s';"%(left7d, NowDate)) # DB 데이터 선택
    df = cursor.fetchall() # 변수에 데이터 저장
    df = pd.DataFrame(df) # 데이터프레임으로 변경
    days = 0
    days_mean = list()
    while days <= 7:
        day = datetime.date.today() - datetime.timedelta(days=days) # 평균 낼 날자 지정
        day = datetime.datetime.combine(day, datetime.time()) # datetime -> date 형식으로 변경
        one_day = (df['timestamp']>= day) & (df['timestamp']< (day + datetime.timedelta(hours=24))) # 1일동안으로 범위 지정
        df_1d = df.loc[one_day]
        mean_1d = {"days_ago": days, "date":day.strftime("%Y-%m-%d"), "pm1": df_1d['PM1'].mean(), "pm25": df_1d['PM25'].mean(), "pm10": df_1d['PM10'].mean()} # 데이터별 평균을 구해서, dict형식으로 저장
        days_mean.append(mean_1d)# dict변수 mean_1d를 list변수 days_mean에 추가
        days += 1
    return days_mean # list변수 리턴

def dummy_week():
    cursor = dust_db2.cursor(pymysql.cursors.DictCursor)
    a = 0
    while a<8:
        start_date = datetime.datetime(2020,11,13,14,0) + datetime.timedelta(days=a)
        cursor.execute("INSERT INTO status(timestamp, powerstate, PM1, PM25, PM10) VALUES ('%s','%d','%d','%d','%d')"%(start_date, 1, rd(3,11), rd(5,21), rd(9,41)))
        dust_db.commit()
        a += 1

def dummy_day():
    cursor = dust_db2.cursor(pymysql.cursors.DictCursor)
    a = 0
    while a<24:
        start_date = datetime.datetime(2020,11,19,0,0) + datetime.timedelta(hours=a)
        cursor.execute("INSERT INTO status(timestamp, powerstate, PM1, PM25, PM10) VALUES ('%s','%d','%d','%d','%d')"%(start_date, 1, rd(3,11), rd(5,21), rd(9,41)))
        dust_db.commit()
        a += 1



if __name__ == "__main__":
    # print(oneweek_days_mean())
    print(oneday_hours_mean())
    # dummy_day()


















