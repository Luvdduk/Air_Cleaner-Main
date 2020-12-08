from gpiozero import Button, RGBLED, DigitalOutputDevice, PWMOutputDevice
from colorzero import Color
from signal import pause
from threading import Thread
import time
import serial
from PMS7003 import PMS7003
import lcd_i2c as lcd
from configparser import ConfigParser
import pymysql
import requests
import json
import datetime

# 핀 설정
powersw = Button(24) # 전원버튼
fansw= Button(26) # 팬속버튼
fan_pwm = PWMOutputDevice(12) # 모터드라이버 pwm
fan_pin1 = DigitalOutputDevice(5) # 모터드라이버 IN1
fan_pin2 = DigitalOutputDevice(6) # 모터드라이버 IN2
led = RGBLED(16, 20, 21) # rgb led

# 초기 전원
power_state=0

#먼지센서 오브젝트
dustlib = PMS7003()

# 시리얼
Speed = 9600
SERIAL_PORT = '/dev/ttyUSB0'

# DB 연결
dust_db = pymysql.connect(
    user='luvdduk', 
    passwd='qazwsxedc123', 
    host='aircleaner.software', 
    db='air-cleaner', 
    charset='utf8'
)
cursor = dust_db.cursor(pymysql.cursors.DictCursor)

# 팬 on/off
ON = 1
OFF = 0

# 팬속
FULL = 1.0
MID = 0.65
SLOW = 0.3


# config.ini 가 있으면 로드 없으면 에러
try:
    conf = ConfigParser()# 설정파일 로드
    conf.read('config.ini')
    fan_state = conf['FAN']['fan_speed']# 팬속 로드
    print("설정파일 팬속도: %s" %fan_state)
except:
    print("설정파일 로드 오류")

# pwm변수로 지정
if fan_state == "FULL":
    fan_pwm.value = 1.0
elif fan_state == "MID":
    fan_pwm.value = 0.65
elif fan_state == "SLOW":
    fan_pwm.value = 0.3
else:
    print("설정파일 로드 오류")

lcd.lcd_init()# lcd초기화

def Button_Ctrl(): # 버튼 제어
    global power_state
    global fan_state
    powersw.when_pressed = powerctrl #파워버튼 누르면 실행
    fansw.when_pressed = fan_speedsw #팬속도 조정버튼 누르면 실행
    pause() # 누를때까지 대기

# 파워 꺼짐: 0, 켜짐: 1, 자동: 2
def powerctrl(): # 전원버튼 누를때마다 실행
    global power_state
    if power_state == 0: # 전원꺼짐 상태일때 전원켬
        power_state = 1
        print("전원켬")
        return
    if power_state == 1: # 전원켜짐 상태일 때 자동모드로 변경
        power_state = 2
        print("자동모드로 변경")
        return
    if power_state == 2: # 자동모드일때 전원꺼짐 상태로 변경
        power_state = 0
        print("전원끔")
        return


def fan_speedsw(): # 팬 스피드 조절, 팬속버튼 누를때마다 실행
    global fan_state, power_state
    if power_state == 1: #일반모드, 전원켜짐 상태에서만 동작
        if fan_state == "SLOW": # 팬속도가 1단계일때 2단계로 변경
            fan_pwm.value = 0.65
            fan_state = "MID"
            conf['FAN']['fan_speed'] = fan_state
            with open('config.ini', 'w') as configfile:
                conf.write(configfile)
            print("팬속도: %f"%fan_pwm.value)
            return
        if fan_state == "MID": # 팬속도가 2단계일때 3단계로 변경
            fan_pwm.value = 1
            fan_state = "FULL"
            conf['FAN']['fan_speed'] = fan_state
            with open('config.ini', 'w') as configfile:
                conf.write(configfile)
            print("팬속도: %f"%fan_pwm.value)
            return
        if fan_state == "FULL": # 팬속도가 3단계일때 1단계로 변경
            fan_pwm.value = 0.3
            fan_state = "SLOW"
            conf['FAN']['fan_speed'] = fan_state
            with open('config.ini', 'w') as configfile:
                conf.write(configfile)
            print("팬속도: %f"%fan_pwm.value)
            return
    else:
        print("일반모드에서만 동작")



# 팬 on/off 제어
def fan_power(state):
    if state: # 1이 입력되면 팬 전원 켬
        fan_pin1.on() # 순방향으로 동작
        fan_pin2.off()
    else: # 팬 전원 끔
        fan_pin1.off()
        fan_pin2.off()

# lcd에 먼지농도 표시, 매개변수로 pm1, pm25, pm10변수를 전달받음
def display_dust(duststate1, duststate2, duststate3):
    global power_state, fan_state
    # 좋음
    if duststate3 <= 30 and (duststate1 + duststate2) <= 15 :
        lcd.lcd_string("     GOOD      ", lcd.LCD_LINE_1)
        led.color = Color("blue") # led 색 지정 파랑
        if power_state == 2: #자동모드 팬 속도 30%
            fan_power(OFF)
            
    # 보통
    elif  duststate3 <= 80 and (duststate1 + duststate2) <= 35:
        lcd.lcd_string("     NORMAL    ", lcd.LCD_LINE_1)
        led.color = Color("green") # led 색 지정 초록
        if power_state == 2: #자동모드 팬 속도 30%
            fan_power(ON)
            fan_pwm.value = 0.3
            fan_state = "SLOW"
    # 나쁨
    elif duststate3 <= 150 and (duststate1 + duststate2) <= 75:
        lcd.lcd_string("      BAD      ", lcd.LCD_LINE_1)
        led.color = Color("yellow") # led 색 지정 노랑
        if power_state == 2:#자동모드 팬 속도 65%
            fan_power(ON)
            fan_pwm.value = 0.65
            fan_state = "MID"
    # 매우나쁨
    elif duststate3 > 150 or (duststate1 + duststate2) > 75:
        lcd.lcd_string("    VERY BAD   ", lcd.LCD_LINE_1)
        led.color = Color("red") # led 색 지정 빨강
        if power_state == 2: #자동모드 팬 속도 100%
            fan_power(ON)
            fan_pwm.value = 1
            fan_state = "FULL"
    else:
        print("LCD표기 오류 or 먼지센서 데이터 오류")
    
    # pm1.0 표시
    lcd.lcd_string("PM1.0: %dug/m3 " %duststate1, lcd.LCD_LINE_2)
    powersw.wait_for_press(timeout=2)
    if powersw.is_pressed:
        return
    # pm2.5 표시
    lcd.lcd_string("PM2.5: %dug/m3 " %duststate2, lcd.LCD_LINE_2)
    powersw.wait_for_press(timeout=2)
    if powersw.is_pressed:
        return
    # pm10 표시
    lcd.lcd_string("PM10: %dug/m3  " %duststate3, lcd.LCD_LINE_2)
    return



# 메인루프
def loop():
    global power_state, fan_state
    while True:

        # 먼지센서 동작
        ser = serial.Serial(SERIAL_PORT, Speed, timeout = 1)
        buffer = ser.read(1024)
        if(dustlib.protocol_chk(buffer)):
            data = dustlib.unpack_data(buffer)
            global pm1, pm25, pm10
            # 변수에 데이터 저장
            pm1 = int(data[dustlib.DUST_PM1_0_ATM])
            pm25 = int(data[dustlib.DUST_PM2_5_ATM])
            pm10 = int(data[dustlib.DUST_PM10_0_ATM])

            now = datetime.datetime.now()
            # db에 데이터 저장
            cursor.execute("INSERT INTO status(timestamp, powerstate, PM1, PM25, PM10) VALUES ('%s', '%d', '%d','%d','%d')"%(now, power_state, pm1, pm25, pm10))
            dust_db.commit()
            print("====================")
            print ("PMS 7003 dust data")
            print ("PM 1.0 : %d" % (pm1))
            print ("PM 2.5 : %d" % (pm25))
            print ("PM 10.0 : %d" % (pm10))
            print("====================")
        else:
            print ("먼지센서 데이터 read 오류")

        # 서버통신 - 데이터 수신
        try:
            r_get_order = requests.get('http://aircleaner.software/senddata') #데이터 요청
            order = r_get_order.json()# 데이터 json타입으로 저장
            print(order)
        except :
            print("#################")
            print("리퀘스트 수신 에러")
            print("#################")
        
        if order['power_on'] == True: # 수신값 받아서 설정 변경
            power_state = 1
        if order['power_off']:
            power_state = 0
        if order['auto_mode']:
            power_state = 2
        if order['fan_slow']:
            fan_state = "SLOW"
            fan_pwm.value = 0.3
        if order['fan_mid']:
            fan_state = "MID"
            fan_pwm.value = 0.65
        if order['fan_full']:
            fan_state = "FULL"
            fan_pwm.value = 1
        
        conf['FAN']['fan_speed'] = fan_state # 팬 속도 저장
        with open('config.ini', 'w') as configfile:
            conf.write(configfile)

        send_data = { #보낼 데이터
            'power_state':power_state,
            'fan_state': fan_state,
            'pm1' : pm1,
            'pm25' : pm25,
            'pm10' : pm10
        }
        # 서버통신 - 데이터 전송
        send_data = json.dumps(send_data) # json타입으로 변경
        print(send_data)
        try:
            r_send_data = requests.post('http://aircleaner.software/receivedata', data = send_data ) #json을 post 방식으로 전송
        except:
            print("#################")
            print("리퀘스트 전송 에러")
            print("#################")



        # 전원 상태에 따른 동작
        if power_state == 0:
            print("전원꺼짐")
            fan_power(OFF) #팬 off
            led.off() #led off
            lcd.LCD_BACKLIGHT = 0x00 #lcd 백라이트 off
            lcd.lcd_string("   Power Off   ", lcd.LCD_LINE_1)
            lcd.lcd_string("", lcd.LCD_LINE_2)
        if power_state == 1:
            print("전원켜짐")
            fan_power(ON) #팬 on
            # led.on() #led on
            lcd.LCD_BACKLIGHT = 0x08 #lcd 백라이트 on
            lcd.lcd_string("   Power On    ", lcd.LCD_LINE_1)
            lcd.lcd_string("", lcd.LCD_LINE_2)
            time.sleep(1)
            display_dust(pm1, pm25, pm10) #매개변수로 데이터 전달
        if power_state == 2:
            print("자동모드")
            # led.on() #led on
            lcd.LCD_BACKLIGHT = 0x08 #lcd 백라이트 on
            lcd.lcd_string("   Auto Mode   ", lcd.LCD_LINE_1)
            lcd.lcd_string("", lcd.LCD_LINE_2)
            time.sleep(1)
            display_dust(pm1, pm25, pm10) #매개변수로 데이터 전달
        time.sleep(1)



if __name__ == "__main__":
    # 쓰레딩
    Thread(target=Button_Ctrl).start()
    Thread(target=loop).start()