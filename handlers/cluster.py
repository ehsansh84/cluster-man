from base_handler import BaseHandler
from publics import create_md5, decode_token, encode_token
from datetime import datetime


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
        self.params['status'] = 'unconfigured'
        return True

    def after_post(self):
        col_cluster = self.db['cluster']
        col_server = self.db['server']
        #result = col_cluster.find({'status': 'unconfigured'})
        for i in range(self.params['master_count']):
            col_server.insert({
                'name': self.params['name'] + '_' + 'master' + str(i),
                'status': 'unconfigured',
                'cluster_name': self.params['name'],
                'ip': '',
                'role': 'master',
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
        
        if self.params['master_count'] > 1:
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
