import requests
import re
import json
import os
import time
import datetime
import sys
import logging
from threading import Thread

stats = list()  # List for save check results

cwd = os.path.dirname(__file__)  # Set cwd

logging.basicConfig(format = u'%(levelname)s: %(asctime)s %(message)s', level = logging.INFO)

class SimMon:

    def __init__(self, filename):
        self.filename = filename
        self._read_config()
        self._send_startup_message()
        thread1 = Thread(target=self._find_string)
        thread2 = Thread(target=self._send_failed_message)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

    def _read_config(self):  # Read config file
        try:
            with open(os.path.join(cwd, self.filename)) as file:
                self.config = json.load(file)
                if self.config["proxy"] == None:
                    self._proxy = None
                self._proxy = dict(
                    http=self.config["proxy"], https=self.config["proxy"])  # Set proxy
        except Exception as e:
            logging.error('Config file not readable. Error: ' + str(e))
            sys.exit(1)

    def _send_startup_message(self):  # Send startup message
        self._startup_message = 'Monitoring is up!'
        self._api = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(
            self.config["bot_token"], self.config["chat_id"], self._startup_message)
        r = requests.post(self._api, proxies=self._proxy, timeout=3)
        r.raise_for_status

    def _send_failed_message(self):  # Send failed message
        self.message = "URL: {} is broken! String '{}' not found in answer".format(
            self.config["url"], self.config["find_string"])
        self._api = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(
            self.config["bot_token"], self.config["chat_id"], self.message)
        while True:
            if len(stats) != 0:
                if stats[-1] == 0:
                    r = requests.post(self._api, proxies=self._proxy, timeout=3)
                    r.raise_for_status
            del stats[:] # Flush metrics list
            time.sleep(60)

    def _find_string(self):  # Find string in answer
        while True:
            r = requests.post(self.config["url"], timeout=3)
            r.raise_for_status
            find = len(re.findall(self.config["find_string"], r.text))
            stats.append(find)
            print(stats)
            if find == 1:
                logging.info("CHECK STATUS: match string: '{}' found in url: '{}'".format(self.config["find_string"], self.config["url"]))
            else:
                logging.info("CHECK STATUS: match string: '{}' not found in url: '{}'".format(self.config["find_string"], self.config["url"]))
            time.sleep(5)

if __name__ == "__main__":
    logging.info('SimMon start!')
    start = SimMon('config.json')