__author__ = 'plevytskyi'

from datetime import datetime

from sqlalchemy_searchable import search
from flask.ext.classy import FlaskView, route
from nltk import word_tokenize
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify

from config import POSTS_PER_PAGE
from app import app, db, lm, oid, emails
from app.oauth import OAuthSignIn
from app.models import User, Post
from app.forms import LoginForm, EditForm, PostForm, SearchForm


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
            g.search_form = SearchForm()


class OauthView(BaseView):
    @route('/authorize/<provider>')
    def oauth_authorize(self, provider):
        if g.user is not None and g.user.is_authenticated:
            return redirect(url_for('IndexView:get_1'))
        oauth = OAuthSignIn.get_provider(provider)
        return oauth.authorize()

    @route('/callback/<provider>')
    def oauth_callback(self, provider):
        if not current_user.is_anonymous:
            return redirect(url_for('IndexView:get_1'))
        oauth = OAuthSignIn.get_provider(provider)
        social_id, email, name = oauth.callback()
        if social_id is None:
            flash('Authentication failed.')
            return redirect(url_for('IndexView:get_1'))
        user = User.query.filter_by(social_id=social_id).first()
        if not user:
            user = User(social_id=social_id, full_name=name, email=email)
            db.session.add(user)
            db.session.commit()
        login_user(user, True)
        return redirect(url_for('IndexView:get_1'))


class LoginView(BaseView):

    def get(self):
        if g.user is not None and g.user.is_authenticated:
            return redirect(url_for('IndexView:get_1'))
        form = LoginForm()
        return render_template('login.html', title='Sign In', form=form)

    def post(self):
        if g.user is not None and g.user.is_authenticated:
            return redirect(url_for('IndexView:get_1'))
        form = LoginForm()
        if form.validate_on_submit():
            session['remember_me'] = form.remember_me.data
            return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
        return render_template('login.html', title='Sign In', form=form, providers=app.config['OPENID_PROVIDERS'],
                               error=oid.fetch_error())


class LogoutView(BaseView):

    def get(self):
        app.logger.info('{} log out'.format(g.user.nickname))
        logout_user()
        return redirect(url_for('IndexView:get_1'))


class IndexView(BaseView):

    @route('/')
    @route('/index')
    @route('/index/<int:page>')
    @login_required
    def get(self, page=1):
        user = g.user
        form = PostForm()
        posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
        return render_template('index.html', title='Home', user=user, posts=posts, form=form)

    @login_required
    def post(self):
        form = PostForm()
        if form.validate_on_submit():
            post = Post(title=form.title.data, body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
            db.session.add(post)
            db.session.commit()
            flash('Your post is now live!')
            return redirect(url_for('IndexView:get_1'))
        posts = Post.query.all()
        return render_template('index.html', title='Home', user=g.user, posts=posts, form=form)


class UserView(BaseView):
    @route('/<int:user_id>')
    @route('/<int:user_id>/<int:page>')
    def profile(self, user_id, page=1):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            flash('User with id ' + user_id + ' not found.')
            return redirect(url_for('IndexView:get_1'))
        posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
        return render_template('user.html', user=user, posts=posts)

    @route('/edit')
    @login_required
    def get(self):
        form = EditForm(g.user.nickname)
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        return render_template('edit.html', form=form)

    @route('/edit', methods=['POST'])
    @login_required
    def post(self):
        form = EditForm(g.user.nickname)
        if form.validate_on_submit():
            g.user.nickname = form.nickname.data
            g.user.about_me = form.about_me.data
            db.session.add(g.user)
            db.session.commit()
            flash('Your changes have been saved.')
            app.logger.info('edited profile {}'.format(g.user.nickname))
            return redirect(url_for('UserView:get'))
        return render_template('edit.html', form=form)


class FollowView(BaseView):

    @login_required
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        emails.follower_notification(user, g.user)
        if not user:
            flash('User ' + user.nickname + ' not found.')
            return redirect(url_for('IndexView:get'))
        if user == g.user:
            flash('You can\'t follow yourself!')
            return redirect(url_for('UserView:profile_1', id=user_id))
        u = g.user.follow(user)
        if u is None:
            flash('Cannot follow ' + user.nickname + '.')
            return redirect(url_for('UserView:profile_1', id=user_id))
        db.session.add(u)
        db.session.commit()
        flash('You are now following ' + user.nickname + '!')
        return redirect(url_for('UserView:profile_1', id=user_id))


class UnfollowView(BaseView):

    @login_required
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            flash('User ' + user.nickname + ' not found.')
            return redirect(url_for('index'))
        if user == g.user:
            flash('You can\'t unfollow yourself!')
            return redirect(url_for('UserView:id_1', id=user_id))
        u = g.user.unfollow(user)
        if u is None:
            flash('Cannot unfollow ' + user.nickname + '.')
            return redirect(url_for('UserView:id_1', id=user_id))
        db.session.add(u)
        db.session.commit()
        flash('You have stopped following ' + user.nickname + '.')
        return redirect(url_for('UserView:profile_1', id=user_id))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


class UserApiView(FlaskView):
    def get(self, user_id):
        user = User.query.get(user_id)
        result = user.serialize() if user else {'error': "don't found"}
        return jsonify(result)

    def post(self, user_id):
        return jsonify({'ok': 'ok'})


class ParagraphApiView(FlaskView):
    def get(self, paragraph_id):
        paragraph = Post.query.get(paragraph_id)
        result = paragraph.serialize() if paragraph else {'error': "don't found"}
        return jsonify(result)

    def put(self, paragraph_id):
        paragraph = Post.query.get(paragraph_id)
        if not paragraph:
            return jsonify({'error': 'bad id'})
        title = request.form.get('title', None)
        body = request.form.get('body', None)
        author = request.form.get('author', -1)
        author = User.query.get(author)
        if body is None and title is None and not author:
            return jsonify({'error': 'bad parameters'})
        paragraph.title = title or paragraph.title
        paragraph.body = body or paragraph.body
        paragraph.user_id = author.id if author else paragraph.user_id
        db.session.commit()
        return jsonify(paragraph.serialize())

    def post(self):
        title = request.form.get('title', None)
        body = request.form.get('body', None)
        author = request.form.get('author', -1)
        author = User.query.get(author)
        if body is None or title is None or not author:
            return jsonify({'error': 'bad parameters'})
        paragraph = Post(title=title, body=body, timestamp=datetime.utcnow(), author=author)
        db.session.add(paragraph)
        db.session.commit()

        return jsonify(paragraph.serialize())

    def delete(self, paragraph_id):
        paragraph = Post.query.get(paragraph_id)
        if not paragraph:
            return jsonify({'error': 'bad id'})
        db.session.delete(paragraph)
        db.session.commit()
        return jsonify({'success': '{} deleted'.format(paragraph_id)})


class PostsApiView(FlaskView):
    def get(self):
        paragraphs = Post.query.all()
        return jsonify({'success': [paragraph.serialize() for paragraph in paragraphs]})


class SearchTextApiView(BaseView):

    def post(self):
        searching_text = request.form.get('search', '')
        if not searching_text:
            return redirect(url_for('IndexView:get_1'))
        tokens = word_tokenize(searching_text)
        searching_text = ' or '.join(tokens)
        query = db.session.query(Post)
        results = search(query, searching_text, sort=True).all()
        return render_template('search_results.html', query=searching_text, results=results, user=g.user)
