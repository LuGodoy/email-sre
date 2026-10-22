import os
import requests
from dotenv import load_dotenv
from server import publicar_no_instagram

load_dotenv()

def obter_url_ngrok_automatica():
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        dados = response.json()

        for tunel in dados.get("tunnels", []):
            if tunel.get("proto") == "https":
                return tunel.get("public_url")
    except Exception as e:
        print(f"⚠️ Não foi possível detetar o ngrok automaticamente: {e}")

    return None

if __name__ == "__main__":
    print("A detetar a URL do ngrok automaticamente...")
    NGROK_URL = obter_url_ngrok_automatica()

    if NGROK_URL:
        print(f"🔗 URL encontrada: {NGROK_URL}")
        publicar_no_instagram(NGROK_URL)
    else:
        print("❌ Erro: O ngrok não está a correr ou a porta 4040 não respondeu. Inicie o ngrok no terminal primeiro!")
