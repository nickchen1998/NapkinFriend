import datetime
import requests
import random
import math

from app import app
from flask import request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import LocationMessage, ImageSendMessage
from linebot.models import TemplateSendMessage, MessageTemplateAction
from linebot.models import URITemplateAction
from linebot.models import CarouselTemplate, CarouselColumn
from linebot.models import ButtonsTemplate, ConfirmTemplate
from linebot.models import DatetimePickerTemplateAction, PostbackEvent
from urllib.parse import parse_qsl
from flask_sqlalchemy import SQLAlchemy
from settings import Setting
from model import Cycle, Cotton, PredictDate, Name

setting = Setting()

line_bot_api = LineBotApi(setting.channel_token)
handler = WebhookHandler(setting.channel_secret)

# 資料庫設定
db = SQLAlchemy(app)

use_model = [Cycle, Cotton, PredictDate, Name]


# 主路由
@app.route('/')
def index():
    return '資料庫連線成功'


# 建立資料表
@app.route('/create_table')
def create_table():
    db.drop_all()
    db.create_all()
    return "資料表建立成功"


# 首次設定表單路由
@app.route('/first_time_page')
def first_time_page():
    return render_template('first_time_setting.html', liffid=setting.first_time_liff_id)


# 更新衛生棉表單
@app.route('/update_cotton')
def update_cotton_liff():
    return render_template('cotton_store_query.html', liffid=setting.update_cotton_liff_id)


# 機器人主體路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 接收文字訊息路由
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        order = event.message.text
        user_id = event.source.user_id
        if order == "查詢生理期":
            query_cycle(event, user_id)

        elif order == "輸入生理期":
            input_date(event, user_id)

        elif order == '棉棉庫存量':
            select_cotton(event)

        elif order == "附近藥妝店":
            text = """
            請依照下列方式回傳所在位置 : \n
            1. 點選圖文選單旁的鍵盤樣式 \n 
            2. 點選 " > " \n 
            3. 點選 " + " \n 
            4. 點選 "位置資訊" \n 
            5. 點選所在地回傳地址'
            """

            messages = TextSendMessage(
                text=text
            )
            line_bot_api.reply_message(event.reply_token, messages)

        # 首次使用回傳資料之開頭
        elif order[:3] == '###' and len(order) > 3:
            first_time_set(event, order, user_id)

        elif order == '查詢庫存':
            query_cotton(event, user_id)

        # 更新衛生棉庫存回傳資料開頭
        elif order[:2] == '更新' and len(order) > 2:
            update_cotton(event, order, user_id)

        elif order == '更多功能':
            more_function(event)

        elif order == '刪除資料':
            tConfirm(event)

        elif order == '確定':
            delete_data(event, user_id)

        elif order == '再想想':
            text1 = '請好好考慮清楚吧！'
            messages = TextSendMessage(
                text=text1
            )
            line_bot_api.reply_message(event.reply_token, messages)

        elif order == '首次設定':
            text1 = '請點選下列網址進行首次設定: ' + '\n'
            text1 += 'https://liff.line.me/1655866091-GaYAWL02'
            messages = TextSendMessage(
                text=text1
            )
            line_bot_api.reply_message(event.reply_token, messages)

        elif order == '聯絡我們':
            text1 = '棉棉草泥馬罷工了？！' + '\n'
            text1 += '如果有任何問題或建議' + '\n'
            text1 += '可以到這裡告訴我們喔！' + '\n'
            text1 += 'https://forms.gle/qS4erpRH5gTFD8Co6'
            messages = TextSendMessage(
                text=text1
            )
            line_bot_api.reply_message(event.reply_token, messages)

        elif order == '線上簡易門診':
            url_list = [
                'https://images.pexels.com/photos/7775232/'
                'pexels-photo-7775232.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
                'https://images.pexels.com/photos/7775231/'
                'pexels-photo-7775231.png?auto=compress&cs=tinysrgb&dpr=1&w=500',
                'https://images.pexels.com/photos/7775230/'
                'pexels-photo-7775230.png?auto=compress&cs=tinysrgb&dpr=1&w=500']

            text1 = url_list[random.randint(0, 2)]

            messages = ImageSendMessage(
                original_content_url=text1,
                preview_image_url=text1
            )
            line_bot_api.reply_message(event.reply_token, messages)

        elif order[:4] == '便利商店' and len(order) > 4:
            lat_long = order[4:].split('/')

            find_store(event, float(lat_long[0]), float(lat_long[1]), order[:4])

        elif order[:3] == '康是美' and len(order) > 3:
            lat_long = order[3:].split('/')
            find_store(event, float(lat_long[0]), float(lat_long[1]), order[:3])

        elif order[:3] == '屈臣氏' and len(order) > 3:
            lat_long = order[3:].split('/')

            find_store(event, float(lat_long[0]), float(lat_long[1]), order[:3])
    except Exception as exc:
        print(str(exc))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='接收文字訊息發生錯誤！'))


# 接收位置訊息路由_查詢附近藥妝店
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    try:
        # 取得使用者所在地
        latitude = float(event.message.latitude)
        longitude = float(event.message.longitude)

        text1 = "屈臣氏"
        text1 += str(latitude) + '/'
        text1 += str(longitude)

        text2 = "康是美"
        text2 += str(latitude) + '/'
        text2 += str(longitude)

        text3 = "便利商店"
        text3 += str(latitude) + '/'
        text3 += str(longitude)

        message = TemplateSendMessage(
            alt_text='請選擇要搜尋的商店種類',
            template=ButtonsTemplate(
                # 顯示的圖片
                thumbnail_image_url='https://images.pexels.com/photos/7775892/'
                                    'pexels-photo-7775892.png?auto=compress&cs=tinysrgb&dpr=3&h=750&w=1260',
                title='請選擇要搜尋的商店種類',  # 主標題
                text='今天，我想來點...─=≡Σ((( つ•̀ω•́)つ',  # 副標題
                actions=[
                    # 顯示文字訊息
                    MessageTemplateAction(
                        label='屈臣氏',
                        text=text1
                    ),
                    # 顯示文字訊息
                    MessageTemplateAction(
                        label='康是美',
                        text=text2
                    ),
                    # 顯示文字訊息
                    MessageTemplateAction(
                        label='便利商店',
                        text=text3
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as exc:
        print(str(exc))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='接收位置訊息發生錯誤！'))


@handler.add(PostbackEvent)  # PostbackTemplateAction觸發此事件
def handle_postback(event):
    back_data = dict(parse_qsl(event.postback.data))  # 取得Postback資料
    if back_data.get('action') == 'choice':
        user_id = back_data.get('userid')
        send_back(event, user_id)


def input_date(event, user_id):
    try:
        data_text = "action=choice&userid=%s" % user_id
        message = TemplateSendMessage(
            alt_text='輸入生理期日期',
            template=ButtonsTemplate(
                thumbnail_image_url='https://images.pexels.com/photos/7780388/'
                                    'pexels-photo-7780388.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
                title='輸入生理期日期',
                text='請選擇最近一次的日期：',
                actions=[
                    DatetimePickerTemplateAction(
                        label="選取日期",
                        data=data_text,  # 觸發postback事件
                        mode="date",  # 選取日期
                        initial="%s" % datetime.date.today(),  # 顯示初始日期
                        min="2020-02-22",  # 最小日期
                        max="2070-02-22"  # 最大日期
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as exc:
        print(str(exc))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='產生輸入生理期表單發生錯誤！'))


# 由POSTBACK所觸發之輸入生理期
def send_back(event, user_id):
    try:
        # 獲取取使用者回傳的日期
        dt = str(event.postback.params.get('date'))
        m_dt = datetime.datetime.fromisoformat(dt)

        # 從資料庫調取使用者全部生理期資料
        result = Cycle.query.filter_by(user_id=user_id).order_by(Cycle.id).desc().all()

        # 擷取所有生理期時間以及週期
        cycle_list = []
        for data in result:
            cycle_list.append(data.cycle)

        # 擷取最近一次的生理期時間並進行格式化，方便datetime計算
        last_date = result[0]

        # 計算本次週期
        this_cycle = m_dt - last_date

        # 計算平均週期
        avg_cycle = (sum(cycle_list) + this_cycle.days) / (len(cycle_list) + 1)

        # 產生下個預測日
        next_cycle = m_dt + datetime.timedelta(days=round(avg_cycle))

        data = Cycle(user_id=user_id, past_date=dt, cycle=this_cycle.days)
        db.session.add(data)

        db_predict_date: PredictDate = PredictDate.query.filter_by(user_id=user_id).first()
        db_predict_date.predict_date = next_cycle

        message = TextSendMessage(
            text='已為您新增本次週期資料，請點選查詢生理期進行查看'
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as exc:
        print(str(exc))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='輸入生理期發生錯誤！'))


# 查詢生理期
def query_cycle(event, user_id):
    try:
        # 從週期資料表撈過往週期
        latest_cycle: Cycle = Cycle.query.filter_by(user_id=user_id).order_by(Cycle.id).desc().limit(1).first()
        # 從預測日資料表撈取預測日期
        predict_date: PredictDate = PredictDate.query.filter_by(user_id=user_id).first()

        # 製作字串
        text1 = ''
        text1 += '您目前的平均週期為: ' + '\n'
        text1 += latest_cycle.cycle + '\n'
        text1 += '您最近一次的生理期為: ' + '\n'
        text1 += latest_cycle.past_date.isoformat() + '\n'
        text1 += '您下一次預測的生理期為: ' + '\n'
        text1 += predict_date.predict_date.isoformat()

        message = TextSendMessage(
            text=text1
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as exc:
        print(str(exc))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='查詢生理期發生錯誤！'))


# 衛生棉庫存選取表單
def select_cotton(event):
    try:
        message = TemplateSendMessage(
            alt_text='棉棉庫存量',
            template=ButtonsTemplate(
                # 顯示的圖片
                thumbnail_image_url='https://images.pexels.com/photos/7765684/'
                                    'pexels-photo-7765684.png?auto=compress&cs=tinysrgb&dpr=3&h=750&w=1260',
                title='棉棉庫存量',  # 主標題
                text='今天，我想來點...─=≡Σ((( つ•̀ω•́)つ',  # 副標題
                actions=[
                    # 顯示文字訊息
                    MessageTemplateAction(
                        label='٩(｡・ω・｡)﻿و 查詢庫存 ',
                        text='查詢庫存'
                    ),
                    URITemplateAction(
                        label='輸入庫存 (๑ơ ₃ ơ)',
                        uri='https://liff.line.me/1655866091-bWG8kngj'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as exc:
        print(str(exc))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='產生衛生棉庫存表單發生錯誤！'))


# 衛生棉庫存查詢
def query_cotton(event, user_id):
    try:
        result = Cotton.query.filter_by(user_id=user_id).first()

        text1 = ""
        text1 += "你的棉棉庫存  (✪ω✪) " + "\n"
        text1 += f"輕薄護墊 : {result.pad} 片" + "\n"
        text1 += f"日用量少 : {result.little_daily} 片" + "\n"
        text1 += f"日用正常 : {result.normal_daily} 片" + "\n"
        text1 += f"日用量多 : {result.high_daily} 片" + "\n"
        text1 += f"夜用正常 : {result.normal_night} 片" + "\n"
        text1 += f"夜用量多 : {result.high_night} 片"

        message = TextSendMessage(
            text=text1
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as exc:
        print(str(exc))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="查詢棉棉庫存發生錯誤"))


# 衛生棉更新
def update_cotton(event, mtext, user_id):
    try:
        # 格式化字串
        flist = list(map(int, mtext[2:].split('/')))

        # 讓使用者根據每天使用情況作新增或刪除
        db_cotton: Cotton = Cotton.query.filter_by(user_id=user_id).first()

        db_cotton.pad += flist[0]
        db_cotton.little_daily += flist[1]
        db_cotton.normal_daily += flist[2]
        db_cotton.high_daily += flist[3]
        db_cotton.normal_night += flist[4]
        db_cotton.high_night += flist[5]

        db.session.commit()

        text1 = ''
        text1 += '恭喜你！資料更新成功囉！' + "\n"
        text1 += '點選「查詢庫存」確認看看吧！' + "\n"
        text1 += 'ε٩(๑> ₃ <)۶з'

        # 回傳給使用者查看
        message = TextSendMessage(
            text=text1
        )
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as exc:
        print(str(exc))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='更新棉棉發生錯誤！'))


# 首次設定方法
def first_time_set(event, mtext, user_id):
    try:
        # 將回傳資料進行處理，寫進既定格式並回傳給使用者查看
        flist = mtext[3:].split('/')
        text1 = '姓名：' + str(flist[0]) + '\n'
        text1 += '最近一次生理期日期：' + str(flist[1]) + '\n'
        text1 += '最近一次生理期週期：' + str(flist[2]) + '\n'
        text1 += '剩餘 輕薄護墊 庫存：' + str(flist[3]) + '\n'
        text1 += '剩餘 日用量少 庫存：' + str(flist[4]) + '\n'
        text1 += '剩餘 日用正常 庫存：' + str(flist[5]) + '\n'
        text1 += '剩餘 日用量多 庫存：' + str(flist[6]) + '\n'
        text1 += '剩餘 夜用正常 庫存：' + str(flist[7]) + '\n'
        text1 += '剩餘 夜用量多 庫存：' + str(flist[8]) + '\n'
        text1 += '親愛的 : ' + str(flist[0]) + " 已紀錄您的資料"

        # 計算預測日
        m_this_date = str(flist[1]).split('-')
        predict_date = datetime.date(int(m_this_date[0]), int(m_this_date[1]),
                                     int(m_this_date[2])) + datetime.timedelta(days=int(flist[2]))

        # 將週期資料寫進週期資料表
        insert_cycle_sql = "INSERT INTO cycle (userid, pdate, cycle) VALUES('%s', '%s', '%s')" % (
            str(user_id), str(flist[1]), str(flist[2]))
        db.engine.execute(insert_cycle_sql)

        # 將預測日寫進預測日資料表
        insert_predict_sql = "INSERT INTO predictdate (userid, predictdate) VALUES('%s', '%s')" % (
            str(user_id), str(predict_date))
        db.engine.execute(insert_predict_sql)

        # 將庫存寫進庫存資料表
        insert_cotton_sql = "INSERT INTO cotton (userid, pad, ldailyuse, ndailyuse, hdailyuse, nnightuse, hnightuse) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            str(user_id), str(flist[3]), str(flist[4]), str(flist[5]), str(flist[6]), str(flist[7]), str(flist[8]))
        db.engine.execute(insert_cotton_sql)

        # 將姓名寫進姓名資料表
        insert_name_sql = "INSERT INTO name (userid, name) VALUES('%s', '%s')" % (str(user_id), str(flist[0]))
        db.engine.execute(insert_name_sql)

        # 回傳給使用者查看
        message = TextSendMessage(
            text=text1
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='首次設定發生錯誤！'))


# 更多功能回傳表單
def more_function(event):
    try:
        message = TemplateSendMessage(
            alt_text='更多功能',
            template=ButtonsTemplate(
                # 顯示的圖片
                thumbnail_image_url='https://images.pexels.com/photos/7774708/pexels-photo-7774708.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940',
                title='更多功能',  # 主標題
                text='今天，我想來點...─=≡Σ((( つ•̀ω•́)つ',  # 副標題
                actions=[
                    # 顯示文字訊息
                    MessageTemplateAction(
                        label='首次設定',
                        text='首次設定'
                    ),
                    # 顯示文字訊息
                    MessageTemplateAction(
                        label='刪除資料',
                        text='刪除資料'
                    ),
                    # 顯示文字訊息
                    MessageTemplateAction(
                        label='聯絡我們',
                        text='聯絡我們'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='產生更多功能表單發生錯誤！'))


# 刪除資料功能
def delete_data(event, user_id):
    try:
        del_cycle_sql = "DELETE FROM cycle WHERE userid = '%s'" % (user_id)
        db.engine.execute(del_cycle_sql)

        del_cotton_sql = "DELETE FROM cotton WHERE userid = '%s'" % (user_id)
        db.engine.execute(del_cotton_sql)

        del_name_sql = "DELETE FROM name WHERE userid = '%s'" % (user_id)
        db.engine.execute(del_name_sql)

        del_pre_sql = "DELETE FROM predictdate WHERE userid = '%s'" % (user_id)
        db.engine.execute(del_pre_sql)

        text1 = '已經和草泥馬和平分手(｡ ︿ ｡)' + '\n'
        text1 += '希望下次還可以再見面呢！' + '\n'
        text1 += '如果要重新認養，請在「更多功能」內進行「首次設定」'

        message = TextSendMessage(
            text=text1
        )
        line_bot_api.reply_message(event.reply_token, message)

    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='刪除資料發生錯誤！'))


def find_store(event, latitude, longitude, mtext):
    # 建立 list 來存取萃取出的店家資料
    search_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?" \
                 "key={}&location={},{}&rankby=distance&keyword={}&language=zh-TW".format(setting.google_map_key,
                                                                                          latitude,
                                                                                          longitude,
                                                                                          mtext)
    search_url_result = requests.get(search_url)
    json_result = search_url_result.json()

    name_result_list = []
    place_id_result_list = []
    address_result_list = []
    latitude_result_list = []
    longitude_result_list = []
    rate_result_list = []
    photo_url_list = []
    map_url_list = []
    distance_list = []

    # 擷取所需資料，並存入 list 當中
    for i in range(3):
        name_result_list.append(json_result['results'][i]['name'])
        place_id_result_list.append(json_result['results'][i]['place_id'])
        address_result_list.append(json_result['results'][i]['vicinity'])
        latitude_result_list.append(float(json_result['results'][i]['geometry']['location']['lat']))
        longitude_result_list.append(float(json_result['results'][i]['geometry']['location']['lng']))
        rate_result_list.append(float(json_result['results'][i]['rating']))
        # 製造用於查詢 google map 的語法
        # 語法來源參考:https://www.tpisoftware.com/tpu/articleDetails/1136
        map_url_list.append(
            "https://www.google.com/maps/search/?api=1&query={},{}&query_place_id={}".format(latitude_result_list[i],
                                                                                             longitude_result_list[i],
                                                                                             place_id_result_list[i]))

        # 製造用於查詢 google map 當中店家截圖的語法
        # 切記不能塞NONE進去網址連結，若沒有預設圖片，須自己製作OR隨意指定
        if 'photos' not in json_result['results'][i]:
            photo_url_list.append(
                'https://images.pexels.com/photos/7774217/'
                'pexels-photo-7774217.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940')
        else:
            photo_ref = json_result['results'][i]['photos'][0]['photo_reference']  # 圖片參考 ID
            photo_width = json_result['results'][i]['photos'][0]['width']  # 圖片寬度
            # 語法來源參考: https://www.tpisoftware.com/tpu/articleDetails/1136
            photo_url_list.append(
                'https://maps.googleapis.com/maps/api/place/photo?'
                'key={}&photoreference={}&maxwidth={}'.format(setting.google_map_key,
                                                              photo_ref,
                                                              photo_width))

        distance = math.sqrt(
            ((latitude - latitude_result_list[i]) ** 2) + ((longitude - longitude_result_list[i]) ** 2))
        distance_list.append(distance)

    # 於機器人中使用旋轉樣板來顯示推薦店家
    # 萃取前三筆資料
    a1 = photo_url_list[0]
    b1 = name_result_list[0]
    c1 = rate_result_list[0]
    d1 = map_url_list[0]
    e1 = address_result_list[0]
    dist1 = float(distance_list[0]) * 111

    a2 = photo_url_list[1]
    b2 = name_result_list[1]
    c2 = rate_result_list[1]
    d2 = map_url_list[1]
    e2 = address_result_list[1]
    dist2 = float(distance_list[1]) * 111

    a3 = photo_url_list[2]
    b3 = name_result_list[2]
    c3 = rate_result_list[2]
    d3 = map_url_list[2]
    e3 = address_result_list[2]
    dist3 = float(distance_list[2]) * 111

    text1 = '評價 : %s' % c1 + '\n'
    text1 += '距離 : %.2f 公里' % dist1 + '\n'
    text1 += '地址: %s' % e1

    text2 = '評價 : %s' % c2 + '\n'
    text2 += '距離 : %.2f 公里' % dist2 + '\n'
    text2 += '地址: %s' % e2

    text3 = '評價 : %s' % c3 + '\n'
    text3 += '距離 : %.2f 公里' % dist3 + '\n'
    text3 += '地址: %s' % e3

    # 旋轉樣板主體
    try:
        messages = TemplateSendMessage(
            alt_text='推薦附近店家',
            template=CarouselTemplate(
                columns=[
                    # 第一間
                    CarouselColumn(
                        thumbnail_image_url=a1,
                        title=b1,
                        text=text1,
                        actions=[
                            URITemplateAction(
                                label="查看地圖",
                                uri=d1
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=a2,
                        title=b2,
                        text=text2,
                        actions=[
                            URITemplateAction(
                                label="查看地圖",
                                uri=d2
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=a3,
                        title=b3,
                        text=text3,
                        actions=[
                            URITemplateAction(
                                label="查看地圖",
                                uri=d3
                            )
                        ]
                    )

                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, messages)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='查找店家發生錯誤！'))


def tConfirm(event):  # 按鈕樣版
    text1 = '確定要放棄這隻棉棉草泥馬了嗎？草泥馬會很難過的！' + '\n'
    text1 += '（注意！資料將會全部刪除）'

    message = TemplateSendMessage(
        alt_text='刪除資料確認',
        template=ConfirmTemplate(
            title='刪除資料確認',  # 主標題
            text=text1,  # 副標題
            actions=[
                MessageTemplateAction(  # 顯示文字計息
                    label='確定',
                    text='確定'
                ),
                MessageTemplateAction(
                    label='再想想',
                    text='再想想'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)


# 查詢近三次生理期的方法
def query_pass_cycle(event, user_id):
    # 從週期資料表撈過往週期
    sql = "SELECT * FROM cycle WHERE userid = '%s' ORDER BY id DESC LIMIT 3" % (user_id)
    result = db.engine.execute(sql)
    data_list = []
    for i in range(len(result)):
        data_list.append([])
        for data in result:
            data_list[i].append(data['pdate'])
            data_list[i].append(data['cycle'])

    # 製作字串
    text1 = ''
    for i in range(len(data_list)):
        if i == 0:
            text1 += '您最近一次的生理期為:' + '\n'
            text1 += data_list[i]
        elif i == 1:
            text1 += '您的上上次的生理期為:' + '\n'
            text1 += data_list[i]
        elif i == 2:
            text1 += '您上上上次的生理期為:' + '\n'
            text1 += data_list[i]
            break

    message = TextSendMessage(
        text=text1
    )
    line_bot_api.reply_message(event.reply_token, message)


if __name__ == '__main__':
    app.run()
