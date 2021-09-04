from pymongo import MongoClient
con = MongoClient('mongodb://localhost:27021')
db = con['km']

col_cluster = db['cluster']
col_server = db['server']
col_ha = db['ha']
import sys, os, subprocess

def create_ha_config(ha, masters):
    try:
      f = open('../templates/haproxy/body.tmpl')
      body_template = f.read()
      f.close()
      f = open('../templates/haproxy/head.tmpl')
      head_template = f.read()
      f.close()
    
      backend = ""
      for server in masters:
        backend += "  server %s %s:6443 check fall 3 rise 2\n" % (server['name'],server['ip'])
      tmpl = body_template % (ha, backend)
      tmpl = head_template + tmpl
      if not os.path.exists('../../temp'):
        os.makedirs('../../temp')
      f = open('../temp/haproxy.cfg', 'w')
      f.write(tmpl)
      f.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

def create_etc_hosts(masters):
    try:
      hosts = ""
      for server in masters:
        hosts += "%s %s\n" % (server['ip'], server['name'])
      f = open('../temp/hosts', 'w')
      hosts = "127.0.0.1 localhost\n" + hosts
      f.write(hosts)
      f.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
#print(cluster_info['masters_ha'])

def config_ha(ha, masters):
  create_ha_config(ha, masters)  
  create_etc_hosts(masters)
  print(col_server.update_one({'ip': ha}, {'$set': {'status': 'pending'}}).raw_result)
  try:
    command = "ansible-playbook ../playbooks/config-ha.yml -i %s," % ha
    print(command)
    output = subprocess.check_output(command, shell=True).decode()
    print(output)
    col_server.update_one({'ip': ha}, {'$set': {'status': 'done'}})
  except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
        col_server.update_one({'ip': ha}, {'$set': {'status': 'error'}})


