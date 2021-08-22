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

def load_cluster_info():
  c_info = {
        'masters_ha' : '',
        'masters': [],
        'workers': []
        }
  result = col_server.find({'cluster_name': 'tcluster'})
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
  return c_info

cluster_info = load_cluster_info()
#print(cluster_info)
def create_ha_config():
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

def create_etc_hosts():
  hosts = ""
  for server in cluster_info['masters']:
    hosts += "%s %s\n" % (server['ip'], server['name'])
  f = open('../temp/hosts', 'w')
  hosts = "127.0.0.1 localhost\n" + hosts
  f.write(hosts)
  f.close()
#print(cluster_info['masters_ha'])

def config_ha():
  print(col_server.update_one({'ip': cluster_info['masters_ha']}, {'$set': {'status': 'pending'}}).raw_result)
  try:
    command = "ansible-playbook ../playbooks/config-ha.yml -i %s," % cluster_info['masters_haa']
    #print(command)
    output = subprocess.check_output(command, shell=True).decode()
    #print(output)
    col_server.update_one({'ip': cluster_info['masters_ha']}, {'$set': {'status': 'done'}})
  except Exception as e:
    print(str(e))
    col_server.update_one({'ip': cluster_info['masters_ha']}, {'$set': {'status': 'error'}})

#create_ha_config()
#create_etc_hosts()
#config_ha()

def config_master():
  #print(cluster_info) 
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


#        with open('activate_master.log', 'wb') as f:  # replace 'w' with 'wb' for Python 3
#          process = subprocess.Popen(command, stdout=subprocess.PIPE)
#          for c in iter(lambda: process.stdout.read(1), 'b'):  # replace '' with b'' for Python 3
#            sys.stdout.write(c)
#            f.write(c)
#        f.close()
        col_server.update_one({'ip': master['ip']}, {'$set': {'status': 'done'}})
      except:
        col_server.update_one({'ip': master['ip']}, {'$set': {'status': 'error'}})

def get_token():
    command = "ansible-playbook ../playbooks/token.yml -i %s," % cluster_info['masters'][0]['ip']
    print(command)
    output = subprocess.check_output(command, shell=True).decode()
    print(output)

#get_token()

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

config_other_masters()

#        ips += master['ip'] + ","
#    if ips != ",":
#      command = "ansible-playbook join-master.yml -i %s," % ips
#      #print(command)
#      if print_mode:
#        print(command)
#      else:
#        output = subprocess.check_output(command, shell=True).decode()
#)

