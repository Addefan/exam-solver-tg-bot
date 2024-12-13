import json

from services.telegram import send_message, get_file_path, get_image
from services.yandex_cloud import recognize_text, get_answer_from_gpt
from texts import WELCOME, CANT_ANSWER, CAN_HANDLE_ONLY_ONE_PHOTO, CAN_HANDLE_ONLY_TEXT_OR_PHOTO
from utils import encode_to_base64

SUCCESS_RESPONSE = {
    "statusCode": 200,
}


def handle_text_message(text, message, iam_token):
    answer = get_answer_from_gpt(text, iam_token)
    if not answer:
        send_message(CANT_ANSWER, message)
        return

    send_message(answer, message)


def handle_photo_message(tg_photo, message, iam_token):
    image_id = tg_photo[-1]["file_id"]
    image_path = get_file_path(image_id)
    image = get_image(image_path)
    text = recognize_text(encode_to_base64(image), iam_token)
    if not text:
        send_message(CANT_ANSWER, message)
        return

    handle_text_message(text, message, iam_token)


def handle_message(message, iam_token):
    if (text := message.get("text")) and text in {"/start", "/help"}:
        send_message(WELCOME, message)

    elif text := message.get("text"):
        handle_text_message(text, message, iam_token)

    elif message.get("photo") and message.get("media_group_id"):
        send_message(CAN_HANDLE_ONLY_ONE_PHOTO, message)

    elif image := message.get("photo"):
        handle_photo_message(image, message, iam_token)

    else:
        send_message(CAN_HANDLE_ONLY_TEXT_OR_PHOTO, message)


def handler(event, context):
    update = json.loads(event["body"])
    message = update.get("message")

    if not message:
        return SUCCESS_RESPONSE

    handle_message(message, context.token["access_token"])

    return SUCCESS_RESPONSE
