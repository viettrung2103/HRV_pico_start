from ssd1306 import SSD1306_I2C
from fifo import Fifo
from machine import UART, Pin, I2C, Timer, ADC
from piotimer import Piotimer
import math
import time
import ujson
# import network
# # from time import sleep
# from umqtt.simple import MQTTClient

from mqtt import Mqtt

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
Y_ROW_6 = Y_ROW_5 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_7 = Y_ROW_6 + COLUMN_SPACE + LETTER_HEIGHT



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
# MIN_HR = 50
# MAX_HR = 240 - age
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

Y_ROW_1 = 0
Y_ROW_2 = COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_3 = Y_ROW_2 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_4 = Y_ROW_3 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_5 = Y_ROW_4 + COLUMN_SPACE + LETTER_HEIGHT


#MQTT
SSID = "KMD658_Group_4"
PASSWORD = "00000000"
BROKER_IP = "192.168.4.253"



class Opt22_Display:
    def __init__(self, i2c, scl_pin, sda_pin, frequency, oled_w, oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda=sda_pin, freq=frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)

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


class Opt22:
    def __init__(self,name, display,encoder,mqtt, selector = None, data = None, ):
        self.name = name
        self.display = display
        self.encoder = encoder
        self.stop_flag = False
        self.selector = selector
        self.press = False
        self.data = data
        self.error_flag = False
        self.connect_flag = False
        self.mqtt = mqtt
        
    def is_active(self):
        return self.current_flag
    
    

            
    def create_data(self):
        file_name = "result_21.json"
        data = util.read_file(file_name)        
        return data
            

    
    def on(self):
        data_json = self.create_data()
        data_str = ujson.dumps(data_json)
        
        self.press = False
        self.stop_flag = False
        self.encoder.update_program(self)
        self.mqtt.default_setting()
        self.mqtt.add_data(data_str)
        self.run()

    def is_connected():
        return True

    def run(self):
        while self.stop_flag == False and self.mqtt.stop_flag == False:
            self.display.show()
            self.mqtt.run()
            self.handle_press()
        

            if self.mqtt.error_flag == True :
                self.stop()
            if self.mqtt.stop_flag == True:
                self.stop()
        self.stop()

    def stop(self):

        self.press = True
            
            
    def handle_press(self):
        p22_fifo = self.encoder.p22_fifo

        while p22_fifo.has_data():
            value = p22_fifo.get()

            if value == 1:
                self.stop_flag == True
                self.press = True
            


    def off(self):
        self.press = False
        self.stop_flag = True
        self.encoder.stop_flag = True
        self.mqtt.stop_flag = True
        self.mqtt.data = None
        
