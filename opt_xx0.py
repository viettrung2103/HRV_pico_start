# from machine import UART, Pin, I2C, Timer
from ssd1306 import SSD1306_I2C
from machine import UART, Pin, I2C, ADC
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

class Optxx0_Display:
    def __init__(self, i2c, scl_pin, sda_pin, frequency, oled_w, oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda=sda_pin, freq=frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)
#         self.current_flag = True
    def reset(self):
        self.display.fill(0)
    
    def show(self, program_name):
        if program_name == "210" or program_name =="310":
            text1 = "ERROR"
        elif program_name =="220" or program_name == "320":
            text1 = "NETWORK ERROR"
        text2 = "RETRY BY"

        text3 = "PRESSING"
        text4 = "THE BUTTON"
        x1 = util.get_x_starting(text1)
        x2 = util.get_x_starting(text2)
        x3 = util.get_x_starting(text3)
        x4 = util.get_x_starting(text4)
        self.reset()
        self.display.text(text1,x1,Y_ROW_2)
        self.display.text(text2,x2,Y_ROW_3)
        self.display.text(text3,x3,Y_ROW_4)
        self.display.text(text4,x4,Y_ROW_5)
        self.display.show()

class Optxx0:
    def __init__(self,name, display, encoder, selector = None):
        self.name = name
        self.display = display
        self.encoder = encoder
        self.stop_flag = False
        self.selector = selector
        self.press = False
        
    def is_active(self):
        if self.stop_flag == False:
            return True
        else:
            return False

    
    def on(self):
        self.press = False
        self.stop_flag = False
        self.encoder.update_program(self)
        self.run()

#         self.handle_turn()

    def run(self):
        self.display.show(self.name)
        self.handle_press()

        
    def handle_press(self):

        # if self.name == "21":
        #     p_fifo = self.encoder.p21_fifo
        # if self.name == "31":
        #     p_fifo = self.encoder.p31_fifo
        p_fifo = self.encoder.p_xx0_fifo
#         print(p210_fifo)
        while p_fifo.has_data():
            value = p_fifo.get()
            print(f"program {self.name} press")
            if value == 1:
                self.press = True

    def off(self):
        self.stop_flag = True
        self.encoder.stop_flag = True



