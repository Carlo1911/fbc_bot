import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from fb import Bot


app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bot = Bot(os.environ["PAGE_ACCESS_TOKEN"])

from project.views import project_blueprint

app.register_blueprint(project_blueprint)

from .models import User
