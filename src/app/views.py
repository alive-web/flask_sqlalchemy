__author__ = 'plevytskyi'

from datetime import datetime

from forms import LoginForm, EditForm
from flask.ext.classy import FlaskView, route
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required

from app import app, db, lm, oid
from models import User, ROLE_USER


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class BaseView(FlaskView):

    def before_request(self, name, *args, **kwargs):
        g.user = current_user
        if g.user.is_authenticated:
            g.user.last_seen = datetime.utcnow()
            db.session.add(g.user)
            db.session.commit()


class LoginView(BaseView):

    @oid.loginhandler
    def get(self):
        if g.user is not None and g.user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        return render_template('login.html', title='Sign In', form=form, providers=app.config['OPENID_PROVIDERS'],
                               error=oid.fetch_error())

    @oid.loginhandler
    def post(self):
        if g.user is not None and g.user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            session['remember_me'] = form.remember_me.data
            return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
        return render_template('login.html', title='Sign In', form=form, providers=app.config['OPENID_PROVIDERS'],
                               error=oid.fetch_error())

    @oid.after_login
    def after_login(resp):
        if resp.email is None or resp.email == "":
            flash('Invalid login. Please try again.')
            return redirect(url_for('login'))
        user = User.query.filter_by(email=resp.email).first()
        if user is None:
            nickname = resp.nickname
            if nickname is None or nickname == "":
                nickname = resp.email.split('@')[0]
            user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
            db.session.add(user)
            db.session.commit()
        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)
        login_user(user, remember=remember_me)
        return redirect(request.args.get('next') or url_for('index'))


class LogoutView(BaseView):

    def get(self):
        logout_user()
        return redirect(url_for('IndexView:get'))


class IndexView(BaseView):

    @login_required
    def get(self):
        user = g.user
        posts = [
            {
                'author': {'nickname': 'John'},
                'body': 'Beautiful day in Portland!'
            },
            {
                'author': {'nickname': 'Susan'},
                'body': 'The Avengers movie was so cool!'
            }
        ]
        return render_template('index.html', title='Home', user=user, posts=posts)


class UserView(BaseView):

    @route('/<nickname>')
    @login_required
    def profile(self, nickname):
        user = User.query.filter_by(nickname=nickname).first()
        if not user:
            flash('User ' + nickname + ' not found.')
            return redirect(url_for('IndexView:get'))
        posts = [
            {'author': user, 'body': 'Test post #1'},
            {'author': user, 'body': 'Test post #2'}
        ]
        return render_template('user.html', user=user, posts=posts)

    @route('/edit')
    @login_required
    def get(self):
        app.logger.info('edit profile {}'.format(g.user.nickname))
        form = EditForm()
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        return render_template('edit.html', form=form)

    @route('/edit', methods=['POST'])
    @login_required
    def post(self):
        form = EditForm()
        if form.validate_on_submit():
            g.user.nickname = form.nickname.data
            g.user.about_me = form.about_me.data
            db.session.add(g.user)
            db.session.commit()
            flash('Your changes have been saved.')
            app.logger.info('edited profile {}'.format(g.user.nickname))
            return redirect(url_for('UserView:get'))
        return render_template('edit.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
