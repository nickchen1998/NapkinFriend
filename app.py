from settings import Setting
from flask import Flask

setting = Setting()
app = Flask(__name__)

# 資料庫設定
db_url = setting.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
