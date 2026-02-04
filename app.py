from flask import Flask
from routes.routes import routes
from routes.painel_routes import painel
from database.schema import criar_tabelas
from config import PORT

app = Flask(__name__)

# registra as rotas (webhook)
app.register_blueprint(routes)
app.register_blueprint(painel)   # painel web 👈

# rota raiz (health check do Render)
@app.route("/")
def home():
    return "Bot WhatsApp Caeté rodando 🚀"

if __name__ == "__main__":

    # cria/ajusta tabelas no startup
    criar_tabelas()

    # inicia servidor na porta do Render
    app.run(host="0.0.0.0", port=PORT)


