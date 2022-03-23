from flask import Flask
from settings import Setting

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Setting.database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
