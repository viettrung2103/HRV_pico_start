import ujson

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
        print("done")
        
def read_file(file_name):
    with open(file_name) as f:
        payload = ujson.load(f)
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
# min_ppi_count = find_ppi_count_from_hr(MAX_HR)
# max_ppi_count = find_ppi_count_from_hr(MIN_HR)

# MIN_PULSE = find_beat_from_hr(MIN_HR)
# MAX_PULSE = find_beat_from_hr(MAX_HR)