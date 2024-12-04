import json
from os import getenv

import requests

from src.texts import WELCOME

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


def handle_message(message):
    if (text := message.get("text")) and text in {"/start", "/help"}:
        send_message(WELCOME, message)


def handler(event, context):
    update = json.loads(event["body"])
    message = update.get("message")

    if not message:
        return SUCCESS_RESPONSE

    handle_message(message)

    return SUCCESS_RESPONSE
