import requests
from config import GEMINI_API_KEY

def gerar_resposta(comentario: str, contexto_marca: str = "") -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""Você é o atendimento de uma marca nas redes sociais.
{contexto_marca}

Regras:
- Responda de forma simpática, curta e em português
- Máximo 2 frases
- Nunca mencione preços ou promoções
- Se for reclamação, peça para entrar em contato pelo direct
- Sempre responda, mesmo que o comentário seja curto ou em outro idioma

Comentário: {comentario}

Resposta:"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return "IGNORAR"
