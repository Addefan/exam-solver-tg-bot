import json
from os import getenv

import requests

from src.texts import WELCOME, CANT_ANSWER

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


def get_answer_from_gpt(question, iam_token):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {iam_token}",
    }

    data = {
        "modelUri": f"gpt://{getenv("FOLDER_ID")}/yandexgpt",
        "messages": [
            {"role": "system", "text": "Ответь на экзаменационный билет."},
            {"role": "user", "text": question},
        ],
    }

    response = requests.post(url=url, headers=headers, json=data)
    if response.status_code != 200:
        return None

    alternatives = response.json()["result"]["alternatives"]
    final_alternatives = list(filter(
        lambda alternative: alternative["status"] == "ALTERNATIVE_STATUS_FINAL",
        alternatives,
    ))

    if not final_alternatives:
        return None

    answer = final_alternatives[0]["message"].get("text")
    return answer


def handle_message(message, iam_token):
    if (text := message.get("text")) and text in {"/start", "/help"}:
        send_message(WELCOME, message)
    elif text := message.get("text"):
        answer = get_answer_from_gpt(text, iam_token)
        if not answer:
            send_message(CANT_ANSWER, message)
            return

        send_message(answer, message)


def handler(event, context):
    update = json.loads(event["body"])
    message = update.get("message")

    if not message:
        return SUCCESS_RESPONSE

    handle_message(message, context.token["access_token"])

    return SUCCESS_RESPONSE
