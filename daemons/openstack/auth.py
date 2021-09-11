import os
import re, sys
import requests
import json
from datetime import datetime
sys.path.append('/app')
from publics import consts
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


f = open(consts.SERVER_DATA)
#f = open("afranet.json")
# f = open("tabriz.json")
data = json.load(f)
f.close()

base_url = "https://%s:8774/v2.1" % data['server_ip']
auth_base_url = "https://%s:5000/v3"  % data['server_ip']

def get_token():
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

