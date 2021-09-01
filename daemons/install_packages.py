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

cluster_info = load_cluster_info('ehsan')

def install_helm():
  #print(cluster_infoter(ter(ter() 
      print(cluster_info['masters'][0]['ip'])
      try:
        command = "ansible-playbook ../playbooks/install-helm.yml -i %s," % cluster_info['masters'][0]['ip']
        print(command)
        output = subprocess.check_output(command, shell=True).decode()
        print(output)
      except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

install_helm()
