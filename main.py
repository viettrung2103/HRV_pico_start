# from machine import UART, Pin, I2C, Timer
from ssd1306 import SSD1306_I2C
from fifo import Fifo
import gc


from machine import UART, Pin, I2C, Timer, ADC
from piotimer import Piotimer
import math
import time

from encoder import Isr_Fifo, Encoder
from mqtt import Mqtt, Wlan
from kubios import Kubios
from history_list import History_List



from opt22 import Opt22, Opt22_Display

from opt32 import Opt32, Opt32_Display


from opt_x0 import Opt_x0, Opt_x0_Display
from opt_x1 import Opt_x1, Opt_x1_Display, Opt_x1_Mean_Program
from opt_x3 import Opt_x3, Opt_x3_Display
from opt_xx0 import Opt_xx0, Opt_xx0_Display


from opt00 import Program, Opt00_Display, Opt00_Selector, Opt00_Str, Opt00
from opt40 import Opt40, Opt40_Display, Opt40_Selector
from opt_4i import Opt4i, Opt_4i_Display

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


#MQTT
SSID = "KMD658_Group_4"
PASSWORD = "00000000"
BROKER_IP = "192.168.4.253"

#KUBIOS
APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"

LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"
ANALYSIS_URL = "https://analysis.kubioscloud.com/v2/analytics/analyze"




class Main:
    def __init__(self,delay, opt00, opt10, opt11,opt20, opt21, opt210, opt22, opt220, opt23, opt30, opt31, opt310,opt32, opt320, opt33, opt_40, encoder,  opt_4i_display):
#         self.control_flag = None
        self.delay = delay
        self.opt00 = opt00
        self.opt10 = opt10
        self.opt11 = opt11
        self.opt20 = opt20
        self.opt21 = opt21
        self.opt210 = opt210
        self.opt22 = opt22
        self.opt220 = opt220
        self.opt23 = opt23
        self.opt30 = opt30
        self.opt31 = opt31
        self.opt310 = opt310
        self.opt32 = opt32
        self.opt320 = opt320
        self.opt33 = opt33
        self.opt_40 = opt_40
        self.encoder = encoder
        self.opt_4i_display = opt_4i_display
        #self.opt4i = opt4i
#         self.encoder = encoder
        self.state = self.state_00
        self.error_count_opt2 = 0
        self.error_count_opt3 = 0
        
    def execute(self):
        self.state()
        
    def update_state_4i(self,program):
        self.opt_4i = Opt4i("4i", self.opt_4i_display, encoder, program)
        print("opt 4i", self.opt_4i)
    

    def reset_to_state_00(self):
        print("reset go to state 00")
        if self.error_count_opt2 >= 5:
            self.error_count_opt2 = 0
        if self.error_count_opt3 >= 5:
            self.error_count_opt3 = 0
        self.state = self.state_00
        
    def state_00(self):
#         print("here")
#         print("Free memory:", gc.mem_free(), "bytes")
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        
        self.opt00.on()
        time.sleep(self.delay)
        if self.opt00.press:
            self.opt00.press = False
            current_program = self.opt00.current_program
            if current_program.name == opt10.name:
                print("to state 10")
                self.state = self.state_10
            elif current_program.name == opt20.name:
                print("to state 20")
                self.state = self.state_20
            elif current_program.name == opt30.name:
                print("to state 30")
                self.state =self.state_30
            elif current_program.name == opt40.name:
                print("to state 40")
                self.state = self.state_40
                
            
        else:
            self.state = self.state_00
        
        
    def state_10(self):
#         print("Free memory:", gc.mem_free(), "bytes")
        self.opt00.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt10.on()
        time.sleep(self.delay)
        if self.opt10.press:
            print("to state 11")
            self.state = self.state_11
        else:
            self.state = self.state_10
            
    def state_11(self):
        self.opt10.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt11.on()
        time.sleep(self.delay)
        if self.opt11.press:
            print("to state 00")
            self.state = self.state_00
        else:
            self.state = self.state_11
        
    def state_20(self):
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt20.on()
        time.sleep(self.delay)
        if self.opt20.press:
            print("to state 21")
            self.state = self.state_21
        else:
            self.state = self.state_20
            
    def state_21(self):
#         print("Free memory:", gc.mem_free(), "bytes")

        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt21.on()
        time.sleep(self.delay)
        if self.opt21.press:
            if self.opt21.error_flag == True:
                self.error_count_opt2 +=1
                print(self.error_count_opt2)
                print("to state 210")
                self.state = self.state_210

            else:
                print("to state 22")
                data = self.opt21.create_data()
                print("data ",data)
                # self.opt22.receive_data(data)
                self.state = self.state_22
        else:
            self.state = self.state_21
            
    def state_210(self):
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt210.on()
        time.sleep(self.delay)
        if self.opt210.press:
            if self.error_count_opt2 >= 5:
                self.reset_to_state_00()
            else:
                print("to state 21")
                self.state = self.state_21
        else:

            self.state = self.state_210
            
    def state_22(self):
#         print("Free memory:", gc.mem_free(), "bytes")
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt22.on()

        time.sleep(self.delay)
        if self.opt22.press:
            if self.opt22.mqtt.error_flag == True:
                print("to state 220")
                self.error_count_opt2 += 1
                self.state = self.state_220
            else:
                print("to state 23")
                # data = self.opt22.create_data()
                # self.opt23.add_data()
                self.state = self.state_23
        else:
            self.state = self.state_22
            
    def state_220(self):
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt220.on()

        time.sleep(self.delay)
        if self.opt220.press:
            if self.error_count_opt2 >= 5:
                # print("reset go to state 00")    
                # self.error_count_opt2 = 0
                # self.state = self.state_00
                self.reset_to_state_00()
            else:
                print("to state 22")
                data = self.opt21.create_data()
                print("data ",data)
                self.opt22.receive_data(data)
                self.state = self.state_22
        else:
            self.state = self.state_220
            
    def state_23(self):
#         print("Free memory:", gc.mem_free(), "bytes")
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt23.on()
        time.sleep(self.delay)
        if self.opt23.press:
            print("to state 00")
            self.state = self.state_00
        else:
            self.state = self.state_23
        
    def state_30(self):
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        # self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt30.on()
        time.sleep(self.delay)
        if self.opt30.press:
            print("to state 31")
            self.state = self.state_31
        else:
            self.state = self.state_30
            
    def state_31(self):
#         print("Free memory:", gc.mem_free(), "bytes")
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt31.on()
        
        time.sleep(self.delay)
        if self.opt31.press:
            if self.opt31.error_flag == True:
                self.error_count_opt3 +=1
                print(self.error_count_opt3)
                print("to state 310")
                self.state = self.state_310

            else:
                print("to state 32")
#                 ppi_list = self.opt31.send_ppi_list()
# #                 print("ppi list ",ppi_list)
#                 self.opt32.add_ppi_list(ppi_list)
                self.state = self.state_32
        else:
            self.state = self.state_31
            
    def state_310(self):
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt310.on()
        time.sleep(self.delay)
        if self.opt310.press:
            if self.error_count_opt3 >= 5:
                self.reset_to_state_00()
            else:
                print("to state 31")
                self.state = self.state_31
        else:

            self.state = self.state_310
            
    def state_32(self):
#         print("Free memory:", gc.mem_free(), "bytes")
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt320.off()
        self.opt33.off()
#         self.opt40.off()

        self.opt32.on()
        

        time.sleep(self.delay)
        if self.opt32.press:
            if self.opt32.kubios.error_flag == True:
                print("to state 320")
                self.error_count_opt3 += 1
                self.state = self.state_320
            else:
                print("to state 33")
#                 data = self.opt32.send_response()
#                 self.opt33.add_data(data)
                self.state = self.state_33
        else:
            self.state = self.state_32
            
    def state_320(self):
        gc.collect()
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt33.off()
#         self.opt40.off()
        self.opt320.on()

        time.sleep(self.delay)
        if self.opt320.press:
            if self.error_count_opt3 >= 5:

                self.reset_to_state_00()
            else:
                print("to state 32")
#                 ppi_list = self.opt31.send_ppi_list()
# #                 print("ppi list ",ppi_list)
#                 self.opt32.add_ppi_list(ppi_list)
                self.state = self.state_32
        else:
            self.state = self.state_320
            
    def state_33(self):
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
#         self.opt40.off()
        self.opt33.on()
        
        time.sleep(self.delay)
        if self.opt33.press:
            print("to state 00")
            self.state = self.state_00
        else:
            self.state = self.state_33
            
    def state_40(self):
        self.opt00.off()
        self.opt10.off()
        self.opt11.off()
        self.opt20.off()
        self.opt21.off()
        self.opt210.off()
        self.opt22.off()
        self.opt220.off()
        self.opt23.off()
        self.opt30.off()
        self.opt31.off()
        self.opt310.off()
        self.opt32.off()
        self.opt320.off()
        self.opt33.off()
        self.opt_40.on()
#         print("what about here")
        self.opt_40.run()        
        time.sleep(self.delay)
        if self.opt_40.press:
            self.opt_40.press = False
            current_program = self.opt_40.current_program
#             print("current program", current_program)
            self.update_state_4i(current_program)
            
            if current_program["idx"] != len(self.opt_40.obj_list) -1:
#                 print("to state 4i", current_program.name)
                
                self.state = self.state_4i
                self.opt_40.reset()
            # elif current_program.name == opt20.name:
            #     print("to state 20")
            #     self.state = self.state_20
            # elif current_program.name == opt30.name:
            else:
                print('go back')
        else:
            self.state = self.state_40

    def state_40(self):
        self.opt_40.on()
#         print("what about here")
        self.opt_40.run()
        if self.opt_40.press:
            self.opt_40.press = False
            current_program = self.opt_40.current_program
#             print("current program", current_program)
            self.update_state_4i(current_program)
            
            if current_program["idx"] != len(self.opt_40.obj_list) -1:
#                 print("to state 4i", current_program.name)
                
                self.state = self.state_4i
                self.opt_40.reset()
            # elif current_program.name == opt20.name:
            #     print("to state 20")
            #     self.state = self.state_20
            # elif current_program.name == opt30.name:
            else:
                print('go back')
                self.state = self.state_00
         #history detail
        #opt4i = opt40.create_option >> OptI(program)
    def state_4i(self):
        self.opt_4i.on()
#         self.opt_4i.display.update_program(self.opt_4i)
#         self.opt_4i.encoder.update_program()
        self.opt_4i.run() 
        if self.opt_4i.press:
            print("go back to history list")
            self.state = self.state_40
#             self.opt_4i.press = False
        else:
            self.state = self.state_4i
            
      #def state_4i(self):
#         self.opt00.off()
#         self.opt10.off()
#         self.opt11.off()
#         self.opt20.off()
#         self.opt21.off()
#         self.opt210.off()
#         self.opt22.off()
#         self.opt220.off()
#         self.opt23.off()
#         self.opt30.off()
#         self.opt31.off()
#         self.opt310.off()
#         self.opt32.off()
#         self.opt320.off()
#         self.opt33.off()
#         self.opt40.off()
#         self.opt4i.on()
#         if self.opt4i.press:
#             print("to state 40")
#             self.state = self.state40
#         else:
#             self.state = self.state_4i
        

        
            
text1 = '1.MEASURE HR'
text2 = "2.HRV ANALYSIS"
text3 = "3.KUBIOS"
text4 = "4.HISTORY"

x_starting = ROW_START
y_starting1 = Y_ROW_1
y_starting2 = Y_ROW_2
y_starting3 = Y_ROW_3
y_starting4 = Y_ROW_4

adc_pin_nr = 27
sample_size = 500 # want 250
sensor_fifo_size= 4000
test_sample_size = 500
sample_rate = 250
hz = 20
wait = round(1/hz,2)

#Menu Program

program_1 = Program("MEASURE HR")
program_2 = Program("Basic HRV Analysic")
program_3 = Program("KUBIOS")
program_4 = Program("HISTORY")


samples = Isr_Fifo(sensor_fifo_size,adc_pin_nr)
timer = Piotimer(mode = Piotimer.PERIODIC, freq = sample_rate, callback = samples.handler)
encoder = Encoder(ROT_A_PIN,ROT_B_PIN,ROT_SW_PIN)

wlan = Wlan()
mqtt = Mqtt("project", wlan)
history_list = History_List()

# kubios = Kubios(APIKEY,CLIENT_ID,CLIENT_SECRET,LOGIN_URL,TOKEN_URL,REDIRECT_URI,ANALYSIS_URL)
kubios = Kubios(APIKEY, CLIENT_ID, CLIENT_SECRET, LOGIN_URL, TOKEN_URL, REDIRECT_URI, ANALYSIS_URL)

opt00_display = Opt00_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
opt00_selector = Opt00_Selector(ROW_START,HEIGHT_START)
opt00 = Opt00("00",opt00_display, encoder,samples, opt00_selector)

opt10_display = Opt_x0_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
opt10 = Opt_x0("10",opt10_display,encoder)

opt11_display = Opt_x1_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
opt11_mean_program = Opt_x1_Mean_Program(step)
opt11 = Opt_x1("11", opt11_display,opt11_mean_program, test_sample_size, sample_size,frequency, encoder,samples)

opt20_display = Opt_x0_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
opt20 = Opt_x0("20",opt10_display,encoder)

opt21_display = Opt_x1_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
opt21_mean_program = Opt_x1_Mean_Program(step)
opt21 = Opt_x1("21", opt21_display,opt21_mean_program, test_sample_size, sample_size,frequency, encoder,samples)

opt210_display = Opt_xx0_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
opt210 = Opt_xx0("210",opt210_display,encoder)

opt22_display = Opt22_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
opt22 = Opt22("22",opt22_display,encoder, mqtt)


opt220_display = Opt_xx0_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
opt220 = Opt_xx0("220",opt220_display,encoder)



opt23_display = Opt_x3_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
opt23 = Opt_x3("23",opt23_display,encoder)


opt30_display = Opt_x0_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
opt30 = Opt_x0("30",opt30_display,encoder)

opt31_display = Opt_x1_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
opt31_mean_program = Opt_x1_Mean_Program(step)
opt31 = Opt_x1("31", opt31_display,opt31_mean_program, test_sample_size, sample_size,frequency, encoder,samples)

opt310_display = Opt_xx0_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
opt310 = Opt_xx0("310",opt310_display,encoder)

opt32_display = Opt32_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
opt32 = Opt32("32",opt32_display,encoder,kubios, wlan)

opt320_display = Opt_xx0_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
opt320 = Opt_xx0("320",opt320_display,encoder)

opt33_display = Opt_x3_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
opt33 = Opt_x3("33",opt33_display,encoder, history_list)

opt40_display = Opt40_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
opt40_selector = Opt40_Selector(ROW_START,HEIGHT_START)
opt40 = Opt40("40",opt40_display, encoder,samples, opt40_selector, history_list)

opt4i_display = Opt_4i_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
        
opt40_display = Opt40_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)
opt40_selector = Opt40_Selector(ROW_START,HEIGHT_START)
opt40 = Opt40("40",opt40_display, encoder, opt40_selector, history_list)
# main = Main(wait, opt40, encoder,  opt4i_display)

# menu_prog.add_program(hr_program)
opt00.add_program(opt10)
opt00.add_program(opt20)
opt00.add_program(opt30)
# opt00.add_program(program_4)
opt00.add_program(opt40)

# program_str_1 = Program_str(text1,x_starting,y_starting1, hr_program)
Opt00_str_1 = Opt00_Str(text1,x_starting,y_starting1, opt10)
Opt00_str_2 = Opt00_Str(text2,x_starting,y_starting2, opt20)
Opt00_str_3 = Opt00_Str(text3,x_starting,y_starting3, opt30)
# Opt00_str_4 = Opt00_Str(text4,x_starting,y_starting4, program_4)
Opt00_str_4 = Opt00_Str(text4,x_starting,y_starting4, opt40)

# led_str3 = Led_str(text1_3,x_starting,y_starting3, led3)

opt00_display.add_text(Opt00_str_1)
opt00_display.add_text(Opt00_str_2)
opt00_display.add_text(Opt00_str_3)
opt00_display.add_text(Opt00_str_4)



# menu_display = Menu_Display(I2C_MODE,SCL_PIN,SDA_PIN ,FREQ, OLED_WIDTH, OLED_HEIGHT)

# opt10_encoder = Encoder(ROT_SW_PIN)


# main = Main(wait,opt00,opt10, opt11, opt20, opt21, opt210, opt22, opt220, opt23, opt30, opt31, opt310, opt32, opt320, opt33)

main = Main(wait,opt00,opt10, opt11, opt20, opt21, opt210, opt22, opt220, opt23, opt30, opt31, opt310, opt32, opt320, opt33, opt40 ,encoder,  opt4i_display)
#add opt4i to main later

while True:
    main.execute()
    gc.collect()
#     opt20.on()






