
from linebot import LineBotApi, WebhookHandler
from linebot.models import RichMenu
from pathlib import Path
from dotenv import load_dotenv
import json
import os

load_dotenv(dotenv_path=Path('linevote/.env'))

LINE_BOT_ID = os.getenv('LINE_BOT_ID')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_VOTE_HTML = os.getenv('LINE_VOTE_HTML')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
headers = { 'Authorization': 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN, 'Content-Type':'application/json' }
rich_menu_id = 'richmenu-54e28e9c1637b07b3f3f209df60a3413'

# document
# https://line-bot-sdk-python.readthedocs.io/en/latest/

# call python functions
# %> python -c 'from vote import richmenu; richmenu.create_menu()'

def test():
    print("debug: test .......")

def create_menu():
    rich_menu = {
        "size": { "width": 800, "height": 270 },
        "selected": True,
        "name": "Vote Menu",
        "chat_bar_text": "選單",
        "areas": [
            {
                "bounds": { "x": 0, "y": 0, "width": 266, "height": 270 },
                "action": { "type": "uri", "uri": "https://line.me/R/nv/recommendOA/%40"+LINE_BOT_ID }
            },
            {
                "bounds": { "x": 266, "y": 0, "width": 267, "height": 270 },
                "action": { "type": "postback", "label": "vote", "data": "vote" }
            },
            {
                "bounds": { "x": 533, "y": 0, "width": 266, "height": 270 },
                "action": { "type": "uri", "uri": LINE_VOTE_HTML }
            },
        ]
    }

    # create menu
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=RichMenu(**rich_menu), timeout=None)
    print("debug: rich_menu_id = ", rich_menu_id)

    # set image
    with open("static/votemenue.png", 'rb') as img:
        line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", img, timeout=None)

    # set menu
    line_bot_api.set_default_rich_menu(rich_menu_id, timeout=None)


def get_menu():
    menu_list = line_bot_api.get_rich_menu_list(timeout=None)
    print(menu_list)


def del_menu():
    line_bot_api.delete_rich_menu(rich_menu_id, timeout=None)

