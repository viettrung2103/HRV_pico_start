import util

class History_List:
    def __init__(self,size = 6):
        self.size = size
        # self.cur = 0
        self.default_value = {"num":"0","idx":"0","name":"Back","value":"Back"}
        self.list = []
        self.data = None
        self.highest_num = 0
        self.new_history = None
        self.file_name = "history.json"
        self.key_name = "history_list"

#         self.current_
    def add(self,response):

        new_history = self.create_new_history(response)
        print(new_history['name'])
        #program_list len = 6 # [1,2,3,4,5'back']
        #>> real_list = n - 1
        #real list len = n -1
        n = len(self.list) 
        final_index = 0

        if n <= self.size - 1:
            # self.current_list = self.list[:n-1]
            for i in range(n-1,-1,-1):
                # print("index {}".format(i))
                self.list[i] = self.list[i-1]
                if i == 0:
                    self.list[i] = new_history
                self.list[i]["idx"] = i
                # print("current ",self.list)
                final_index = i
            final_index += 1  
            self.default_value["idx"] = n
            self.list.append(self.default_value)
        else:
            for i in range(n-2,-1,-1):
                self.list[i] = self.list[i-1]
                if i == 0:
                    self.list[i] = new_history
                self.list[i]["idx"] = i
                # final_index = i
            
        # print("final", self.list)
        self.save_list()
    def is_exist(self):
        return self.exist_flag
        
    def create_list(self):
        self.list.append(self.default_value)
        

        
    def load_list_from_json(self):
        data = util.read_file(self.file_name)
        if not data:
            self.create_list() 
        else:
            self.list = data[self.key_name]
    
    def save_list(self):
        list_dict = {self.key_name:self.list}
        util.write_file(self.file_name,list_dict)
        
    def update_highest_number(self):
        if self.list:
            for i in range(len(self.list) - 1):
                history_object = self.list[i]
                history_object_numb = int(history_object["num"])
                self.highest_num = max(self.highest_num,history_object_numb)
        # print("highest number",self.highest_num)
            
    def create_new_history(self,response):
        self.update_highest_number()
        text = "MEASUREMENT {}".format(self.highest_num +1)
        new_history = {
            "num": str(self.highest_num + 1),
            "name": text,
            "idx":0,
            "value": response
        }
        # print("new history ",new_history)
        return new_history
        
    def get_history_detail(self,idx):
        return self.list[idx]
    
    
    def show_list(self):
        return self.list
    
