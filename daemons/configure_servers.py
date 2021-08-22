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


from pymongo import MongoClient
con = MongoClient('mongodb://localhost:27021')
db = con['km']

col_cluster = db['cluster']
col_server = db['server']
cluster_info = {
        'masters_ha' : '',
        'masters': [],
        'workers': []
        }
#result = col_cluster.find({'status': 'unconfigured'})
result = col_server.find({'status': 'ip'})
for server in result:
    if server['role'] == 'ha':
        cluster_info['masters_ha'] = server['ip']
    elif server['role'] == 'master':
        cluster_info['masters'].append({
					'ip': server['ip'],
					'name': server['name']})
    elif server['role'] == 'worker':
        cluster_info['workers'].append({
					'ip': server['ip'],
					'name': server['name']})

print(cluster_info)
f = open('../templates/hacfg.tmpl')
ha_template = f.read()
f.close()

backend = ""
for server in cluster_info['masters']:
  backend += "  server %s %s:6443 check fall 3 rise 2\n" % (server['name'],server['ip'])
tmpl = ha_template % (cluster_info['masters_ha'], backend)
if not os.path.exists('../temp'):
  os.makedirs('../temp')
f = open('../temp/haproxy.cfg', 'w')
f.write(tmpl)
f.close()

hosts = ""
for server in cluster_info['masters']:
  hosts += "%s %s\n" % (server['ip'], server['name'])
f = open('../temp/hosts', 'w')
hosts = "127.0.0.1 localhost\n" + hosts
f.write(hosts)
f.close()


command = "ansible-playbook ../playbooks/config-ha.yml -i %s," % cluster_info['masters_ha']
print(command)
output = subprocess.check_output(command, shell=True).decode()
print(output)

