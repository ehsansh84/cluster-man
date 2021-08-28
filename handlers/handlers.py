from base_handler import BaseHandler
from publics import create_md5, decode_token, encode_token
from datetime import datetime
import subprocess

#class Login(BaseHandler):
#    def init_method(self):
#        print('login')
#        self.required = {
#            'post': ['username', 'password']
#        }
#        self.inputs = {
#            'post': ['username', 'password']
#        }
#        self.tokenless = True
#
#    def before_post(self):
#        try:
#          col_users = self.db['users']
#          # col_user_logins = self.db['user_logins']
#          user_info = col_users.find_one(
#              {'username': self.params['username'], 'password': create_md5(self.params['password'])})
#          if user_info is None:
#              self.set_output('user', 'wrong_login_info')
#          else:
#              self.user_role = user_info['role']
#              user_info = self.after_get_one(user_info)
#              if user_info['confirmed']:
#                  self.user_id = user_info['id']
#                  self.set_output('public_operations', 'successful') #TODO self.success
#                  self.output['token'] = encode_token(
#                      {'user_id': user_info['id']}).decode('utf-8')
#                  #if self.user_role != 'guest':
#                  #    self.new_session(self.output['token'])
#                  self.user_id = user_info['id']
#                  # TODO: this should be in permission system
#                  if 'last_update' in user_info: del user_info['last_update']
#                  if 'password_pure' in user_info: del user_info['password_pure']
#                  if 'password' in user_info: del user_info['password']
#                  if 'activation_code' in user_info: del user_info['activation_code']
#                  if '_id' in user_info: del user_info['_id']
#                  self.output['data']['item'] = user_info
#              else:
#                  self.set_output('user', 'inactive')
#          try:
#              col_user_logins = self.db['user_logins']
#              col_user_logins.insert({
#                  'user_id': self.user_id,
#                  'username': self.params.get('username'),
#                  'password': self.params.get('password'),
#                  'status': self.status,
#                  'date': datetime.now(),
#                  'notes': self.note_id
#              })
#          except:
#              self.PrintException()
#        except:
#            self.PrintException()
#            self.fail()
#        self.allow_action = False
    
    
#class Cluster(BaseHandler):
#    def init_method(self):
#        self.required = {
#            'post': ['master_count', 'worker_count', 'name'],
#        }
#        self.inputs = {
#            'post': ['master_count', 'worker_count', 'name'],
#        }
#        self.casting['ints'] = ['master_count', 'worker_count']
#        self.tokenless = True
#
#    def before_post(self):
#        self.params['status'] = 'unconfigured'
#        return True


#class Server(BaseHandler):
#    def init_method(self):
#        self.required = {
#            'post': ['name'],
#        }
#        self.inputs = {
#            'post': ['ip', 'status', 'name', 'cluster', 'role'],
#        }
#        self.tokenless = True
#
#    def before_post(self):
#        import os
#        import re
#        os.environ["OS_DOMAIN_ID"] = "default"
#        os.environ["OS_DOMAIN_NAME"] = "default"
#        command = "ansible-playbook /home/ubuntu/private-playoobks/tabriz_node.yml -e 'name=%s'" % self.params['name']
#        print(command)
#        output = subprocess.check_output(command, shell=True).decode()
#        pat = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
#        IP = pat.search(output)
#        self.params['ip'] = IP.group()
#        self.params['status'] = 'free'
#        self.output['data']['item']['ip'] = IP.group()
#        self.success() 
#        return True


class SampleClass(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['field1']
        }
        self.multilingual = ['field2']
        self.inputs = {
            'post': ['field1', 'field2', 'field3'],
            'put': ['field1', 'field2', 'field3']
        }

