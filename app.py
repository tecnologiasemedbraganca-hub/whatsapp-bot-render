import os
import psycopg2
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔹 Variáveis de ambiente
DATABASE_URL = os.environ.get("DATABASE_URL")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")


# 🔹 Conexão com banco
def get_db():
    return psycopg2.connect(DATABASE_URL)


# 🔹 Enviar mensagem pelo WhatsApp
def enviar_mensagem_whatsapp(numero, texto):
    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {
            "body": texto
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Resposta envio:", response.text)
@app.route("/teste-envio", methods=["GET"])
def teste_envio():
    enviar_mensagem_whatsapp("5591984319683", "Teste manual OK 🚀")
    return "ok"

# 🔹 Rota raiz (teste)
@app.route("/", methods=["GET"])
def home():
    return "Bot WhatsApp rodando com banco 🚀"



# 🔹 WEBHOOK (GET + POST)
@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # ✅ Verificação do webhook (META)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Token inválido", 403

    # ✅ Recebimento de mensagens
    if request.method == "POST":
        data = request.get_json()
        print("Webhook recebido:", data)

        try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        messages = value.get("messages")
        if not messages:
            return jsonify({"status": "no message"}), 200

        msg = messages[0]
        telefone = msg.get("from")

        texto = ""
        if msg.get("text"):
            texto = msg["text"].get("body", "")
        else:
            texto = f"Mensagem do tipo {msg.get('type')}"

        print("Telefone:", telefone)
        print("Texto:", texto)

        enviar_mensagem_whatsapp(
            telefone,
            "Olá! Recebi sua mensagem com sucesso ✅"
        )

    except Exception as e:
        print("Erro ao processar webhook:", e)

    return jsonify({"status": "ok"}), 200


                # 🔹 Salvar no banco
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

                # 🔹 Responder no WhatsApp
                enviar_mensagem_whatsapp(
                    telefone,
                    "Mensagem recebida com sucesso ✅"
                )

        except Exception as e:
            print("Erro ao processar webhook:", e)

        return jsonify({"status": "ok"}), 200


# 🔹 Start do app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
