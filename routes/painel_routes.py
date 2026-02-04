from flask import Blueprint
from controllers.painel_controller import (
    listar_conversas,
    obter_conversa,
    responder_conversa
)

painel = Blueprint("painel", __name__)

# Interface
@painel.route("/painel")
def painel_view():
    from flask import render_template
    return render_template("painel.html")

# API
@painel.route("/api/conversas")
def api_conversas():
    return listar_conversas()

@painel.route("/api/conversa/<int:conversa_id>")
def api_conversa(conversa_id):
    return obter_conversa(conversa_id)

@painel.route("/api/responder", methods=["POST"])
def api_responder():
    return responder_conversa()

