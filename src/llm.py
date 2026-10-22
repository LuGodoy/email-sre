"""Geração de posts a partir de mensagens positivas do Discord usando Groq."""

import json
import os
from datetime import datetime, timezone

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

POSTS_PENDENTES = os.path.join(os.path.dirname(__file__), "..", "data", "pending_posts.json")

PROMPT_SISTEMA = (
    "Você é um redator especialista em comunicação corporativa. "
    "Receberá uma mensagem positiva de um usuário e deve gerar um post para LinkedIn. "
    "Responda SOMENTE com JSON válido, sem texto antes ou depois, neste formato exato:\n"
    '{"titulo": "até 60 caracteres", "post": "post de até 120 palavras, português do Brasil, sem emoji, sem hashtag"}'
)


def _cliente() -> Groq:
    chave = os.getenv("GROQ_API_KEY", "")
    if not chave:
        raise RuntimeError("GROQ_API_KEY não encontrada no .env")
    return Groq(api_key=chave)


def gerar_post(autor: str, canal: str, mensagem: str) -> dict:
    """Gera um post LinkedIn a partir de uma mensagem positiva e salva em posts_pendentes.json."""
    resposta = _cliente().chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": mensagem},
        ],
        temperature=0.6,
        max_tokens=300,
    )

    texto = resposta.choices[0].message.content or ""

    try:
        conteudo = json.loads(texto)
    except json.JSONDecodeError:
        conteudo = {"titulo": "Post gerado automaticamente", "post": texto.strip()}

    post = {
        "id": f"post_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "autor": autor,
        "canal": canal,
        "mensagem_original": mensagem,
        "titulo": conteudo.get("titulo", ""),
        "post": conteudo.get("post", ""),
        "status": "pendente",
        "criado_em": datetime.now(timezone.utc).isoformat(),
    }

    _salvar(post)
    return post


def _salvar(post: dict) -> None:
    pendentes = _carregar(POSTS_PENDENTES)
    pendentes.append(post)
    with open(POSTS_PENDENTES, "w", encoding="utf-8") as f:
        json.dump(pendentes, f, ensure_ascii=False, indent=2)


def _carregar(caminho: str) -> list:
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []
