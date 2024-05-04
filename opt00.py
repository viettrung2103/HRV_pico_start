# from machine import UART, Pin, I2C, Timer
from ssd1306 import SSD1306_I2C
from fifo import Fifo


from machine import UART, Pin, I2C, Timer, ADC
from piotimer import Piotimer
import math
import time

from encoder import Isr_Fifo, Encoder


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



        
class Program:
  def __init__(self,name):
    self.name = name
    
  def run(self):
    print(self.name)

class Opt00_Display:
    def __init__(self,i2c,scl_pin,sda_pin,frequency,oled_w, oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda = sda_pin, freq = frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)
        self.program_str_list = []       
        
    def add_text(self,text):
        self.program_str_list.append(text)
        
    def reset(self):
        self.display.fill(0)
        

    def show_result(self,selector):
        self.reset()
        for index, program_str in enumerate(self.program_str_list):
            if selector.current_pos == index:
                self.display.text(selector.str, selector.x_loc, selector.y_loc, 1)
            else:
                self.display.text(program_str.text, program_str.x_loc, program_str.y_loc, 1)
        self.display.show()
        
        
class Opt00_str:
    def __init__(self,text,x_loc,y_loc, program):
        self.text = text
        self.x_loc = x_loc
        self.y_loc = y_loc
        self.program = program
#         self.led_status = led.status
    def get_x(self):
        return self.x_loc
    
    def get_y(self):
        return self.y_loc
    
    def str_len(self):
        return len(text)


    def fulltext(self):
        return f"{self.text}"
    




class Opt00_Selector:
    def __init__(self,x_loc,y_loc):
        self.x_loc = x_loc
        self.y_loc = y_loc

        self.str = ""
        self.current_pos = 0
        self.stop_flag = True
        
    def get_select_str(self,program_str):
        return f"{program_str.fulltext()} <-"
    

class Opt00:
    def __init__(self,name,display,encoder,isf_fifo,selector):
        self.name = name
        self.display = display
        self.encoder = encoder
        self.isf_fifo = isf_fifo
        self.selector = selector
        self.current_program = None
        self.program_list = []
        self.stop_flag = True
        self.press = False
        
    def update_selector(self):
        if self.stop_flag == False:
            current_pg_str = self.display.program_str_list[self.selector.current_pos]
            self.selector.str = self.selector.get_select_str(current_pg_str)
            # self.selector.x_loc = get_x_starting(self.selector.str)
            self.selector.x_loc = 0
            self.selector.y_loc = current_pg_str.get_y()
        
    def add_program(self, program):
        self.program_list.append(program)
        
    def turn_encoder(self):
        turn_fifo = self.encoder.t00_fifo
        while turn_fifo.has_data():
            if self.stop_flag == False:
                # turn_fifo = self.encoder.t00_fifo
                start = 0
                end = len(self.display.program_str_list) -1
                direction = turn_fifo.get()
                self.selector.current_pos += direction
                if self.selector.current_pos <= start:
                    self.selector.current_pos = start
                if self.selector.current_pos >= end:
                    self.selector.current_pos = end
            
    def press_encoder(self):
        press_fifo = self.encoder.p00_fifo
        
        while press_fifo.has_data():

            if self.stop_flag == False:
                program_index = press_fifo.get()
                program = self.display.program_str_list[program_index].program
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
        self.run()

    def off(self):
        self.press = False
        self.stop_flag = True
        self.display.stop_flag = True
        self.encoder.stop_flag = True
        self.selector.stop_flag = True