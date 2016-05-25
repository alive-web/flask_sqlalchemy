__author__ = 'plevytskyi'
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.ext.mail import Mail
from flask.ext.openid import OpenID
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from config import basedir


app = Flask(__name__)
app.config.from_object('config')

mail = Mail(app)

# tmp = os.path.join(basedir, '/tmp')
#
# if not os.path.exists(tmp):
#     os.makedirs(tmp)
file_handler = RotatingFileHandler('microblog.log', 'a', 1 * 1024 * 1024, 10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.setLevel(logging.INFO)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.info('microblog startup')

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'LoginView:get'

oid = OpenID(app, os.path.join(basedir, 'tmp'))

from app import views, models, urls
