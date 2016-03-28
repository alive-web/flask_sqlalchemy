__author__ = 'plevytskyi'

from flask import render_template
from flask.ext.mail import Message

from app import app, mail
from config import ADMINS
from decorators import async


def follower_notification(followed, follower):
    send_email("[microblog] %s is now following you!" % follower.nickname,
               ADMINS[0],
               [followed.email],
               render_template("follower_email.html", user=followed, follower=follower))


@async
def send_async_email(msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    send_async_email(msg)