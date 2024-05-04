import urequests as requests
import ujson
import network
import time
import gc
import util
# import secret


# APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
# CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
# CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"

# LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
# TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
# REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"
# ANALYSIS_URL = "https://analysis.kubioscloud.com/v2/analytics/analyze"

APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"

LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token" 
REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"
ANALYSIS_URL = "https://analysis.kubioscloud.com/v2/analytics/analyze"

class Kubios:

    def __init__(self, wlan,apikey, client_id, client_secret, login_url, token_url, redirect_uri, analysis_url ):

        self.wlan = wlan
        # self.result = None  
        self.apikey = apikey
        self.client_id = client_id
        self.client_secret = client_secret
        self.login_url = login_url
        self.token_url = token_url
        self.redirect_uri = redirect_uri
        self.analysis_url = analysis_url
        self.ppi_list = None
        self.stop_flag = False
        self.error_flag = False
        self.try_count = 1
        self.num_error = 0
        # self.ppi_list = [664, 844, 856, 764, 648, 804, 724, 812, 896, 796, 804, 736, 800, 788, 856, 832, 884]
        self.ppi_list = []
        # self.ppi_list = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800] 
        # self.error_message = ""
        
    def default_setting(self):
        self.try_count = 1
        self.num_error = 0
        self.result = None
        # self.access_token = None
        # self.dataset = None
        self.ppi_list = []
    
    def create_login_response(self):
        try:
            print("create login response")
            login_response = requests.post(
                # url = TOKEN_URL,
                url = self.token_url,
                # data = 'grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
                data = 'grant_type=client_credentials&client_id={}'.format(self.client_id),
                headers = {'Content-Type':'application/x-www-form-urlencoded'},
                # auth = (CLIENT_ID, CLIENT_SECRET))
                auth = (self.client_id, self.client_secret))
            print("login response",login_response)
            json_login_response =login_response.json()
            access_token = json_login_response["access_token"]
            # self.login_response = json_login_response
            gc.collect()
            return access_token
        
        except Exception as e:
            print(f"Failed to login to Kubios Server: {e}")
            self.error_flag = True
            self.stop_flag = True
    

    def add_ppi_list(self,ppi_list):
        if self.ppi_list == []:
            self.ppi_list = ppi_list
            
    def create_data_set(self):
        if self.stop_flag == False:
            if self.ppi_list != []:
                print("create data set")
                dataset = {
                    "type"      : "RRI",
                    "data"      : self.ppi_list,
                    "analysis"  : {
                        "type":"readiness"
                    }
                }
                return dataset
            
    def create_analysis_response(self, dataset, access_token):
        try:
            print("create analysis response")
            analysis_response = requests.post(
                # url = "https://analysis.kubioscloud.com/v2/analytics/analyze",
                # url = ANALYSIS_URL,
                url = self.analysis_url,
                headers = { "Authorization": "Bearer {}".format(access_token), #use access token to access your Kubios Cloud analysis session
                # "X-Api-Key": APIKEY},
                "X-Api-Key": self.apikey},
                json = dataset) #dataset will be automatically converted to JSON by the urequests library

            json_analysis_response = analysis_response.json()
            # self.analysis_response = json_analysis_response
            # print(self.analysis_response)
            print(json_analysis_response)
            self.stop_flag = True
            time.sleep(3) 
            gc.collect()
            return json_analysis_response
        except Exception as e:
            print(f"Failed to login to Kubios Server: {e}")
            self.error_flag = True
            self.stop_flag = True
        # print(self.analysis_response)
        
    def analyse(self):
            print("analyse")
                # return json_login_response, access_token
            access_token  = self.create_login_response()
            # self.add_ppi_list(ppi_list)
            dataset = self.create_data_set()
            json_analysis_response = self.create_analysis_response(dataset, access_token)
            
            return json_analysis_response
            
    def validate_response(self, json_analysis_reponse):
        if self.stop_flag == False:
            print("validate")
            if json_analysis_reponse != None:
                if analysis_response["status"] == "ok":
                    self.error_flag = False
                else:
                    self.error_flag = True
                    self.stop = True
            else:
                self.error_flag = True
                self.stop_flag = True
            
    def saving_result(self, json_analysis_reponse):
        # if self.result == None:
        file_name = "response_opt3.json"
        self.result = {
            "artefact_level"    : json_analysis_reponse['analysis']["artefact_level"],
            "create_timestamp"  : json_analysis_reponse['analysis']["create_timestamp"],
            "mean_hr_bpm"       : json_analysis_reponse['analysis']["mean_hr_bpm"],
            "mean_rr_ms"        : json_analysis_reponse['analysis']["mean_rr_ms"],
            "rmssd_ms"          : json_analysis_reponse['analysis']["rmssd_ms"],
            "sdnn_ms"           : json_analysis_reponse['analysis']["sdnn_ms"],
            "sns_index"         : json_analysis_reponse['analysis']["sns_index"],
            "pns_index"         : json_analysis_reponse['analysis']["pns_index"],
        }
        util.write_file(file_name,self.result)
        
            
        
    def test_run(self):

        print("Free memory:", gc.mem_free(), "bytes")

        SSID = "KMD658_Group_4"
        PASSWORD = "00000000"
        BROKER_IP = "192.168.4.253"

        APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
        CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
        CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"
        LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
        TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token" 
        REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"
        
        ppi_list = [664, 844, 856, 764, 648, 804, 724, 812, 896, 796, 804, 736, 800, 788, 856, 832, 884]

        response = requests.post(
        url = TOKEN_URL,
        data = 'grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
        headers = {'Content-Type':'application/x-www-form-urlencoded'},
        auth = (CLIENT_ID, CLIENT_SECRET))
        response = response.json() 
        #Parse JSON response into a python dictionary 
        access_token = response["access_token"]
        print("Free memory:", gc.mem_free(), "bytes")

        #Parse access token #Interval data to be sent to Kubios Cloud. Replace with your own data: intervals = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800] 
        # #Create the dataset dictionary HERE # Make the readiness analysis with the given data 
        dataset = { 
                "type": "RRI",
                "data": ppi_list,
                "analysis": {"type": "readiness"} 
                }

        response = requests.post(
        url = "https://analysis.kubioscloud.com/v2/analytics/analyze",
        headers = { "Authorization": "Bearer {}".format(access_token), #use access token to access your Kubios Cloud analysis session 
                    "X-Api-Key": APIKEY},
        json = dataset) #dataset will be automatically converted to JSON by the urequests library 
        response = response.json()
        print(response)
        print("Free memory:", gc.mem_free(), "bytes")
        gc.collect()
        print("Free memory:", gc.mem_free(), "bytes")   
        return response
        
    def create_response(self):
        while (self.try_count <200):
            time.sleep(0.05)
            try:
                                            
                print("Free memory:", gc.mem_free(), "bytes")

                SSID = "KMD658_Group_4"
                PASSWORD = "00000000"
                BROKER_IP = "192.168.4.253"

                APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
                CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
                CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"
                LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
                TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token" 
                REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"

                response = requests.post(
                url = TOKEN_URL,
                data = 'grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
                headers = {'Content-Type':'application/x-www-form-urlencoded'},
                auth = (CLIENT_ID, CLIENT_SECRET))
                response = response.json() 
                #Parse JSON response into a python dictionary 
                access_token = response["access_token"]
                print("Free memory:", gc.mem_free(), "bytes")

                #Parse access token #Interval data to be sent to Kubios Cloud. Replace with your own data: 
                # intervals = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800] 
                # #Create the dataset dictionary HERE # Make the readiness analysis with the given data 
                dataset = { 
                        "type": "RRI",
                        "data": self.ppi_list,
                        "analysis": {"type": "readiness"} 
                        }

                response = requests.post(
                url = "https://analysis.kubioscloud.com/v2/analytics/analyze",
                headers = { "Authorization": "Bearer {}".format(access_token), #use access token to access your Kubios Cloud analysis session 
                            "X-Api-Key": APIKEY},
                json = dataset) #dataset will be automatically converted to JSON by the urequests library 
                response = response.json()
                print(response)
                print("Free memory:", gc.mem_free(), "bytes")
                gc.collect()
                print("Free memory:", gc.mem_free(), "bytes")
            
            except Exception as e:
                print(f"Failed to login to Kubios Server: {e}")
                self.num_error += 1
                print("error ",self.num_error)
                gc.collect()
                if self.try_count <200:
                    continue
                else:
                    self.error_flag = True
                    self.stop_flag = True
            
    def run(self):
        print("start kubios")
        # print(self.stop_flag)
        if self.stop_flag == False:
            print(self.ppi_list)
            if not self.wlan.is_connected():
                self.wlan.connect_wlan()
            else:
                # response = self.create_response()
                # response = self.test_run()
                gc.collect()
                json_analysis_reponse = self.analyse()
                self.validate_response(json_analysis_reponse)
                print("analysis" ,json_analysis_reponse)
                if self.error_flag == False:
                    print("save result")
                    self.saving_result(response)
                    print(self.result)
                    self.stop_flag = True

    def on(self):
        self.error_flag = False
        self.stop_flag = False
        pass
    
    def off(self):
        self.stop_flag = True