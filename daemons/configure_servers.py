import os
import re, sys
import subprocess
sys.path.append('/app')
from datetime import datetime
from functions.ha import config_ha
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
col_ha = db['ha']

def load_cluster_info(clustername):
  c_info = {
        'masters_ha' : '',
        'workers_ha' : [],
        'masters': [],
        'workers': []
        }
  result = col_server.find({'cluster_name': clustername})
  for server in result:
    if server['role'] == 'ha':
        c_info['masters_ha'] = server['ip']
    elif server['role'] == 'master':
        c_info['masters'].append({
					'ip': server['ip'],
					'name': server['name']})
    elif server['role'] == 'worker':
        c_info['workers'].append({
					'ip': server['ip'],
					'name': server['name']})
    elif server['role'] == 'workers_ha':
        c_info['workers_ha'].append({
					'ip': server['ip'],
					'name': server['name']})
  return c_info


def config_master():
  #print(cluster_infoter(ter(ter() 
  for master in cluster_info['masters']:
    if '0' in master['name']:
      col_server.update_one({'ip': master['ip']}, {'$set': {'status': 'pending'}})
      try:
        print(master)
        os.system(' ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R "%s"' % master['ip'])
        command = "ansible-playbook ../playbooks/activate-masters.yml -e 'ha_ip=%s' -i %s," % (cluster_info['masters_ha'], master['ip'])
        print(command)
        output = subprocess.check_output(command, shell=True).decode()
        print(output)
        col_server.update_one({'ip': master['ip']}, {'$set': {'status': 'done'}})
      except:
        col_server.update_one({'ip': master['ip']}, {'$set': {'status': 'error'}})

def get_token():
    command = "ansible-playbook ../playbooks/token.yml -i %s," % cluster_info['masters'][0]['ip']
    print(command)
    output = subprocess.check_output(command, shell=True).decode()
    print(output)


def config_other_masters():
  #print(cluster_info) 
  ips = ""
  ip_list = [] 
  for master in cluster_info['masters']:
    if '0' not in master['name']:
      col_server.update_one({'ip': master['ip']}, {'$set': {'status': 'pending'}})
      os.system(' ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R "%s"' % master['ip'])
      ips+= master['ip'] + ","
      ip_list.append(master['ip'])
  print(ips)
   
  try:
    command = "ansible-playbook ../playbooks/join-master.yml -e 'ha_ip=%s' -i %s" % (cluster_info['masters_ha'], ips)
    print(command)
    if ips != ",":
      output = subprocess.check_output(command, shell=True).decode()
      print(output)
      col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'done'}}, multi=True)

  except:
    col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'error'}}, multi=True)




def join_workers():
#    command = "ansible-playbook ../playbooks/token.yml -i %s," % cluster_info['masters'][0]['ip']
#    print(command)
#    if print_mode:
#      print(command)
#    else:
#      output = subprocess.check_output(command, shell=True).decode()
#
#    worker = get_free_server(CLUSTER_NAME, 'Worker')
    ips = ""
    ip_list = []
    for worker in cluster_info['workers']:
      ips += worker['ip'] + ","
      ip_list.append(worker['ip'])
    col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'pending'}}, multi=True)
    try:
      if ips != ",":
        command = "ansible-playbook ../playbooks/join-worker.yml -i %s" % ips
        print(command)
        output = subprocess.check_output(command, shell=True).decode()
    except:
      col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'error'}}, multi=True)


for cluster in col_cluster.find({"status": "pending"}):
    cluster_info = load_cluster_info(cluster['name'])
    print(cluster['master_count'])
    print(cluster['name'])
    print(cluster['master_count'])
    if cluster['master_count'] > 1:
        ha_id = ''
        if col_ha.find_one({'name': cluster['name']}) is None:
            ha_id = col_ha.insert({
                'name': cluster['name'],
                'frontend': cluster_info['masters_ha'],
                'backend': cluster_info['masters'],
                'status': 'pending'
            })
            try:
                config_ha(cluster_info['masters_ha'], cluster_info['masters'])
                col_ha.update_one({'_id': ha_id}, {'$set': {'status': 'done'}})
            except Exception as e:
                #TODO Good to have error message here
                print(str(e))
                print('============================================')
                print(type(ha_id))
                print(ha_id)
                col_ha.update_one({'_id': ha_id}, {'$set': {'status': 'error'}})

        config_master()
        get_token()
        config_other_masters()
        join_workers()
    else:
        print(1)
        pass
