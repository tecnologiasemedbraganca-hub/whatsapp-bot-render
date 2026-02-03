from flask import request, jsonify
from database.connection import get_db
from services.whatsapp_service import enviar_mensagem_whatsapp
from config import VERIFY_TOKEN

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

            # usuario
            cur.execute("""
                INSERT INTO usuario (telefone, nome)
                VALUES (%s,%s)
                ON CONFLICT (telefone)
                DO UPDATE SET nome=EXCLUDED.nome
            """, (telefone, nome))

            cur.execute("SELECT id FROM usuario WHERE telefone=%s", (telefone,))
            usuario_id = cur.fetchone()[0]

            # conversa
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

            # duplicidade
            cur.execute("SELECT id FROM mensagem WHERE whatsapp_id=%s", (whatsapp_id,))
            if cur.fetchone():
                return jsonify({"status": "duplicada"}), 200

            # feedback
            if texto in ["1","2","3","4","5"]:

                cur.execute("""
                    INSERT INTO feedback (conversa_id, nota)
                    VALUES (%s,%s)
                """, (conversa_id, int(texto)))

                conn.commit()

                enviar_mensagem_whatsapp(telefone, "Obrigado pelo feedback ❤️")
                return jsonify({"status": "feedback"}), 200

            # salvar mensagem usuario
            cur.execute("""
                INSERT INTO mensagem (
                    conversa_id, whatsapp_id, remetente, conteudo, tipo
                )
                VALUES (%s,%s,%s,%s,%s)
            """, (conversa_id, whatsapp_id, "usuario", texto, tipo))

            resposta = (
                "👋 Olá! Eu sou o *Caeté*, assistente virtual.\n\n"
                "1 - Atendimento\n"
                "2 - Informações\n"
                "3 - Falar com humano"
            )

            enviar_mensagem_whatsapp(telefone, resposta)

            cur.execute("""
                INSERT INTO mensagem (
                    conversa_id, remetente, conteudo, tipo
                )
                VALUES (%s,%s,%s,%s)
            """, (conversa_id, "bot", resposta, "texto"))

            conn.commit()

        except Exception as e:
            if conn:
                conn.rollback()
            print(e)

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

        return jsonify({"status": "ok"}), 200
