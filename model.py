from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Cotton(db.Model):
    __tablename__ = "cotton"
    id = db.Column(db.INT, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    pad = db.Column(db.INT, nullable=False)
    little_daily = db.Column(db.INT, nullable=False)
    normal_daily = db.Column(db.INT, nullable=False)
    high_daily = db.Column(db.INT, nullable=False)
    normal_night = db.Column(db.INT, nullable=False)
    high_night = db.Column(db.INT, nullable=False)

    def __init__(self, user_id: str = None, pad: int = None,
                 little_daily: int = None, normal_daily: int = None, high_daily: int = None,
                 normal_night: int = None, high_night: int = None):
        self.user_id = user_id
        self.pad = pad
        self.little_daily = little_daily
        self.normal_daily = normal_daily
        self.high_daily = high_daily
        self.normal_night = normal_night
        self.high_night = high_night


class Cycle(db.Model):
    __tablename__ = "cycle"
    id = db.Column(db.INT, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    mc_date = db.Column(db.DateTime, nullable=False)
    cycle = db.Column(db.INT, nullable=False)

    def __init__(self, user_id: str = None, mc_date: datetime = None, cycle: int = None):
        self.user_id = user_id
        self.mc_date = mc_date
        self.cycle = cycle


class Name(db.Model):
    __tablename = "name"
    id = db.Column(db.INT, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, user_id: str = None, name: str = None):
        self.user_id = user_id
        self.name = name


class PredictDate(db.Model):
    __tablename__ = "predict_date"
    id = db.Column(db.INT, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    predict_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id: str = None, predict_date: datetime = None):
        self.user_id = user_id
        self.predict_date = predict_date
