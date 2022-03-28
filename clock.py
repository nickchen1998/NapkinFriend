from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from settings import Setting
from model import Cotton, PredictDate, Name, db
from datetime import datetime, timedelta
from app import app

setting = Setting()
line_bot_api = LineBotApi(setting.channel_token)
handler = WebhookHandler(setting.channel_secret)

db.init_app(app)


def get_data():
    with app.app_context():
        predict_dates = PredictDate.query.all()
        if predict_dates:
            for _item in predict_dates:
                name = Name.query.filter_by(user_id=_item.user_id).first()

                today = datetime.utcnow() + timedelta(hours=8)
                calculate_day = today.replace(tzinfo=None) - _item.predict_date.replace(tzinfo=None)

                if 32 > abs(calculate_day.days) > 0:
                    save_message = "棉棉庫存量足夠"
                    danger_message = "以下種類的棉棉可能不足："

                    # 讀取衛生棉存量，並判斷安全存量
                    db_cotton: Cotton = Cotton.query.filter_by(user_id=_item.user_id).first()
                    category = ["護墊", "日用量少", "日用正常", "日用量多", "夜用正常", "夜用量多"]
                    amount = [db_cotton.pad, db_cotton.little_daily, db_cotton.normal_daily,
                              db_cotton.high_daily, db_cotton.normal_night, db_cotton.high_night]

                    for _category, _amount in zip(category, amount):
                        if _amount < 10:
                            danger_message += f"\n {_category} 剩餘 {_amount} 片"

                    cotton_message = save_message if danger_message == '以下種類的棉棉可能不足：' else danger_message

                    msg = f"親愛的 {name.name} 您好\n"
                    msg += f"您的生理期預計於 {calculate_day.days} 內到來 \n"
                    msg += f"{cotton_message}"

                    line_bot_api.push_message(to=_item.user_id, messages=TextSendMessage(text=msg))


if __name__ == '__main__':
    get_data()
