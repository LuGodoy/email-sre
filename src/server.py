import os
import time
import requests
from pathlib import Path
from flask import Flask, abort, send_file
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
IG_USER_ID = os.getenv("INSTAGRAM_USER_ID")
GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v19.0")

IMAGE_PATH = Path(__file__).parent.parent / "image" / "Pequenos Hábitos, Grandes Conquistas.png"
CAPTION = "Criamos o futuro do seu negócio com tecnologia inteligente. 🚀💻 #ONE #Software #Python"

@app.get("/")
def home():
    return "Servidor Flask para automação do Instagram da ONE está a funcionar! Acesse /post.png para ver a imagem.", 200

@app.get("/post.png")
def servir_imagem():
    if not IMAGE_PATH.is_file():
        abort(404, description="Imagem não encontrada no caminho especificado")
    return send_file(IMAGE_PATH, mimetype="image/png", conditional=True)


def publicar_no_instagram(ngrok_url):
    image_url = f"{ngrok_url}/post.png"
    print("\nPasso 1: Solicitando criação do container de mídia na Meta...")

    url_container = f"https://graph.facebook.com/{GRAPH_VERSION}/{IG_USER_ID}/media"
    payload_container = {
        'image_url': image_url,
        'caption': CAPTION,
        'access_token': ACCESS_TOKEN
    }

    response = requests.post(url_container, data=payload_container)
    resultado = response.json()

    if 'id' in resultado:
        creation_id = resultado['id']
        print(f"Container criado com sucesso! ID: {creation_id}")

        time.sleep(3)

        print("Passo 2: Publicando a mídia no feed do Instagram...")
        url_publish = f"https://graph.facebook.com/{GRAPH_VERSION}/{IG_USER_ID}/media_publish"
        payload_publish = {
            'creation_id': creation_id,
            'access_token': ACCESS_TOKEN
        }

        response_pub = requests.post(url_publish, data=payload_publish)
        resultado_pub = response_pub.json()

        if 'id' in resultado_pub:
            print(f"🎉 Post publicado com sucesso! ID final da mídia: {resultado_pub['id']}")
        else:
            print(f"❌ Erro ao publicar o container: {resultado_pub}")
    else:
        print(f"❌ Erro ao criar o container de mídia: {resultado}")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
