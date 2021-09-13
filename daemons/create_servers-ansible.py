import os
import re, sys
import subprocess
sys.path.append('/app')
from datetime import datetime
#os.environ["MONGO"] = "localhost:27021"
#ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(ROOT_DIR+ '/..')
#sys.path.append(os.path.join(sys.path[0], '..'))
#from publics import db
#from publics import localdb 
from publics import PrintException

from pymongo import MongoClient
con = MongoClient('mongodb://localhost:27021')
db = con['km']

col_cluster = db['cluster']
col_server = db['server']
#CLUSTER_NAME = 'hashimoto'
#result = col_server.find({'ip': ''})
#for server in result:
#  for i in range(cluster['master_count']):
#    col_server.insert({
#	'name': cluster['name'] + '_' + 'master' + str(i),
#	'status': 'unconfigured',
#	'cluster_name': cluster['name'],
#	'ip': '',
#	'role': 'master',
#	'create_date': datetime.now(),
#	'last_update': datetime.now()
#})
#  for i in range(cluster['worker_count']):
#    col_server.insert({
#	'name': cluster['name'] + '_' + 'worker' + str(i),
#	'status': 'unconfigured',
#	'cluster_name': cluster['name'],
#	'ip': '',
#	'role': 'worker',
#	'create_date': datetime.now(),
#	'last_update': datetime.now()
#})
#  col_server.insert({
#	'name': cluster['name'] + '_' + 'masters_ha',
#	'status': 'unconfigured',
#	'cluster_name': cluster['name'],
#	'ip': '',
#	'role': 'ha',
#	'create_date': datetime.now(),
#	'last_update': datetime.now()
#})
#  col_cluster.update_one({'_id': cluster['_id']}, {'$set': {'status': 'pending'}})

import base64
from consts import consts

os.environ["OS_DOMAIN_ID"] = "default"
os.environ["OS_DOMAIN_NAME"] = "default"

for server in col_server.find({'ip': ''}):
  command = f"ansible-playbook {consts.PLAYBOOK_DIR}/tabriz_node.yml -e 'name=%s flavor_id=%s'" % (server['name'],server['flavor_id'])
  print(command)
  user_data = base64.b64decode(server['user_data'])
  f = open('/temp/user_data.yml', 'w')
  f.write(user_data.decode())
  f.close()
  output = subprocess.check_output(command, shell=True).decode()
  pat = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
  IP = pat.search(output)
  col_server.update_one({'_id': server['_id']}, {'$set': {'ip': IP.group(), 'status': 'ip'}})

