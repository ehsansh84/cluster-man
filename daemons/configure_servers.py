import os
import re, sys
import subprocess
sys.path.append('/app')
from datetime import datetime
from functions.ha import config_ha
#from .publics import PrintException
#os.environ["MONGO"] = "localhost:27021"
#ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(ROOT_DIR+ '/..')
#sys.path.append(os.path.join(sys.path[0], '..'))
#from publics import db
#from publics import localdb 


from pymongo import MongoClient
con = MongoClient('mongodb://localhost:27021')
db = con['km']

col_cluster = db['cluster']
col_server = db['server']
col_ha = db['ha']


def config_master(cluster_name, ha_ip):
    servers = col_server.find({'cluster_name': cluster_name, 'role': {'$in': ['master', 'main_master']}, 'status': {'$nin': ['done', 'pending']}, 'ip': {'$ne': ''}})
    print({'cluster_name': cluster_name, 'role': {'$in': ['master', 'main_master']}, 'status': {'$nin': ['done', 'pending']}, 'ip': {'$ne': ''}})
    print(f'{servers.count()} servers found to config as masters')
    masters = []
    main_master = {}
    for server in servers:
        print(server['name'], server['role'])
        if server['role'] == 'main_master':
            main_master = {'name': server['name'], 'ip': server['ip']}
        elif server['role'] == 'master':
            masters.append({'name': server['name'], 'ip': server['ip']})
    print(masters)
    print(main_master)
    #for master in cluster_info['masters']:
      #if '0' in master['name']:
    if main_master == {}:
        print('No unconfigured main master detected!')
    else:
        col_server.update_one({'ip': main_master['ip']}, {'$set': {'status': 'pending'}})
        try:
          print('========================================')
          os.system(' ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R "%s"' % main_master['ip'])
          command = "ansible-playbook ../playbooks/activate-masters.yml -e 'ha_ip=%s' -i %s," % (ha_ip, main_master['ip'])
          print(command)
          output = subprocess.check_output(command, shell=True).decode()
          print(output)
          col_server.update_one({'ip': main_master['ip']}, {'$set': {'status': 'done'}})
        except:
          cluster_error = True
          col_server.update_one({'ip': main_master['ip']}, {'$set': {'status': 'error'}})
  
  
    main_master = col_server.find_one({'cluster_name': cluster_name, 'role': 'main_master'})
    if main_master is None:
        print('No main master detected!')
        exit() 
        
    if main_master['ip'] == '':
        print('Main master have not an IP')
        exit()
    print('Going to get a token...')
    get_token(main_master['ip'])
    print('Tokens are stored')
    print(masters)
    if masters == []:
        print('No unconfigured masters detected!')
    else:
        ips = ""
        ip_list = [] 
        for master in masters:
            col_server.update_one({'ip': master['ip']}, {'$set': {'status': 'pending'}})
            os.system(' ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R "%s"' % master['ip'])
            ips+= master['ip'] + ","
            ip_list.append(master['ip'])
        print(ips)
         
        try:
          command = "ansible-playbook ../playbooks/join-master.yml -e 'ha_ip=%s' -i %s" % (ha_ip, ips)
          print(command)
          if ips != ",":
            output = subprocess.check_output(command, shell=True).decode()
            print(output)
            col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'done'}}, multi=True)
      
        except:
          cluster_error = True
          col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'error'}}, multi=True)

def get_token(main_master_ip):
    command = "ansible-playbook ../playbooks/token.yml -i %s," % main_master_ip
    print(command)
    output = subprocess.check_output(command, shell=True).decode()
    print(output)


#def config_other_masters():
#  #print(cluster_info) 
#  ips = ""
#  ip_list = [] 
#  for master in cluster_info['masters']:
#    if '0' not in master['name']:
#      col_server.update_one({'ip': master['ip']}, {'$set': {'status': 'pending'}})
#      os.system(' ssh-keygen -f "/home/ubuntu/.ssh/known_hosts" -R "%s"' % master['ip'])
#      ips+= master['ip'] + ","
#      ip_list.append(master['ip'])
#  print(ips)
#   
#  try:
#    command = "ansible-playbook ../playbooks/join-master.yml -e 'ha_ip=%s' -i %s" % (cluster_info['masters_ha'], ips)
#    print(command)
#    if ips != ",":
#      output = subprocess.check_output(command, shell=True).decode()
#      print(output)
#      col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'done'}}, multi=True)
#
#  except:
#    col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'error'}}, multi=True)


def join_workers(cluster_name):
    servers = col_server.find({'cluster_name': cluster_name, 'role': 'worker', 'status': {'$nin': ['done', 'pending']}, 'ip': {'$ne': ''}})

#    command = "ansible-playbook ../playbooks/token.yml -i %s," % cluster_info['masters'][0]['ip']
#    print(command)
#    if print_mode:
#      print(command)
#    else:
#      output = subprocess.check_output(command, shell=True).decode()
#
#    worker = get_free_server(CLUSTER_NAME, 'Worker')
    if servers.count_documents() == 0:
        print('No workers to joins')
    else:
        ips = ""
        ip_list = []
        for worker in servers:
          ips += worker['ip'] + ","
          ip_list.append(worker['ip'])
        col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'pending'}}, multi=True)
        try:
          if ips != ",":
            command = "ansible-playbook ../playbooks/join-worker.yml -i %s" % ips
            print(command)
            output = subprocess.check_output(command, shell=True).decode()
            col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'done'}}, multi=True)
        except:
          cluster_error = True
          col_server.update({'ip': {'$in': ip_list}}, {'$set': {'status': 'error'}}, multi=True)

print('HELLO!')
for cluster in col_cluster.find({"status": {'$in': ["pending", "error"]}}):
    try:
        cluster_error = False
        print('Goins go config cluster: %s' % cluster['name'])
        #servers = col_server.find({'cluster_name': cluster['name']})
        if cluster['master_count'] > 1:
            ha = col_server.find_one({'cluster_name': cluster['name'], 'role': 'ha'})
            if ha is None:
                col_cluster.update_one({'_id': cluster['_id']}, {'$set': {'status': 'error', 'note': 'No HA available!'}})
                print('HA not available')
                break
            try:
                if ha['status'] not in ['done', 'pending']:
                    masters = col_server.find({'cluster_name': cluster['name'], 'role': {'$in': ['master', 'main_master']}})
                    masters_list = [{'name': item['name'], 'ip': item['ip']} for item in masters]
                    print(masters_list)
                    print('Start configuring HA')
                    if config_ha(ha['ip'], masters_list):
                        col_ha.update_one({'_id': ha['_id']}, {'$set': {'status': 'done'}})
                        print('HA has been configured')
                    else:
                        print('HA Can not be configured!')
                else:
                    print('HA is done or pending!')
            except Exception as e:
                cluster_error = True
                #TODO Good to have error message here
                print(str(e))
                print('============================================')
                #col_ha.update_one({'_id': ha_id}, {'$set': {'status': 'error'}})
            config_master(cluster['name'], ha['ip'])
            #get_token()
            #config_other_masters()
            join_workers(cluster['name'])
        else:
            print(1)
            pass

    except:
        cluster_error = True
    cluster_status = 'error' if cluster_error else 'done'
    col_cluster.update_one({'_id': cluster['_id']}, {'$set': {'status': cluster_status}})
