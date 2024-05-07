import time
import network
# from time import sleep
from umqtt.simple import MQTTClient

SSID = "KMD658_Group_4"
PASSWORD = "00000000"
BROKER_IP = "192.168.4.253"

class Wlan:
    def __init__ (self):
        self.wifi_flag = False
        self.stop_flag = False
        self.error_flag =False
        self.wlan = None
        
    def connect_wlan(self):
    # Connecting to the group WLAN
        try:
            if self.wifi_flag == False:
                self.wlan = network.WLAN(network.STA_IF)
                self.wlan.active(True)
                self.wlan.connect(SSID, PASSWORD)
                print("")
                # Attempt to connect once per second
                while self.wlan.isconnected() == False:
                    print("Connecting... ")
                    time.sleep(1)
                    # if self.wlan.isconnected() == True:
                if self.wlan.isconnected() == True:
                    self.wifi_flag = True
                    # print("Connect success")
                    print("Connection successful. Pico IP:", self.wlan.ifconfig()[0])
        except Exception as e:
            print("Cannot connect to network", e)
            self.error_flag = True
            self.stop_flag = True
            self.wlan = None
                    
    def is_connected(self):
        if self.wifi_flag == True:
            print("Connected to Wifi")
            return True
        else:
            return False
        


class Mqtt:
    def __init__(self,topic, wlan):
        self.topic = topic
        # self.ssid = ssid
        # self.password = password
        self.wlan = wlan
        self.mqtt_client = None
        self.data = None
        self.connect_wlan_flag = False
        self.connect_mqtt_flag = False
        self.data_flag = False
        self.error_flag = False
        self.stop_flag = False
        # self.message = None
        # self.stop_flag = True
        
    def has_data(self):
        if self.data != None:
            return True
        else:
            return False
    
                
        # Print the IP address of the Pico
            
            # print("Connection successful. Pico IP:", self.wlan.ifconfig()[0])
    
    def connect_mqtt(self):
        if self.wlan.is_connected():
            if self.connect_mqtt_flag == False:
                self.mqtt_client = MQTTClient("", BROKER_IP)
                self.mqtt_client.connect(clean_session=True)
                self.connect_mqtt_flag = True
                print("Connect Successfully to MQTT")
        # return mqtt_client
        
    def convert_data_to_message(self):
        
        self.message = f"""
        {
            "mean_hr" : "{self.data["mean_hr"]}", 
            "mean_ppi" : "{self.data["mean_ppi"]}", 
            "rmssd" : "{self.data["rmssd"]}", 
            "sdnn" : "{self.data["sdnn"]}", 
        }
        """
    
    def add_data(self,data):
        self.data = data
        self.data_flag = True
        
    def publish_data(self):
        try:

            if self.connect_mqtt_flag == True and self.stop_flag == False:
                    self.mqtt_client.publish(self.topic, self.data)
                    print(f"Sending to MQTT: {self.topic} -> {self.data}")

                    time.sleep(2)
                    print("Done")
                    self.stop_flag = True
                    
        except Exception as e:
                print(f"Failed to send MQTT message: {e}")
                self.error_flag = True
                
    def reset_data(self):
        # self.data = None
        # self.wlan = None
        self.mqtt_client = None
        # self.message = None
    
    def run(self):
        # self.add_data(data)
        if self.has_data() and self.stop_flag == False:
            # print("here")
            if not self.wlan.is_connected():
                self.wlan.connect_wlan()
        # Connect to MQTT
            if self.wlan.error_flag == True:
                self.stop_flag = True
                
            try:
                self.connect_mqtt()                
            except Exception as e:
                print(f"Failed to connect to MQTT: {e}")
                self.error_flag = True
                self.stop_flag = True

            self.publish_data()
            self.data_flag  = False
            self.stop_flag = True
            
            
            
    def default_setting(self):
        # self.stop_flag = False
        # self.connect_wlan_flag = False
        self.connect_mqtt_flag = False
        self.error_flag = False
        self.stop_flag = False
        self.reset_data()