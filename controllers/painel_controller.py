from flask import jsonify, request

def listar_conversas():

    conversas_fake = [
        {
            "id": 1,
            "nome": "Maria Silva",
            "telefone": "5591999999999",
            "ultima_mensagem": "Olá, preciso de ajuda",
            "status": "aberta"
        },
        {
            "id": 2,
            "nome": "João Santos",
            "telefone": "5591888888888",
            "ultima_mensagem": "Bom dia",
            "status": "aberta"
        }
    ]

    return jsonify(conversas_fake)


def obter_conversa(conversa_id):

    mensagens_fake = [
        {"remetente": "usuario", "conteudo": "Olá, preciso de ajuda"},
        {"remetente": "bot", "conteudo": "Olá! Eu sou o Caeté 😊"},
        {"remetente": "atendente", "conteudo": "Bom dia! Em que posso ajudar?"}
    ]

    return jsonify({
        "conversa_id": conversa_id,
        "mensagens": mensagens_fake
    })


def responder_conversa():

    data = request.json
    print("Resposta manual:", data)

    return jsonify({"status": "ok"})
