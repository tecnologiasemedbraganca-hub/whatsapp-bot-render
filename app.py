import os
import psycopg2
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==============================
# 🔹 Variáveis de ambiente
# ==============================
DATABASE_URL = os.environ.get("DATABASE_URL")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# ==============================
# 🔹 Conexão com banco PostgreSQL
# ==============================
def get_db():
    return psycopg2.connect(DATABASE_URL)

# ==============================
# 🔹 Criação das tabelas (1x)
# ==============================
def criar_tabelas():
    conn = get_db()
    cur = conn.cursor()

    # Usuário do WhatsApp
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id SERIAL PRIMARY KEY,
            telefone TEXT UNIQUE,
            nome TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Atendente humano
    cur.execute("""
        CREATE TABLE IF NOT EXISTS atendente (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            email TEXT,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)

    # Conversa
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversa (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuario(id),
            atendente_id INTEGER REFERENCES atendente(id),
            status TEXT DEFAULT 'aberta',
            iniciada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finalizada_em TIMESTAMP
        )
    """)

    # Mensagem
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mensagem (
            id SERIAL PRIMARY KEY,
            conversa_id INTEGER REFERENCES conversa(id),
            remetente TEXT,
            conteudo TEXT,
            tipo TEXT DEFAULT 'texto',
            criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Arquivo (imagem, áudio, pdf etc)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS arquivo (
            id SERIAL PRIMARY KEY,
            mensagem_id INTEGER REFERENCES mensagem(id),
            tipo TEXT,
            url TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

# ==============================
# 🔹 Enviar mensagem WhatsApp
# ==============================
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

# ==============================
# 🔹 Rota teste de envio
# ==============================
@app.route("/teste-envio", methods=["GET"])
def teste_envio():
    enviar_mensagem_whatsapp(
        "5591984319683",
        "👋 Olá! Eu sou o *Caeté*, assistente virtual 🤖"
    )
    return "ok"

# ==============================
# 🔹 Rota raiz
# ==============================
@app.route("/", methods=["GET"])
def home():
    return "Bot WhatsApp rodando com PostgreSQL 🚀"

# ==============================
# 🔹 Webhook WhatsApp
# ==============================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # 🔹 Verificação META
    if request.method == "GET":
        if (
            request.args.get("hub.mode") == "subscribe"
            and request.args.get("hub.verify_token") == VERIFY_TOKEN
        ):
            return request.args.get("hub.challenge"), 200
        return "Token inválido", 403

    # 🔹 Recebimento de mensagem
    if request.method == "POST":
        data = request.get_json()
        print("Webhook recebido:", data)

        try:
            value = data["entry"][0]["changes"][0]["value"]
            messages = value.get("messages")

            if not messages:
                return jsonify({"status": "no message"}), 200

            msg = messages[0]
            telefone = msg.get("from")
            texto = msg.get("text", {}).get("body", "")
            tipo = msg.get("type")

            conn = get_db()
            cur = conn.cursor()

            # 🔹 Criar usuário se não existir
            cur.execute(
                "INSERT INTO usuario (telefone) VALUES (%s) ON CONFLICT (telefone) DO NOTHING",
                (telefone,)
            )

            # 🔹 Buscar usuário
            cur.execute("SELECT id FROM usuario WHERE telefone=%s", (telefone,))
            usuario_id = cur.fetchone()[0]

            # 🔹 Criar conversa se não existir aberta
            cur.execute("""
                SELECT id FROM conversa
                WHERE usuario_id=%s AND status='aberta'
            """, (usuario_id,))
            conversa = cur.fetchone()

            if conversa:
                conversa_id = conversa[0]
            else:
                cur.execute(
                    "INSERT INTO conversa (usuario_id) VALUES (%s) RETURNING id",
                    (usuario_id,)
                )
                conversa_id = cur.fetchone()[0]

            # 🔹 Salvar mensagem
            cur.execute("""
                INSERT INTO mensagem (conversa_id, remetente, conteudo, tipo)
                VALUES (%s, %s, %s, %s)
            """, (conversa_id, "usuario", texto, tipo))

            conn.commit()
            cur.close()
            conn.close()

            # 🔹 Resposta automática
            enviar_mensagem_whatsapp(
                telefone,
                "👋 Olá! Eu sou o *Caeté*, assistente virtual da instituição.\n\nComo posso te ajudar hoje?"
            )

        except Exception as e:
            print("Erro no webhook:", e)

        return jsonify({"status": "ok"}), 200

# ==============================
# 🔹 Start do app
# ==============================
if __name__ == "__main__":
    criar_tabelas()  # cria tudo automaticamente
    app.run(host="0.0.0.0", port=10000)
