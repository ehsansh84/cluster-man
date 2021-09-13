import os
import subprocess
import sys
from base_handler import BaseHandler


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

    def before_get(self):
        try:
            number = 10 if self.params.get('number') == None else self.params.get('number')
            output = subprocess.check_output(f"tail  -n {number}  /home/ubuntu/log/cron/{self.params['name']}.log | grep -v DEBUG", shell=True).decode()
            self.output = output
        except:
            pass
        self.allow_action = False
        return True

