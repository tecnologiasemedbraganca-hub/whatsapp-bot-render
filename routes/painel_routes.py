from flask import Blueprint, render_template

painel = Blueprint("painel", __name__)

@painel.route("/painel")
def painel_view():
    return render_template("painel.html")
