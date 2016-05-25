__author__ = 'plevytskyi'
import os

CRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]

OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '557253961121082',
        'secret': 'b81d01a22223cba9c4bc375fa6899d88'
    },
}

basedir = os.path.abspath(os.path.dirname(__file__))

# DB = 'microblog'
# DB_USER = 'microblog'
# DB_PASSWORD = 'mypass'

DB = 'd7q24mhem5apdn'
DB_USER = 'szixouzvokkrwy'
DB_PASSWORD = 'urLiVIVSntE3v3Vzk6ZgyuNMGj'

SQLALCHEMY_TRACK_MODIFICATIONS = False
# SQLALCHEMY_DATABASE_URI = 'postgresql://' + DB_USER + ':' + DB_PASSWORD + '@localhost/' + DB
SQLALCHEMY_DATABASE_URI = 'postgresql://' + DB_USER + ':' + DB_PASSWORD + '@ec2-50-17-237-148.compute-1.amazonaws.com:5432/' + DB

# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# pagination
POSTS_PER_PAGE = 3

# mail
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'MMGMarketingAutomation'
MAIL_PASSWORD = 'market1ng'

ADMINS = ['MMGMarketingAutomation@gmail.com']