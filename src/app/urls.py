__author__ = 'plevytskyi'

from app import app
from app import views

views.IndexView.register(app, route_base='/')
views.LoginView.register(app, route_base='/login')
views.LogoutView.register(app, route_base='/logout')
views.UserView.register(app, route_base='/profile')
views.UserApiView.register(app, route_base='/api/user/<int:user_id>')
views.ParagraphApiView.register(app, route_base='/api/paragraph')
views.SearchTextApiView.register(app, route_base='/api/search')
