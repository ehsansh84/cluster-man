from base_handler import BaseHandler
from publics import create_md5, decode_token, encode_token
from datetime import datetime
import subprocess


class Server(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['name'],
        }
        self.inputs = {
            'post': ['ip', 'status', 'name', 'cluster', 'role'],
        }
        self.tokenless = True

    def before_post(self):
        import os
        import re
        os.environ["OS_DOMAIN_ID"] = "default"
        os.environ["OS_DOMAIN_NAME"] = "default"
        command = "ansible-playbook /home/ubuntu/private-playoobks/tabriz_node.yml -e 'name=%s'" % self.params['name']
        print(command)
        output = subprocess.check_output(command, shell=True).decode()
        pat = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        IP = pat.search(output)
        self.params['ip'] = IP.group()
        self.params['status'] = 'free'
        self.output['data']['item']['ip'] = IP.group()
        self.success()
        return True

