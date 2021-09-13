import sys, os
sys.path.append('/root/dev/app')
from consts import consts
from log_tools import log


def PrintException():
    import linecache
    import sys
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    log.error('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    # return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


def ExceptionLine():
    import linecache
    import sys
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return f"{filename}:{lineno} => {line.strip()}"


def set_db(name):
    global db_name
    db_name = name


def set_test_mode(mode):
    consts.TEST_MODE = mode


def es():
    from elasticsearch import Elasticsearch
    return Elasticsearch('localhost')


def db():
    try:
        from pymongo import MongoClient
        MONGO_CONNECTION = os.getenv('MONGO')
        # log.info(f'MONGO_CONNECTION: {MONGO_CONNECTION}')
        con = MongoClient('mongodb://localhost:27021')
        # con = MongoClient('mongodb://' + MONGO_CONNECTION)
        return con[consts.DB_NAME]
    except:
        PrintException()
    return None

def localdb():
    try:
        from pymongo import MongoClient
        con = MongoClient('mongodb://localhost:27021')
        return con[consts.DB_NAME]
    except:
        PrintException()
    return None


def load_messages():
    messages = {}
    try:
        set_db(consts.DB_NAME)
        col_server_messages = db()['server_messages']
        for item in col_server_messages.find():
            group = item['group']
            name = item['name']
            if group not in messages: messages[group] = {}
            del item['group']
            del item['name']
            messages[group][name] = item
    except:
        PrintException()
    return messages


def load_notifications():
    notifications = {}
    try:
        set_db(consts.DB_NAME)
        col_server_notifications = db()['server_notifications']
        for item in col_server_notifications.find():
            group = item['group']
            name = item['name']
            if group not in notifications: notifications[group] = {}
            del item['_id']
            del item['group']
            del item['name']
            notifications[group][name] = item
    except:
        PrintException()
    return notifications


def create_md5(s, encoding='utf-8'):
    from hashlib import md5
    return md5(s.encode(encoding)).hexdigest()


def encode_token(data):
    import jwt
    import datetime
    data['date'] = str(datetime.datetime.now())
    return jwt.encode(data, 'ThisIsASecret@2019', algorithm='HS256')


def decode_token(token):
    import jwt
    try:
        result = jwt.decode(token, 'ThisIsASecret@2019', algorithms=['HS256'])
    except:
        result = None
        PrintException()
    return result


def log_status(l):
    from datetime import datetime
    col = db()['logs']
    del l['date']
    l['date'] = datetime.now()
    col.insert(l)


def get_platform_data(name):
    try:
        from json import load
        # f = open(f'/app/daemons/openstack/{name}.json')
        # import os
        # log.info(os.getcwd())
        f = open(f'/home/ehsan/dev/cluster-man/daemons/openstack/{name}.json')
        data = load(f)
        f.close()
        log.info(f'Platform data loaded for {name}')
        return data
    except Exception as e:
        PrintException()
        log.error(f'Getting platform data failed! {str(e)}')
        return None
