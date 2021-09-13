import sys
sys.path.append('/app')
sys.path.append('/home/ehsan/dev/cluster-man/')
import json
import requests
from publics import consts, PrintException, get_platform_data, ExceptionLine
# from publics import logger
from log_tools import log
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# f = open(consts.SERVER_DATA)
# data = json.load(f)
# f.close()

# base_url = "https://%s:8774/v2.1" % data['server_ip']


def get_token(platform):
    data = get_platform_data(platform)
    auth_base_url = "https://%s:5000/v3" % data['server_ip']
    headers = {"content-type": "application/json"}
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
        log.info('Going to get a token from OpenStack...')
        log.debug(link)
        response = requests.post(link, json=params, verify=False, headers=headers)
        log.debug(f'Response code is: {response.status_code}')
        if "X-Subject-Token" not in response.headers:
            return ""
        else:
            token = response.headers["X-Subject-Token"]
            log.info('Authentication done.')
            return token
    except Exception as e:
        log.error(f'Getting token failed! {ExceptionLine()} {str(e)}')
        PrintException()

