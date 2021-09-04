import os
import re, sys
import subprocess
import requests
import json
from datetime import datetime
sys.path.append('/app')

f = open("afranet.json")
data = json.load(f)
print(data)
f.close()

base_url = "https://%s:8774/v2.1" % data['server_ip']
auth_base_url = "https://%s:5000/v3"  % data['server_ip']

def createInstance(token):
    link = base_url + "/servers"
    params = {
            "server": {
                "name": "APISERVER7",
                "flavorRef": "dd40659a-c2d1-48f3-83a3-3e5871eb1d2d",
                "networks": [{"uuid": "16da6665-9150-4288-883e-9cf1368d8add"}],
                "imageRef": "87b0c926-6d1a-4ec0-98b9-bafa5c8177bd",
                "availability_zone": "nova",
            }
        }
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    try:
        response = requests.post(
            link, json=params, headers=headers, verify=False
        ).json()
        if "server" not in response:
            serverId = "NO"
        else:
            server_id = response["server"]["id"]
            print('================= response ================')
            print(response['server']['id'])
            link = f"{base_url}/servers/{server_id}"
            print(link)
            try:
                response = requests.get(link, headers=headers, verify=False).json()
                print(response)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)        
                print(str(e))


    except:
        token = ""
        print(" :::: cloud connection failed\n")

def authorize():
    headers = {"content-type":"application/json"}
    link = auth_base_url + '/auth/tokens'
    params = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": data['username'],
                        "domain": {"id": 'default'},
                        "password": data['password'],
                    }
                },
            },
            "scope": {
                "project": {"name": data['project_name'], "domain": {"id": "default"}}
            },
        }
    }
    try:
        response = requests.post(link, json=params, verify=False, headers=headers)
        if "X-Subject-Token" not in response.headers:
            token = ""
        else:
            token = response.headers["X-Subject-Token"]
            print("cloud authentication ok")
            return token
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)        
        token = ""
        print('ERROR')
        print(str(e))

token = authorize()
print(token)
createInstance(token)

