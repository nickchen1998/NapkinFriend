# -*- coding: utf-8 -*-
"""
Created on Sat May  1 10:00:39 2021

@author: nick
"""

from flask import Flask
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from flask_sqlalchemy import SQLAlchemy
import datetime, urllib3
from apscheduler.schedulers.blocking import BlockingScheduler


#line bot 的 channel token
line_bot_api = LineBotApi('')
#line bot 的 channel secret
handler = WebhookHandler('')
sched = BlockingScheduler()
app = Flask(__name__)

#資料庫設定
uri = ""  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI']= uri
#app.config['DATABASE_URL']=uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
db=SQLAlchemy(app)





@sched.scheduled_job('interval', days=1, start_date='2021-05-04 08:00:00', timezone='Asia/Taipei')
def scheduled_job():
    #撈取預測日
    sql = "SELECT * FROM predictdate "
    result = db.engine.execute(sql)
    id_list = []
    predictdate_list = []
    for data in result:
         id_list.append(data['userid'])
         predictdate_list.append(data['predictdate'])
    
    #每日進行一次全部人距離預測日的運算
    for i in range(len(predictdate_list)):
        x = predictdate_list[i].split('-')
        y = datetime.date(int(x[0]), int(x[1]), int(x[2]))
        today = datetime.date.today()
        c = int(str(today - y)[:3])
        if c < 0:
            c = -c

        #撈取名字
        sql = "SELECT * FROM name WHERE userid = '%s'" %(id_list[i])
        name_result = db.engine.execute(sql)
        name = ''
        for data in name_result:
            name = data['name']
       
        #判斷神麼時候提醒
        if c < 32:
            #獲取ID
            to = id_list[i]
            
            #撈取衛生棉庫存
            sql = "SELECT * FROM cotton WHERE userid = '%s'"%(to)
            result = db.engine.execute(sql)
            cotton_category_list = ['輕薄護墊', '日用量少', '日用正常', '日用量多', '夜用正常', '夜用量多']
            cotton_sotre_list = []
            for data in result:
                cotton_sotre_list.append(data['pad'])
                cotton_sotre_list.append(data['ldailyuse'])
                cotton_sotre_list.append(data['ndailyuse'])
                cotton_sotre_list.append(data['hdailyuse'])
                cotton_sotre_list.append(data['nnightuse'])
                cotton_sotre_list.append(data['hnightuse'])
            
            #開始進行判別安全存量
            save_store = 10
            save_flag = True
            save_message = '棉棉存量足夠'
            unsave_message = '以下種類的棉棉可能不足：'
            final_send_message = ''
            for i in range(len(cotton_sotre_list)):
                if int(cotton_sotre_list[i]) < save_store:
                    save_flag = False
                    unsave_message += '\n' + cotton_category_list[i] + "剩餘 " + cotton_sotre_list[i] + ' 片'
            
            if save_flag == True:
                final_send_message = save_message
            else:
                final_send_message = unsave_message
            
            msg = ""
            msg += "親愛的" + name + " 您好: " + "\n"
            msg += "您的生理期預計於 " + str(c) + " 天之內到來" + '\n'
            msg += final_send_message
            line_bot_api.push_message(to, TextSendMessage(text=msg))

@sched.scheduled_job('interval',  minutes=20, start_date='2021-05-03 10:50:00', timezone='Asia/Taipei')
def d_scheduled_job():
    http = urllib3.PoolManager()
    r = http.request('GET', "https://cotton-line-bot-via2.herokuapp.com/")
    r.status

sched.start()
