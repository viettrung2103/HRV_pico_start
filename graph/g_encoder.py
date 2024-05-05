from filefifo import Filefifo
from fifo import Fifo
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
import math
import time

BOUNCE_TIME = 200


class Isr_Fifo(Fifo):
    def __init__(self, size, adc_pin_nr):
        super().__init__(size)
        self.av = ADC(adc_pin_nr)
        self.dbg = Pin(0,Pin.OUT)
        self.cur_program = None
        self.stop_flag = False
        # self.display = display
        
    def update_program(self,program):
            self.cur_program = program    
    
    def handler_11_or_21(self):
        if self.stop_flag == False :
            self.put(self.av.read_u16())
            self.dbg.toggle()  
  
    def handler(self,tid):
        if self.cur_program != None:
            name = self.cur_program.name
            if name == "11" or name == "21" :           
                self.handler_11_or_21()
        

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
        self.p00_fifo = Fifo(30)
        self.t00_fifo = Fifo(30, typecode = "i") #signed = "i"
        
        self.p10_fifo = Fifo(30) #default is unsigned "H"
        self.p11_fifo = Fifo(30)
        
        self.p20_fifo = Fifo(30)
        self.p21_fifo = Fifo(30)
        self.p210_fifo = Fifo(30)
        self.p22_fifo = Fifo(30)
        self.p220_fifo = Fifo(30)
        self.p23_fifo = Fifo(30)
        
        self.sw.irq(handler = self.press_handler, trigger = Pin.IRQ_RISING, hard = True)
        self.a.irq (handler = self.turn_handler, trigger = Pin.IRQ_RISING, hard = True)

    
    # def update_selector(self,selector):
    #     self.cur_selector = selector
        
    def update_program(self, program):
        self.cur_program = program
        self.cur_selector = program.selector
        
    def get_press_fifo_number(self):
        name = self.cur_program.name
        if name == "00":
            return self.p00_fifo
        elif name == "10":
            return self.p10_fifo
        elif name == "11":
            return self.p11_fifo
        elif name == "20":
            return self.p20_fifo
        elif name == "21":
            return self.p21_fifo
        elif name == "210":
            return self.p210_fifo
        elif name == "22":
            return self.p22_fifo
        elif name == "220":
            return self.p220_fifo
        elif name == "23":
            return self.p23_fifo
                
    
        
    def get_turn_fifo_number(self):
        name = self.cur_program.name
        if name == "00":
            return self.t00_fifo   
#         elif name == 10:
#             return self.t10_fifo
            
    # def press_handler(self,pin):
    #     if self.cur_program != None:
    #         p_fifo = self.get_press_fifo_number()
    #         cur_time = time.ticks_ms()
    #         delta = time.ticks_diff(cur_time, self.prev_time)
    #         if delta >= BOUNCE_TIME:
    #             p_fifo.put(1)
    #             self.prev_time = cur_time
                
    def press_handler(self,pin):
        if self.cur_program != None:
            p_fifo = self.get_press_fifo_number()
            name = self.cur_program.name
            cur_time = time.ticks_ms()
            delta = time.ticks_diff(cur_time, self.prev_time)
            if delta >= BOUNCE_TIME:
                if name == "00":
    #                     print("index ",self.cur_selector.current_pos)
                    p_fifo.put(self.cur_selector.current_pos)
                elif name == "40":
                    pass
                else:

                    p_fifo.put(1)
                self.prev_time = cur_time
                
    def turn_handler(self,pin):
        if self.cur_selector != None:
            t_fifo = self.get_turn_fifo_number()
            if self.b():
                t_fifo.put(1)
            else:
                t_fifo.put(-1)  