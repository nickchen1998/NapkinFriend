from app import app
from flask_sqlalchemy import SQLAlchemy
from model import Cotton, Cycle, Name, PredictDate

db = SQLAlchemy(app)
use_class = [Cotton, Cycle, Name, PredictDate]


def create_table():
    db.drop_all()
    db.create_all()
