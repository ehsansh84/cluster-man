import os
import subprocess
import sys
from base_handler import BaseHandler
from log_tools import log


class Log(BaseHandler):
    def init_method(self):
        self.required = {
            'get': ['name']
        }
        self.inputs = {
            'get': ['name', 'number']
        }
        self.tokenless = True
        self.casting['ints'] = ['number']

    def get(self, *args, **kwargs):
        print("Start")
        log.info('Start')
        try:
            number = 10 if self.params.get('number') == None else self.params.get('number')
            output = subprocess.check_output(f"tail  -n {number}  /home/ubuntu/log/cron/{self.params['name']}.log | grep -v DEBUG", shell=True).decode()
            print(output)

            self.write('WTF?')
            self.write(output)
        except:
            pass

