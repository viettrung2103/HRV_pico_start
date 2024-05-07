from ssd1306 import SSD1306_I2C
from fifo import Fifo
from machine import UART, Pin, I2C, Timer, ADC
from piotimer import Piotimer
import math
import time
import ujson

import urequests as requests
import ujson
import network
# from time import sleep
from kubios import Kubios
from mqtt import Wlan
import gc


from encoder import Isr_Fifo, Encoder
import util

import micropython
micropython.alloc_emergency_exception_buf(200)


# const for display
I2C_MODE = 1
SCL_PIN = Pin(15)
SDA_PIN = Pin(14)
FREQ = 400000

OLED_WIDTH = 128
OLED_HEIGHT = 64
ROW_START = 0
ROW_EDGE = OLED_WIDTH - 1 #127
HEIGHT_START = 0
HEIGHT_EDGE = OLED_HEIGHT -1 #63

BLANK = 0
FILLED = 1
COLUMN_SPACE = 2
LETTER_HEIGHT = 8
LETTER_WIDTH = 8
Y_ROW_1 = 0
Y_ROW_2 = COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_3 = Y_ROW_2 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_4 = Y_ROW_3 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_5 = Y_ROW_4 + COLUMN_SPACE + LETTER_HEIGHT


#hr
t = 4 #4ms
frequency = 250
MINUTE = 60
SECOND = 1
THOUSAND = 1000
TWO = 2
test_duration = TWO  * SECOND * THOUSAND # to ms
duration = TWO * SECOND * THOUSAND

# total_time = 2 * SECOND
test_sample_size =round(test_duration / t , 0)
sample_size = round(duration / t, 0)
step = 3

age = 30

MIN_HR = 50
MAX_HR = 150



MAX_ADC = 2 ** 16 -1
MIN_ADC = 0
DELTA = MAX_ADC - MIN_ADC
PERCENT = 0.12
LOWER_LIM = round(DELTA * PERCENT,0)

#for encoder
ROT_A_PIN = Pin(10)
ROT_B_PIN = Pin(11)
ROT_SW_PIN = Pin(12)
BOUNCE_TIME = 200




#MQTT
SSID = "KMD658_Group_4"
PASSWORD = "00000000"
BROKER_IP = "192.168.4.253"

#kubios
APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"

LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"
ANALYSIS_URL = "https://analysis.kubioscloud.com/v2/analytics/analyze"



class Opt32_Display:
    def __init__(self, i2c, scl_pin, sda_pin, frequency, oled_w, oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda=sda_pin, freq=frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)
#         self.current_flag = True

    def reset(self):
        self.display.fill(0)
    
    def show(self):

        text1 = "Sending Data..."
        text2 = "DO NOT PRESS"
        
        x1 = util.get_x_starting(text1)
        x2 = util.get_x_starting(text2)
        self.reset()
        self.display.text(text1,x1,Y_ROW_3)
        self.display.text(text2,x2,Y_ROW_5)

        self.display.show()


class Opt32:
    def __init__(self,name, display,encoder,kubios,wlan, selector = None, data = None, ):
        self.name = name
        self.display = display
        self.encoder = encoder
        self.selector = selector
        self.kubios = kubios
        self.wlan = wlan
        # self.response_file_name = "response_32.json"
        self.ppi_list = None        
#         self.response = None
        self.stop_flag = False
        self.error_flag = False
        # self.connect_flag = False
        self.press = False
        self.history_name = "history.json"
        
    
    def add_ppi_list(self):
        if self.ppi_list == None:
            file_name = "ppi_list_31.json"
            data = util.read_file(file_name)
            self.ppi_list = data['ppi_list']
            print(self.ppi_list)    

            
    
    def on(self):
        gc.collect()
        print("Free memory:", gc.mem_free(), "bytes")
        self.press = False
        self.stop_flag = False
        self.encoder.update_program(self)
        self.kubios.on()
        self.kubios.default_setting()
        # ppi_list = [664, 844, 856, 764, 648, 804, 724, 812, 896, 796, 804, 736, 800, 788, 856, 832, 884]
        self.add_ppi_list()
        self.kubios.add_ppi_list(self.ppi_list)
        if not self.wlan.is_connected():
            self.wlan.connect_wlan()
        else:
            self.run()
            print("Free memory:", gc.mem_free(), "bytes")
            gc.collect()

    def is_connected():
        return True

    def run(self):
        self.display.show()
        if self.stop_flag == False :
            if self.kubios.stop_flag == False:
                self.run_kubios()

        self.stop()

        
    
    def run_kubios(self):
        self.kubios.run()
        if self.kubios.error_flag == True :
            print('error')
            self.error_flag = True
            self.stop_flag = True
        if self.kubios.stop_flag == True:
            self.stop_flag = True
    
    def stop(self):
        # if self.is_connected():
        if self.stop_flag == True:
            self.press = True
            
            
    def handle_press(self):
        p32_fifo = self.encoder.p32_fifo
        # print(p32_fifo.has_data())
        while p32_fifo.has_data():
            value = p32_fifo.get()
            print(value)
            if value == 1:
                if self.kubios.stop_flag == True:
                    self.stop_flag == True
                    self.press = True

    def off(self):
        self.press = False
        self.stop_flag = True
        self.encoder.stop_flag = True
        self.kubios.stop_flag = True

