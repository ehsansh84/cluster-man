from base_handler import BaseHandler
from publics import create_md5, decode_token, encode_token
from datetime import datetime
import sys, os, subprocess
import threading


class Cluster(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['master_count', 'worker_count', 'name'],
        }
        self.inputs = {
            'post': ['master_count', 'worker_count', 'name'],
        }
        self.casting['ints'] = ['master_count', 'worker_count']
        self.tokenless = True

    def before_post(self):
        col = self.db['cluster']
        if col.count({'name': self.params['name']}) > 0:
            self.set_output('cluster', 'name_exists')
            return False
        self.params['status'] = 'unconfigured'
        return True

    def after_post(self):
        col_cluster = self.db['cluster']
        col_server = self.db['server']
        #result = col_cluster.find({'status': 'unconfigured'})
        for i in range(self.params['master_count']):
            if i == 0:
                role = 'main_master'
            else:
                role = 'master'
            col_server.insert({
                'name': self.params['name'] + '_' + 'master' + str(i),
                'status': 'unconfigured',
                'cluster_name': self.params['name'],
                'ip': '',
                'role': role,
		'flavor_id': self.params['masters_flavor_id'],
		'user_data': self.params['masters_user_data'],
                'create_date': datetime.now(),
                'last_update': datetime.now()
        })


        for i in range(self.params['worker_count']):
            col_server.insert({
                'name': self.params['name'] + '_' + 'worker' + str(i),
                'status': 'unconfigured',
                'cluster_name': self.params['name'],
                'ip': '',
                'role': 'worker',
		'flavor_id': self.params['workers_flavor_id'],
		'user_data': self.params['workers_user_data'],
                'create_date': datetime.now(),
                'last_update': datetime.now()
        })
        
        # if self.params['master_count'] > 1:
        col_server.insert({
            'name': self.params['name'] + '_' + 'masters_ha',
            'status': 'unconfigured',
            'cluster_name': self.params['name'],
            'ip': '',
            'role': 'ha',
		'flavor_id': self.params['masters_flavor_id'],
		'user_data': self.params['masters_user_data'],
                'create_date': datetime.now(),
                'last_update': datetime.now()
        })
        col_cluster.update_one({'name': self.params['name']}, {'$set': {'status': 'pending'}})

    def before_put(self):
        if 'install' in self.params:
            print('YES!')
            self.allow_action = False
            if self.params['install'] == 'helm':
              try:
                col_server = self.db['server']
                main_master = col_server.find_one({'role': 'main_master', 'cluster_name': self.params['cluster_name']})
                if main_master is not None:
                    command = "ansible-playbook playbooks/install-helm.yml -i %s," % main_master['ip']
                    print(command)
                    output = subprocess.check_output(command, shell=True).decode()
                    print(output)
                    self.success()
                else:
                    print("Main master not found!")
              except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
            elif self.params['install'] == 'traefik':
              try:
                col_server = self.db['server']
                main_master = col_server.find_one({'role': 'main_master', 'cluster_name': self.params['cluster_name']})
                if main_master is not None:
                    command = "ansible-playbook playbooks/install-traefik.yml -i %s," % main_master['ip']
                    print(command)
                    output = subprocess.check_output(command, shell=True).decode()
                    print(output)
                    self.success()
                else:
                    print("Main master not found!")
              except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
