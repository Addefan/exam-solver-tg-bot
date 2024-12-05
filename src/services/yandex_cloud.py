import requests

from src.settings import YC_API_OCR_URL, FOLDER_ID, YC_API_GPT_URL


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
