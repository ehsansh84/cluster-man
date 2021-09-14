#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options
from urls import url_patterns
from publics import load_messages, load_notifications
if sys.argv[-1] == 'dev':
    os.environ["MONGO"] = "localhost:27021"
    print(os.getenv('MONGO'))

from publics import set_db, consts
import socket

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

print("os.getenv(MONGO)")
print(os.getenv('MONGO'))
if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(url_patterns)
    https_app = tornado.httpserver.HTTPServer(app)
    # set_db(consts.DB_NAME)
    if os.getenv('MONGO'):
        consts.MESSAGES = load_messages()
        consts.NOTIFICATIONS = load_notifications()
        app.listen(int(consts.SERVER_PORT))
        tornado.ioloop.IOLoop.current().start()
        print(consts.MESSAGES)
    else:
        print('Fatal error: You must supply MONGO environment variable with mongodb docker name')

