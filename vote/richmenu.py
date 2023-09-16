import requests
import json
from linebot import LineBotApi, WebhookHandler

LINE_CHANNEL_ACCESS_TOKEN = 'remMXY/W7NSflAfWaIHA6M9xH9nfy7jeVLyZOL6jS4B4MM7nJkwTpK2QotrmwQE2exSsaEtQMqTH/tBaHVvROhDz2joiUzRtjnHdSZbHl6RbT/loIXDZH2CSSUgMxI6kMe4PzA3uK6qfVZeCi2YGGQdB04t89/1O/w1cDnyilFU='
headers = { 'Authorization': 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN, 'Content-Type':'application/json' }
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
line_id = '812mbauq'
menu_id = 'richmenu-a4d26d324c8c4196f630386c4e17daa6'

def get_user_profile():
    uid = 'U0eedfc601eb97c8627a0367d463c40bd'
    profile = line_bot_api.get_profile(uid)
    print(profile)

# document: https://developers.line.biz/en/docs/messaging-api/using-rich-menus/#other-rich-menu-features
# https://line-bot-sdk-python.readthedocs.io/en/latest/

def upload_menu():
    body = {
        "size": { "width": 800, "height": 270 },
        "selected": True,
        "name": "Vote Menu",
        "chatBarText": "選單",
        "areas": [
            {
                "bounds": { "x": 0, "y": 0, "width": 266, "height": 270 },
                "action": { "type": "uri", "uri": "https://line.me/R/nv/recommendOA/%40"+line_id }
            },
            {
                "bounds": { "x": 266, "y": 0, "width": 267, "height": 270 },
                "action": { "type": "postback", "data": "vote" }
            },
            {
                "bounds": { "x": 533, "y": 0, "width": 266, "height": 270 },
                "action": { "type": "uri", "uri": "https://www.yahoo.com.tw" }
            },
        ]
    }

    # 向指定網址發送 request
    req = requests.post('https://api.line.me/v2/bot/richmenu', headers=headers, data=json.dumps(body).encode('utf-8'))
    # 印出得到的結果
    print(req.text)


def upload_image():
    # headers['Content-Type'] = 'image/png'
    # files = {'file': open('/home/scylla/linebot/linevote/static/votemenue.png', 'rb') }
    # req = requests.post('https://api-data.line.me/v2/bot/richmenu/'+menu_id+'/content', headers=headers, files=files)
    with open("/home/scylla/linebot/linevote/static/votemenue.png", 'rb') as f:
        line_bot_api.set_rich_menu_image(menu_id, "image/png", f)


def set_menu():
    req = requests.post('https://api.line.me/v2/bot/user/all/richmenu/'+menu_id, headers=headers)
    print(req.text)


def get_menu():
    req = requests.get('https://api.line.me/v2/bot/richmenu/list', headers=headers)
    print(req.text)


def del_menu():
    req = requests.delete('https://api.line.me/v2/bot/richmenu/'+menu_id, headers=headers)
    print(req.text)

