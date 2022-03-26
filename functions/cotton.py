from linebot.models import MessageEvent
from datetime import datetime, timedelta
from model.model import Cycle, Cotton, PredictDate, Name
from flask_sqlalchemy import SQLAlchemy


def insert_mc_date(db: SQLAlchemy, event: MessageEvent, user_id: str):
    # 獲取取使用者回傳的日期
    dt = str(event.postback.params.get('date'))
    m_dt = datetime.fromisoformat(dt)

    # 從資料庫調取使用者全部生理期資料
    result = Cycle.query.filter_by(user_id=user_id).order_by(Cycle.id).desc().all()

    # 擷取所有生理期時間以及週期
    cycle_list = []
    for data in result:
        cycle_list.append(data.cycle)

    # 擷取最近一次的生理期時間計算
    last_date = result[0]

    # 計算本次週期
    this_cycle = m_dt - last_date

    # 計算平均週期
    avg_cycle = (sum(cycle_list) + this_cycle.days) / (len(cycle_list) + 1)

    # 產生下個預測日
    next_cycle = m_dt + timedelta(days=round(avg_cycle))

    data = Cycle(user_id=user_id, mc_date=m_dt, cycle=this_cycle.days)
    db.session.add(data)

    db_predict_date: PredictDate = PredictDate.query.filter_by(user_id=user_id).first()
    db_predict_date.predict_date = next_cycle

    db.session.commit()


def query_cycle():
    # 從週期資料表撈過往週期
    latest_cycle: Cycle = Cycle.query.filter_by(user_id=user_id).order_by(Cycle.id).desc().limit(1).first()
    # 從預測日資料表撈取預測日期
    predict_date: PredictDate = PredictDate.query.filter_by(user_id=user_id).first()

    # 製作字串
    text1 = ''
    text1 += '您目前的平均週期為: ' + '\n'
    text1 += f"{latest_cycle.cycle}" + '\n'
    text1 += '您最近一次的生理期為: ' + '\n'
    text1 += latest_cycle.mc_date.isoformat() + '\n'
    text1 += '您下一次預測的生理期為: ' + '\n'
    text1 += predict_date.predict_date.isoformat()

    return text1
