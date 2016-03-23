__author__ = 'plevytskyi'
from flask.ext.wtf import Form
from wtforms import BooleanField, TextAreaField, StringField
from wtforms.validators import Length, DataRequired


class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])


class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class PostForm(Form):
    title = StringField('title', validators=[DataRequired()])
    post = StringField('post', validators=[DataRequired()])
