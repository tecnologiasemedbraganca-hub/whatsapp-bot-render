from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot WhatsApp rodando 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(data)  # depois vamos tratar a mensagem
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

