from flask import Blueprint, render_template
from controllers.painel_controller import (
    listar_conversas,
    obter_conversa,
    responder_conversa
)

# Blueprint do painel
painel_routes = Blueprint(
    "painel_routes",
    __name__,
    url_prefix="/painel"
)

# =========================
# Interface (NOVO PAINEL)
# =========================
@painel_routes.route("/")
def painel_view():
    return render_template("whatsapp.html")

# =========================
# API do painel
# =========================
@painel_routes.route("/api/conversas")
def api_conversas():
    return listar_conversas()

@painel_routes.route("/api/conversa/<int:conversa_id>")
def api_conversa(conversa_id):
    return obter_conversa(conversa_id)

@painel_routes.route("/api/responder", methods=["POST"])
def api_responder():
    return responder_conversa()
