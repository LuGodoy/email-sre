import os
import mailtrap as mt
from dotenv import load_dotenv

load_dotenv()

def processar_e_enviar_alerta_sre(lista_dados):
    if not lista_dados:
        return

    email_destino = "support_empresa@gmail.com"
    assunto = f"🚨 [ALERTA SRE] {len(lista_dados)} Feedback(s) Negativo(s) Detectado(s)"

    # Monta as linhas da tabela em HTML
    linhas_tabela = ""
    for i, dados in enumerate(lista_dados, 1):
        link_discord = dados.get('link', '#')
        linhas_tabela += f"""
        <tr style="border-bottom: 1px solid #e0e0e0;">
            <td style="padding: 10px; text-align: center; font-weight: bold;">{i}</td>
            <td style="padding: 10px;"><b>{dados.get('author', 'Desconhecido')}</b></td>
            <td style="padding: 10px; color: #555;">{dados.get('canal', '')}</td>
            <td style="padding: 10px; font-size: 12px; color: #777;">{dados.get('timestamp', '')}</td>
            <td style="padding: 10px; color: #d9534f; font-style: italic;">"{dados.get('content', '')}"</td>
            <td style="padding: 10px; text-align: center;">
                <a href="{link_discord}" target="_blank" style="background-color: #5865F2; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 12px;">Ver no Discord</a>
            </td>
        </tr>
        """

    # Corpo em HTML formatado com CSS inline
    corpo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px;">
        <div style="max-width: 800px; background-color: #ffffff; margin: 0 auto; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="border-bottom: 2px solid #d9534f; padding-bottom: 10px; margin-bottom: 20px;">
                <h2 style="color: #d9534f; margin: 0;">🚨 Alerta de Monitoramento SRE</h2>
                <p style="color: #666; margin-top: 5px;">Detecção automática de feedbacks negativos no Discord</p>
            </div>
            
            <p style="font-size: 15px; color: #333;">Olá Equipe SRE,</p>
            <p style="font-size: 14px; color: #555;">
                Foram identificados <b>{len(lista_dados)}</b> feedback(s) com sentimento 
                <span style="background-color: #f8d7da; color: #721c24; padding: 2px 6px; border-radius: 4px; font-weight: bold;">NEGATIVO</span>.
            </p>

            <table style="width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px;">
                <thead>
                    <tr style="background-color: #2c3e50; color: #ffffff;">
                        <th style="padding: 10px;">#</th>
                        <th style="padding: 10px; text-align: left;">Autor</th>
                        <th style="padding: 10px; text-align: left;">Canal</th>
                        <th style="padding: 10px; text-align: left;">Data/Hora</th>
                        <th style="padding: 10px; text-align: left;">Mensagem</th>
                        <th style="padding: 10px; text-align: center;">Ação</th>
                    </tr>
                </thead>
                <tbody>
                    {linhas_tabela}
                </tbody>
            </table>

            <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; font-size: 12px; color: #888;">
                <p>Por favor, verifiquem a situação e tomem as providências necessárias.</p>
                <p><b>Sistema de Monitoramento Automático SRE</b></p>
            </div>
        </div>
    </body>
    </html>
    """

    # Versão em texto simples como fallback (boa prática de e-mail)
    corpo_texto = f"Olá Equipe SRE,\n\n{len(lista_dados)} feedback(s) com sentimento NEGATIVO foram detectados no Discord.\nPor favor, verifiquem o painel."

    API_TOKEN = os.getenv("MAILTRAP_API_TOKEN")
    if not API_TOKEN:
        print("  ⚠️ Erro: A variável MAILTRAP_API_TOKEN não foi encontrada no .env!")
        return

    # Passamos tanto 'text' quanto 'html' no construtor do mt.Mail
    mail = mt.Mail(
        sender=mt.Address(email="monitor-discord@suaempresa.com", name="Monitor Discord"),
        to=[mt.Address(email=email_destino)],
        subject=assunto,
        text=corpo_texto,
        html=corpo_html,
        category="Alerta SRE Discord",
    )

    try:
        client = mt.MailtrapClient(token=API_TOKEN, sandbox=True, inbox_id=4968839)
        client.send(mail)
        print(f"  🚨 [ALERTA ENVIADO] E-mail HTML com {len(lista_dados)} mensagem(ns) negativa(s) enviado para o Mailtrap!")
    except Exception as e:
        print(f"  ❌ Falha ao enviar e-mail pelo Mailtrap: {e}")