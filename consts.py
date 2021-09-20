class consts(object):
    import os
    PROJECT_NAME = 'cman'
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    page_size = 20
    MAX_TOKEN_DURATION = 1000000
    MESSAGES = None
    NOTIFICATIONS = None
    CONSOLE_LOG = True
    LOG_ACTIVE = True
    MONGODB_PORT = '27021'
    # PDP_ROOT = '/www/'
    # CDN_ADDRESS = 'https://cdn.domain.info'
    # ODP_ROOT = CDN_ADDRESS + '/'+ PROJECT_NAME +'/'
    # ODP_IMAGES = ODP_ROOT + 'images/'
    # PDP_IMAGES = PDP_ROOT + 'images/'
    SERVER_PORT = '8282'
    DB_NAME = PROJECT_NAME
    TEST_MODE = False
    TEMP_DIR = '/temp'
    # TEMP_DIR = '/home/ehsan/temp'
    # TEMP_DIR = '/home/ubuntu/temp'
    # PROJECT_DIR = '/home/ehsan/dev/cluster-man'
    # PROJECT_DIR = '/home/ubuntu/dev/cluster-man'
    PROJECT_DIR = '/app'
    PLAYBOOK_DIR = PROJECT_DIR + '/playbooks'

