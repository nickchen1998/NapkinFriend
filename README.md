## 創作者: 
1. 致理科技大學 資訊管理系 陳柏翰 (已畢業)
2. 國立台灣藝術大學 圖文傳播學系 曾廣聞 (大四)

## 創作理念連結:
https://hackmd.io/wFY-3J6KTmuRBDUSU_1I3g?view

## 若要部屬到 Heroku 要加入以下檔案
1. Porcfile (無副檔名)
2. requirements.txt
3. runtime.txt

## Procfile
```
web: gunicorn main:app
clock: python clock.py
```

## requirements.txt
```
APScheduler==3.7.0
certifi==2020.12.5
chardet==4.0.0
click==7.1.2
DateTime==4.3
Flask==1.1.2
Flask-APScheduler==1.12.2
Flask-SQLAlchemy==2.5.1
future==0.18.2
googlemaps==4.4.5
greenlet==1.0.0
gunicorn==20.1.0
idna==2.10
itsdangerous==1.1.0
Jinja2==2.11.3
line-bot-sdk==1.18.0
MarkupSafe==1.1.1
psycopg2==2.8.6
python-dateutil==2.8.1
pytz==2021.1
requests==2.25.1
six==1.15.0
SQLAlchemy==1.4.9
tzlocal==2.1
urllib3==1.26.4
Werkzeug==1.0.1
zope.interface==5.4.0
```

## runtime.txt
```
python-3.9.2
```
