import json
from os import getenv

import requests

SUCCESS_RESPONSE = {
    "statusCode": 200,
}


def send_message(reply_text, input_message):
    url = f"https://api.telegram.org/bot{getenv("TG_BOT_KEY")}/sendMessage"

    data = {
        "chat_id": input_message["chat"]["id"],
        "text": reply_text,
        "reply_parameters": {
            "message_id": input_message["message_id"],
        },
    }

    requests.post(url=url, json=data)


def handler(event, context):
    update = json.loads(event["body"])
    message = update.get("message")

    if not message:
        return SUCCESS_RESPONSE

    return SUCCESS_RESPONSE
