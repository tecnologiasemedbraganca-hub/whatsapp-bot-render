import os
import psycopg2
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==============================
# 🔹 Variáveis ambiente
# ==============================
DATABASE_URL = os.environ.get("DATABASE_URL")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")


# ==============================
# 🔹 Conexão banco
# ==============================
def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


# ==============================
# 🔹 Criar tabelas + ajustes
# ==============================
def criar_tabelas():

    conn = get_db()
    cur = conn.cursor()

    # USUARIO
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id SERIAL PRIMARY KEY,
            telefone TEXT UNIQUE,
            nome TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ATENDENTE (com telefone)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS atendente (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            email TEXT,
            telefone TEXT UNIQUE,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)

    # 🔹 Caso tabela já exista sem telefone
    cur.execute("""
        ALTER TABLE atendente
        ADD COLUMN IF NOT EXISTS telefone TEXT UNIQUE
    """)

    # CONVERSA
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

    # MENSAGEM
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mensagem (
            id SERIAL PRIMARY KEY,
            conversa_id INTEGER REFERENCES conversa(id),
            whatsapp_id TEXT,
            remetente TEXT,
            conteudo TEXT,
            tipo TEXT DEFAULT 'texto',
            criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ARQUIVO
    cur.execute("""
        CREATE TABLE IF NOT EXISTS arquivo (
            id SERIAL PRIMARY KEY,
            mensagem_id INTEGER REFERENCES mensagem(id),
            tipo TEXT,
            url TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # FEEDBACK
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            conversa_id INTEGER REFERENCES conversa(id),
            atendente_id INTEGER REFERENCES atendente(id),
            nota INTEGER CHECK (nota BETWEEN 1 AND 5),
            comentario TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Índices
    cur.execute("CREATE INDEX IF NOT EXISTS idx_usuario_tel ON usuario(telefone)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_msg_conv ON mensagem(conversa_id)")

    conn.commit()
    cur.close()
    conn.close()


# ==============================
# 🔹 Migração opcional
# ==============================
def migrar_mensagens_antigas():

    if os.environ.get("MIGRAR_TABELA_ANTIGA") != "true":
        return

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'mensagens'
            )
        """)

        if not cur.fetchone()[0]:
            return

        cur.execute("SELECT telefone, mensagem, data FROM mensagens")
        registros = cur.fetchall()

        for telefone, texto, data in registros:

            cur.execute("""
                INSERT INTO usuario (telefone)
                VALUES (%s)
                ON CONFLICT (telefone) DO NOTHING
            """, (telefone,))

            cur.execute("SELECT id FROM usuario WHERE telefone=%s", (telefone,))
            usuario_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO conversa (usuario_id)
                VALUES (%s)
                RETURNING id
            """, (usuario_id,))
            conversa_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO mensagem (
                    conversa_id, remetente, conteudo, criada_em
                )
                VALUES (%s,%s,%s,%s)
            """, (conversa_id, "usuario", texto, data))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Erro migração:", e)

    finally:
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
        "text": {"body": texto}
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Resposta envio:", response.text)


# ==============================
# 🔹 Rota raiz
# ==============================
@app.route("/", methods=["GET"])
def home():
    return "Bot WhatsApp Caeté rodando 🚀"


# ==============================
# 🔹 Webhook WhatsApp
# ==============================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":
        if (
            request.args.get("hub.mode") == "subscribe"
            and request.args.get("hub.verify_token") == VERIFY_TOKEN
        ):
            return request.args.get("hub.challenge"), 200
        return "Token inválido", 403

    if request.method == "POST":

        data = request.get_json()
        print("Webhook:", data)

        conn = None
        cur = None

        try:
            value = data["entry"][0]["changes"][0]["value"]
            messages = value.get("messages")

            if not messages:
                return jsonify({"status": "no message"}), 200

            msg = messages[0]

            telefone = msg["from"]
            texto = msg.get("text", {}).get("body", "")
            tipo = msg.get("type")
            whatsapp_id = msg.get("id")

            nome = value.get("contacts", [{}])[0].get("profile", {}).get("name")

            conn = get_db()
            cur = conn.cursor()

            # Criar usuário
            cur.execute("""
                INSERT INTO usuario (telefone, nome)
                VALUES (%s,%s)
                ON CONFLICT (telefone)
                DO UPDATE SET nome=EXCLUDED.nome
            """, (telefone, nome))

            cur.execute("SELECT id FROM usuario WHERE telefone=%s", (telefone,))
            usuario_id = cur.fetchone()[0]

            # Buscar conversa aberta
            cur.execute("""
                SELECT id FROM conversa
                WHERE usuario_id=%s AND status='aberta'
            """, (usuario_id,))
            conversa = cur.fetchone()

            if conversa:
                conversa_id = conversa[0]
            else:
                cur.execute("""
                    INSERT INTO conversa (usuario_id)
                    VALUES (%s) RETURNING id
                """, (usuario_id,))
                conversa_id = cur.fetchone()[0]

            # Evitar duplicidade
            cur.execute("""
                SELECT id FROM mensagem WHERE whatsapp_id=%s
            """, (whatsapp_id,))
            if cur.fetchone():
                return jsonify({"status": "duplicada"}), 200

            # Feedback automático
            if texto in ["1","2","3","4","5"]:

                cur.execute("""
                    INSERT INTO feedback (conversa_id, nota)
                    VALUES (%s,%s)
                """, (conversa_id, int(texto)))

                conn.commit()

                enviar_mensagem_whatsapp(telefone, "Obrigado pelo feedback ❤️")

                return jsonify({"status": "feedback"}), 200

            # Salvar mensagem usuário
            cur.execute("""
                INSERT INTO mensagem (
                    conversa_id, whatsapp_id, remetente, conteudo, tipo
                )
                VALUES (%s,%s,%s,%s,%s)
            """, (conversa_id, whatsapp_id, "usuario", texto, tipo))

            resposta_bot = (
                "👋 Olá! Eu sou o *Caeté*, assistente virtual.\n\n"
                "Digite:\n"
                "1 - Atendimento\n"
                "2 - Informações\n"
                "3 - Falar com humano"
            )

            enviar_mensagem_whatsapp(telefone, resposta_bot)

            # Salvar resposta do bot
            cur.execute("""
                INSERT INTO mensagem (
                    conversa_id, remetente, conteudo, tipo
                )
                VALUES (%s,%s,%s,%s)
            """, (conversa_id, "bot", resposta_bot, "texto"))

            conn.commit()

        except Exception as e:
            if conn:
                conn.rollback()
            print("Erro webhook:", e)

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

        return jsonify({"status": "ok"}), 200


# ==============================
# 🔹 Encerrar conversa
# ==============================
@app.route("/encerrar/<telefone>")
def encerrar_conversa(telefone):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id FROM conversa c
        JOIN usuario u ON u.id=c.usuario_id
        WHERE u.telefone=%s AND status='aberta'
    """, (telefone,))

    conversa = cur.fetchone()

    if not conversa:
        return "Nenhuma conversa aberta"

    conversa_id = conversa[0]

    cur.execute("""
        UPDATE conversa
        SET status='finalizada', finalizada_em=NOW()
        WHERE id=%s
    """, (conversa_id,))

    conn.commit()
    cur.close()
    conn.close()

    enviar_mensagem_whatsapp(
        telefone,
        "Atendimento encerrado.\n\n⭐ Avalie de 1 a 5"
    )

    return "Conversa encerrada"


# ==============================
# 🔹 Start app
# ==============================
if __name__ == "__main__":
    criar_tabelas()
    migrar_mensagens_antigas()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
