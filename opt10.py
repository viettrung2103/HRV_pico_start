from filefifo import Filefifo
from fifo import Fifo
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
import math
import time
from encoder import Isr_Fifo, Encoder
import util


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
# print(round(50/60,0))
#display
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

def get_x_starting(text):
    str_len = len(text) * LETTER_WIDTH
    middle_str = int(round((str_len /2),0))
    x_middle = int(round(OLED_WIDTH / 2, 0)) #0 - 127
    x_starting = x_middle - middle_str
    return x_starting
        
class Opt10_selector:
    def __init__(self,size):
        self.size =size

class Opt10_Display:
    def __init__(self, i2c, scl_pin, sda_pin, frequency, oled_w, oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda=sda_pin, freq=frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)
#         self.current_flag = True
        
    def reset(self):
        self.display.fill(0)
    
    def show(self):
        text1 = "START"
        text2 = "MEASUREMENT"
        text3 = "BY"
        text4 = "PRESSING"
        text5 = "THE BUTTON"
        x1 = get_x_starting(text1)
        x2 = get_x_starting(text2)
        x3 = get_x_starting(text3)
        x4 = get_x_starting(text4)
        x5 = get_x_starting(text5)
        self.reset()
        self.display.text(text1,x1,Y_ROW_1)
        self.display.text(text2,x2,Y_ROW_2)
        self.display.text(text3,x3,Y_ROW_3)
        self.display.text(text4,x4,Y_ROW_4)
        self.display.text(text5,x5,Y_ROW_5)
        self.display.show()

class Opt10:
    def __init__(self,name, display,encoder, selector = None):
#         self.opt10_display = opt10_display
        self.name = name
        self.display = display
        self.encoder = encoder
        self.stop_flag = False
#         self.press_flag = False
        self.selector = selector
        self.press = False
        
    def is_active(self):
        return self.current_flag

    
    def on(self):
        self.press = False
        self.stop_flag = True
        self.encoder.update_program(self)
#         self.encoder.update_selector(self.selector)
        self.display.show()
        self.handle_press()
#         self.handle_turn()

        
    def handle_press(self):
        p10_fifo = self.encoder.p10_fifo
        while p10_fifo.has_data():
            value = p10_fifo.get()
            print(f"program {self.name} press")
            if value == 1:
                
                self.press = True
            
#     def handle_turn(self):
#         t10_fifo = self.encoder.t10_fifo
#         while t10_fifo.has_data():
#             value = t10_fifo.get()
#             self.selector.size += value
#             print(f"program: {self.name} selector: {self.selector.size}")
        

    def off(self):
        self.current_flag = False

        self.encoder.current_flag = False

# samples = Isr_Fifo(sample_size,adc_pin_nr)
        
# encoder = Encoder(ROT_A_PIN,ROT_B_PIN,ROT_SW_PIN)
        
# opt10_display = Opt10_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
# opt10 = Opt10("10",encoder, opt10_display)

# opt10.on()

