import requests

from debug import logger
from settings import TELEGRAM_API_URL, TELEGRAM_FILE_URL, DEBUG


def send_message(reply_text, input_message):
    url = f"{TELEGRAM_API_URL}/sendMessage"

    data = {
        "chat_id": input_message["chat"]["id"],
        "text": reply_text,
        "reply_parameters": {
            "message_id": input_message["message_id"],
        },
    }

    response = requests.post(url=url, json=data)
    if DEBUG:
        logger.debug(
            message=f"Message sent with status code {response.status_code}.",
            data=response.json(),
        )


def get_file_path(file_id):
    url = f"{TELEGRAM_API_URL}/getFile"

    data = {
        "file_id": file_id,
    }

    response = requests.get(url=url, params=data)
    if response.status_code != 200:
        return None

    return response.json()["result"].get("file_path")


def get_image(file_path):
    url = f"{TELEGRAM_FILE_URL}/{file_path}"

    response = requests.get(url=url)
    if response.status_code != 200:
        return None

    if DEBUG:
        logger.debug(
            message=f"Image received with status code {response.status_code}.",
        )

    return response.content
