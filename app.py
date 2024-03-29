import os
import sys
import chromedriver_autoinstaller
from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from fsm import TocMachine
from utils import send_text_message
from library import dict_cn_en , dict_tw_en , dict_tw_cn , dict_cn_tw , dict_en_tw , create_dictionary

chromedriver_autoinstaller.install()
load_dotenv()

machine = TocMachine(
    states = ["user","menu","feature","input_name","select_service","send_image","opgg_url","story_url","input_lane","input_tier","select_info","win_rate","pick_rate","input_lane_matchup","input_name_matchup","matchup_winrate"],
    transitions = 
    [
        {
            "trigger": "advance",
            "source": "user",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "feature",
            "conditions": "is_going_to_feature",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "input_name",
            "conditions": "is_going_to_input_name",
        },        
        {
            "trigger": "advance",
            "source": "input_name",
            "dest": "select_service",
            "conditions": "is_going_to_select_service",
        },
        {
            "trigger": "advance",
            "source": "select_service",
            "dest": "send_image",
            "conditions": "is_going_to_send_image",
        },
        {
            "trigger": "advance",
            "source": "select_service",
            "dest": "opgg_url",
            "conditions": "is_going_to_opgg_url",
        },
        {
            "trigger": "advance",
            "source": "select_service",
            "dest": "story_url",
            "conditions": "is_going_to_story_url",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "input_lane",
            "conditions": "is_going_to_input_lane",
        }, 
        {
            "trigger": "advance",
            "source": "input_lane",
            "dest": "input_tier",
            "conditions": "is_going_to_input_tier",
        },
        {
            "trigger": "advance",
            "source": "input_tier",
            "dest": "select_info",
            "conditions": "is_going_to_select_info",
        },
        
        {
            "trigger": "advance",
            "source": "select_info",
            "dest": "win_rate",
            "conditions": "is_going_to_win_rate",
        },
        {
            "trigger": "advance",
            "source": "select_info",
            "dest": "pick_rate",
            "conditions": "is_going_to_pick_rate",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "input_lane_matchup",
            "conditions": "is_going_to_input_lane_matchup",
        },
        {
            "trigger": "advance",
            "source": "input_lane_matchup",
            "dest": "input_name_matchup",
            "conditions": "is_going_to_input_name_matchup",
        },
        {
            "trigger": "advance",
            "source": "input_name_matchup",
            "dest": "matchup_winrate",
            "conditions": "is_going_to_matchup_winrate",
        },        
        {
            "trigger": "go_back",
            "source": ["feature" , "send_image" , "opgg_url" , "story_url" , "win_rate" , "pick_rate" , "matchup_winrate"],
            "dest": "user"
        }
        
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    except exceptions:
        abort(400)
    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "請輸入正確格式")

    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
    except exceptions:
        abort(400)
    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "請輸入正確格式")
    return "OK"

@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")

if __name__ == "__main__":
    #machine.get_graph().draw("fsm.png", prog="dot", format="png")
    create_dictionary();
    port = os.getenv("PORT", None)
    app.run(host="0.0.0.0", port=port, debug=True)