import sys
sys.path.append('/app')
sys.path.append('/home/ehsan/dev/cluster-man/')
sys.path.append('/home/ubuntu/dev/cluster-man/')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from publics import db
from log_tools import log
from auth import get_token
from publics import get_platform_data, ExceptionLine
import requests

col_flavor = db()['flavor']
col_cluster = db()['cluster']
col_server = db()['server']
col_ha = db()['ha']


def get_flavors(platform):
    log.info(f'Crawling flavors for {platform}...')
    token=get_token(platform)
    try:
        data = get_platform_data(platform)
        base_url = "https://%s:8774/v2.1" % data['server_ip']
        link = f"{base_url}/flavors/detail"
        print(link)
        headers = {"X-Auth-Token": token, "Content-Type": "application/json", "X-OpenStack-Nova-API-Version": "2.55"}
        print(headers)
        response = requests.get(link, headers=headers, verify=False)
        if response.status_code < 400:
            flavors = response.json()['flavors']
            for flavor in flavors:
                print(flavor)
                if col_flavor.find_one({'flavor_id': flavor['id']}) is None:
                    col_flavor.insert_one({
                        'platform': platform,
                        'flavor_id': flavor['id'],
                        'name': flavor['name'],
                        'ram': flavor['ram'],
                        'disk': flavor['disk'],
                        'vcpus': flavor['vcpus']
                    })
    except:
        log.error(f"Error while getting server_id: {ExceptionLine()}")

get_flavors('afranet')
get_flavors('tabriz')
