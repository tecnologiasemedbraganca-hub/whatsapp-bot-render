from flask import request, jsonify
from database.connection import get_db
from services.whatsapp_service import enviar_mensagem_whatsapp
from config import VERIFY_TOKEN
import json


def webhook():

    # ====================================
    # 🔹 VERIFICAÇÃO META
    # ====================================
    if request.method == "GET":

        if (
            request.args.get("hub.mode") == "subscribe"
            and request.args.get("hub.verify_token") == VERIFY_TOKEN
        ):
            return request.args.get("hub.challenge"), 200

        return "Token inválido", 403

    # ====================================
    # 🔹 RECEBIMENTO DE EVENTOS
    # ====================================
    if request.method == "POST":

        data = request.get_json()

        print("\n===== WEBHOOK RECEBIDO =====")
        print(json.dumps(data, indent=2))

        conn = None
        cur = None

        try:

            # 🔹 Extrai payload com segurança
            entry = data.get("entry", [])
            if not entry:
                return jsonify({"status": "evento vazio"}), 200

            changes = entry[0].get("changes", [])
            if not changes:
                return jsonify({"status": "sem changes"}), 200

            value = changes[0].get("value", {})
            messages = value.get("messages")

            # 🔹 Evento sem mensagem (status, entrega, etc)
            if not messages:
                print("⚠ Evento sem mensagem")
                return jsonify({"status": "no message"}), 200

            print("📩 Mensagem recebida")

            msg = messages[0]

            telefone = msg.get("from")
            texto = msg.get("text", {}).get("body", "")
            tipo = msg.get("type")
            whatsapp_id = msg.get("id")

            nome = (
                value.get("contacts", [{}])[0]
                .get("profile", {})
                .get("name")
            )

            conn = get_db()
            cur = conn.cursor()

            # ====================================
            # 🔹 USUARIO
            # ====================================
            cur.execute("""
                INSERT INTO usuario (telefone, nome)
                VALUES (%s,%s)
                ON CONFLICT (telefone)
                DO UPDATE SET nome = EXCLUDED.nome
            """, (telefone, nome))

            cur.execute(
                "SELECT id FROM usuario WHERE telefone=%s",
                (telefone,)
            )

            usuario_id = cur.fetchone()[0]

            # ====================================
            # 🔹 CONVERSA
            # ====================================
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
                    VALUES (%s)
                    RETURNING id
                """, (usuario_id,))
                conversa_id = cur.fetchone()[0]

            # ====================================
            # 🔹 EVITAR DUPLICIDADE
            # ====================================
            cur.execute(
                "SELECT id FROM mensagem WHERE whatsapp_id=%s",
                (whatsapp_id,)
            )

            if cur.fetchone():
                print("Mensagem duplicada ignorada")
                return jsonify({"status": "duplicada"}), 200

            # ====================================
            # 🔹 FEEDBACK AUTOMÁTICO
            # ====================================
            if texto in ["1", "2", "3", "4", "5"]:

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

            # ====================================
            # 🔹 SALVAR MENSAGEM USUÁRIO
            # ====================================
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

            # ====================================
            # 🔹 RESPOSTA BOT
            # ====================================
            resposta = (
                "👋 Olá! Eu sou o *Caeté*, assistente virtual.\n\n"
                "1 - Atendimento\n"
                "2 - Informações\n"
                "3 - Falar com humano"
            )

            enviar_mensagem_whatsapp(telefone, resposta)

            # Salvar resposta bot
            cur.execute("""
                INSERT INTO mensagem (
                    conversa_id,
                    remetente,
                    conteudo,
                    tipo
                )
                VALUES (%s,%s,%s,%s)
            """, (conversa_id, "bot", resposta, "texto"))

            conn.commit()

        except Exception as e:

            if conn:
                conn.rollback()

            print("\n❌ ERRO NO WEBHOOK:")
            print(e)

        finally:

            if cur:
                cur.close()

            if conn:
                conn.close()

        return jsonify({"status": "ok"}), 200
