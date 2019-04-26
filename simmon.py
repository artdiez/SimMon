import requests, re, json, os, time, sys
from threading import Thread

stats = list() #List for save check results

cwd = os.path.dirname(__file__) #Set cwd

class WebCheckBot:

    def __init__(self, filename):
        self.filename = filename
        self._read()
        self._send_startup_message()
        thread1 = Thread(target=self._find_string)
        thread2 = Thread(target=self._send_failed_message)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
    
    def _read (self): #Read config file
        
        try:
            with open(os.path.join(cwd, self.filename)) as file:
                self.config=json.load(file)
                if self.config["proxy"] == None: 
                    self._proxy=None
                self._proxy=dict(http=self.config["proxy"],https=self.config["proxy"]) #Set proxy
        except Exception as e:
            print('Config file not readable. Error: ' + str(e),file=sys.stderr)

    
    def _send_startup_message(self): #Send startup message
        self._startup_message='Monitoring is up!'
        self._api="https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(self.config["bot_token"],self.config["chat_id"],self._startup_message)
        r = requests.post(self._api, proxies=self._proxy, timeout=3)
        r.raise_for_status

    def _send_failed_message(self): #Send failed message
        self.message="URL: {} is broken! String '{}' not found in answer".format(self.config["url"], self.config["find_string"])
        self.api="https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(self.config["bot_token"],self.config["chat_id"],self.message)
        while True:
            if len(stats) != 0:
                if stats[-1] == 1: 
                    r = requests.post(self.api, proxies=self._proxy, timeout=3)
                    r.raise_for_status
            time.sleep(60)

    def _find_string(self): #Find string in answer
        while True:
          r = requests.post(self.config["url"], timeout=3)
          r.raise_for_status
          find = len(re.findall(self.config["find_string"],r.text))
          stats.append(find)
          print(stats) #Debug
          time.sleep(5)

if __name__ == "__main__":  
    start=WebCheckBot('config.json')