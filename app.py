from flask import Flask
from routes.routes import routes
from routes.painel_routes import painel_routes
from database.schema import criar_tabelas
from config import PORT

app = Flask(__name__)

# Rotas principais
app.register_blueprint(routes)          # webhook / api
app.register_blueprint(painel_routes)   # painel web

# Health check do Render
@app.route("/")
def home():
    return "Bot WhatsApp Caeté rodando 🚀"

if __name__ == "__main__":
    criar_tabelas()
    app.run(host="0.0.0.0", port=PORT)
