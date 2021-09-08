import os
import re, sys
import subprocess
import requests
import json
from datetime import datetime
from auth import get_token
sys.path.append('/app')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from publics import db

f = open("tabriz.json")
#f = open("afranet.json")
data = json.load(f)
#print(data)
f.close()

base_url = "https://%s:8774/v2.1" % data['server_ip']
auth_base_url = "https://%s:5000/v3"  % data['server_ip']

token = get_token()
print(token)
headers = {"X-Auth-Token": token, "Content-Type": "application/json"}

# from pymongo import MongoClient
# con = MongoClient('mongodb://localhost:27021')
# db = con['km']

col_cluster = db()['cluster']
col_server = db()['server']
import base64

for server in col_server.find({'status': {'$in': ['creating', '']}}):
  print('=================================================D')
  print(server['name'])
  print(server)
  status_url= f"{base_url}/servers/{server['server_id']}"

  print(status_url)
  try:
      print(headers)
      print(status_url)
      response = requests.get(status_url, headers=headers, verify=False).json()
      print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
      print(response)
      r = response['server']
      #print(r)
      #print(r['name'], r['status'])
      ip = r['addresses'][data['network_name']][0]['addr']

      col_server.update_one({'_id': server['_id']}, {'$set': {'status': 'ip', 'ip': ip}})
  except Exception as e:
          #print(server)
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)        
      print(str(e))
      #print('11111111111111111111111')
      #print(response)
      #if r['status'] == 'ERROR':
      #    col_server.update_one({'_id': server['_id']}, {'$set': {'status': 'creating', 'server_id': '', 'ip': ''}})
  #response = create_server(token, server['name'], server['flavor_id'], data['image_id'], server['user_data'])
  #print(response)
  #print(response['server']['id'])
  #col_server.update_one({'_id': server['_id']}, {'$set': {'status': 'creating', 'server_id': response['server']['id']}})










  #command = "ansible-playbook ../playbooks/tabriz_node.yml -e 'name=%s flavor_id=%s'" % (server['name'],server['flavor_id'])
  #print(command)
  #user_data = base64.b64decode(server['user_data'])
  #f = open('../temp/user_data.yml', 'w')
  #f.write(user_data.decode())
  #f.close()
  #output = subprocess.check_output(command, shell=True).decode()
  #pat = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
  #IP = pat.search(output)
  
#col_server.update_one({'_id': server['_id']}, {'$set': {'ip': IP.group(), 'status': 'ip'}})

