from model import Cycle
from flask_sqlalchemy import SQLAlchemy


def get_user_cycle(user_id: str):
    data = Cycle.query.filter_by(user_id=user_id).order_by(Cycle.id).desc()

    return data


def add_user_cycle(db: SQLAlchemy, data: Cycle):
    db.session.add(data)
    db.session.commit()
