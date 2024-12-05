import base64
import json

import requests

from src.settings import TELEGRAM_API_URL, YC_API_GPT_URL, TELEGRAM_FILE_URL, FOLDER_ID, YC_API_OCR_URL
from src.texts import WELCOME, CANT_ANSWER, CAN_HANDLE_ONLY_ONE_PHOTO

SUCCESS_RESPONSE = {
    "statusCode": 200,
}


def encode_to_base64(bytes_content):
    return base64.b64encode(bytes_content).decode("utf-8")


def send_message(reply_text, input_message):
    url = f"{TELEGRAM_API_URL}/sendMessage"

    data = {
        "chat_id": input_message["chat"]["id"],
        "text": reply_text,
        "reply_parameters": {
            "message_id": input_message["message_id"],
        },
    }

    requests.post(url=url, json=data)


def get_answer_from_gpt(question, iam_token):
    url = YC_API_GPT_URL

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {iam_token}",
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt",
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

    return response.content


def recognize_text(base64_image, iam_token):
    url = YC_API_OCR_URL

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}",
    }

    data = {
        "content": base64_image,
        "mimeType": "image/jpeg",
        "languageCodes": ["ru", "en"],
    }

    response = requests.post(url=url, headers=headers, json=data)
    if response.status_code != 200:
        return None

    text = response.json()["result"]["textAnnotation"]["fullText"]
    text = text.replace("-\n", "").replace("\n", " ")
    if not text:
        return None

    return text


def handle_message(message, iam_token):
    if (text := message.get("text")) and text in {"/start", "/help"}:
        send_message(WELCOME, message)
    elif text := message.get("text"):
        answer = get_answer_from_gpt(text, iam_token)
        if not answer:
            send_message(CANT_ANSWER, message)
            return

        send_message(answer, message)
    elif message.get("photo") and message.get("media_group_id"):
        send_message(CAN_HANDLE_ONLY_ONE_PHOTO, message)
    elif image := message.get("photo"):
        image_id = image[-1]["file_id"]
        image_path = get_file_path(image_id)
        image = get_image(image_path)
        text = recognize_text(image, iam_token)
        if not text:
            send_message(CANT_ANSWER, message)
            return

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
