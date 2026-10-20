import os
import certifi
import json
import discord
from dotenv import load_dotenv
from groq import Groq

# Configuração SSL (para macOS)
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

load_dotenv()

# Importa a função de e-mail que criamos anteriormente
from envio_email import processar_e_enviar_alerta_sre

# Inicializa o cliente Groq e o Token do Discord
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

ALERTAS_FILE = "alertas_enviados.json"

def carregar_alertas():
    if os.path.exists(ALERTAS_FILE):
        with open(ALERTAS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def salvar_alertas(ids: set):
    with open(ALERTAS_FILE, "w") as f:
        json.dump(list(ids), f)

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
            model="qwen/qwen3.8-27b", # Modelo robusto e atualizado na Groq
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
    global mensagens_alertadas
    mensagens_alertadas = carregar_alertas()
    print(f'Bot conectado como: {client.user}\n')
    
    if not client.guilds:
        print("O bot não está em nenhum servidor.")
        await client.close()
        return

    guild = client.guilds[0]
    print(f"==========================================")
    print(f" Analisando Servidor: {guild.name}")
    print(f"==========================================\n")

    novas_negativas = []

    for canal in guild.text_channels:
        print(f"------------------------------------------")
        print(f"📖 Canal: #{canal.name}")
        print(f"------------------------------------------")
        
        contador = {"POS": 0, "NEU": 0, "NEG": 0}
        total_mensagens = 0

        try:
            async for mensagem in canal.history(limit=50):
                if mensagem.author.bot or not mensagem.content.strip():
                    continue
                
                total_mensagens += 1
                
                # Obtém a resposta estruturada da Groq
                resposta_groq = analisar_sentimento_groq(mensagem.content)
                
                # Extrai o sentimento de forma simples da resposta da IA
                sentimento_texto = "NEU"
                if "Negativo" in resposta_groq:
                    sentimento_texto = "NEG"
                    contador["NEG"] += 1
                elif "Positivo" in resposta_groq:
                    sentimento_texto = "POS"
                    contador["POS"] += 1
                else:
                    contador["NEU"] += 1

                data_return = { 
                    "timestamp": mensagem.created_at.isoformat(),
                    "author": mensagem.author.display_name,
                    "content": mensagem.content,
                    "sentimento": sentimento_texto,
                    "link": f"https://discord.com/channels/{guild.id}/{canal.id}/{mensagem.id}"
                }
                
                print(f"  [{mensagem.author.display_name}]: {mensagem.content}")
                print(f"  {resposta_groq}")
                print("-" * 40)

                # Acumula mensagens negativas ainda não alertadas
                if sentimento_texto == "NEG" and str(mensagem.id) not in mensagens_alertadas:
                    data_return["canal"] = f"#{canal.name}"
                    novas_negativas.append(data_return)
                    mensagens_alertadas.add(str(mensagem.id))

            if total_mensagens == 0:
                print("  (Nenhuma mensagem encontrada neste canal)")
            else:
                print(f"\n  📊 Resumo do #{canal.name}: {total_mensagens} mensagens")
                print(f"  🟢 Positivas: {contador['POS']} | ⚪ Neutras: {contador['NEU']} | 🔴 Negativas: {contador['NEG']}")
            
            print("\n")

        except discord.errors.Forbidden:
            print(f"  ⚠️ Sem permissão para ler as mensagens do canal #{canal.name}.\n")
        except Exception as e:
            print(f"  ❌ Erro ao ler o canal #{canal.name}: {e}\n")

    # Envia um único e-mail com todas as mensagens negativas novas
    if novas_negativas:
        salvar_alertas(mensagens_alertadas)
        processar_e_enviar_alerta_sre(novas_negativas)

    await client.close()

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)