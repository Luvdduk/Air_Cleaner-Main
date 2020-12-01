# app.py
from flask import Flask, render_template, jsonify, request
# import main
import time
from threading import Thread
import maintest
import database
import pandas as pd

#Flask 객체 인스턴스 생성
app = Flask(__name__)

@app.route('/') # index.html 렌더링
def index():
  return render_template('index.html')

@app.route('/graph') # graph.html 렌더링
def graph():
  return render_template('graph.html')

@app.route('/dustinfo') # dustinfo.html 렌더링
def dustinfo():
  return render_template('dustinfo.html')

@app.route('/fan_speed') # fan_speed.html 렌더링
def fan_speed():
  return render_template('fan_speed.html')

@app.route('/poweron') # main 전원변수 0으로
def poweron():
  print ("poweron")
  maintest.power_state = 1
  return ("nothing")

@app.route('/poweroff') # main 전원변수 1로
def poweroff():
  print ("poweroff")
  maintest.power_state = 0
  return ("nothing")

@app.route('/modeauto') # main 전원변수 2로
def modeauto():
  print ("automode")
  maintest.power_state = 2
  return ("nothing")

@app.route('/fanslow') # main 팬 PWM Value값 0.3으로 변경
def fanslow():
  print ("fanslow")
  # main.fan_pwm.value = 0.3
  # main.fan_state = "SLOW"
  return ("nothing")

@app.route('/fanmid') # main 팬 PWM Value값 0.65으로 변경
def fanmid():
  print ("fanmid")
  # main.fan_pwm.value = 0.65
  # main.fan_state = "MID"
  return ("nothing")

@app.route('/fanfull') # main 팬 PWM Value값 1로 변경
def fanfull():
  print ("fanfull")
  # main.fan_pwm.value = 1.0
  # main.fan_state = "FULL"
  return ("nothing")


@app.route('/hours_graph', methods = ['GET']) # 1시간별 데이터 반환, GET요청만 허용
def hours_graph():
  #database.py의 list변수를 데이터프레임으로 변환
  df = pd.DataFrame(database.oneday_hours_mean())
  df = df.set_index("hours") # index를 Hours 변수로 지정 (1~24)
  return df.to_json() # json타입으로 변환하여 리턴

@app.route('/days_graph', methods = ['GET']) # 1일별 데이터 반환, GET요청만 허용
def days_graph():
  #database.py의 list변수를 데이터프레임으로 변환
  df = pd.DataFrame(database.oneweek_days_mean())
  df = df.set_index("days_ago")# index를 Days_ago 변수로 지정 (1~7)
  return df.to_json() # json타입으로 변환하여 리턴


@app.route('/stuff', methods = ['GET']) # 실시간 데이터 반환, GET요청만 허용
def stuff():
  # main에서 변수를 실시간으로 연동해서, json타입으로 변환해서 리턴
  return jsonify(pm1=maintest.pm1, pm25= maintest.pm25, pm10=maintest.pm10, power_state=maintest.power_state, fan_speed=maintest.fan_state)
  # return jsonify(pm1=main.pm1, pm25= main.pm25, pm10=main.pm10, power_state=main.power_state, fan_speed=main.fan_state)

if __name__=="__main__":
  # Thread(target=main.Button_Ctrl).start() # 쓰레드0
  Thread(target=maintest.loop).start() # 쓰레드1
  app.run(host="0.0.0.0", debug=True) # 쓰레드2
  
  
  # host 등을 직접 지정하고 싶다면
  # app.run(host="0.0.0.0", port="5000", debug=True)