import os
import subprocess
import sys
from base_handler import BaseHandler
from log_tools import log
from publics import PrintException


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
        # print("Start")
        log.info('Start')
        try:
            self.params = {k: self.get_argument(k) for k in self.request.arguments}
            number = 10 if self.params.get('number') == None else self.params.get('number')
            log.info(f"tail  -n {number}  /home/ubuntu/log/cron/{self.params['name']}.log | grep -v DEBUG")
            output = subprocess.check_output(f"tail  -n {number}  /home/ubuntu/log/cron/{self.params['name']}.log | grep -v DEBUG", shell=True).decode()
            log.info('output')

            self.write('WTF?')
            self.write(output)
        except:
            PrintException()

