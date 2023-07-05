import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

SESSION_TIME = timedelta(minutes=int(os.environ['SESSION_TIME_MINUTES']))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_ECHO'] = os.environ['SQLALCHEMY_ECHO']

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager(app)
