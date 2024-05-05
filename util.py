import ujson
# from history_list import History_List

t = 4 #4ms
frequency = 250
MINUTE = 60
SECOND = 1
THOUSAND = 1000
TWO = 2

age = 30
# MIN_HR = 50
# MAX_HR = 240 - age
MIN_HR = 50
MAX_HR = 150

BLANK = 0
FILLED = 1
COLUMN_SPACE = 2
LETTER_HEIGHT = 8
LETTER_WIDTH = 8
Y_ROW_1 = 0
Y_ROW_2 = COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_3 = Y_ROW_2 + COLUMN_SPACE + LETTER_HEIGHT

OLED_WIDTH = 128
OLED_HEIGHT = 64
ROW_START = 0
ROW_EDGE = OLED_WIDTH - 1 #127
HEIGHT_START = 0
HEIGHT_EDGE = OLED_HEIGHT -1 #63



# #utility
def find_beat_from_hr(hr):#2 second
    beat = round(hr/MINUTE,0) * 2
    return beat

def find_hr_from_ppi(ppi):
    hr = 0
    if ppi != 0:
        hr = round(MINUTE * THOUSAND / ppi,0)
    return hr

def find_hr_from_ppi_count(ppi_count):
    hr = 0
    ppi  = ppi_count * t
    if ppi_count != 0:
        hr = round(MINUTE * THOUSAND / ppi,0)
    return hr

def find_ppi_from_ppi_count(ppi_count):
    ppi = 0
    if ppi_count != 0:
        ppi = ppi_count * t
    return ppi

def find_ppi_from_hr(hr):
    ppi = 0
    if hr != 0:
        ppi = int(round(MINUTE * THOUSAND / hr,0))
    return ppi

def find_ppi_count_from_hr(hr):
    ppi_count = 0
    if hr != 0:
        ppi = int(round(MINUTE * THOUSAND / hr,0))
        ppi_count = ppi / t
    return ppi_count
 
def find_mean_from_list(my_list):
    sum = 0
    result = 0
    N = len(my_list)
    for value in my_list:
        sum += value
    if N != 0:
        result = int(round(sum / len(my_list),0))
    return result


def get_x_starting(text):
    str_len = len(text) * LETTER_WIDTH
    middle_str = int(round((str_len /2),0))
    x_middle = int(round(OLED_WIDTH / 2, 0)) #0 - 127
    x_starting = x_middle - middle_str
    return x_starting

def convert_timestamp_str(timestamp):
    yyyy = timestamp[:4]
    mm = timestamp[5:7]
    dd = timestamp[8:10]
    h = timestamp[11:13]
    m = timestamp[14:16]
    s = timestamp[17:19]
    time_obj = {
        "yyyy": yyyy,
        "mm"  : mm,
        "dd"  : dd,
        "h"   : h,
        "m"   : m,
        "s"   : s
        }
    return time_obj

def write_file(file_name, response):
    with open(file_name, "w") as f:
        ujson.dump(response,f)
        print("read to file ",file_name)
        
def read_file(file_name):
    payload = None
    try:
        with open(file_name) as f:
            payload = ujson.load(f)
            print("read from file ",file_name)
            return payload
    except Exception as e:
        print("There no file")
    finally:
        return payload
    
    
def convert_to_int(num):
    new_num = int(round(num,0))
    return new_num

def get_x_starting(text):
    str_len = len(text) * LETTER_WIDTH
    middle_str = int(round((str_len /2),0))
    x_middle = int(round(OLED_WIDTH / 2, 0)) #0 - 127
    x_starting = x_middle - middle_str
    return x_starting



# class History_List:
#     def __init__(self,size = 6):
#         self.size = size
#         # self.cur = 0
#         self.default_value = {"num":"0","name":"Back"}
#         self.list = []
#         self.data = None
#         self.highest_num = 0
#         self.new_history = None
#         self.file_name = "history.json"
#         self.key_name = "history_list"

# #         self.current_
#     def add(self,response):
#         # print("start ",self.list)
#         # print("add ",response)
#         new_history = self.create_new_history(response)
#         print(new_history['name'])
#         #real list len = n -1
#         n = len(self.list) #max = 7

#         #real_n = n -1 = 6
#         if n <= 5:
#             # self.current_list = self.list[:n-1]
#             for i in range(n-1,-1,-1):
#                 # print("index {}".format(i))
#                 self.list[i] = self.list[i-1] 
#                 if i == 0:
#                     self.list[i] = new_history
#                 # print("current ",self.list)   
#             self.list.append(self.default_value)
#         else:
#             for i in range(n-2,-1,-1):
#                 self.list[i] = self.list[i-1]
#                 if i == 0:
#                     self.list[i] = new_history
#         # print("final", self.list)
#         self.save_list()
    
#     def is_exist(self):
#         return self.exist_flag
        
#     def create_list(self):
#         # back_object = {
#         #     "name":str(self.highest_num),
#         #     "value": self.default_value 
#         #     }
#         # self.default_value = back_object
#         self.list.append(self.default_value)
        
#     def load_list_from_json(self):
#         data = read_file(self.file_name)
#         if not data:
#             self.create_list() 
#             # print("New list ",self.list)
#         else:
#             self.list = data[self.key_name]
#             # print("list exist ",self.list)
    
#     def save_list(self):
#         list_dict = {self.key_name:self.list}
#         write_file(self.file_name,list_dict)
        
#     def update_highest_number(self):
#         if self.list:
#             for i in range(len(self.list) - 1):
#                 history_object = self.list[i]
#                 history_object_numb = int(history_object["num"])
#                 self.highest_num = max(self.highest_num,history_object_numb)
#         # print("highest number",self.highest_num)
            
#     def create_new_history(self,response):
#         self.update_highest_number()
#         text = "MEASUREMENT {}".format(self.highest_num +1)
#         new_history = {
#             "num": str(self.highest_num + 1),
#             "name": text,
#             "value": response
#         }
#         # print("new history ",new_history)
#         return new_history
        
#     def show_list(self):
#         return self.list
            
        
                
# response = {"create_timestamp": "2024-05-04T21:15:51.910675+00:00", "rmssd": 31.36466, "sdnn": 20.96066, "sns": 3.407736, "mean_ppi": 715.1667, "pns": -0.9618915, "artefact_level": "GOOD", "mean_hr": 83.89652}

            
                

# for i in range(6,-1,-1):
#     print(i)     
# history_list = History_List()
# history_list.add(2)
# print(history_list.list) 
# history_list.add(3)
# print(history_list.list) 
# history_list.add(4)
# print(history_list.list) 
# history_list.add(5)
# print(history_list.list) 
# history_list.add(6)
# print(history_list.list) 
# history_list.add(7)
# print(history_list.list) 
# history_list.add(8)
# print(history_list.list) 
# history_list.add(9)
# print(history_list.list) 
# history_list.add(10)
# print(history_list.list) 
        
# a_list = [1,2,3,4,5,6]
# n = len(a_list)
# print(a_list[:n-1])
# min_ppi_count = find_ppi_count_from_hr(MAX_HR)
# max_ppi_count = find_ppi_count_from_hr(MIN_HR)

# MIN_PULSE = find_beat_from_hr(MIN_HR)
# MAX_PULSE = find_beat_from_hr(MAX_HR)