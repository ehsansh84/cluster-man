# from handlers.handlers import *
from handlers.login import Login
from handlers.cluster import Cluster
from handlers.server import Server
from handlers.log import Log
from handlers.flavors import Flavor


url_patterns = [
    # ("/v1/", SampleClass, None, "sample_class"),
    ("/v1/login/", Login, None, "login"),
    ("/v1/server/?([^/]+)?", Server, None, "server"),
    ("/v1/cluster/?([^/]+)?", Cluster, None, "cluster"),
    ("/v1/flavor/?([^/]+)?", Flavor, None, "flavor"),
    ("/v1/log/?([^/]+)?", Log, None, "log"),
]
