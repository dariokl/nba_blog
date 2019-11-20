import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask import current_app
from flask_socketio import SocketIO


app = Flask(__name__)

#############################################################################
############ CONFIGURATIONS (CAN BE SEPARATE CONFIG.PY FILE) ###############
###########################################################################

# Remember you need to set your environment variables at the command line
# when you deploy this to a real website.
# export SECRET_KEY=mysecret
# set SECRET_KEY=mysecret
app.config['SECRET_KEY'] = 'mysecret'


socketio = SocketIO(app)
#################################
### DATABASE SETUPS ############
###############################

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
Migrate(app,db)

config_file = 'key.py'
app.config.from_pyfile(config_file)


login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'users.login'


###############################
######### VIEWS ###############
##############################

from webapp.core.views import core
from webapp.users.views import users
from webapp.chat.views import chating

app.register_blueprint(users)
app.register_blueprint(core)
app.register_blueprint(chating)
