from flask import Flask
from routes.routes import routes
from database.schema import criar_tabelas
from config import PORT

app = Flask(__name__)

app.register_blueprint(routes)

@app.route("/")
def home():
    return "Bot WhatsApp Caeté rodando 🚀"

if __name__ == "__main__":

    criar_tabelas()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

