from flask import Flask, request, jsonify
from config import VERIFY_TOKEN
from gemini import gerar_resposta
from instagram import responder_comentario

app = Flask(__name__)

# Contexto da marca — edite conforme o cliente
CONTEXTO_MARCA = """
Esta é uma marca de moda feminina chamada Exemplo Store.
Tom de voz: descontraído, próximo, use emojis com moderação.
Nunca fale sobre concorrentes.
"""

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    """Verificação inicial exigida pela Meta"""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403


@app.route("/webhook", methods=["POST"])
def receber_comentario():
    """Recebe os eventos do Instagram"""
    data = request.json

    try:
        changes = data["entry"][0]["changes"][0]
        
        # Só processa comentários (ignora outros eventos)
        if changes["field"] != "comments":
            return jsonify({"status": "ignorado"}), 200

        comentario_texto = changes["value"]["text"]
        comment_id = changes["value"]["id"]

        # Ignora comentários muito curtos (emojis, spam)
        if len(comentario_texto) < 10:
            return jsonify({"status": "muito curto"}), 200

        # Gera resposta com Gemini
        resposta = gerar_resposta(comentario_texto, CONTEXTO_MARCA)

        # Ignora se o Gemini decidiu não responder
        if resposta == "IGNORAR":
            return jsonify({"status": "ignorado pelo gemini"}), 200

        # Posta a resposta no Instagram
        sucesso = responder_comentario(comment_id, resposta)

        status = "respondido" if sucesso else "erro ao postar"
        return jsonify({"status": status}), 200

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"status": "erro"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
