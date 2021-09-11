import os
import re, sys
import subprocess
import requests
import json
from datetime import datetime
from auth import get_token
import threading
from publics import db, consts
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from bson import ObjectId
sys.path.append('/app')

#f = open("afranet.json")
f = open(consts.SERVER_DATA)
data = json.load(f)
#print(data)
f.close()

base_url = "https://%s:8774/v2.1" % data['server_ip']
auth_base_url = "https://%s:5000/v3"  % data['server_ip']

def create_server(token, _id, name, flavor_id, image_id, user_data):
    link = base_url + "/servers"
    params = {
            "server": {
                "name": name,
                "flavorRef": flavor_id,
                "networks": [{"uuid": data['network_id']}],
                "imageRef": image_id,
                "availability_zone": "nova",
                "user_data": user_data,
            }
        }
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    try:
        # print(f'server name: {name}')
        r = requests.post(
            link, json=params, headers=headers, verify=False
        )
        print(r.text)
        response = r.json()
        print('posted!')
        print(response)
        if "server" not in response:
            serverId = "NO"
        else:
            server_id = response["server"]["id"]
            link = f"{base_url}/servers/{server_id}"
            try:
                response = requests.get(link, headers=headers, verify=False).json()
                col_server.update_one({'_id': _id}, {'$set': {'status': 'creating', 'server_id': response['server']['id']}})
                return response
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)        
                print(str(e))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        print(" :::: cloud connection failed\n")

        
token = get_token()
print(token)

# from pymongo import MongoClient
# con = MongoClient('mongodb://localhost:27021')
# db = con['km']

col_cluster = db()['cluster']
col_server = db()['server']

for server in col_server.find({'ip': '', 'status': {'$ne': 'creating'}}):
    try:
        print('=================================================D')
        #print(server)
        x = threading.Thread(target=create_server, args=(token, server['_id'], server['name'], server['flavor_id'], data['image_id'], server['user_data'],))
        x.start()
    except Exception as e:
        print('ERROR HERE')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        #col_server.update_one({'ip': ha}, {'$set': {'status': 'error'}})
    
  
