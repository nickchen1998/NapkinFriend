from model import PredictDate
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


def update_predict_date_by_user_id(db: SQLAlchemy, user_id: str, predict_date: datetime):
    data = PredictDate.query.filter_by(user_id=user_id).first()
    data.predict_date = predict_date
    db.session.commit()
