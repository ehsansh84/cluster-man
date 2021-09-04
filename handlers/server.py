from base_handler import BaseHandler
from publics import create_md5, decode_token, encode_token
from datetime import datetime
import subprocess, sys, os


class Server(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['name', 'cluster_name', 'flavor_id'],
        }
        self.inputs = {
            'post': ['ip', 'status', 'name', 'cluster', 'role', 'cluster_name', 'flavor_id'],
        }
        self.tokenless = True
        self.casting['lists'] = ['server_ips']

    def before_post(self):
        import os
        import re
        #TODO: there must be a default user data
        os.environ["OS_DOMAIN_ID"] = "default"
        os.environ["OS_DOMAIN_NAME"] = "default"
        command = "ansible-playbook /home/ubuntu/private-playoobks/tabriz_node.yml -e 'name=%s'" % self.params['name']
        print(command)
        output = subprocess.check_output(command, shell=True).decode()
        pat = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        IP = pat.search(output)
        self.params['ip'] = IP.group()
        self.params['status'] = 'unconfigured'
        self.output['data']['item']['ip'] = IP.group()
        self.success()
        return True


    def before_put(self):
        if 'join_as_worker' in self.params:
            try:
                print(self.params)
                #TODO: Should use daemon's code
                command = "ansible-playbook playbooks/token.yml -i %s," % self.params['join_as_worker']
                print(command)
                output = subprocess.check_output(command, shell=True).decode()
                print(output)
    
                ips = ""
                ip_list = []
                for worker in self.params['server_ips']:
                  ips += worker + ","
                  ip_list.append(worker['ip'])
                col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'pending'}}, multi=True)
                try:
                  if ips != ",":
                    command = "ansible-playbook playbooks/join-worker.yml -i %s" % ips
                    print(command)
                    output = subprocess.check_output(command, shell=True).decode()
                except:
                  col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'error'}}, multi=True)
    
            except Exception as e:
              exc_type, exc_obj, exc_tb = sys.exc_info()
              fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
              print(exc_type, fname, exc_tb.tb_lineno)
              print(str(e))
              self.fail()
            
            self.allow = False


