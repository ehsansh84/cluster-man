from consts import consts
from log_tools import log
from publics import db

col_cluster = db()['cluster']
col_server = db()['server']
col_ha = db()['ha']
import os, subprocess


def create_ha_config(ha, masters):
    try:
        f = open(f'{consts.PROJECT_DIR}/templates/haproxy/body.tmpl')
        body_template = f.read()
        f.close()
        f = open(f'{consts.PROJECT_DIR}/templates/haproxy/head.tmpl')
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
        log.error(str(e))


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
        log.error(str(e))


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
        log.error(str(e))
        col_server.update_one({'ip': ha}, {'$set': {'status': 'error'}})
        return False
