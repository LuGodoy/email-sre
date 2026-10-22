# 🤖 SRE Monitor — Automação de Feedback com IA

Sistema que monitora mensagens em tempo real no Discord, analisa o sentimento com IA e executa ações automáticas: dispara alertas por e-mail para feedbacks negativos e gera posts para o Instagram a partir de feedbacks positivos, com moderação humana antes da publicação.

---

## 🏗️ Arquitetura

```
Discord (mensagens em tempo real)
          │
          ▼
   orquestrador.py
   (Bot Discord + Groq IA)
          │
          ├── Sentimento NEGATIVO
          │         │
          │         ▼
          │   envio_email.py
          │   Alerta SRE via Mailtrap
          │   → e-mail para equipe
          │
          └── Sentimento POSITIVO
                    │
                    ▼
               llm.py (Groq)
          Gera post e salva como pendente
                    │
                    ▼
             app.py (Streamlit)
          Painel de moderação humana
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     ✅ Aprovar          ❌ Reprovar
          │                   │
          ▼                   ▼
    servidor.py         Arquivado em
    Flask + ngrok       posts_moderados.json
    Publica no Instagram
```

---

## 📁 Estrutura do Projeto

```
email-sre/
├── src/
│   ├── orchestrator.py       # Bot Discord + análise de sentimento
│   ├── email_sender.py       # Envio de alertas via Mailtrap
│   ├── llm.py                # Geração de posts com Groq
│   └── server.py             # Servidor Flask + publicação no Instagram
├── data/
│   ├── pending_posts.json    # Posts aguardando moderação
│   └── moderated_posts.json  # Histórico de posts aprovados/reprovados
├── image/
│   └── *.png                 # Imagem usada nos posts do Instagram
├── app.py                    # Painel de moderação (Streamlit)
├── requirements.txt
├── .env                      # Variáveis de ambiente (não versionado)
├── .env.exemplo              # Modelo do .env
└── Describe.md               # Guia para obter as chaves de API
```

---

## 🔧 Pré-requisitos

- Python 3.10+
- Conta no [Discord Developer Portal](https://discord.com/developers/applications)
- Conta no [Mailtrap](https://mailtrap.io)
- Conta no [Meta for Developers](https://developers.facebook.com) com Instagram Profissional
- Conta no [Groq Console](https://console.groq.com)
- [ngrok](https://ngrok.com) instalado

---

## 🚀 Como replicar localmente

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd email-sre
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas chaves:

```bash
cp .env.exemplo .env
```

Edite o `.env`:

```env
GROQ_API_KEY=sua_chave_aqui

DISCORD_TOKEN=seu_token_aqui
CANAL_ID=seu_canal_id_aqui

MAILTRAP_API_TOKEN=seu_token_aqui

INSTAGRAM_USER_ID=seu_user_id_aqui
META_ACCESS_TOKEN=seu_token_aqui
GRAPH_VERSION=v26.0

NGROK_AUTH_TOKEN=seu_token_aqui
```

> Consulte o `Describe.md` para instruções detalhadas de como obter cada chave.

### 4. Configure o ngrok

```bash
ngrok config add-authtoken SEU_NGROK_TOKEN
```

---

## ▶️ Como executar

Abra **3 terminais** na raiz do projeto:

**Terminal 1 — Orquestrador (Bot Discord + alertas de e-mail):**
```bash
cd src
python3 orchestrator.py
```

**Terminal 2 — Painel de moderação (posts do Instagram):**
```bash
streamlit run app.py
```

**Terminal 3 — Túnel ngrok (necessário para publicar no Instagram):**
```bash
ngrok http 5001
```

---

## 🔄 Fluxo de uso

### Mensagem negativa no Discord
1. Usuário envia mensagem no Discord
2. O orquestrador detecta sentimento negativo via Groq
3. E-mail de alerta é enviado automaticamente para a equipe SRE via Mailtrap

### Mensagem positiva no Discord
1. Usuário envia mensagem no Discord
2. O orquestrador detecta sentimento positivo via Groq
3. Um post é gerado automaticamente com IA e salvo como pendente
4. O moderador abre o painel (`http://localhost:8501`) e revisa o post
5. Ao aprovar, o post é publicado automaticamente no Instagram

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Uso |
|---|---|
| [Discord.py](https://discordpy.readthedocs.io) | Leitura de mensagens em tempo real |
| [Groq](https://console.groq.com) + Qwen 3 | Análise de sentimento e geração de posts |
| [Mailtrap](https://mailtrap.io) | Envio de e-mails de alerta |
| [Meta Graph API](https://developers.facebook.com/docs/instagram-api) | Publicação no Instagram |
| [Flask](https://flask.palletsprojects.com) | Servidor local para servir imagens |
| [ngrok](https://ngrok.com) | Túnel HTTPS para expor o servidor local |
| [Streamlit](https://streamlit.io) | Painel de moderação de posts |

---

## ⚠️ Observações

- O `META_ACCESS_TOKEN` expira em ~60 dias. Consulte o `Describe.md` para renová-lo.
- O ngrok precisa estar rodando antes de aprovar um post no painel.
- O `MAILTRAP_API_TOKEN` usa o modo sandbox por padrão — os e-mails ficam na inbox do Mailtrap, não chegam em caixas reais.
