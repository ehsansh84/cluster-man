import sys
sys.path.append('/home/ehsan/dev/cluster-man/')
sys.path.append('/home/ubuntu/dev/cluster-man/')
sys.path.append('/app')
import threading
import requests
import urllib3
from auth import get_token
from publics import db, PrintException, get_platform_data, ExceptionLine
from log_tools import log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append('/app')
log.info(f'Delete servers daemon is started...')

# http://{{ip}}:8774/v2.1/servers/{{instanceRef}}/action
def delete_server(platform, token, server_id):
    log.info(f'Deleting a server with id: {server_id}')
    data = get_platform_data(platform)
    url = f"https://{data['server_ip']}:8774/v2.1/servers/{server_id}/action"
    params = {"forceDelete": "null"}
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    try:
        log.info(f'Making a request to {url}')
        # log.debug(f'With params {params} and headers {headers}')
        r = requests.post(url, json=params, headers=headers, verify=False)
        log.info(f'Request is done and status code is {r.status_code}')
        log.debug(f'Response is {r.text}')
        # response = r.json()
        # log.debug(response)
    except Exception as e:
        log.error(f'Error while creating server: {ExceptionLine()} {str(e)}')


col_cluster = db()['cluster']
col_server = db()['server']
tokens = {}
platform_data = {}

for server in col_server.find({'status': 'deleting'}):
    try:
        platform = server['platform']
        log.debug(f"Platform {platform}")
        if platform not in tokens.keys():
            tokens[platform] = get_token(platform)
        if platform not in platform_data.keys():
            platform_data[platform] = get_platform_data(platform)
        log.debug(server['name'])
        delete_server(platform, tokens[platform], server['server_id'], )
        # x = threading.Thread(target=delete_server,
        #                      args=(server['platform'], tokens[server['platform']], server['server_id'],))
        # x.start()
    except Exception as e:
        log.error(f'Error while getting server_id: {ExceptionLine()} {str(e)}')
        PrintException()


log.info(f'Delete servers daemon is finished...')
