import sys
sys.path.append('/home/ehsan/dev/cluster-man/')
sys.path.append('/app')
import threading
import requests
import urllib3
from auth import get_token
from publics import db, PrintException, get_platform_data, ExceptionLine
from log_tools import log
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append('/app')
log.info(f'Create servers daemon is started...')


def create_server(platform, token, _id, name, flavor_id, user_data):
    log.info(f'Creating a server named: {server["name"]}')
    data = get_platform_data(platform)
    base_url = "https://%s:8774/v2.1" % data['server_ip']

    link = base_url + "/servers"
    params = {
            "server": {
                "name": name,
                "flavorRef": flavor_id,
                "networks": [{"uuid": data['network_id']}],
                "imageRef": data['image_id'],
                "availability_zone": "nova",
                "user_data": user_data,
            }
        }
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    try:
        log.info(f'Making a request to {link}')
        # log.debug(f'With params {params} and headers {headers}')
        r = requests.post(
            link, json=params, headers=headers, verify=False
        )
        log.info(f'Request is done and status code is {r.status_code}')
        log.debug(f'Response is {r.text}')
        # log.debug(f'Response is {r.json()}')
        response = r.json()
        if "server" in response:
            server_id = response["server"]["id"]
            link = f"{base_url}/servers/{server_id}"
            try:
                response = requests.get(link, headers=headers, verify=False).json()
                col_server.update_one({'_id': _id}, {'$set': {'status': 'creating', 'server_id': response['server']['id']}})
                return response
            except Exception as e:
                log.error(f'Error while getting server_id: {ExceptionLine()} {str(e)}')
    except Exception as e:
        log.error(f'Error while creating server: {ExceptionLine()} {str(e)}')


col_cluster = db()['cluster']
col_server = db()['server']
tokens = {}

for server in col_server.find({'ip': '', 'status': {'$ne': 'creating'}}):
    try:
        if server['platform'] not in tokens.keys():
            tokens[server['platform']] = get_token(server['platform'])

        x = threading.Thread(target=create_server, args=(server['platform'], tokens[server['platform']], server['_id'], server['name'],
                                                         server['flavor_id'], server['user_data'],))
        x.start()
    except Exception as e:
        log.error(f'Error while getting server_id: {ExceptionLine()} {str(e)}')
        PrintException()


log.info(f'Create servers daemon is finished...')
