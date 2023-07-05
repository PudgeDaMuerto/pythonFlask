from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

SESSION_TIME = timedelta(minutes=30)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'an(v$g+fv=&5%bp*-nt)rkv6y1^vi)v%ew_sm_p8sqiseyjrh%'
app.config['SQLALCHEMY_ECHO'] = False

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager(app)
