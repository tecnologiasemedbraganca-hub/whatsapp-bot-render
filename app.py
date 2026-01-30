import os
import psycopg2
from flask import Flask, request, jsonify

# ✅ PRIMEIRO cria o app
app = Flask(__name__)

# ✅ DEPOIS carrega as variáveis de ambiente
DATABASE_URL = os.environ.get("DATABASE_URL")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# ✅ SÓ AGORA usa @app.route
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        print("TOKEN RECEBIDO:", token)
        print("TOKEN DO AMBIENTE:", VERIFY_TOKEN)

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Token inválido", 403

    if request.method == "POST":
        data = request.get_json()
        print("Mensagem recebida:", data)
        return jsonify(status="ok"), 200


# ✅ FINAL DO ARQUIVO
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

