from filefifo import Filefifo
from fifo import Fifo
from machine import UART, Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
from piotimer import Piotimer
import math
import time
from encoder import Isr_Fifo, Encoder
import util
import ujson 


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

Y_ROW_1 = 0
Y_ROW_2 = COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_3 = Y_ROW_2 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_4 = Y_ROW_3 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_5 = Y_ROW_4 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_6 = Y_ROW_5 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_7 = Y_ROW_6 + COLUMN_SPACE + LETTER_HEIGHT

min_ppi_count = util.find_ppi_count_from_hr(MAX_HR)
max_ppi_count = util.find_ppi_count_from_hr(MIN_HR)

MIN_PULSE = util.find_beat_from_hr(MIN_HR)
MAX_PULSE = util.find_beat_from_hr(MAX_HR)

class Optx1_Mean_Program:
    def __init__(self,size):
        self.size = size
        self.array = []
        self.mean = 0
        
    def add(self,value):
        if len(self.array) < self.size:
            self.array.append(value)          
        else:
            self.array.append(value)
            self.array = self.array[1:len(self.array)]
    
    def is_full(self):
        return self.size == len(self.array)
    
    def show_array(self):
        print(self.array)
            
    def find_sum(self):
        sum = 0
        for index in range(self.size):
            sum += self.array[index]
        return sum
    
    def find_mean(self):
        sum = self.find_sum()
        self.mean = round(sum / self.size,0)

    def add_and_find_mean(self,value):
        self.add(value)
        if self.is_full():
            self.find_mean()
            

class Optx1:
    def __init__(self,name,display, mean_program, test_sample_size, sample_size,frequency, encoder,isr_fifo, selector = None):
        
        self.name = name
        self.display = display
        self.encoder = encoder
        self.isr_fifo = isr_fifo
        self.selector = selector
        self.mean_program = mean_program
        self.frequency = frequency
        self.min = 0
        self.max = 0
        self.test_sample_size = test_sample_size #2s
        self.sample_size = sample_size
        self.pre_on_th = 0
        self.pre_off_th = 0
        self.th_flag = False # to find th
        self.good_th_flag = False # to check if it is a good sample
        self.good_th_count = 0
        self.cur_val = 0
        self.pre_val = 0
        self.slp = 0
        self.data_count = 0 # count data between 2 peaks
        self.peak_count = 0
        self.count_flag = False
        self.crs_down_off_flag = False
        self.ppi_count = 0
        self.ppi = 0
        self.hr = 0
        self.found_ppi_flag = False
        self.hard_reset_flag = False
        self.soft_reset_flag = False
        self.sample_count = 0 #count data read from fifo
        self.ppi_count = 0
        self.peak_flag = False
        self.hr_count = 0
        self.time_count = 0
        self.ppi_list = []
        self.hr_list = []
        self.first_flag = True
        self.mean_ppi = 0
        self.mean_hr = 0
        self.rmssd = 0
        self.sdnn = 0
        self.time = 0
        self.data = None
        self.stop_flag = False
        self.press = False
        self.error_flag = False
        
    def default_value(self):
        self.min = 0
        self.max = 0
        self.pre_on_th = 0
        self.pre_off_th = 0
        self.good_th_count = 0
        self.cur_val = 0
        self.pre_val = 0
        self.slp = 0
        self.data_count = 0 # count data between 2 peaks
        self.peak_count = 0
        self.count_flag = False
        self.crs_down_off_flag = False
        self.ppi_count = 0
        self.ppi = 0
        self.hr = 0
        self.found_ppi_flag = False
        self.hard_reset_flag = False
        self.soft_reset_flag = False
        self.sample_count = 0 #count data read from fifo
        self.ppi_count = 0
        self.peak_flag = False
        self.hr_count = 0
        self.time_count = 0
        self.ppi_list = []
        self.hr_list = []
        self.first_flag = True
        self.mean_ppi = 0
        self.mean_hr = 0
        self.rmssd = 0
        self.sdnn = 0
        self.time = 0
        self.data = None
        
        self.stop_flag = False
        self.press = False
        self.error_flag = False
        
    def is_greater(self,value):
        return value > self.max
    
    def is_smaller(self, value):
        return value < self.min
    
    def greater(self,value):
        self.max = max(self.max, value)
        
    def smaller(self, value):
        self.min = min(self.min, value)
        
    def find_min_max(self,value):
        if self.is_greater(value):
            self.greater(value)
        else:
            self.smaller(value)
    
    def find_slp(self):
        self.slp = self.cur_val - self.pre_val
        
    def is_crs_up(self):
        if self.pre_val < self.pre_on_th and self.pre_on_th < self.cur_val:
            return True
        else:
            return False
        
    def is_crs_down_off_th(self):
        if self.pre_val > self.pre_off_th and self.pre_off_th > self.cur_val:
            return True
        else:
            return False
        
    def is_above_pre_on_th(self):
        if self.cur_val > self.pre_on_th:
            return True
        else: 
            return False
        
    def is_under_pre_off_th(self):
        if self.cur_val < self.pre_off_th:
            return True
        else:
            return False

    def is_good_th(self): # test whether the chosen sample has good read, min, max and th:
        if MIN_PULSE <= self.good_th_count or self.good_th_count <= MAX_PULSE: # 1 < 8
            return True
        else:
            return False
        
    def is_first_time(self):
        if self.first_flag == True:
            return True
        else:
            return False
        
    def has_th(self):
        if self.pre_on_th != 0:
            return True
        else:
            return False
        
    def find_good_th_count(self):
        if self.is_crs_up() == True:
            self.good_th_count += 1
            
    def is_peak(self):
        if self.slp <= 0:
            return True
        else:
            return False
        
    def is_at_peak(self):
        if self.peak_flag == True:
            return True
        else:
            return False
        
    def is_bad_hr(self,hr):
        if MIN_HR+5  > hr or hr > MAX_HR-20 :
            return True
        else:
            return False
        
    def is_too_bad_hr(self,hr):
        if self.hr > 140 and hr > 140:
            return True
        else:
            return False
        
    def is_too_long_time(self):
        if self.time > 13 and len(self.ppi_list) == 0:
            return True
        else:
            return False
        
    def validate_long_time(self):
        if self.is_too_long_time():
            self.hard_reset_flag = True
    
    def found_too_bad_hr(self):
        self.hard_reset_flag = True
        
    def found_bad_hr(self):
        self.soft_reset_flag = True
        
    def validate_hr(self,hr):
        if self.is_bad_hr(hr):
            self.found_bad_hr()
        if self.is_too_bad_hr(hr):
            self.found_too_bad_hr()
        
    def is_good_ppi_count(self):
        if min_ppi_count < self.ppi_count and self.ppi_count < max_ppi_count: #100-300
            return True
        else:
            return False
        
    def found_good_ppi(self):
        self.found_ppi_flag = True
        
    def is_error(self):
        if len(self.ppi_list) <= 6 and self.time >= 20:
            return True
        else:
            return False
    
    def found_error(self):         
        self.error_flag = True
        self.stop_flag = True
        self.press = True
            
    def check_error(self):
        if self.is_error():
            print("error")
            self.found_error()
    
    def validate_ppi_count(self):
        if self.is_good_ppi_count():
            self.found_good_ppi()
            
    def display_hr(self,ppi, hr):
        if self.found_ppi_flag == True:
            self.ppi = ppi
            self.hr = hr
            self.ppi_list.append(self.ppi)
            self.hr_list.append(self.hr)
            print("____")
            print(f"HR = {self.hr} BPM")
            self.soft_reset_flag = True
            
    def find_hr_v2(self):
        self.ppi_count = self.data_count
        hr = util.find_hr_from_ppi_count(self.ppi_count)
        ppi = util.find_ppi_from_ppi_count(self.ppi_count)
        #check if the ppi count within range, then check the calculated hr is within range
        if not self.ppi_list and self.hr >= 100:
            self.sorf_reset_flag = True
        self.validate_hr(hr)
        self.validate_ppi_count()


        if self.soft_reset_flag == False and self.hard_reset_flag == False  and self.found_ppi_flag == True and self.error_flag == False:
            self.display_hr(ppi, hr)
        else:
            self.soft_reset()


    def find_ppi_v3(self):
        if self.is_above_pre_on_th() :
            if self.is_peak() and self.peak_count == 0:
                self.count_flag = True
                self.peak_count += 1
        
        if self.is_crs_down_off_th() and self.peak_count >= 1 :
                self.crs_down_off_flag = True       
                
        if self.crs_down_off_flag == True and self.is_above_pre_on_th():
            if self.is_peak():
                self.peak_count += 1
                self.peak_flag = True
                
        if self.count_flag == True :
            self.data_count += 1
            
        if self.peak_count <= 8 and self.peak_flag == True:
            self.find_hr_v2()
            

            
        # if self.sample_count % 250 == 0:
        #     self.display.update_time_str(self.time)
        #   self.display.upda(self.hr, self.time)



        if self.sample_count >= self.sample_size:
            self.hard_reset_flag = True
        
    
    def soft_reset(self):
        if self.soft_reset_flag == True:
            self.data_count = 0
            self.crs_down_off_flag = False
            self.peak_flag = False
            self.found_ppi_flag = False
            self.soft_reset_flag = False

    def hard_reset(self):
        self.count_flag = False
        self.crs_down_off_flag = False
        self.found_ppi_flag = False
        self.hard_reset_flag = False
        self.soft_reset_flag = False
        self.peak_count = 0
        self.data_count = 0
        self.sample_count = 0
        self.time_count += 2 #+ two second
        
    def update_time(self):
        # if self.sample_count >0:
        if self.sample_count % self.frequency == 0:
            self.time += 1
            
    def read_find_mean_v3(self,data):
        if self.mean_program.size == 1:
            self.mean_program.add_and_find_mean(data)
        elif self.sample_count < self.mean_program.size:
            self.mean_program.add(data)
        else:
            self.mean_program.add_and_find_mean(data)
            
    def find_cur_val_pre_val_slp_v3(self):
        if self.sample_count == self.mean_program.size:  
            self.pre_val = self.mean_program.mean
        # when get 2nd mean value
        elif self.sample_count == self.mean_program.size + 1:
            self.cur_val = self.mean_program.mean
            self.find_slp()
        else:
            self.pre_val = self.cur_val
            self.cur_val = self.mean_program.mean
            self.find_slp()
        
    def read_data_v3(self,data):
        self.read_find_mean_v3(data)
        self.find_cur_val_pre_val_slp_v3()
        
    def read_v3(self,data):
        self.read_data_v3(data)
        self.find_ppi_v3()
        
    def find_th_v3(self):
        # 75
        on_percent = 0.75
        off_percent = 0.45
        self.cur_on_th = self.min + round( (self.max - self.min) * on_percent, 0)
        self.cur_off_th = self.min + round( (self.max - self.min) * off_percent, 0)
        self.th_flag = True
        if not self.is_first_time():
            self.pre_on_th = self.cur_on_th
            self.pre_off_th = self.cur_off_th
            self.cur_on_th = 0
            self.cur_off_th = 0
        else:
            self.time_count += 2
                    
    def find_min_max_th_v3(self,data):    
        if self.sample_count == 1:
            self.min = data
            self.max = data
#             self.display.update_str(self.hr, self.time)
            self.display.update_hr_str(self.hr)
        if self.sample_count < self.mean_program.size: # when mean_program size is not full
            self.mean_program.add(data)
        else:
            self.mean_program.add_and_find_mean(data)
            mean = self.mean_program.mean
            self.find_min_max(mean)
        if self.sample_count == self.test_sample_size:
            self.find_th_v3()
            if self.is_first_time():
                self.sample_count = 0
                self.first_flag = False
                              
    def display_current_time(self):
        if self.sample_count % frequency == 0:
            self.display.update_time_str(self.time)
            print("t = ",self.time)

    def find_mean_ppi(self):
        self.mean_ppi = util.find_mean_from_list(self.ppi_list)
        
    def find_mean_hr(self):
        self.mean_hr = util.find_mean_from_list(self.hr_list)
        
    def find_rmssd(self):
        sum = 0
        N = len(self.ppi_list)
        final = 0
        if N > 1:
            for i in range(N-1):
                result = (self.ppi_list[i+1] - self.ppi_list[i]) ** 2
                sum += result
            final = math.sqrt((1/(N-1) * sum))
        self.rmssd = int(round(final,0))
        
    def find_sdnn(self):
        sum = 0
        N = len(self.ppi_list) 
        final = 0
        if N > 1:
            for i in range(N):
                result = (self.ppi_list[i] - self.mean_ppi) ** 2
                sum += result
            final = math.sqrt((1/(N-1) * sum))
        self.sdnn = int(round(final,0))
    
    def display_result(self):
        self.find_mean_ppi()
        self.find_mean_hr()
        self.find_rmssd()
        self.find_sdnn()
        print(f"""
len      = {len(self.ppi_list)} 
mean PPI = {self.mean_ppi} ms
mean HR  = {self.mean_hr} BPM
rmssd    = {self.rmssd}
sdnn     = {self.sdnn}
""")              
        
    def press_encoder(self):

        p_fifo = self.encoder.p_x1_fifo        
        while p_fifo.has_data():

            option = p_fifo.get()
            if option == 1:
                if self.name == "11":
                    print("pressed")

                    self.stop_flag = True
                else:
                    if len(self.ppi_list) < 15 and self.time < 30:
                        print("pressed")
                        self.error_flag = True
                        self.stop_flag = True
#                 self.stop_flag = True
#                 pass
        

    def is_program_stop(self):
#         if self.time == 30 or self.stop_flag == True:
#         if self.stop_flag == True:
#             return True
        if self.time >= 30 and len(self.ppi_list) >= 15:    
            return True
        elif self.error_flag == True:
            return True
        else:
            return False

    def is_main_program_run(self):
        if self.isr_fifo.has_data() and self.stop_flag == False:
            return True
        else:
            return False

    def hr_program(self):
        while self.is_main_program_run():
            self.validate_long_time()
            self.check_error()
            
            data = self.isr_fifo.get()
            self.sample_count += 1
#               print(data)
            if LOWER_LIM <= data and data <= MAX_ADC - LOWER_LIM:
                
            #   self.display_current_time()
                self.find_min_max_th_v3(data)
                if self.has_th():    
                    self.read_v3(data) 
                if self.hard_reset_flag == True:
                    self.hard_reset()
                
#               while self.encoder.p21_fifo.has_data():
            self.update_time()
            self.display_current_time()
            
#             self.display.u
            if self.sample_count % 250 == 125:
                self.display.update_hr_str(self.hr)
            self.press_encoder()    
            if self.is_program_stop():
                self.stop()
    
    def send_ppi_list(self):
        if self.ppi_list != []:
            return self.ppi_list
    
    def create_data(self):
        # measure = {}
        if self.error_flag == False:
            measure = {
                "mean_hr" : f"{self.mean_hr}",
                "mean_ppi" : f"{self.mean_ppi}",
                "rmssd" : f"{self.rmssd}",
                "sdnn" : f"{self.sdnn}",
            }
            if self.name == "11":
                file_name = "result_11.json"
            if self.name == "21":
                file_name = "result_21.json"
            if self.name == "31":
                file_name = "result_31.json"
            util.write_file(file_name,measure)
        # self.data = ujson.dumps(measure)
        # else:
        #     self.data = {}
        # return self.data

                  
    def on(self):
        self.press = False
        self.stop_flag = False
        self.display.stop_flag = False
        self.isr_fifo.stop_flag = False
        self.error_flag = False
        self.encoder.update_program(self)
        self.isr_fifo.update_program(self)
        self.display.default_setting()
        self.run()
        
    def off(self):
        self.stop_flag = True
        self.display.stop_flag = True
        self.isr_fifo.stop_flag = True
        
    def stop(self):
#         self.stop_flag = True
#         self.isr_fifo.stop_flag = True
        self.off()
        self.display_result()
        print(f"program {self.name} stop")
        self.create_data()
        self.press = True
            
    def run(self):
        print(f"program {self.name} run")
        print("start reading")
#         while True:
        self.default_value()
        self.display.show_result()
        while self.stop_flag != True:
            if self.display.update_flag == False:
                if self.hard_reset_flag == True:
                    self.hard_reset()
                else:
                    self.hr_program()
            else:
                self.display.show_result()

                
# def get_x_starting(text):
#     str_len = len(text) * LETTER_WIDTH
#     middle_str = int(round((str_len /2),0))
#     x_middle = int(round(OLED_WIDTH / 2, 0)) #0 - 127
#     x_starting = x_middle - middle_str
#     return x_starting



# 
class Optx1_Display:
    def __init__(self,i2c,scl_pin,sda_pin,frequency,oled_w,oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda = sda_pin, freq = frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)
        self.hr_str = "00 BPM"
        self.time_str = "t = 00s"
        self.measure_str = "MEASURE.. "
        self.stop_flag = False
        self.update_flag = True
        # self.update_flag = False

    def update_hr_str(self, hr):
        if self.update_flag == False:
            if hr > 10:
                self.hr_str = f"{hr} BPM"
            else:
                self.hr_str = f"0{hr} BPM"
            # self.time_str = f"t = {time}"
            # print("updating")
            # print("hr_str ",self.hr_str)
            self.update_flag =True
            
    def update_time_str(self,time):
        if self.update_flag == False:
            if time < 10:
                self.time_str = f"t = 0{time}s"
            else:
                self.time_str = f"t = {time}s"
            if time % 4 == 0:
                self.measure_str = "MEASURE.. "
            elif time % 4 == 1:
                self.measure_str = "MEASURE. ."     
            elif time % 4 == 2:
                self.measure_str = "MEASURE .."
            else :
                self.measure_str = "MEASURE. ."   
                self.update_flag = True
                
    def default_setting(self):
        self.hr_str = "00 BPM"
        self.time_str = "t = 00s"
        self.stop_flag = False
        self.update_flag = True
        # self.update_flag = False
            
    # def update_str(self,hr, time):
    #     if self.update_flag == False:
    #         self.update_hr_str(hr)
    #         self.update_time_str(time)
    #         self.update_flag = True
        
    def reset(self):
        self.display.fill(0)

    def show_result(self):
        
        if self.update_flag == True:
            # text_1 = "MEASURING ..."
#             text_2 = "TO STOP"
            
            time_str_x = util.get_x_starting(self.time_str)
            hr_str_x = util.get_x_starting(self.hr_str)
            text_1_x = util.get_x_starting(self.measure_str)
#             text_2_x = util.get_x_starting(text_2)
            
            self.reset()
            self.display.text(self.time_str, time_str_x,Y_ROW_2)
            self.display.text(self.hr_str, hr_str_x,Y_ROW_3)
            self.display.text(self.measure_str,text_1_x,Y_ROW_5)
#             self.display.text(text_2,text_2_x,Y_ROW_6)
            self.update_flag = False
            self.display.show()
            
# hz = 20
# wait = round(1/hz,2)
# 
# adc_pin_nr = 27
# sample_size = 500 # want 250
# test_sample_size = 500
# sample_rate = 250            
# #             
# encoder = Encoder(ROT_A_PIN,ROT_B_PIN,ROT_SW_PIN)
# samples = Isr_Fifo(sample_size,adc_pin_nr)
# timer = Piotimer(mode = Piotimer.PERIODIC, freq = sample_rate, callback = samples.handler) 
#  
# opt21_display = Optx1_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
# opt21_mean_program = Optx1_Mean_Program(step)
# opt21 = Optx1("21", opt21_display,opt21_mean_program, test_sample_size, sample_size,frequency, encoder,samples)
# 
# opt21.on()