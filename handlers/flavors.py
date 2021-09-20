from base_handler import BaseHandler
from publics import create_md5, decode_token, encode_token
from datetime import datetime


class Flavor(BaseHandler):
    def init_method(self):
        self.required = {

        }
        self.tokenless = True

