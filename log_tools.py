import logging
LOG_LEVEL = logging.DEBUG
LOGFORMAT = "  %(log_color)s %(asctime)s, %(levelname)-8s [%(filename)s:%(lineno)d] %(reset)s | %(message)s"
from colorlog import ColoredFormatter
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)

