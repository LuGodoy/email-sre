import os
import mailtrap as mt
from dotenv import load_dotenv

load_dotenv()

def processar_e_enviar_alerta_sre(lista_dados):
    if not lista_dados:
        return

    email_destino = "support_empresa@gmail.com"
    assunto = f"[ALERTA SRE] {len(lista_dados)} Feedback(s) Negativo(s) Detectado(s)"

    itens = ""
    for i, dados in enumerate(lista_dados, 1):
        itens += (
            f"{i}. Autor: {dados.get('author', 'Desconhecido')}\n"
            f"   Canal: {dados.get('canal', '')}\n"
            f"   Data/Hora: {dados.get('timestamp', '')}\n"
            f"   Mensagem: \"{dados.get('content', '')}\"\n"
            f"   Link: {dados.get('link', '')}\n\n"
        )

    corpo = f"""Olá Equipe SRE,

{len(lista_dados)} feedback(s) com sentimento NEGATIVO foram detectados no Discord:

{itens}Por favor, verifiquem a situação e tomem as providências necessárias.

Atenciosamente,
Sistema de Monitoramento Automático
"""

    API_TOKEN = os.getenv("MAILTRAP_API_TOKEN")
    if not API_TOKEN:
        print("  ⚠️ Erro: A variável MAILTRAP_API_TOKEN não foi encontrada no .env!")
        return

    mail = mt.Mail(
        sender=mt.Address(email="monitor-discord@suaempresa.com", name="Monitor Discord"),
        to=[mt.Address(email=email_destino)],
        subject=assunto,
        text=corpo,
        category="Alerta SRE Discord",
    )

    try:
        client = mt.MailtrapClient(token=API_TOKEN, sandbox=True, inbox_id=4968839)
        client.send(mail)
        print(f"  🚨 [ALERTA ENVIADO] E-mail com {len(lista_dados)} mensagem(ns) negativa(s) enviado para o Mailtrap!")
    except Exception as e:
        print(f"  ❌ Falha ao enviar e-mail pelo Mailtrap: {e}")
