import os
import certifi
import discord
from dotenv import load_dotenv
from groq import Groq

# Configuração SSL (para macOS)
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

load_dotenv()

# Importa a função de e-mail do seu arquivo envio_email.py
from envio_email import processar_e_enviar_alerta_sre

# Inicializa o cliente Groq e o Token do Discord
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

def analisar_sentimento_groq(mensagem: str) -> str:
    """Analisa o sentimento de uma mensagem usando a API da Groq."""
    prompt_sistema = (
        "Você é um especialista em análise de sentimentos e suporte técnico para equipes de SRE. "
        "Analise a mensagem considerando gírias, emojis, ironias e relatos de falhas/bugs/problemas técnicos. "
        "Se a mensagem contiver qualquer reclamação, erro de sistema ou falha (mesmo que comece com uma saudação educada), "
        "ela DEVE ser classificada como Negativo. "
        "Responda estritamente no formato:\n"
        "Sentimento: [Positivo / Negativo / Neutro]\n"
        "Justificativa: [Explicação curta em uma linha]"
    )

    try:
        chat_completion = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": mensagem},
            ],
            temperature=0.1,
            max_tokens=150,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Sentimento: Neutro\nErro ao chamar a API da Groq: {e}"

# Configuração do Bot do Discord
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'🤖 Bot conectado e a escutar em tempo real como: {client.user}\n')

@client.event
async def on_message(mensagem):
    # Ignora mensagens enviadas pelo próprio bot ou mensagens vazias
    if mensagem.author.bot or not mensagem.content.strip():
        return

    print(f"📩 Nova mensagem recebida em #{mensagem.channel.name} de [{mensagem.author.display_name}]: {mensagem.content}")

    # Analisa o sentimento com a Groq
    resposta_groq = analisar_sentimento_groq(mensagem.content)
    print(f"  {resposta_groq}")
    print("-" * 40)

    # Extrai o sentimento
    sentimento_texto = "NEU"
    if "Negativo" in resposta_groq:
        sentimento_texto = "NEG"
    elif "Positivo" in resposta_groq:
        sentimento_texto = "POS"

    # Se a mensagem for classificada como NEGATIVA, dispara o e-mail de imediato
    if sentimento_texto == "NEG":
        dados_alerta = [{
            "timestamp": mensagem.created_at.isoformat(),
            "author": mensagem.author.display_name,
            "content": mensagem.content,
            "sentimento": sentimento_texto,
            "canal": f"#{mensagem.channel.name}",
            "link": f"https://discord.com/channels/{mensagem.guild.id}/{mensagem.channel.id}/{mensagem.id}"
        }]
        
        # Chama a função que envia para o Mailtrap[cite: 4]
        processar_e_enviar_alerta_sre(dados_alerta)

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)