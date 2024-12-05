import json

from src.services.telegram import send_message, get_file_path, get_image
from src.services.yandex_cloud import recognize_text, get_answer_from_gpt
from src.texts import WELCOME, CANT_ANSWER, CAN_HANDLE_ONLY_ONE_PHOTO, CAN_HANDLE_ONLY_TEXT_OR_PHOTO
from src.utils import encode_to_base64

SUCCESS_RESPONSE = {
    "statusCode": 200,
}


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
        text = recognize_text(encode_to_base64(image), iam_token)
        if not text:
            send_message(CANT_ANSWER, message)
            return

        answer = get_answer_from_gpt(text, iam_token)
        if not answer:
            send_message(CANT_ANSWER, message)
            return

        send_message(answer, message)
    else:
        send_message(CAN_HANDLE_ONLY_TEXT_OR_PHOTO, message)


def handler(event, context):
    update = json.loads(event["body"])
    message = update.get("message")

    if not message:
        return SUCCESS_RESPONSE

    handle_message(message, context.token["access_token"])

    return SUCCESS_RESPONSE
