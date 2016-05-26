__author__ = 'plevytskyi'
from flask.ext.wtf import Form
from wtforms import BooleanField, TextAreaField, StringField, PasswordField, SubmitField
from wtforms.validators import Length, DataRequired

from app.models import User


class LoginForm(Form):
    nickname = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(
            nickname=self.nickname.data).first()
        if user is None or not hasattr(user, 'check_password') or not user.check_password(self.password.data):
            self.nickname.errors.append('Wrong name or password')
            return False

        self.user = user
        return True


class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True


class PostForm(Form):
    title = StringField('title', validators=[DataRequired()])
    post = TextAreaField('post', validators=[DataRequired()])


class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])
