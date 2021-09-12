import json
import sys
import requests
sys.path.append('/app')
from publics import consts, PrintException
from publics import logger
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

f = open(consts.SERVER_DATA)
data = json.load(f)
f.close()

base_url = "https://%s:8774/v2.1" % data['server_ip']
auth_base_url = "https://%s:5000/v3" % data['server_ip']


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
        logger.info('Going to get a token from OpenStack...')
        response = requests.post(link, json=params, verify=False, headers=headers)
        if "X-Subject-Token" not in response.headers:
            return ""
        else:
            token = response.headers["X-Subject-Token"]
            logger.info('Authentication done.')
            return token
    except Exception as e:
        logger.error(f'Getting token failed!')
        PrintException()

