import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.environ["IG_ACCESS_TOKEN"]
version = os.environ["IG_GRAPH_VERSION"]

url = f"https://graph.instagram.com/{version}/me"

response = requests.get(
    url,
    params={
        "fields": "user_id,username,account_type",
        "access_token": token,
    },
    timeout=30,
)

data = response.json()

if not response.ok:
    print("Falha na API:", data.get("error", {}).get("message", data))
    raise SystemExit(1)

print("Conexão realizada!")
print("Usuário:", data.get("username"))
print("ID retornado:", data.get("user_id"))
print("Tipo de conta:", data.get("account_type"))
