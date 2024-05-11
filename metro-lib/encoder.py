from filefifo import Filefifo
from fifo import Fifo
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
import math
import time

BOUNCE_TIME = 300


class Isr_Fifo(Fifo):
    def __init__(self, size, adc_pin_nr):
        super().__init__(size)
        self.av = ADC(adc_pin_nr)
        self.dbg = Pin(0,Pin.OUT)
        self.cur_program = None
        self.stop_flag = False
        
    def update_program(self,program):
            self.cur_program = program    
            
        
    
    def handler_11_21_31(self):
        if self.cur_program.stop_flag == False:

            self.put(self.av.read_u16())
            self.dbg.toggle()  

    def handler(self,tid):
        if self.cur_program != None:
            name = self.cur_program.name
            if name == "11" or name == "21" or name == "31" :           
                self.handler_11_21_31()
        

class Encoder:
    def __init__ (self, rot_a_pin, rot_b_pin, rot_sw_pin):
        self.a = Pin(rot_a_pin, mode = Pin.IN, pull = Pin.PULL_UP)
        self.b = Pin(rot_b_pin, mode = Pin.IN, pull = Pin.PULL_UP)
        self.sw = Pin(rot_sw_pin, pull = Pin.PULL_UP, mode = Pin.IN)
        self.stop_flag = False
        self.prev_time = 0
        self.cur_selector = None
        self.cur_program  = None
        # self.press = False
        self.p00_fifo = Fifo(15)
        self.t00_fifo = Fifo(15, typecode = "i") #signed = "i"
        
        self.p_l0_fifo = Fifo(15)
        self.t_l0_fifo = Fifo(15, typecode = "i")
        
        self.p_x1_fifo = Fifo(15)
        self.p_x0_fifo = Fifo(15)
        self.p_x3_fifo = Fifo(15)
        # self.p_x10_fifo = Fifo(15)
        self.p_xx0_fifo = Fifo(15)
        
        self.p21_fifo = Fifo(15)
        self.p22_fifo = Fifo(15)

        self.p32_fifo = Fifo(15)
        # self.p320_fifo = Fifo(15)
        # self.p33_fifo = Fifo(15)
        
        self.p40_fifo = Fifo(15)
        self.t40_fifo = Fifo(15)
        self.p41_fifo = Fifo(15)
        
        self.sw.irq(handler = self.press_handler, trigger = Pin.IRQ_RISING, hard = True)
        self.a.irq (handler = self.turn_handler, trigger = Pin.IRQ_RISING, hard = True)

    
        
    def update_program(self, program):
        self.cur_program = program
        self.cur_selector = program.selector
#         print(f"program {self.cur_program.name} use encoder")
        
    def get_press_fifo_number(self):
        name = self.cur_program.name
        if name == "00" or name =="40":
        
            return self.p_l0_fifo
        elif name == "10" or name == "20" or name == "30":
            return self.p_x0_fifo    
        elif name == "11" or name == "21" or name == "31":   
            return self.p_x1_fifo
#         elif name == "21":
#             return self.p21_fifo
        elif name == "210" or name == "310" or name == "220" or name == "320":            
            return self.p_xx0_fifo
        elif name =="23" or name == "33" or name == "33d" or name == "4i":
            return self.p_x3_fifo
        elif name == "22":
            return self.p22_fifo
        elif name == "32":
            return self.p32_fifo
        print("press name" ,name)    

    
        
    def get_turn_fifo_number(self):
        name = self.cur_program.name

        if name == "00" or name =="40":
            print("turn name" ,name)

            return self.t_l0_fifo

            

                
    def press_handler(self,pin):
        if self.cur_program != None:
            print(self.cur_program.stop_flag)
            if self.cur_program.stop_flag == False:
                print("is it here")
                p_fifo = self.get_press_fifo_number()
                name = self.cur_program.name
                cur_time = time.ticks_ms()
                delta = time.ticks_diff(cur_time, self.prev_time)
                if delta >= BOUNCE_TIME:
                    if name == "00" or name == "40":
        #                     print("index ",self.cur_selector.current_pos)
                        p_fifo.put(self.cur_selector.current_pos)
                    # elif name == "40":
                    #     pass
                    else:
                        print("put 1 to fifo")
                        p_fifo.put(1)
                    self.prev_time = cur_time
                
    def turn_handler(self,pin):
        if self.cur_selector != None:
            if self.cur_program.stop_flag == False:
                t_fifo = self.get_turn_fifo_number()
                if self.b():
                    t_fifo.put(1)
                else:
                    t_fifo.put(-1)  