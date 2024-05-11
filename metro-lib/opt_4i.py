# from machine import UART, Pin, I2C, Timer
from ssd1306 import SSD1306_I2C
from fifo import Fifo


from machine import UART, Pin, I2C, Timer, ADC
from piotimer import Piotimer
import math
import time

from encoder import Isr_Fifo, Encoder
from encoder import Isr_Fifo
import util
from history_list import History_List

import gc
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
ROW_SPACE = 1
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
X_DEFAULT = 0
Y_ROW_1 = 0
Y_ROW_2 = ROW_SPACE + LETTER_HEIGHT
Y_ROW_3 = Y_ROW_2 + ROW_SPACE + LETTER_HEIGHT
Y_ROW_4 = Y_ROW_3 + ROW_SPACE + LETTER_HEIGHT
Y_ROW_5 = Y_ROW_4 + ROW_SPACE + LETTER_HEIGHT
Y_ROW_6 = Y_ROW_5 + ROW_SPACE + LETTER_HEIGHT
Y_ROW_7 = Y_ROW_6 + ROW_SPACE + LETTER_HEIGHT

Y_ROW_LIST = [Y_ROW_1, Y_ROW_2, Y_ROW_3, Y_ROW_4, Y_ROW_5 ,Y_ROW_6 ,Y_ROW_7]


# from filefifo import Filefifo
# from fifo import Fifo
# from machine import UART, Pin, I2C, Timer, ADC
# from ssd1306 import SSD1306_I2C
# from piotimer import Piotimer
# import math
# import time

BOUNCE_TIME = 300


class Opt_4i_Display:
    def __init__(self, i2c, scl_pin, sda_pin, frequency, oled_w, oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda=sda_pin, freq=frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)
        self.program  = None
        self.timestamp_str = ""
        self.mean_hr_str = ""
        self.mean_ppi_str = ""
        self.rmssd_str = ""
        self.sdnn_str = ""
        self.sns_str = ""
        self.pns_str = ""
        self.stop_flag = True
        self.update_flag = False
#         self.current_flag = True

    def update_program(self,program):
#         print("inside here display")
        self.program = program
        
    def default_value(self):
        self.program  = None
        self.timestamp_str = ""
        self.mean_hr_str = ""
        self.mean_ppi_str = ""
        self.rmssd_str = ""
        self.sdnn_str = ""
        self.sns_str = ""
        self.pns_str = ""

            
    def update_str(self, response):
        if self.update_flag == False and self.program != None:
        # if json_data != None:
#             print("____")
            # print("data ",data["sns_index"])
            data = response['value']
#             print(data)
            mean_hr = util.convert_to_int(data["mean_hr"])
            mean_ppi = util.convert_to_int(data["mean_ppi"])
            rmssd = util.convert_to_int(data["rmssd"])
            sdnn = util.convert_to_int(data["sdnn"])
            
            self.mean_hr_str = f"MEAN HR : {mean_hr} "
            self.mean_ppi_str = f"MEAN PPI: {mean_ppi}" 
            self.rmssd_str = f"RMSSD   : {rmssd}"
            self.sdnn_str = f"SDNN    : {sdnn}"
            
            if self.program.name == "33" or self.program.name == "4i":
                ts = util.convert_timestamp_str(data["create_timestamp"])
                sns = data["sns"]
                pns = data["pns"]
                
                self.timestamp_str = "{}.{}.{} {}:{}".format(ts['dd'],ts['mm'],ts['yyyy'],ts['h'],ts['m'])
                self.sns_str = f"SNS     : {sns:.2}"
                # print(self.snd)
                self.pns_str = f"PNS     : {pns:.2}"
#                 print("pns ",self.pns_str)
                
        self.update_flag = True

    def reset(self):
        self.display.fill(0)
    
    def show(self):
#         print("show now")
        # text1 = self.mean_hr_str
        # text2 = self.mean_ppi_str
        # text3 = self.rmssd_str
        # text4 = self.sdnn_str
        self.reset()
    
        self.display.text(self.mean_hr_str,0,Y_ROW_2)
        self.display.text(self.mean_ppi_str,0,Y_ROW_3)
        self.display.text(self.rmssd_str,0,Y_ROW_4)
        self.display.text(self.sdnn_str,0,Y_ROW_5)
#         print("program name", self.program.name)
        if self.program.name == "4i":
            ts_str_x  = util.get_x_starting(self.timestamp_str)
            # print(self.timestamp_str)        
            self.display.text(self.timestamp_str,ts_str_x,Y_ROW_1)
            self.display.text(self.sns_str,0,Y_ROW_6)
            self.display.text(self.pns_str,0,Y_ROW_7)

        self.display.show()
        self.update_flag = False

        
class Opt4i:
    def __init__(self,name,display, encoder, obj, selector = None):
        self.name = name
        self.display = display
        self.encoder = encoder
        self.obj = obj
        self.selector = selector
        self.stop_flag = False
        self.press = False
        
    def on(self):
#         print("here now")
        self.encoder.update_program(self)
        self.display.update_program(self)
        self.press = False
        self.stop_flag = False

    def run(self):
        if self.stop_flag == False:
            # if not self.has_data():
            #     self.load_data()
            # else :
            self.display.update_str(self.obj)
            self.display.show()
            self.handle_press()
#         else:
#             # self.display.default_value()
#             # self.default_value()
#             # self.press = True
#             self.stop()

        
    def handle_press(self):
        p_fifo = self.encoder.p_x3_fifo
#         print("have data here")
        while p_fifo.has_data():
            value = p_fifo.get()
            print("take one from fifo")
            
            if value == 1:
                print("is press from 4i")
#                 print(f"program {self.name} press")                
                self.stop_flag = True
                self.press = True
#                 self.stop()
