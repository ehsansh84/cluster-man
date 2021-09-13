import os
import subprocess
import sys
from base_handler import BaseHandler


class Server(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['name', 'cluster_name', 'flavor_id', 'platform'],
        }
        self.inputs = {
            'post': ['ip', 'status', 'name', 'cluster', 'role', 'cluster_name', 'flavor_id', 'platform'],
        }
        self.tokenless = True
        self.casting['lists'] = ['server_ips']

    def before_post(self):
        if 'ip' not in self.params:
            self.params['ip'] = ''
        self.params['status'] = 'unconfigured'
        col_cluster = self.db['cluster']
        col_cluster.update_one({'name': self.params['cluster_name']}, {'$set': {'status': 'pending'}})
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


