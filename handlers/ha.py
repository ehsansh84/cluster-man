from base_handler import BaseHandler
from publics import create_md5, decode_token, encode_token
from datetime import datetime


class Ha(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['ip', 'name', 'frontend', 'backend'],
        }
        self.inputs = {
            'post': ['ip', 'name', 'frontend', 'backend'],
        }
        self.casting['lists'] = ['backend']
        self.tokenless = True

    def before_post(self):
        self.params['status'] = 'unconfigured'
        return True
