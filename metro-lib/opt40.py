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

# 
# class History_List:
#     def __init__(self,size = 6):
#         self.size = size
#         self.default_value = {"num":"0","idx":"0","name":"BACK","value":"BACK"}
#         self.list = []
#         self.data = None
#         self.highest_num = 0
#         self.new_history = None
#         self.file_name = "history.json"
#         self.key_name = "history_list"
#         self.update = True
# 
# #         self.current_
#     def add(self,response):
#         
# 
#         new_history = self.create_new_history(response)
#         print(new_history['name'])
# #         program_list  #len = 6 # [1,2,3,4,5'back']
# #         #>> real_list = n - 1
# #         #real list len = n -1
#         n = len(self.list) 
#         final_index = 0
# 
#         if n <= self.size - 1:
#    
#             for i in range(n-1,-1,-1):
#    
#                 self.list[i] = self.list[i-1]
#                 if i == 0:
#                     self.list[i] = new_history
#                 self.list[i]["idx"] = i
#                 final_index = i
#             final_index += 1  
#             self.default_value["idx"] = n
#             self.list.append(self.default_value)
#         else:
#             for i in range(n-2,-1,-1):
#                 self.list[i] = self.list[i-1]
#                 if i == 0:
#                     self.list[i] = new_history
#                 self.list[i]["idx"] = i
#             
#         self.save_list()
#     def is_exist(self):
#         return self.exist_flag
#         
#     def create_list(self):
#         self.list.append(self.default_value)
#         
#     def load_list_from_json(self):
#         data = util.read_file(self.file_name)
# #         print("data inside history list", data)
#         if not data:
#             self.create_list() 
#         else:
#             self.list = data[self.key_name]
#         return self.list
#     
#     def save_list(self):
#         list_dict = {self.key_name:self.list}
#         util.write_file(self.file_name,list_dict)
#         
#     def update_highest_number(self):
#         if self.list:
#             for i in range(len(self.list) - 1):
#                 history_object = self.list[i]
#                 history_object_numb = int(history_object["num"])
#                 self.highest_num = max(self.highest_num,history_object_numb)
#             
#     def create_new_history(self,response):
#         self.update_highest_number()
#         text = "MEASUREMENT {}".format(self.highest_num +1)
#         new_history = {
#             "num": str(self.highest_num + 1),
#             "name": text,
#             "idx":0,
#             "value": response
#         }
#         return new_history
#         
#     def get_history_detail(self,idx):
#         return self.list[idx]
#     
#     def show_list(self):
#         return self.list


# class Isr_Fifo(Fifo):
#     def __init__(self, size, adc_pin_nr):
#         super().__init__(size)
#         self.av = ADC(adc_pin_nr)
#         self.dbg = Pin(0,Pin.OUT)
#         self.cur_program = None
#         self.stop_flag = False
#         
#     def update_program(self,program):
#             self.cur_program = program    
#             
#         
#     
#     def handler_11_21_31(self):
#         if self.cur_program.stop_flag == False:
# 
#             self.put(self.av.read_u16())
#             self.dbg.toggle()  
# 
#     def handler(self,tid):
#         if self.cur_program != None:
#             name = self.cur_program.name
#             if name == "11" or name == "21" or name == "31" :           
#                 self.handler_11_21_31()
#         
# 
# 
# class Encoder:
#     def __init__ (self, rot_a_pin, rot_b_pin, rot_sw_pin):
#         self.a = Pin(rot_a_pin, mode = Pin.IN, pull = Pin.PULL_UP)
#         self.b = Pin(rot_b_pin, mode = Pin.IN, pull = Pin.PULL_UP)
#         self.sw = Pin(rot_sw_pin, pull = Pin.PULL_UP, mode = Pin.IN)
#         self.stop_flag = False
#         self.prev_time = 0
#         self.cur_selector = None
#         self.cur_program  = None
#         # self.press = False
#         self.p00_fifo = Fifo(15)
#         self.t00_fifo = Fifo(15, typecode = "i") #signed = "i"
#         
#         self.p_l0_fifo = Fifo(15)
#         self.t_l0_fifo = Fifo(15, typecode = "i")
#         
#         self.p_x1_fifo = Fifo(15)
#         self.p_x0_fifo = Fifo(15)
#         self.p_x3_fifo = Fifo(15)
#         # self.p_x10_fifo = Fifo(15)
#         self.p_xx0_fifo = Fifo(15)
#         
#         self.p21_fifo = Fifo(15)
#         self.p22_fifo = Fifo(15)
# 
#         self.p32_fifo = Fifo(15)
#         # self.p320_fifo = Fifo(15)
#         # self.p33_fifo = Fifo(15)
#         
#         self.p40_fifo = Fifo(15)
#         self.t40_fifo = Fifo(15)
#         self.p41_fifo = Fifo(15)
#         
#         self.sw.irq(handler = self.press_handler, trigger = Pin.IRQ_RISING, hard = True)
#         self.a.irq (handler = self.turn_handler, trigger = Pin.IRQ_RISING, hard = True)
# 
#     
#         
#     def update_program(self, program):
#         self.cur_program = program
#         self.cur_selector = program.selector
# #         print(f"program {self.cur_program.name} use encoder")
#         
#     def get_press_fifo_number(self):
#         name = self.cur_program.name
#         if name == "00" or name =="40" or name == "4i":
#         
#             return self.p_l0_fifo
#         elif name == "10" or name == "20" or name == "30":
#             return self.p_x0_fifo    
#         elif name == "11" or name == "21" or name == "31":   
#             return self.p_x1_fifo
# #         elif name == "21":
# #             return self.p21_fifo
#         elif name == "210" or name == "310" or name == "220" or name == "320" or name == "4i":            
#             return self.p_xx0_fifo
#         elif name =="23" or name == "33" or name == "33d":
#             return self.p_x3_fifo
#         elif name == "22":
#             return self.p22_fifo
#         elif name == "32":
#             return self.p32_fifo
#         print("press name" ,name)    
# 
#     
#         
#     def get_turn_fifo_number(self):
#         name = self.cur_program.name
# 
#         if name == "00" or name =="40":
#             print("turn name" ,name)
# 
#             return self.t_l0_fifo
# 
#             
# 
#                 
#     def press_handler(self,pin):
#         if self.cur_program != None:
#             if self.cur_program.stop_flag == False:
# 
#                 p_fifo = self.get_press_fifo_number()
#                 name = self.cur_program.name
#                 cur_time = time.ticks_ms()
#                 delta = time.ticks_diff(cur_time, self.prev_time)
#                 if delta >= BOUNCE_TIME:
#                     if name == "00" or name == "40":
#         #                     print("index ",self.cur_selector.current_pos)
#                         p_fifo.put(self.cur_selector.current_pos)
#                     # elif name == "40":
#                     #     pass
#                     else:
#                         p_fifo.put(1)
#                     self.prev_time = cur_time
#                 
#     def turn_handler(self,pin):
#         if self.cur_selector != None:
#             if self.cur_program.stop_flag == False:
#                 t_fifo = self.get_turn_fifo_number()
#                 if self.b():
#                     t_fifo.put(1)
#                 else:
#                     t_fifo.put(-1)  


        
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
#         print("Free memory:", gc.mem_free(), "bytes")
#         print(obj)
        obj_str = Opt40_Str(obj["name"], X_DEFAULT, Y_ROW_LIST[obj["idx"]], obj)
#         print(obj["name"])
        self.add_obj_str(obj_str)
#         print("list here ",self.obj_str_list)
        # return obj_str
    
    # def add
        

    def show_result(self,selector):
        # if self.update_flag == True:
        # print(selector.current_pos)
        self.reset()
        for index, history_str in enumerate(self.obj_str_list):
#                 print("index" ,index)
            if selector.current_pos == index:
                self.display.text(selector.str, selector.x_loc, selector.y_loc, 1)
            else:
                self.display.text(history_str.name, history_str.x_loc, history_str.y_loc, 1)
        self.display.show()
            # self.update_flag = False
        
        
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
        self.load_flag = False
        # self.load_flag = True
    
        
    def update_selector(self):
        # print("obj list", self.obj_list)
        if self.stop_flag == False:
            # print(self.display.obj_str_list)
            current_pg_str = self.display.obj_str_list[self.selector.current_pos]
            # print(current_pg_str.name)
            self.selector.str = self.selector.get_select_str(current_pg_str)
            # self.selector.x_loc = get_x_starting(self.selector.str)
            self.selector.x_loc = X_DEFAULT
            self.selector.y_loc = current_pg_str.get_y()
#             print("selector x ", self.selector.x_loc)
#             print("selector y ", self.selector.y_loc)            
            
    def add_program(self, program):
        self.obj_list.append(program)
        
    def convert_history_to_str_and_add_to_display_list(self):
        for i in range(len(self.obj_list)):
#             print("index ",i)
#             print("Free memory:", gc.mem_free(), "bytes")

            
            history_obj = self.obj_list[i]
#             print("name ", history_obj["name"])
            # print(history_obj)
            self.display.create_str_from_obj(history_obj)
            gc.collect()
        
        
    def load_history(self):
#         print("are you here")        
        if self.load_flag == False:
            if self.name == "40":
#                 data = util.read_file(self.file_name)
                data = self.history_list.load_list_from_json()
#                 print(self.load_flag)
            
                # self.obj_list = data["history_list"]
                self.obj_list = data #data insice history_list key
                self.load_flag = True
                if self.obj_list == []:
                    self.history_list
                
                self.convert_history_to_str_and_add_to_display_list()
        
    def turn_encoder(self):
        turn_fifo = self.encoder.t_l0_fifo
#         print("fifo ", turn_fifo)
        
        while turn_fifo.has_data():
            # print(turn_fifo.has_data())
            if self.stop_flag == False:
                # turn_fifo = self.encoder.t00_fifo
                start = 0
                end = len(self.display.obj_str_list) -1
                direction = turn_fifo.get()
#                 print("list ",self.display.obj_str_list)
                
                
                self.selector.current_pos += direction
        #                 print("selector current pos", self.selector.current_pos)
                if self.selector.current_pos <= start:
                    self.selector.current_pos = start
        #                     print(" now selector current pos", self.selector.current_pos)
                if self.selector.current_pos >= end:

                    self.selector.current_pos = end
                print(" now selector current pos", self.selector.current_pos)

            
    def press_encoder(self):
        press_fifo = self.encoder.p_l0_fifo
        
        while press_fifo.has_data():
            if self.stop_flag == False:
                program_index = press_fifo.get()
                program = self.display.obj_str_list[program_index].obj
                self.current_program = program
                self.press = True
#                 print("current program name ",self.current_program.name)
#                 print(program_index)
                if self.press == True:
                    print("go to program ",self.current_program["name"])
#                     if self.current_program["name"] == "BACK":
#                         print("Go back")
#                     else:
#                         print("load program")    
#                         print("program", self.current_program)
#                         opt_4i_display = Opt_4i_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
#                         opt_4i  = Opt4i("4i", opt_4i_display, encoder, self.current_program )
#                         opt_4i.on()
#                         opt_4i.run()
# #                     program.run()
# #                     self.press = False
#                     # self.press = False
#                     pass
#                 self
        
    def run(self):

        if self.stop_flag == False:
#             print("is it run")
            self.update_selector()
            self.display.show_result(self.selector)    
            self.turn_encoder()
            self.press_encoder()
#             self.update_selector()
            
    def on(self):
#         if self.stop_flag == False:
        self.press = False
        self.stop_flag = False
        self.display.stop_flag = False
        self.encoder.stop_flag = False
        self.selector.stop_flag = False
        self.encoder.update_program(self)
        self.display.update_program(self)
#         print("are you here")
        self.load_history()
            
#             self.convert_history_to_str_and_add_to_display_list()
#         self.run()

    def reset(self):
        self.press = False
        self.stop_flag = False
#         self.display.stop_flag = True
#         self.encoder.stop_flag = True
#         self.selector.stop_flag = True
        self.load_flag = False
        self.obj_list = []
        self.display.obj_str_list = []
