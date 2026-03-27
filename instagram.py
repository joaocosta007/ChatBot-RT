import requests
from config import INSTAGRAM_ACCESS_TOKEN

def responder_comentario(comment_id: str, mensagem: str) -> bool:
    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"

    payload = {
        "message": mensagem,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }

    response = requests.post(url, data=payload)
    return response.status_code == 200
