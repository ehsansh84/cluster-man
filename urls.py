from handlers.handlers import SampleClass, Login


url_patterns = [
    ("/v1/", SampleClass, None, "sample_class"),
    ("/v1/login/", Login, None, "login"),
]
