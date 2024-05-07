# from machine import UART, Pin, I2C, Timer
from ssd1306 import SSD1306_I2C
from fifo import Fifo


from machine import UART, Pin, I2C, Timer, ADC
from piotimer import Piotimer
import math
import time

from encoder import Isr_Fifo, Encoder
import util
from history_list import History_List


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
X_DEFAULT = 0
Y_ROW_1 = 0
Y_ROW_2 = COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_3 = Y_ROW_2 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_4 = Y_ROW_3 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_5 = Y_ROW_4 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_6 = Y_ROW_5 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_7 = Y_ROW_6 + COLUMN_SPACE + LETTER_HEIGHT

Y_ROW_LIST = [Y_ROW_1, Y_ROW_2, Y_ROW_3, Y_ROW_4, Y_ROW_5 ,Y_ROW_6 ,Y_ROW_7]



        
class Program:
  def __init__(self,name):
    self.name = name
    
  def run(self):
    print(self.name)

class Opt40_Display:
    def __init__(self,i2c,scl_pin,sda_pin,frequency,oled_w, oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda = sda_pin, freq = frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)
        self.current_program = None
        self.stop_flag = False
        self.update_flag = True
        self.current_index = 0
        
        self.obj_str_list = []       
        
    def add_obj_str(self,obj_str):
        self.obj_str_list.append(obj_str)
        
    def reset(self):
        self.display.fill(0)
    
    def update_program(self,program):
        self.current_program = program
        
    def create_str_from_obj(self,obj):
        obj_str = Opt40_Str(obj["name"], X_DEFAULT, Y_ROW_LIST[obj["idx"]], obj)
        self.add_obj_str(obj_str)
        # return obj_str
    
    # def add
        

    def show_result(self,selector):
        if self.update_flag == True:
            self.reset()
            for index, history_str in enumerate(self.obj_str_list):
                if selector.current_pos == index:
                    self.display.text(selector.str, selector.x_loc, selector.y_loc, 1)
                else:
                    self.display.text(history_str.name, history_str.x_loc, history_str.y_loc, 1)
            self.display.show()
            self.update_flag = False
        
        
class Opt40_Str:
    def __init__(self,name,x_loc,y_loc, obj):
        self.name = name
        self.x_loc = x_loc
        self.y_loc = y_loc
        self.obj = obj
#         self.led_status = led.status
    def get_x(self):
        return self.x_loc
    
    def get_y(self):
        return self.y_loc
    
    def str_len(self):
        return len(self.name)

    def content(self):
        return f"{self.name}"
    




class Opt40_Selector:
    def __init__(self,x_loc,y_loc):
        self.x_loc = x_loc
        self.y_loc = y_loc

        self.str = ""
        self.current_pos = 0
        self.stop_flag = True
        
    def get_select_str(self,history_str):
        return f"{history_str.name} <-"
    

class Opt40:
    def __init__(self, name, display, encoder, selector, history_list, isf_fifo = None):
        self.name = name
        self.display = display
        self.encoder = encoder
        self.selector = selector
        self.history_list = history_list
        self.isf_fifo = isf_fifo
        self.file_name = "history.json"
        self.current_program = None
        self.obj_list = []
        self.stop_flag = True
        self.press = False
        # self.load_flag = True
    
        
    def update_selector(self):
        if self.stop_flag == False:
            # print(self.display.obj_str_list)
            current_pg_str = self.display.obj_str_list[self.selector.current_pos]
            # print(current_pg_str.name)
            self.selector.str = self.selector.get_select_str(current_pg_str)
            # self.selector.x_loc = get_x_starting(self.selector.str)
            self.selector.x_loc = X_DEFAULT
            self.selector.y_loc = current_pg_str.get_y()
            
    def add_program(self, program):
        self.obj_list.append(program)
        
    def convert_history_to_str_and_add_to_display_list(self):
        for i in range(len(self.obj_list) - 1):
            history_obj = self.obj_list[i]
            print("name ", history_obj["name"])
            # print(history_obj)
            self.display.create_str_from_obj(history_obj)
        
        
    def load_history(self):
        if self.obj_list == []:
            if self.name == "40":
                data = util.read_file(self.file_name)
                self.obj_list = data["history_list"]
        
        
    def turn_encoder(self):
        turn_fifo = self.encoder.t_l0_fifo
        while turn_fifo.has_data():
            if self.stop_flag == False:
                # turn_fifo = self.encoder.t00_fifo
                start = 0
                end = len(self.display.obj_str_list) -1
                direction = turn_fifo.get()
                self.selector.current_pos += direction
                if self.selector.current_pos <= start:
                    self.selector.current_pos = start
                if self.selector.current_pos >= end:
                    self.selector.current_pos = end
            
    def press_encoder(self):
        press_fifo = self.encoder.p_l0_fifo
        
        while press_fifo.has_data():
            if self.stop_flag == False:
                program_index = press_fifo.get()
                program = self.display.obj_str_list[program_index].program
                self.current_program = program
#                 print("current program name ",self.current_program.name)
#                 print(program_index)
                if self.press == True:
                    print(f"program: {self.name} run {program.name}")
#                     program.run()
#                     self.press = False
                self.press = True
#                 self
        
    def run(self):

        if self.stop_flag == False:
            self.update_selector()
            self.display.show_result(self.selector)    
            self.turn_encoder()
            self.press_encoder()
            
    def on(self):
        self.stop_flag = False
        self.display.stop_flag = False
        self.encoder.stop_flag = False
        self.selector.stop_flag = False
        self.encoder.update_program(self)
        self.display.update_program(self)
        self.load_history()
        self.convert_history_to_str_and_add_to_display_list()
        self.run()

    def off(self):
        self.press = False
        self.stop_flag = True
        self.display.stop_flag = True
        self.encoder.stop_flag = True
        self.selector.stop_flag = True
        
# adc_pin_nr = 27
# sample_size = 500 # want 250
# test_sample_size = 500
# sample_rate = 250
# hz = 20
# wait = round(1/hz,2)        
        
# samples = Isr_Fifo(sample_size,adc_pin_nr)
# timer = Piotimer(mode = Piotimer.PERIODIC, freq = sample_rate, callback = samples.handler)
# encoder = Encoder(ROT_A_PIN,ROT_B_PIN,ROT_SW_PIN)
# 
# # /wlan = Wlan()
# # mqtt = Mqtt("project", wlan)
# history_list = History_List()
#         
# opt40_display = Opt40_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
# opt40_selector = Opt40_Selector(ROW_START,HEIGHT_START)
# opt40 = Opt40("40",opt40_display, encoder, opt40_selector, history_list)
# 
# while True:
#     opt40.on()