import base64


def encode_to_base64(bytes_content):
    return base64.b64encode(bytes_content).decode("utf-8")
