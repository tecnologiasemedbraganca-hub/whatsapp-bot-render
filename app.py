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
    return psycopg2.connect(DATABASE_URL)


# ==============================
# 🔹 Criar tabelas
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

    # ATENDENTE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS atendente (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            email TEXT,
            ativo BOOLEAN DEFAULT TRUE
        )
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

    # ⭐ FEEDBACK
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

    conn.commit()
    cur.close()
    conn.close()


# ==============================
# 🔹 Migrar tabela antiga
# ==============================
def migrar_mensagens_antigas():

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

        print("Migrando mensagens antigas...")

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
                INSERT INTO mensagem (conversa_id, remetente, conteudo, criada_em)
                VALUES (%s,%s,%s,%s)
            """, (conversa_id, "usuario", texto, data))

        conn.commit()
        print("Migração concluída.")

    except Exception as e:
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
# 🔹 Webhook WhatsApp
# ==============================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # Verificação META
    if request.method == "GET":

        if (
            request.args.get("hub.mode") == "subscribe"
            and request.args.get("hub.verify_token") == VERIFY_TOKEN
        ):
            return request.args.get("hub.challenge"), 200

        return "Token inválido", 403

    # Recebimento mensagens
    if request.method == "POST":

        data = request.get_json()
        print("Webhook:", data)

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

            # ⭐ Verifica se é feedback (1 a 5)
            if texto in ["1","2","3","4","5"]:

                cur.execute("""
                    INSERT INTO feedback (conversa_id, nota)
                    VALUES (%s,%s)
                """, (conversa_id, int(texto)))

                conn.commit()

                enviar_mensagem_whatsapp(
                    telefone,
                    "Obrigado pelo feedback ❤️"
                )

                return jsonify({"status": "feedback"}), 200

            # Salvar mensagem normal
            cur.execute("""
                INSERT INTO mensagem (
                    conversa_id,
                    whatsapp_id,
                    remetente,
                    conteudo,
                    tipo
                )
                VALUES (%s,%s,%s,%s,%s)
            """, (conversa_id, whatsapp_id, "usuario", texto, tipo))

            conn.commit()
            cur.close()
            conn.close()

            # Resposta automática
            enviar_mensagem_whatsapp(
                telefone,
                "👋 Olá! Eu sou o *Caeté*, assistente virtual.\n\nDigite:\n1 - Atendimento\n2 - Informações\n3 - Falar com humano"
            )

        except Exception as e:
            print("Erro webhook:", e)

        return jsonify({"status": "ok"}), 200


# ==============================
# 🔹 Encerrar conversa manual (TESTE)
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
    app.run(host="0.0.0.0", port=10000)
