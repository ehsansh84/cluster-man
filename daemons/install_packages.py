import os
import re, sys
import subprocess
sys.path.append('/app')
from datetime import datetime
from functions.ha import config_ha
#os.environ["MONGO"] = "localhost:27021"
#ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(ROOT_DIR+ '/..')
#sys.path.append(os.path.join(sys.path[0], '..'))
#from publics import db
#from publics import localdb 

from pymongo import MongoClient
con = MongoClient('mongodb://localhost:27021')
db = con['km']

col_cluster = db['cluster']
col_server = db['server']
col_ha = db['ha']



def install_helm():
  #print(cluster_infoter(ter(ter() 
      print(cluster_info['masters'][0]['ip'])
      try:
        command = "ansible-playbook /app/playbooks/install-helm.yml -i %s," % cluster_info['masters'][0]['ip']
        print(command)
        output = subprocess.check_output(command, shell=True).decode()
        print(output)
      except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

install_helm()
