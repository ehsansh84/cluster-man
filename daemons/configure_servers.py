import os
import subprocess
import sys
sys.path.append('/app')
sys.path.append('/home/ehsan/dev/cluster-man/')
sys.path.append('/home/ubuntu/dev/cluster-man/')
from consts import consts
from functions.ha import config_ha
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from publics import db, ExceptionLine
from log_tools import log

col_cluster = db()['cluster']
col_server = db()['server']
col_ha = db()['ha']


def get_masters(cluster_name):
    log.info('Looking for unconfigured masters...')
    masters = []
    main_master = {}
    main_master_configured = False
    try:
        main_master_server = col_server.find_one({'cluster_name': cluster_name, 'role': 'main_master'})
        main_master = {'name': main_master_server['name'], 'ip': main_master_server['ip']}
        main_master_configured = main_master_server['status'] == 'done'
        log.info(f'Main master configuration status for cluster {cluster_name} is: {main_master_configured}')
        servers = col_server.find({'cluster_name': cluster_name, 'role': {'$in': ['master']},
                                   'status': {'$nin': ['done', 'pending']}, 'ip': {'$ne': ''}})
        for server in servers:
            masters.append({'name': server['name'], 'ip': server['ip']})
    except:
        log.error(f"Error while getting server_id: {ExceptionLine()}")
    return main_master, masters, main_master_configured


def config_main_master(ip, ha_ip):
    col_server.update_one({'ip': ip}, {'$set': {'status': 'pending'}})
    try:
        log.info(f'Going to configure main master {ip} using HA {ha_ip}')
        os.system(' ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R "%s"' % ip)
        command = f"ansible-playbook {consts.PLAYBOOK_DIR}/activate-masters.yml -e 'ha_ip=%s' -i ubuntu@%s," % (ha_ip, ip)
        log.info(command)
        output = subprocess.check_output(command, shell=True).decode()
        log.debug(f'Ansible command is done, Output is: {output}')
        col_server.update_one({'ip': ip}, {'$set': {'status': 'done'}})
        log.info('Main master has been configured.')
    except:
        log.error(f'Error while getting server_id: {ExceptionLine()}')
        col_server.update_one({'ip': ip}, {'$set': {'status': 'error'}})


def join_masters(ha_ip, ips, ip_list):
    try:
        log.info(f'Going to join other masters...')
        command = f"ansible-playbook {consts.PLAYBOOK_DIR}/join-master.yml -e 'ha_ip={ha_ip}' -e 'TEMP_DIR={consts.TEMP_DIR}' -i {ips}"
        log.info(command)
        if ips != ",":
            output = subprocess.check_output(command, shell=True).decode()
            log.debug(f'Ansible command is done, Output is: {output}')
            col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'done'}}, multi=True)
    except:
        log.error(f'Error while getting server_id: {ExceptionLine()}')
        col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'error'}}, multi=True)


def config_master(cluster_name, ha_ip):
    try:
        main_master, masters, main_master_configured = get_masters(cluster_name)
        if main_master_configured:
            log.info('Main master already configured!')
        else:
            config_main_master(main_master['ip'], ha_ip)
            get_kubeconfig(main_master['ip'], cluster_name)
            main_master = col_server.find_one({'cluster_name': cluster_name, 'role': 'main_master'})
            if main_master is None:
                log.error('No main master detected!')
                exit()
            if main_master['ip'] == '':
                log.error('Main master have not an IP')
                exit()
        if masters == []:
            log.info('No unconfigured main master detected!')
        else:
            print(f'Going to get a token from {main_master["ip"]}...')
            get_token(main_master['ip'])
            print('Tokens are stored')
            ips = ""
            ip_list = []
            for master in masters:
                col_server.update_one({'ip': master['ip']}, {'$set': {'status': 'pending'}})
                os.system(' ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R "%s"' % master['ip'])
                ips += "ubuntu@" + master['ip'] + ","
                ip_list.append(master['ip'])
        #TODO: Better to check if there is a token or not
        #TODO Check if there is a worker
        get_token(main_master['ip'])
        join_masters(ha_ip, ips, ip_list)
    except:
        log.error(f'Error while getting server_id: {ExceptionLine()}')


def get_token(main_master_ip):
    try:
        log.info(f'Going to get a token from {main_master_ip}...')
        command = f"ansible-playbook {consts.PLAYBOOK_DIR}/token.yml -e 'TEMP_DIR={consts.TEMP_DIR}' -i ubuntu@%s," % main_master_ip
        log.info(command)
        output = subprocess.check_output(command, shell=True).decode()
        log.debug(f'Ansible command is done, Output is: {output}')
    except Exception as e:
        log.error(f'Error while getting server_id: {ExceptionLine()}')


def get_kubeconfig(main_master_ip, cluster_name):
    try:
        log.info(f'Going to get a kube config from {main_master_ip}...')
        command = f"ansible-playbook {consts.PLAYBOOK_DIR}/get-kubeconfig.yml -e 'TEMP_DIR={consts.TEMP_DIR}' -i ubuntu@%s," % main_master_ip
        log.info(command)
        output = subprocess.check_output(command, shell=True).decode()
        log.debug(f'Ansible command is done, Output is: {output}')
    except Exception as e:
        log.error(f'Error while getting server_id: {ExceptionLine()}')

    try:
        f = open(f'{consts.TEMP_DIR}/kube.conf')
        data = f.read()
        f.close()
        # print(data)
        col_cluster.update_one({'name': cluster_name}, {'$set': {'kube_config': data}})
    except Exception as e:
        log.error(f'Error while Sending data to database: {ExceptionLine()}')


def join_workers(cluster_name):
    try:
        log.info(f'Going to get a token from {cluster_name}...')
        servers = col_server.find({'cluster_name': cluster_name, 'role': 'worker', 'status': {'$nin': ['done', 'pending']}, 'ip': {'$ne': ''}})
        if servers.count() == 0:
            log.info(f'No workers to join...')
        else:
            log.info(f'Joining {servers.count()} workers')
            ips = ""
            ip_list = []
            for worker in servers:
                ips += 'ubuntu@' + worker['ip'] + ","
                ip_list.append(worker['ip'])
            col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'pending'}}, multi=True)
            try:
                if ips != ",":
                    log.debug(ips)
                    command = f"ansible-playbook {consts.PLAYBOOK_DIR}/join-worker.yml -e 'TEMP_DIR={consts.TEMP_DIR}' -i {ips}"
                    log.info(command)
                    output = subprocess.check_output(command, shell=True).decode()
                    log.debug(f'Ansible command is done, Output is: {output}')
                    col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'done'}}, multi=True)
            except Exception as e:
                log.error(f'Error while getting server_id: {ExceptionLine()}')
                col_server.update_many({'ip': {'$in': ip_list}}, {'$set': {'status': 'error'}})
    except Exception as e:
        log.error(f'Error while getting server_id: {ExceptionLine()}')


log.info(f'Server configuration daemon is started...')

# exit()
for cluster in col_cluster.find():
    try:
        cluster_error = False
        log.info(f'Goins go config cluster: {cluster["name"]}')
        ha = col_server.find_one({'cluster_name': cluster['name'], 'role': 'ha'})
        if ha is None:
            col_cluster.update_one({'_id': cluster['_id']}, {'$set': {'status': 'error', 'note': 'No HA available!'}})
            log.info(f'HA is not available!')
            break
        try:
            if ha['status'] not in ['done', 'pending']:
                masters = col_server.find({'cluster_name': cluster['name'], 'role': {'$in': ['master', 'main_master']}})
                masters_list = [{'name': item['name'], 'ip': item['ip']} for item in masters]
                log.info('Start configuring HA')
                if config_ha(ha['ip'], masters_list):
                    col_ha.update_one({'_id': ha['_id']}, {'$set': {'status': 'done'}})
                    log.info('HA has been configured')
                else:
                    log.error('HA Can not be configured!')
                    exit()
            else:
                log.info('HA is done or pending!')
        except Exception as e:
            log.error(f'Error while getting server_id: {ExceptionLine()}')
            cluster_error = True
        config_master(cluster['name'], ha['ip'])
        join_workers(cluster['name'])
    except Exception as e:
        log.error(f'Error while getting server_id: {ExceptionLine()}')
        cluster_error = True
    cluster_status = 'error' if cluster_error else 'done'
    col_cluster.update_one({'_id': cluster['_id']}, {'$set': {'status': cluster_status}})
