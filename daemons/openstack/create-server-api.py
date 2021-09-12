import json
import os
import sys
sys.path.append('/app')
import threading
import requests
import urllib3
from auth import get_token
from publics import db, consts
from log_tools import log
# log.debug("FUCK?!")
# log.debug("A quirky message only developers care about")
# log.info("Curious users might want to know this")
# log.warning("Something is wrong and any user should be informed")
# log.error("Serious stuff, this is red for a reason")
# log.critical("OH NO everything is on fire")



# exit()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.append('/app')

f = open(consts.SERVER_DATA)
data = json.load(f)
f.close()

base_url = "https://%s:8774/v2.1" % data['server_ip']
auth_base_url = "https://%s:5000/v3" % data['server_ip']
log.info(f'Create servers daemon is started...')


def create_server(token, _id, name, flavor_id, image_id, user_data):
    log.info(f'Creating a server named: {server["name"]}')
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
        log.info(f'Making a request to {link}')
        log.debug(f'With params {params} and headers {headers}')
        r = requests.post(
            link, json=params, headers=headers, verify=False
        )
        log.info(f'Request is done and status code is {r.status_code}')
        log.debug(f'Response is {r.json()}')
        # print(r.text)
        response = r.json()
        # print('posted!')
        # print(response)
        if "server" in response:
            server_id = response["server"]["id"]
            link = f"{base_url}/servers/{server_id}"
            try:
                response = requests.get(link, headers=headers, verify=False).json()
                col_server.update_one({'_id': _id}, {'$set': {'status': 'creating', 'server_id': response['server']['id']}})
                return response
            except Exception as e:
                log.error(f'Error while getting server_id: {str(e)}')
                # exc_type, exc_obj, exc_tb = sys.exc_info()
                # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                # print(exc_type, fname, exc_tb.tb_lineno)
                # print(str(e))
    except Exception as e:
        log.error(f'Error while creating server: {str(e)}')
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno)
        # print(str(e))
        # print(" :::: cloud connection failed\n")


token = get_token()
# print(token)

# from pymongo import MongoClient
# con = MongoClient('mongodb://localhost:27021')
# db = con['km']

col_cluster = db()['cluster']
col_server = db()['server']

for server in col_server.find({'ip': '', 'status': {'$ne': 'creating'}}):
    try:
        # print('=================================================D')
        #print(server)
        x = threading.Thread(target=create_server, args=(token, server['_id'], server['name'], server['flavor_id'], data['image_id'], server['user_data'],))
        x.start()
    except Exception as e:
        log.error(f'Error while getting server_id: {str(e)}')
        # print('ERROR HERE')
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno)
        # print(str(e))
        #col_server.update_one({'ip': ha}, {'$set': {'status': 'error'}})


