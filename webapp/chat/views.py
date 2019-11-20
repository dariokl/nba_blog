from webapp import app
from flask import Blueprint, render_template, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from webapp.models import User
from webapp import socketio
from flask_socketio import send, emit
from time import localtime, strftime
from flask import current_app
import os

chating = Blueprint('chating',__name__)



@chating.route('/chat')
def chat():

    return render_template('chat.html', username=current_user.username)


@socketio.on('message')
def message(data):

    print(data)

    send({'msg' : data['msg'], 'username' : data['username'], 'time_stamp' : strftime('%H:%M', localtime()), 'profile' : 'static/profile_pics/' + current_user.profile_image})
