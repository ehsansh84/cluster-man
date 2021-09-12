import os
import subprocess
import sys
sys.path.append('/app')
from functions.ha import config_ha
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from publics import db, logger

col_cluster = db()['cluster']
col_server = db()['server']
col_ha = db()['ha']


def get_masters(cluster_name):
    logger.info('Looking for unconfigured masters...')
    masters = []
    main_master = {}
    main_master_configured = False
    try:
        main_master_server = col_server.find_one({'cluster_name': cluster_name, 'role': 'main_master'})
        main_master = {'name': main_master_server['name'], 'ip': main_master_server['ip']}
        main_master_configured = main_master_server['status'] == 'done'
        logger.info(f'Main master configuration status for cluster {cluster_name} is: {main_master_configured}')
        servers = col_server.find({'cluster_name': cluster_name, 'role': {'$in': ['master']},
                                   'status': {'$nin': ['done', 'pending']}, 'ip': {'$ne': ''}})
        # print(f'{servers.count()} servers found to config as masters')
        for server in servers:
            masters.append({'name': server['name'], 'ip': server['ip']})
    except:
        logger.error(f'Error while getting server_id: {str(e)}')
        # PrintException()
    # print(f'INSIDE {main_master_configured}')
    return main_master, masters, main_master_configured


def config_main_master(ip, ha_ip):
    col_server.update_one({'ip': ip}, {'$set': {'status': 'pending'}})
    try:
        logger.info(f'Going to configure main master {ip} using HA {ha_ip}')
        # print('')
        os.system(' ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R "%s"' % ip)
        command = "ansible-playbook /app/playbooks/activate-masters.yml -e 'ha_ip=%s' -i ubuntu@%s," % (ha_ip, ip)
        logger.info(command)
        # print(command)
        output = subprocess.check_output(command, shell=True).decode()
        logger.info(f'Ansible command is done, Output is: {output}')
        col_server.update_one({'ip': ip}, {'$set': {'status': 'done'}})
        logger.info('Main master has been configured.')
    except:
        logger.error(f'Error while getting server_id: {str(e)}')
        # cluster_error = True
        col_server.update_one({'ip': ip}, {'$set': {'status': 'error'}})
        # print('Unable to configure main master!')
        # PrintException()


def join_masters(ha_ip, ips, ip_list):
    try:
        logger.info(f'Going to join other masters...')
        command = "ansible-playbook /app/playbooks/join-master.yml -e 'ha_ip=%s' -i %s" % (ha_ip, ips)
        logger.info(command)
        # print(command)
        if ips != ",":
            output = subprocess.check_output(command, shell=True).decode()
            logger.info(f'Ansible command is done, Output is: {output}')
            col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'done'}}, multi=True)
    except:
        logger.error(f'Error while getting server_id: {str(e)}')
        col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'error'}}, multi=True)
        # print('Error while configuring other masters!')
        # PrintException()


def config_master(cluster_name, ha_ip):
    try:
        main_master, masters, main_master_configured = get_masters(cluster_name)
        # print(masters)
        # print(main_master)
        # if main_master == {}:
        #     logger.info('No unconfigured main master detected!')
        # print(main_master_configured)
        if main_master_configured:
            logger.info('Main master already configured!')
        else:
            config_main_master(main_master['ip'], ha_ip)
            main_master = col_server.find_one({'cluster_name': cluster_name, 'role': 'main_master'})
            if main_master is None:
                logger.error('No main master detected!')
                exit()
            if main_master['ip'] == '':
                logger.error('Main master have not an IP')
                exit()
        if masters == []:
            logger.info('No unconfigured main master detected!')
        else:
            # print(f'Going to get a token from {main_master["ip"]}...')
            get_token(main_master['ip'])
            print('Tokens are stored')
            # print(masters)
            ips = ""
            ip_list = []
            for master in masters:
                col_server.update_one({'ip': master['ip']}, {'$set': {'status': 'pending'}})
                os.system(' ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R "%s"' % master['ip'])
                ips += "ubuntu@" + master['ip'] + ","
                ip_list.append(master['ip'])
            print(ips)
        #TODO: Better to check if there is a token or not
        #TODO Check if there is a worker
        get_token(main_master['ip'])
        join_masters(ha_ip, ips, ip_list)
    except:
        logger.error(f'Error while getting server_id: {str(e)}')
        # PrintException()
  

def get_token(main_master_ip):
    try:
        logger.info(f'Going to get a token from {main_master_ip}...')
        command = "ansible-playbook /app/playbooks/token.yml -i ubuntu@%s," % main_master_ip
        logger.info(command)
        output = subprocess.check_output(command, shell=True).decode()
        logger.info(f'Ansible command is done, Output is: {output}')
        # print(output)
    except Exception as e:
        logger.error(f'Error while getting server_id: {str(e)}')


def join_workers(cluster_name):
    try:
        logger.info(f'Going to get a token from {cluster_name}...')
        # print(f'Preparing to join workers to cluster {cluster_name}')
        servers = col_server.find({'cluster_name': cluster_name, 'role': 'worker', 'status': {'$nin': ['done', 'pending']}, 'ip': {'$ne': ''}})
        # print('test...')
        # print({'cluster_name': cluster_name, 'role': 'worker', 'status': {'$nin': ['done', 'pending']}, 'ip': {'$ne': ''}})
        if servers.count() == 0:
            logger.info(f'No workers to join...')
            # print('No workers to joins')
        else:
            logger.info(f'Joining {servers.count()} workers')
            # print(f'Joining {servers.count()} workers')
            ips = ""
            ip_list = []
            for worker in servers:
                ips += worker['ip'] + ","
                ip_list.append(worker['ip'])
            col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'pending'}}, multi=True)
            try:
                if ips != ",":
                    command = "ansible-playbook /app/playbooks/join-worker.yml -i ubuntu@%s" % ips
                    logger.info(command)
                    output = subprocess.check_output(command, shell=True).decode()
                    logger.info(f'Ansible command is done, Output is: {output}')
                    col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'done'}}, multi=True)
            except Exception as e:
                logger.error(f'Error while getting server_id: {str(e)}')
                # cluster_error = True
                col_server.update_many({'ip': {'$in': ip_list}}, {'$set': {'status': 'error'}})
    except Exception as e:
        logger.error(f'Error while getting server_id: {str(e)}')
        # print('Error while joining workers!')
        # PrintException()


logger.info(f'Server configuration daemon is started...')

for cluster in col_cluster.find():
    try:
        cluster_error = False
        logger.info(f'Goins go config cluster: {cluster["name"]}')
        # print('Goins go config cluster: %s' % cluster['name'])
        #servers = col_server.find({'cluster_name': cluster['name']})
        # if cluster['master_count'] > 1:
        ha = col_server.find_one({'cluster_name': cluster['name'], 'role': 'ha'})
        if ha is None:
            col_cluster.update_one({'_id': cluster['_id']}, {'$set': {'status': 'error', 'note': 'No HA available!'}})
            logger.info(f'HA is not available!')
            break
        try:
            if ha['status'] not in ['done', 'pending']:
                masters = col_server.find({'cluster_name': cluster['name'], 'role': {'$in': ['master', 'main_master']}})
                masters_list = [{'name': item['name'], 'ip': item['ip']} for item in masters]
                # print(masters_list)
                logger.info('Start configuring HA')
                if config_ha(ha['ip'], masters_list):
                    col_ha.update_one({'_id': ha['_id']}, {'$set': {'status': 'done'}})
                    logger.info('HA has been configured')
                else:
                    logger.error('HA Can not be configured!')
            else:
                logger.info('HA is done or pending!')
        except Exception as e:
            logger.error(f'Error while getting server_id: {str(e)}')
            cluster_error = True
            #TODO Good to have error message here
            # print(str(e))
            # print('============================================')
            #col_ha.update_one({'_id': ha_id}, {'$set': {'status': 'error'}})
        config_master(cluster['name'], ha['ip'])
        #get_token()
        #config_other_masters()
        join_workers(cluster['name'])
    except:
        logger.error(f'Error while getting server_id: {str(e)}')
        cluster_error = True
    cluster_status = 'error' if cluster_error else 'done'
    col_cluster.update_one({'_id': cluster['_id']}, {'$set': {'status': cluster_status}})
