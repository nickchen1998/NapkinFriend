from flask import Flask
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from settings import Setting
from model import Cotton, PredictDate, Name, db
from datetime import datetime
import pytz

setting = Setting()
line_bot_api = LineBotApi(setting.channel_token)
handler = WebhookHandler(setting.channel_secret)
app = Flask(__name__)

# 資料庫設定
db_url = setting.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)


def get_data():
    predict_dates = PredictDate.query.all()
    if predict_dates:
        for _predict_date in predict_dates:
            name = Name.query.filter_by(user_id=_predict_date.user_id).first()

            timezone = pytz.timezone("Asia/Taipei")
            today = timezone.localize(datetime.today())

            calculate_day = today - _predict_date.predict_date

            if 32 > calculate_day > 0:
                save_message = "棉棉庫存量足夠"
                danger_message = "以下種類的棉棉可能不足："

                # 讀取衛生棉存量，並判斷安全存量
                db_cotton: Cotton = Cotton.query.filter_by(user_id=_predict_date.user_id).first()
                for key, value in db_cotton.to_dict().items():
                    if value < 10:
                        danger_message += f"\n {key} 剩餘 {value} 片"

                cotton_message = save_message if danger_message is '以下種類的棉棉可能不足：' else danger_message

                msg = f"親愛的 {name.name} 您好\n"
                msg += f"您的生理期預計於 {calculate_day} 內到來 \n"
                msg += f"{cotton_message}"

                line_bot_api.push_message(to=_predict_date.user_id, messages=TextSendMessage(text=msg))


if __name__ == '__main__':
    get_data()