from slacker import Slacker
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import json

import requests

token = os.environ['SLACK_TOKEN']
slack = Slacker(token)

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User, Match

@app.route("/")
def hello():
    slack.chat.post_message("#random", "Slacker test")
    return "Hello World!!"


def register(slack_id, intra_id):
    try:
        user=User(
            slack_id=slack_id,
            intra_id=intra_id,
        )
        db.session.add(user)
        db.session.commit()
        return "Success"
    except Exception as e:
            return(str(e))


@app.route("/slack/command", methods=['POST'])
def command_view():
    slack_id = request.form.getlist('user_id')
    user_name = request.form.getlist('user_name')
    attachments = [
        {
            "fallback": "You are unable to choose a action",
            "callback_id": "choose_action",
            "color": "#FF6F61",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "join",
                    "text": "내일 만나기",
                    "style": "primary",
                    "type": "button",
                    "value": "join"
                },
                {
                    "name": "bye",
                    "text": "내일 만나지 않기",
                    "type": "button",
                    "value": "bye"
                },
                {
                    "name": "register",
                    "text": "42mate 등록하기",
                    "style": "primary",
                    "type": "button",
                    "value": "register",
                },
                {
                    "name": "unregister",
                    "text": "42mate 휴식하기",
                    "style": "danger",
                    "type": "button",
                    "value": "unregister",
                    "confirm": {
                        "title": "정말 휴식하시겠어요?",
                        "text": "언제라도 다시 돌아오세요.",
                        "ok_text": "휴식하기",
                        "dismiss_text": "더 생각해보기"
                    }
                }
            ]
        }
    ]
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    if User.query.filter_by(slack_id=slack_id[0]).count():
        slack.chat.post_message(channel=channel, text="re-visit text", attachments=attachments)
    else:
        register(slack_id[0], user_name[0])
        update_without_register_button()
        slack.chat.post_message(channel=channel, text="first-visit-text", attachments=attachments)
    return ("", 200)


@app.route("/test/make_match")
def make_match():
    users = User.query.all()
    print(users)
    print(users[0])
    print(users[1])
    try:
        match=Match(
            user1 = users[0],
            user2 = users[1]
        )
        db.session.add(match)
        db.session.commit()
        return "Success"
    except Exception as e:
            return(str(e))

@app.route("/test/match_list")
def match_list():
    match = Match.query.all()[0]
    print(match.users)
    return (match.users, 200)





#data = request.get_data()
@app.route("/slack/callback", methods=['POST'])
def command_callback():
    #data = request.form.getlist('text')
    #print(data)
    #data = request.get_json(force=True)
    data = json.loads(request.form['payload'])
    channel = data['channel']['id']
    ts = data['message_ts']
    attachments = [
        {
            "fallback": "You are unable to choose a action",
            "callback_id": "choose_action",
            "color": "#FF6F61",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "join",
                    "text": "내일 만나기",
                    "style": "primary",
                    "type": "button",
                    "value": "join"
                },
                {
                    "name": "register",
                    "text": "42mate 등록하기",
                    "style": "primary",
                    "type": "button",
                    "value": "register",
                },
                {
                    "name": "unregister",
                    "text": "42mate 휴식하기",
                    "style": "danger",
                    "type": "button",
                    "value": "unregister",
                    "confirm": {
                        "title": "정말 휴식하시겠어요?",
                        "text": "언제라도 다시 돌아오세요.",
                        "ok_text": "휴식하기",
                        "dismiss_text": "더 생각해보기"
                    }
                }
            ]
        }
    ]
    slack.chat.update(channel=channel, ts=ts, text="edit-text", attachments=attachments)
    # data = request.get_data()
    #text = data['text']
    #print(text)
    #command = parsing(text)
    # command = parsing()
    # if command == 'register':
    #     register(data)
    # elif command == 'list':
    #     list
    return ("", 200)

if __name__ == "__main__":
    app.run()

#
# @app.route("/slack", methods=["GET", "POST"])
# def hears():
#     slack_event = json.loads(request.data)
#     if "challenge" in slack_event:
#         return make_response(slack_event["challenge"], 200,
#                              {"content_type": "application/json"})
#     if "event" in slack_event:
#         event_type = slack_event["event"]["type"]
#         return event_handler(event_type, slack_event)
#     return make_response("슬랙 요청에 대한 이벤트가 없습니다.", 404,
#                          {"X-Slack-No-Retry": 1})
