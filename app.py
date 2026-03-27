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
    data = request.json
    print("Webhook recebido:", data)  # Log para debug

    try:
        entry = data.get("entry", [])
        if not entry:
            return jsonify({"status": "sem entry"}), 200

        changes = entry[0].get("changes", [])
        if not changes:
            return jsonify({"status": "sem changes"}), 200

        change = changes[0]
        field = change.get("field", "")
        value = change.get("value", {})

        print(f"Campo: {field}")
        print(f"Valor: {value}")

        if field != "comments":
            return jsonify({"status": f"campo ignorado: {field}"}), 200

        comentario_texto = value.get("text", "")
        comment_id = value.get("id", "")

        print(f"Comentário: {comentario_texto}")
        print(f"Comment ID: {comment_id}")

        if not comentario_texto or not comment_id:
            return jsonify({"status": "dados incompletos"}), 200

        if len(comentario_texto) < 10:
            return jsonify({"status": "muito curto"}), 200

        resposta = gerar_resposta(comentario_texto, CONTEXTO_MARCA)
        print(f"Resposta gerada: {resposta}")

        if resposta == "IGNORAR":
            return jsonify({"status": "ignorado pelo gemini"}), 200

        sucesso = responder_comentario(comment_id, resposta)
        print(f"Postado com sucesso: {sucesso}")

        status = "respondido" if sucesso else "erro ao postar"
        return jsonify({"status": status}), 200

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"status": "erro", "detalhe": str(e)}), 500
