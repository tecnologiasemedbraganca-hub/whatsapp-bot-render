import requests
from config import ACCESS_TOKEN, PHONE_NUMBER_ID

def enviar_mensagem_whatsapp(numero, texto):

    url = f"https://graph.facebook.com/v24.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "text": {"body": texto}
    }

    requests.post(url, headers=headers, json=payload)
