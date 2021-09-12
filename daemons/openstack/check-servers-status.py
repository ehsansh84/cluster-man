import json
import sys
import requests
from auth import get_token
sys.path.append('/app')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from publics import db, consts, logger

f = open(consts.SERVER_DATA)
data = json.load(f)
f.close()
base_url = "https://%s:8774/v2.1" % data['server_ip']
auth_base_url = "https://%s:5000/v3"  % data['server_ip']

token = get_token()
headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
col_cluster = db()['cluster']
col_server = db()['server']

logger.info(f'Checking status daemon is started...')

for server in col_server.find({'status': {'$in': ['creating', '']}}):
    logger.info(f'Checking a server status for: {server["name"]}')
    status_url = f"{base_url}/servers/{server['server_id']}"
    try:
        logger.info(f'Calling {status_url} with headers: {headers}')
        r = requests.get(status_url, headers=headers, verify=False)
        response = r.json()
        logger.info(f'Request is done with the status code {r.status_code} and response: {response}')
        r = response['server']
        ip = r['addresses'][data['network_name']][0]['addr']
        col_server.update_one({'_id': server['_id']}, {'$set': {'status': 'ip', 'ip': ip}})
    except Exception as e:
        logger.error(f'Error while getting server_id: {str(e)}')
