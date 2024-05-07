from ssd1306 import SSD1306_I2C
from machine import  Pin, I2C
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
COLUMN_SPACE = 1
LETTER_HEIGHT = 8
LETTER_WIDTH = 8
Y_ROW_1 = 0
Y_ROW_2 = COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_3 = Y_ROW_2 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_4 = Y_ROW_3 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_5 = Y_ROW_4 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_6 = Y_ROW_5 + COLUMN_SPACE + LETTER_HEIGHT
Y_ROW_7 = Y_ROW_6 + COLUMN_SPACE + LETTER_HEIGHT

#hr
t = 4 #4ms
frequency = 250
MINUTE = 60
SECOND = 1
THOUSAND = 1000
TWO = 2
test_duration = TWO  * SECOND * THOUSAND # to ms
duration = TWO * SECOND * THOUSAND


class Opt_x3_Display:
    def __init__(self, i2c, scl_pin, sda_pin, frequency, oled_w, oled_h):
        self.i2c = I2C(i2c, scl=scl_pin, sda=sda_pin, freq=frequency)
        self.display = SSD1306_I2C(oled_w, oled_h, self.i2c)
        self.program  = None
        self.timestamp_str = ""
        self.mean_hr_str = ""
        self.mean_ppi_str = ""
        self.rmssd_str = ""
        self.sdnn_str = ""
        self.sns_str = ""
        self.pns_str = ""
        self.stop_flag = True
        self.update_flag = False
#         self.current_flag = True

    def update_program(self,program):
        self.program = program
        
    def default_value(self):
        self.program  = None
        self.timestamp_str = ""
        self.mean_hr_str = ""
        self.mean_ppi_str = ""
        self.rmssd_str = ""
        self.sdnn_str = ""
        self.sns_str = ""
        self.pns_str = ""

            
    def update_str(self, data):
        if self.update_flag == False:
        # if json_data != None:
            print("____")
            # print("data ",data["sns_index"])
            mean_hr = util.convert_to_int(data["mean_hr"])
            mean_ppi = util.convert_to_int(data["mean_ppi"])
            rmssd = util.convert_to_int(data["rmssd"])
            sdnn = util.convert_to_int(data["sdnn"])
            
            self.mean_hr_str = f"MEAN HR : {mean_hr} "
            self.mean_ppi_str = f"MEAN PPI: {mean_ppi}" 
            self.rmssd_str = f"RMSSD   : {rmssd}"
            self.sdnn_str = f"SDNN    : {sdnn}"
            
            if self.program.name == "33":
                ts = util.convert_timestamp_str(data["create_timestamp"])
                sns = data["sns"]
                pns = data["pns"]
                
                self.timestamp_str = "{}.{}.{} {}:{}".format(ts['dd'],ts['mm'],ts['yyyy'],ts['h'],ts['m'])
                self.sns_str = f"SNS     : {sns:.2}"
                # print(self.snd)
                self.pns_str = f"PNS     : {pns:.2}"
                print("pns ",self.pns_str)
                
        self.update_flag = True

    def reset(self):
        self.display.fill(0)
    
    def show(self):
        # text1 = self.mean_hr_str
        # text2 = self.mean_ppi_str
        # text3 = self.rmssd_str
        # text4 = self.sdnn_str
        if self.update_flag == True:
            print("show")
            self.reset()
            self.display.text(self.mean_hr_str,0,Y_ROW_2)
            self.display.text(self.mean_ppi_str,0,Y_ROW_3)
            self.display.text(self.rmssd_str,0,Y_ROW_4)
            self.display.text(self.sdnn_str,0,Y_ROW_5)
            if self.program.name == "33":
                ts_str_x  = util.get_x_starting(self.timestamp_str)
                # print(self.timestamp_str)        
                self.display.text(self.timestamp_str,ts_str_x,Y_ROW_1)
                self.display.text(self.sns_str,0,Y_ROW_6)
                self.display.text(self.pns_str,0,Y_ROW_7)

            self.display.show()
            self.update_flag = False

class Opt_x3:
    def __init__(self,name, display, encoder, data = None, history_list = None, selector = None):
        self.name = name
        self.display = display
        self.encoder = encoder
        self.selector = selector
        self.stop_flag = False
        self.error_flag = False
        self.history_list = history_list
        self.press = False
        self.data_flag = False
        self.data = data
        
    def default_value(self):
        self.data = None
        
    def has_data(self):
        return self.data_flag
        # if self.data_flag == True:
        #     return True
        # else:
        #     return False

    def load_data(self):
        try:
            if self.name == "33":
                file_name = "response_32.json"
            elif self.name == "33d":
                file_name = "response_32_dummy.json"
            else:
                file_name = "result_21.json"
            self.data = util.read_file(file_name)
            self.data_flag = True
            # return result
        except Exception as e:
            print("Cannot load file ",e)
            self.stop_flag = True
            self.error_flag = True
    
    def on(self):
        self.press = False
        self.stop_flag = False
        self.data_flag = False
        self.encoder.update_program(self)
        self.display.update_program(self)
        self.default_value()
        if not self.has_data():
            self.load_data()
            self.run()
        else:
            self.run()

    def run(self):
        if self.stop_flag == False:
            print("update and show")
            self.display.update_str(self.data)
            self.display.show()
            if self.name == "33":
                self.history_list.load_list_from_history()
                self.history_list.add(self.data)
            self.handle_press()
        else:
            self.stop()

        
    def handle_press(self):
        p_fifo = self.encoder.p_x3_fifo
        while p_fifo.has_data():
            value = p_fifo.get()
            print(f"program {self.name} press")
            if value == 1:
                self.stop_flag = True
                self.stop()
                
    def stop(self):
        self.display.default_value()
        self.default_value()
        self.press = True

    def off(self):
        self.stop_flag = True
        self.encoder.stop_flag = True
        self.data_flag = False
        self.press = False





