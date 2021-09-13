from pymongo import MongoClient
from publics import PrintException, db
from log_tools import log
from consts import consts
# con = MongoClient('mongodb://localhost:27021')
# db = con['km']

col_cluster = db()['cluster']
col_server = db()['server']
col_ha = db()['ha']
import sys, os, subprocess


def create_ha_config(ha, masters):
    try:
      # f = open('/app/templates/haproxy/body.tmpl')
      f = open(f'/home/ehsan/dev/cluster-man/templates/haproxy/body.tmpl')
      body_template = f.read()
      f.close()
      # f = open('/app/templates/haproxy/head.tmpl')
      f = open('/home/ehsan/dev/cluster-man/templates/haproxy/head.tmpl')
      head_template = f.read()
      f.close()
    
      backend = ""
      for server in masters:
        backend += "  server %s %s:6443 check fall 3 rise 2\n" % (server['name'],server['ip'])
      tmpl = body_template % (ha, backend)
      tmpl = head_template + tmpl
      if not os.path.exists(consts.TEMP_DIR):
        os.makedirs(consts.TEMP_DIR)
      f = open(consts.TEMP_DIR+'/haproxy.cfg', 'w')
      f.write(tmpl)
      f.close()
    except Exception as e:
        PrintException()
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno)


def create_etc_hosts(masters):
    try:
      hosts = ""
      for server in masters:
        hosts += "%s %s\n" % (server['ip'], server['name'])
      f = open(consts.TEMP_DIR+'/hosts', 'w')
      hosts = "127.0.0.1 localhost\n" + hosts
      f.write(hosts)
      f.close()
    except Exception as e:
        PrintException()
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno)
#print(cluster_info['masters_ha'])

def config_ha(ha, masters):
  create_ha_config(ha, masters)  
  create_etc_hosts(masters)
  print(col_server.update_one({'ip': ha}, {'$set': {'status': 'pending'}}).raw_result)
  try:
    command = f"ansible-playbook {consts.PLAYBOOK_DIR}/config-ha.yml -e 'TEMP_DIR={consts.TEMP_DIR}' -i ubuntu@{ha},"
    log.info(command)
    output = subprocess.check_output(command, shell=True).decode()
    log.info(output)
    col_server.update_one({'ip': ha}, {'$set': {'status': 'done'}})
    return True
  except Exception as e:
      log.error("WTF HA?")
      PrintException()
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno)
        # print(str(e))
      col_server.update_one({'ip': ha}, {'$set': {'status': 'error'}})
      return False


