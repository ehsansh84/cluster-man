import sys
import requests
from auth import get_token
from publics import PrintException

sys.path.append('/app')
sys.path.append('/home/ehsan/dev/cluster-man/')
sys.path.append('/home/ubuntu/dev/cluster-man/')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from publics import db, get_platform_data
from log_tools import log

# f = open(consts.SERVER_DATA)
# data = json.load(f)
# f.close()
tokens = {}
platform_data = {}
# auth_base_url = "https://%s:5000/v3"  % data['server_ip']

# token = get_token()
headers = {"X-Auth-Token": "", "Content-Type": "application/json"}
col_cluster = db()['cluster']
col_server = db()['server']

log.info('Checking status daemon is started...')

for server in col_server.find({'status': {'$in': ['creating', '']}}):
    try:
        log.info(f'{server["platform"]}')
        # log.info(f'{platform_data}')
        platform = server['platform']
        if platform not in tokens.keys():
            tokens[platform] = get_token(platform)
        if platform not in platform_data.keys():
            platform_data[platform] = get_platform_data(platform)
        # log.info(f'{platform_data}')
        headers = {"X-Auth-Token": tokens[server['platform']], "Content-Type": "application/json"}
        base_url = "https://%s:8774/v2.1" % platform_data[platform]['server_ip']
        log.info(f'Checking a server status for: {server["name"]}')
        status_url = f"{base_url}/servers/{server['server_id']}"
        # log.info(f'Calling {status_url} with headers: {headers}')
        r = requests.get(status_url, headers=headers, verify=False)
        response = r.json()
        log.info(f'Request is done with the status code {r.status_code}')
        # log.debug(f'Response: {response}')
        r = response['server']
        ip = r['addresses'][platform_data[server['platform']]['network_name']][0]['addr']
        col_server.update_one({'_id': server['_id']}, {'$set': {'status': 'ip', 'ip': ip}})
    except Exception as e:
        log.error(f'Error while getting server_id: {str(e)}')
        PrintException()

log.info(f'Checking status daemon is finished...')
