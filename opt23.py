from ssd1306 import SSD1306_I2C
from fifo import Fifo

from machine import UART, Pin, I2C, Timer, ADC
from piotimer import Piotimer
import math
import time
import ujson

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

#const for led
LED1_PIN = Pin(22)
LED2_PIN = Pin(21)
LED3_PIN = Pin(20)
ON = 1 # for led, 1 is on, 0 is off
OFF = 0



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

# MIN_PULSE = 1
# MAX_PULSE = 6

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

        

class Opt23_Display:
    def __init__(self, i2c, scl_pin, sda_pin, frequency, oled_w, oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda=sda_pin, freq=frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)
        self.mean_hr_str = "0"
        self.mean_ppi_str = "0"
        self.rmssd_str = "0"
        self.sdnn_str = "0"
        self.stop_flag = True
        self.update_flag = False
#         self.current_flag = True

    def update_str(self, mean_hr, mean_ppi, rmssd, sdnn):
        if self.update_flag == False:
            # self.mean_hr_str = f"MEAN_HR  = {str(int(mean_hr))} BPM"
            # self.mean_ppi_str = f"MEAN_PPI = {str(int(mean_ppi))}ms" 
            # self.rmssd_str = f"RMSSD    = {str(int(round(rmssd,0)))}"
            # self.sdnn_str = f"SDNN     = {str(int(round(sdnn,0)))}"
            self.mean_hr_str = f"MEAN_HR = {str(mean_hr)} BPM"
            self.mean_ppi_str = f"MEAN_PPI= {str(mean_ppi)}ms" 
            self.rmssd_str = f"RMSSD   = {str(rmssd)}"
            self.sdnn_str = f"SDNN    = {str(sdnn)}"
            self.update_flag = True
        
        
    def reset(self):
        self.display.fill(0)
    
    def show(self):
        text1 = self.mean_hr_str
        text2 = self.mean_ppi_str
        text3 = self.rmssd_str
        text4 = self.sdnn_str

        self.reset()
        self.display.text(text1,0,Y_ROW_2)
        self.display.text(text2,0,Y_ROW_3)
        self.display.text(text3,0,Y_ROW_4)
        self.display.text(text4,0,Y_ROW_5)
        self.display.show()
        self.update_flag = False

class Opt23:
    def __init__(self,name, display,encoder, selector = None, response = None):
        self.name = name
        self.display = display
        self.encoder = encoder
        self.stop_flag = False
        self.selector = selector
        self.press = False
        self.response = response
        self.mean_hr = 0
        self.mean_ppi = 0
        self.rmssd = 0
        self.sdnn = 0
        
    def is_active(self):
        return self.current_flag
    
    def add_data(self,json_data):
        if json_data != None:
            data = ujson.loads(json_data)
            self.mean_hr = data["mean_hr"]
            self.mean_ppi = data["mean_ppi"]
            self.rmssd = data["rmssd"]
            self.sdnn = data["sdnn"]
            
    
    def on(self):
        self.press = False
        self.stop_flag = False
        self.encoder.update_program(self)
        self.run()

#         self.handle_turn()

    def run(self):
        self.display.update_str(self.mean_hr, self.mean_ppi, self.rmssd, self.sdnn)
        self.display.show()
        self.handle_press()

        
    def handle_press(self):
        p23_fifo = self.encoder.p23_fifo
        while p23_fifo.has_data():
            value = p23_fifo.get()
            print(f"program {self.name} press")
            if value == 1:
                self.stop_flag = True
                self.press = True
            


    def off(self):
        self.stop_flag = True
        self.encoder.stop_flag = True


# adc_pin_nr = 27
# sample_size = 500 # want 250
# test_sample_size = 500
# sample_rate = 250
# hz = 20
# wait = round(1/hz,2)
# 
# samples = Isr_Fifo(sample_size,adc_pin_nr)
#         
# encoder = Encoder(ROT_A_PIN,ROT_B_PIN,ROT_SW_PIN)
#         
# opt23_display = Opt23_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
# opt23 = Opt23("23",opt23_display,encoder)
# 
# while True:
#     opt23.on()



