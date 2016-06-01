__author__ = 'plevytskyi'
from hashlib import md5

import sqlalchemy
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import make_searchable
from flask_login import UserMixin
from sqlalchemy_utils import URLType

from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

make_searchable()

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


class User(UserMixin, db.Model):

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        password = kwargs.get('password', '')
        if password:
            self.password = self.get_hash(password)

    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), unique=True)
    nickname = db.Column(db.Unicode(64), unique=True)
    password = db.Column(db.Unicode(64))
    full_name = db.Column(db.Unicode(64))
    email = db.Column(db.Unicode(120), unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.Unicode(140))
    picture = db.Column(URLType())
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    # FIXME: Change coding password
    def get_hash(self, password):
        return md5(password).hexdigest()

    def check_password(self, password):
        return md5(password).hexdigest() == self.password

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).\
            filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'nickname': self.nickname,
            'email': self.email
        }

    def serialize_posts(self):
        return [item.serialize() for item in self.posts.all()]

    def avatar(self, size):
        email = self.email or ''
        return 'http://www.gravatar.com/avatar/' + md5(email).hexdigest() + '?d=mm&s=' + str(size)

    def __repr__(self):
        return '<User %r>' % self.nickname


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(40))
    body = db.Column(db.UnicodeText())
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    search_vector = db.Column(TSVectorType('title', 'body', weights={'title': 'A', 'body': 'B'}))

    def __repr__(self):
        return '<Post %r>' % self.body

    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'created': self.timestamp
        }

sqlalchemy.orm.configure_mappers()
