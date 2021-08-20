from handlers.handlers import *


url_patterns = [
    ("/v1/", SampleClass, None, "sample_class"),
    ("/v1/login/", Login, None, "login"),
    ("/v1/server/?([^/]+)?", Server, None, "server"),
]
