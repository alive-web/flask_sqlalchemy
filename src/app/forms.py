__author__ = 'plevytskyi'
from flask.ext.wtf import Form
from wtforms import BooleanField, TextAreaField, StringField, PasswordField
from wtforms.validators import Length, DataRequired, EqualTo

from app import db
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

        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is None or not hasattr(user, 'check_password') or not user.check_password(self.password.data):
            self.nickname.errors.append('Wrong name or password')
            return False

        self.user = user
        return True


class RegistrationForm(Form):

    nickname = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('confirm', message="Enter twice the same password"),
                                                     Length(min=4, max=20)])
    confirm = PasswordField('Confirm password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user:
            self.nickname.errors.append('User with name {} already exist'.format(self.nickname.data))
            return False

        return True

    def save(self):
        user = User(nickname=self.nickname.data, password=self.password.data)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
        self.user = user


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
