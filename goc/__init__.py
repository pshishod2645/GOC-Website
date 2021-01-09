import os, datetime, timeago, subprocess
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

TEMPLATE_DIR = os.path.join(".", "templates")
STATIC_DIR = os.path.join(".", "static")

app = Flask(__name__, template_folder = TEMPLATE_DIR, static_folder = STATIC_DIR)

app.config['SECRET_KEY'] = 'd035d622dc82b6465e417465da37a499'

app.jinja_env.globals['timeago'] = timeago.format
app.jinja_env.globals['datetime'] = datetime.datetime.utcnow()

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
admin = Admin(app)
USERNAME_REGEX_NOT = '[^a-zA-Z0-9._-]'

def convertHTML(text):
    with open('demo.txt', 'w') as f:
        f.write(text)
    result = subprocess.run(args=['pandoc', 'demo.txt'], shell=True, capture_output=True)
    return result.stdout.decode()

app.jinja_env.globals['convertHTML'] = convertHTML

from goc import routes