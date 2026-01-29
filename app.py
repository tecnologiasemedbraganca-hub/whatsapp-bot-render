import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    return "Bot WhatsApp rodando com banco 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

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

    telefone = data.get("from", "desconhecido")
    mensagem = data.get("text", "vazio")

    cur.execute(
        "INSERT INTO mensagens (telefone, mensagem) VALUES (%s, %s)",
        (telefone, mensagem)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "salvo"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


