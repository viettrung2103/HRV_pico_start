from ssd1306 import SSD1306_I2C
from fifo import Fifo
from machine import UART, Pin, I2C, Timer, ADC
from piotimer import Piotimer
import math
import time
import ujson

import urequests as requests
import ujson
import network
# from time import sleep
from kubios import Kubios
from mqtt import Wlan
import gc

# import network
# # from time import sleep
# from umqtt.simple import MQTTClient

# from mqtt import Mqtt

from encoder import Isr_Fifo, Encoder
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

#kubios
APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"

LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"
ANALYSIS_URL = "https://analysis.kubioscloud.com/v2/analytics/analyze"



# class Kubios:
#   # import urequests as requests
#   # import ujson
#   # import network
#   # from time import sleep
#     def __init__(self,apikey,client_id,client_secret, login_url, token_url, redirect_uri, analysis_url):
#         self.apikey = apikey
#         self.client_id = client_id
#         self.client_secret = client_secret
#         self.login_url = login_url
#         self.token_url = token_url
#         self.redirect_uri = redirect_uri
#         self.analysis_url =analysis_url
#         self.login_response = None
#         self.analysis_response = None
#         self.result = None
#         self.access_token = None
#         self.dataset = None
#         self.ppi_list = []
#         self.stop_flag = False
#         self.error_flag = False
#         # self.error_message = ""
        
#     def default_setting(self):
#         self.login_response = None
#         self.analysis_response = None
#         self.result = None
#         self.access_token = None
#         self.dataset = None
#         self.ppi_list = []
    
#     def create_login_response(self):
#         try:
#             if self.login_response == None:
#                 print("create login response")
#                 login_response = requests.post(
#                     url = self.token_url,
#                     data = 'grant_type=client_credentials&client_id={}'.format(self.client_id),
#                     headers = {'Content-Type':'application/x-www-form-urlencoded'},
#                     auth = (self.client_id, self.client_secret))
#                 json_login_response =login_response.json()
#                 self.access_token = json_login_response["access_token"]
#                 self.login_response = json_login_response
#         except Exception as e:
#             print(f"Failed to login to Kubios Server: {e}")
#             self.error_flag = True
#             self.stop_flag = True
    

#     def add_ppi_list(self,ppi_list):
#         if self.ppi_list == []:
#             self.ppi_list = ppi_list
            
#     def create_data_set(self):
#         if self.stop_flag == False:
#             if self.ppi_list != []:
#                 print("create data set")
#                 self.dataset = {
#                     "type"      : "RRI",
#                     "data"      : self.ppi_list,
#                     "analysis"  : {
#                         "type":"readiness"
#                     }
#                 }
            
#     def create_analysis_response(self):
#         if self.stop_flag == False:
#             print("create analysis response")
#             analysis_response = requests.post(
#                 # url = "https://analysis.kubioscloud.com/v2/analytics/analyze",
#                 url = self.analysis_url,
#                 headers = { "Authorization": "Bearer {}".format(self.access_token), #use access token to access your Kubios Cloud analysis session
#                 "X-Api-Key": self.apikey},
#                 json = self.dataset) #dataset will be automatically converted to JSON by the urequests library

#             json_analysis_response = analysis_response.json()
#             self.analysis_response = json_analysis_response
#             print(self.analysis_response)
#             self.stop_flag = True
#         time.sleep(3) 
#         # print(self.analysis_response)
        
#     def analyse(self):
#             print("analyse")
#             self.create_login_response()
#             # self.add_ppi_list(ppi_list)
#             self.create_data_set()
#             self.create_analysis_response()
            
#     def validate_response(self):
#         if self.stop_flag == False:
#             print("validate")
#             if self.analysis_response != None:
#                 if self.analysis_response["status"] == "ok":
#                     self.error_flag = False
#                 else:
#                     self.error_flag = True
#                     self.stop = True
#             else:
#                 self.error_flag = True
#                 self.stop_flag = True
            
#     def saving_result(self):
#         if self.result == None:
#             self.result = {
#                 "artefact_level"    : self.analysis_response['analysis']["artefact_level"],
#                 "create_timestamp"  : self.analysis_response['analysis']["create_timestamp"],
#                 "mean_hr_bpm"       : self.analysis_response['analysis']["mean_hr_bpm"],
#                 "mean_rr_ms"        : self.analysis_response['analysis']["mean_rr_ms"],
#                 "rmssd_ms"          : self.analysis_response['analysis']["rmssd_ms"],
#                 "sdnn_ms"           : self.analysis_response['analysis']["sdnn_ms"],
#                 "sns_index"         : self.analysis_response['analysis']["sns_index"],
#                 "pns_index"         : self.analysis_response['analysis']["pns_index"],
#             }
        
        
#     def run(self):
#         print("start kubios")
#         # print(self.stop_flag)
#         if self.stop_flag == False:
#             self.analyse()
#             self.validate_response()
#             # print("analysis" ,self.analysis_response)
#             if self.error_flag == False:
#                 print("save result")
#                 self.saving_result()
#                 print(self.result)
#                 self.stop_flag = True

#     def on(self):
#         self.error_flag = False
#         self.stop_flag = False
#         pass
    
#     def off(self):
#         self.stop_flag = True

# 
# class Kubios:
# 
#     def __init__(self, wlan):
# 
#         self.wlan = wlan
#         self.result = None
#    
#         self.ppi_list = []
#         self.stop_flag = False
#         self.error_flag = False
#         self.try_count = 1
#         self.num_error = 0
#         # self.error_message = ""
#         
#     def default_setting(self):
#         self.try_count = 1
#         self.num_error = 0
#         self.result = None
#         # self.access_token = None
#         # self.dataset = None
#         self.ppi_list = []
#     
#     def create_login_response(self):
#         try:
#             print("create login response")
#             login_response = requests.post(
#                 url = TOKEN_URL,
#                 data = 'grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
#                 headers = {'Content-Type':'application/x-www-form-urlencoded'},
#                 auth = (CLIENT_ID, CLIENT_SECRET))
#             json_login_response =login_response.json()
#             access_token = json_login_response["access_token"]
#             # self.login_response = json_login_response
#             return access_token
#         
#         except Exception as e:
#             print(f"Failed to login to Kubios Server: {e}")
#             self.error_flag = True
#             self.stop_flag = True
#     
# 
#     def add_ppi_list(self,ppi_list):
#         if self.ppi_list == []:
#             self.ppi_list = ppi_list
#             
#     def create_data_set(self):
#         if self.stop_flag == False:
#             if self.ppi_list != []:
#                 print("create data set")
#                 dataset = {
#                     "type"      : "RRI",
#                     "data"      : self.ppi_list,
#                     "analysis"  : {
#                         "type":"readiness"
#                     }
#                 }
#                 return dataset
#             
#     def create_analysis_response(self, dataset, access_token):
#         try:
#             print("create analysis response")
#             analysis_response = requests.post(
#                 # url = "https://analysis.kubioscloud.com/v2/analytics/analyze",
#                 url = ANALYSIS_URL,
#                 headers = { "Authorization": "Bearer {}".format(access_token), #use access token to access your Kubios Cloud analysis session
#                 "X-Api-Key": APIKEY},
#                 json = dataset) #dataset will be automatically converted to JSON by the urequests library
# 
#             json_analysis_response = analysis_response.json()
#             # self.analysis_response = json_analysis_response
#             # print(self.analysis_response)
#             print(json_analysis_response)
#             self.stop_flag = True
#             time.sleep(3) 
#             return json_analysis_response
#         except Exception as e:
#             print(f"Failed to login to Kubios Server: {e}")
#             self.error_flag = True
#             self.stop_flag = True
#         # print(self.analysis_response)
#         
#     def analyse(self):
#             print("analyse")
#                 # return json_login_response, access_token
#             access_token  = self.create_login_response()
#             # self.add_ppi_list(ppi_list)
#             dataset = self.create_data_set()
#             json_analysis_response = self.create_analysis_response(dataset, access_token)
#             
#             return json_analysis_response
#             
#     def validate_response(self, json_analysis_reponse):
#         if self.stop_flag == False:
#             print("validate")
#             if json_analysis_reponse != None:
#                 if analysis_response["status"] == "ok":
#                     self.error_flag = False
#                 else:
#                     self.error_flag = True
#                     self.stop = True
#             else:
#                 self.error_flag = True
#                 self.stop_flag = True
#             
#     def saving_result(self, json_analysis_reponse):
#         if self.result == None:
#             self.result = {
#                 "artefact_level"    : json_analysis_reponse['analysis']["artefact_level"],
#                 "create_timestamp"  : json_analysis_reponse['analysis']["create_timestamp"],
#                 "mean_hr_bpm"       : json_analysis_reponse['analysis']["mean_hr_bpm"],
#                 "mean_rr_ms"        : json_analysis_reponse['analysis']["mean_rr_ms"],
#                 "rmssd_ms"          : json_analysis_reponse['analysis']["rmssd_ms"],
#                 "sdnn_ms"           : json_analysis_reponse['analysis']["sdnn_ms"],
#                 "sns_index"         : json_analysis_reponse['analysis']["sns_index"],
#                 "pns_index"         : json_analysis_reponse['analysis']["pns_index"],
#             }
#         
#     def create_response(self):
#         while (self.try_count <200):
#             time.sleep(0.05)
#             try:
#                 print("create login response")
#                 login_response = requests.post(
#                     url = TOKEN_URL,
#                     data = 'grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
#                     headers = {'Content-Type':'application/x-www-form-urlencoded'},
#                     auth = (CLIENT_ID, CLIENT_SECRET))
#                 login_response = login_response.json() 
#                 #Parse JSON login_response into a python dictionary 
#                 access_token = login_response["access_token"] 
#         #Parse access token #Interval data to be sent to Kubios Cloud. Replace with your own data: intervals = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800] 
#         # #Create the dataset dictionary HERE # Make the readiness analysis with the given data 
#                 print("create dataset")
#                 dataset = { 
#                 "type": "RRI",
#                 "data": self.ppi_list,
#                 "analysis": {"type": "readiness"} 
#                 }
#                 print("create analysis response")
#                 response = requests.post(
#                 url = "https://analysis.kubioscloud.com/v2/analytics/analyze",
#                 headers = { "Authorization": "Bearer {}".format(access_token), #use access token to access your Kubios Cloud analysis session 
#                             "X-Api-Key": APIKEY},
#                 json = dataset) #dataset will be automatically converted to JSON by the urequests library 
#                 
#                 response = response.json()
#                 self.try_count = self.try_count +1
#                 print("done")
#                 return response
#             
#             except Exception as e:
#                 print(f"Failed to login to Kubios Server: {e}")
#                 self.num_error += 1
#                 print("error ",self.num_error)
#                 gc.collect()
#                 if self.try_count <200:
#                     continue
#                 else:
#                     self.error_flag = True
#                     self.stop_flag = True
#             
#     def run(self):
#         print("start kubios")
#         # print(self.stop_flag)
#         if self.stop_flag == False:
#             if not self.wlan.is_connected():
#                 self.wlan.connect_wlan()
#             else:
#                 response = self.create_response()
#                 # json_analysis_reponse = self.analyse()
#                 # self.validate_response(json_analysis_reponse)
#                 # print("analysis" ,self.analysis_response)
#                 if self.error_flag == False:
#                     print("save result")
#                     self.saving_result(response)
#                     print(self.result)
#                     self.stop_flag = True
# 
#     def on(self):
#         self.error_flag = False
#         self.stop_flag = False
#         pass
#     
#     def off(self):
#         self.stop_flag = True


class Opt32_Display:
    def __init__(self, i2c, scl_pin, sda_pin, frequency, oled_w, oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda=sda_pin, freq=frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)
#         self.current_flag = True

    def reset(self):
        self.display.fill(0)
    
    def show(self):

        text1 = "Sending Data..."
        text2 = "DO NOT PRESS"
        
        x1 = util.get_x_starting(text1)
        x2 = util.get_x_starting(text2)
        self.reset()
        self.display.text(text1,x1,Y_ROW_3)
        self.display.text(text2,x2,Y_ROW_5)

        self.display.show()


class Opt32:
    def __init__(self,name, display,encoder,kubios,wlan, selector = None, data = None, ):
        self.name = name
        self.display = display
        self.encoder = encoder
        self.selector = selector
        self.kubios = kubios
        self.wlan = wlan
        # self.response_file_name = "response_32.json"
        self.ppi_list = None        
#         self.response = None
        self.stop_flag = False
        self.error_flag = False
        # self.connect_flag = False
        self.press = False
        self.history_name = "history.json"
        
    
    def add_ppi_list(self):
        if self.ppi_list == None:
            file_name = "ppi_list_31.json"
            data = util.read_file(file_name)
            self.ppi_list = data['ppi_list']
            print(self.ppi_list)    

    # def save_to_history(self):
    #     if self.stop_flag == True:
            
    #         # if name == "32" 
            
    
    def on(self):
        gc.collect()
        print("Free memory:", gc.mem_free(), "bytes")
        self.press = False
        self.stop_flag = False
        self.encoder.update_program(self)
        self.kubios.on()
        self.kubios.default_setting()
        # ppi_list = [664, 844, 856, 764, 648, 804, 724, 812, 896, 796, 804, 736, 800, 788, 856, 832, 884]
        self.add_ppi_list()
        self.kubios.add_ppi_list(self.ppi_list)
        if not self.wlan.is_connected():
            self.wlan.connect_wlan()
        else:
            self.run()
            print("Free memory:", gc.mem_free(), "bytes")
            gc.collect()

    def is_connected():
        return True

    def run(self):
        self.display.show()
        if self.stop_flag == False :
            if self.kubios.stop_flag == False:
                self.run_kubios()
            #remember to add ppi list before run
            # self.kubios.add_ppi_list(self.ppi_list)
            
                # self.kubios.run()
                # # self.mqtt.run()

                # if self.kubios.error_flag == True :
                #     print('error')
                #     self.error_flag = True
                #     self.stop_flag = True
                #     # self.stop()
                # if self.kubios.stop_flag == True:
                #     self.stop_flag = True
                    # self.save_response(self.kubios.result)
                    # self.stop()
        self.stop()
        # else:
        #     self.stop()
        
    
    def run_kubios(self):
        self.kubios.run()
        if self.kubios.error_flag == True :
            print('error')
            self.error_flag = True
            self.stop_flag = True
            # self.stop()
        if self.kubios.stop_flag == True:
            self.stop_flag = True
    
    def stop(self):
        # if self.is_connected():
        if self.stop_flag == True:
            print("program stop automatically")
            # self.stop_flag = True
            self.press = True
            
            
    def handle_press(self):
        p32_fifo = self.encoder.p32_fifo
        # print(p32_fifo.has_data())
        while p32_fifo.has_data():
            value = p32_fifo.get()
            print(value)
            print(f"program {self.name} press")
            if value == 1:
                if self.kubios.stop_flag == True:
                    self.stop_flag == True
                    self.press = True

    def off(self):
        self.press = False
        self.stop_flag = True
        self.encoder.stop_flag = True
        self.kubios.stop_flag = True
        # self.kubios.result = None



# 
# 
# data =   {
#     "mean_ppi": "718.0", 
#     "sdnn": "71.26",
#     "rmssd": "105.08",
#     "mean_hr": "84.0"
#     }
# 
# # json_data = ujson.dumps(data)
# adc_pin_nr = 27
# sample_size = 500 # want 250
# test_sample_size = 500
# sample_rate = 250
# hz = 20
# wait = round(1/hz,2)
# 
# samples = Isr_Fifo(sample_size,adc_pin_nr)
#         
# encoder = Encoder(ROT_A_PIN,ROT_B_PIN,ROT_SW_PIN)
# wlan = Wlan()
# kubios = Kubios(wlan)
# 
#         
# opt32_display = Opt32_Display(I2C_MODE, SCL_PIN, SDA_PIN, FREQ, OLED_WIDTH, OLED_HEIGHT)
# opt32 = Opt32("32",opt32_display,encoder,kubios)
# 
# intervals = [664, 844, 856, 764, 648, 804, 724, 812, 896, 796, 804, 736, 800, 788, 856, 832, 884]
# 
# opt32.add_ppi_list(intervals)
# # kubios.add_ppi_list(intervals)
# 
# 
# # opt32.receive_data(json_data)
# 
# # print(opt32.data)
# while True:
#     # kubios.run()
#     opt32.on()
#     gc.collect()
# #     opt32.run()



