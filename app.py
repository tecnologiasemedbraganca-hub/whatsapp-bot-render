import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")


def get_db():
    return psycopg2.connect(DATABASE_URL)

@app.route("/", methods=["GET"])
def home():
    return "Bot WhatsApp rodando com banco 🚀"

# 🔹 VERIFICAÇÃO DO WEBHOOK (META)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Token inválido", 403

# 🔹 RECEBER MENSAGENS
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")

        if messages:
            msg = messages[0]
            telefone = msg["from"]
            texto = msg["text"]["body"]

            conn = get_db()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS mensagens (
                    id SERIAL PRIMARY KEY,
                    telefone TEXT,
                    mensagem TEXT,
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cur.execute(
                "INSERT INTO mensagens (telefone, mensagem) VALUES (%s, %s)",
                (telefone, texto)
            )

            conn.commit()
            cur.close()
            conn.close()

    except Exception as e:
        print("Erro:", e)

    return jsonify({"status": "recebido"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
