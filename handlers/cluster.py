import os
import subprocess
import sys
from datetime import datetime

from base_handler import BaseHandler
from log_tools import log
from publics import PrintException
from bson import ObjectId
from consts import consts


class Cluster(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['master_count', 'worker_count', 'name', 'platform'],
        }
        self.inputs = {
            'post': ['master_count', 'worker_count', 'name', 'platform'],
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
        for i in range(self.params['master_count']):
            if i == 0:
                role = 'main_master'
            else:
                role = 'master'
            col_server.insert({
                'name': self.params['name'] + '_' + 'master' + str(i),
                'status': 'unconfigured',
                'cluster_name': self.params['name'],
                'platform': self.params['platform'],
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
                'platform': self.params['platform'],
                'ip': '',
                'role': 'worker',
		'flavor_id': self.params['workers_flavor_id'],
		'user_data': self.params['workers_user_data'],
                'create_date': datetime.now(),
                'last_update': datetime.now()
        })

        # if self.params['master_count'] > 1:
        print('CREATE an HA')
        col_server.insert({
            'name': self.params['name'] + '_' + 'masters_ha',
            'status': 'unconfigured',
            'cluster_name': self.params['name'],
            'platform': self.params['platform'],
            'ip': '',
            'role': 'ha',
            'flavor_id': self.params['masters_flavor_id'],
            'user_data': self.params['masters_user_data'],
            'create_date': datetime.now(),
            'last_update': datetime.now()
        })
        col_cluster.update_one({'name': self.params['name']}, {'$set': {'status': 'pending'}})

    def before_put(self):
        try:
            if 'install' in self.params:
                self.allow_action = False
                if self.params['install'] == 'helm':
                    try:
                        log.info('Going to install helm...')
                        col_server = self.db['server']
                        main_master = col_server.find_one(
                            {'role': 'main_master', 'cluster_name': self.params['cluster_name']})
                        if main_master is not None:
                            command = f"ansible-playbook {consts.PLAYBOOK_DIR}/install-helm.yml -i ubuntu@%s," % \
                                      main_master['ip']
                            log.debug(command)
                            output = subprocess.check_output(command, shell=True).decode()
                            log.debug(output)
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
                        main_master = col_server.find_one(
                            {'role': 'main_master', 'cluster_name': self.params['cluster_name']})
                        if main_master is not None:
                            command = "ansible-playbook /app/playbooks/install-traefik.yml -i ubuntu@%s," % main_master[
                                'ip']
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
            return True
        except Exception as e:
            log.error(f'Failed {str(e)}')
            return False

    def before_delete(self):
        try:
            col_cluster = self.db['cluster']
            cluster_info = col_cluster.find_one({'_id': self.id})
            log.debug({'cluster_query': {'_id': self.id}})
            col_server = self.db['server']
            log.info('Start deleting servers')
            # log.debug({'cluster_name': cluster_info})
            # log.debug({'cluster_name': cluster_info['name']})
            # log.debug(col_server.remove({'cluster_name': cluster_info['name']}))
            log.debug(col_server.update_many({'cluster_name': cluster_info['name']}, {'$set': {'status': 'deleting'}}).raw_result)
            # log.info('Servers deleted')
            return True
        except Exception as e:
            log.error(f'Can not delete servers for this cluster {str(e)}')
            return False
