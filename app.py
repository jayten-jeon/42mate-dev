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


def get_blocks():
    # blocks = [
    #     {
    #         "type": "section",
    #         "text": {
    #             "type": "mrkdwn",
    #             "text": "42MATE에 오신걸 환영합니다!!"
    #         }
    #     },
    #     {
    #         "type": "actions",
    #         "elements": [
    #             {
    #                 "type": "button",
    #                 "text": {
    #                     "type": "plain_text",
    #                     "text": "42mate 등록하기"
    #                 },
    #                 "style": "primary",
    #                 "value": "register"
    #             },
    #             {
    #                 "type": "button",
    #                 "text": {
    #                     "type": "plain_text",
    #                     "text": "내일 만나기"
    #                 },
    #                 "style": "primary",
    #                 "value": "join"
    #             },
    #             {
    #                 "type": "button",
    #                 "text": {
    #                     "type": "plain_text",
    #                     "text": "내일 만나지 않기"
    #                 },
    #                 "style": "danger",
    #                 "value": "unjoin"
    #             },
    #             {
    #                 "type": "button",
    #                 "text": {
    #                     "type": "plain_text",
    #                     "text": "42mate 휴식하기"
    #                 },
    #                 "style": "danger",
    #                 "value": "unregister",
    #                 "confirm": {
    #                     "title": {
    #                         "type": "plain_text",
    #                         "text": "정말 휴식하시겠어요?"
    #                     },
    #                     "text": {
    #                         "type": "mrkdwn",
    #                         "text": "언제라도 다시 돌아오세요"
    #                     },
    #                     "confirm": {
    #                         "type": "plain_text",
    #                         "text": "휴식하기"
    #                     },
    #                     "deny": {
    #                         "type": "plain_text",
    #                         "text": "더 생각해보기"
    #                     }
    #                 }
    #             }
    #         ]
    #     }
    # ]
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Danny Torrence left the following review for your property:"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<https://example.com|Overlook Hotel> \n :star: \n Doors had too many axe holes, guest in room " +
                        "237 was far too rowdy, whole place felt stuck in the 1920s."
            },
            "accessory": {
                "type": "image",
                "image_url": "https://images.pexels.com/photos/750319/pexels-photo-750319.jpeg",
                "alt_text": "Haunted hotel image"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Average Rating*\n1.0"
                }
            ]
        }
    ]
    return blocks
@app.route("/slack/command", methods=['POST'])
def command_view():
    slack_id = request.form.getlist('user_id')
    user_name = request.form.getlist('user_name')
    blocks = get_blocks()
    response = slack.conversations.open(users=slack_id, return_im=True)
    channel = response.body['channel']['id']
    if User.query.filter_by(slack_id=slack_id[0]).count():
        slack.chat.post_message(channel=channel, blocks=blocks)
    else:
        register(slack_id[0], user_name[0])
        slack.chat.post_message(channel=channel, blocks=blocks)
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
