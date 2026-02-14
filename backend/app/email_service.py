"""
Email service pro odesílání notifikací
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from .email_config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_FROM,
    SMTP_FROM_NAME,
    FRONTEND_URL,
)

logger = logging.getLogger(__name__)


class EmailService:
    """Service pro odesílání emailů"""

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """
        Odešle email

        Args:
            to_email: Email příjemce
            subject: Předmět emailu
            html_body: HTML tělo emailu
            text_body: Textová verze emailu (volitelné)

        Returns:
            True pokud se email podařilo odeslat, jinak False
        """
        try:
            # Vytvoření zprávy
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM}>"
            msg["To"] = to_email

            # Přidání textové verze
            if text_body:
                part1 = MIMEText(text_body, "plain", "utf-8")
                msg.attach(part1)

            # Přidání HTML verze
            part2 = MIMEText(html_body, "html", "utf-8")
            msg.attach(part2)

            # Odeslání emailu
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Email odeslán na {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Chyba při odesílání emailu na {to_email}: {str(e)}")
            return False


# ==========================================
# EMAIL TEMPLATES
# ==========================================


def send_audit_assignment_email(
    to_email: str,
    auditor_name: str,
    line_name: str,
    category_name: str,
    deadline: str,
    assignment_id: int,
) -> bool:
    """Odešle email o přidělení auditu"""

    subject = f"Nový audit: {line_name} - {category_name}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #2563eb;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9fafb;
                padding: 30px;
                border: 1px solid #e5e7eb;
            }}
            .info-box {{
                background-color: white;
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid #2563eb;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 Nový audit byl přidělen</h1>
            </div>
            <div class="content">
                <p>Dobrý den <strong>{auditor_name}</strong>,</p>
                
                <p>byl Vám přidělen nový audit k provedení:</p>
                
                <div class="info-box">
                    <p><strong>📍 Linka:</strong> {line_name}</p>
                    <p><strong>📋 Kategorie:</strong> {category_name}</p>
                    <p><strong>📅 Termín:</strong> {deadline}</p>
                </div>
                
                <p>Prosím, proveďte audit do stanoveného termínu.</p>
                
                <a href="{FRONTEND_URL}/assignments/{assignment_id}" class="button">
                    Zobrazit detail auditu
                </a>
                
                <div class="footer">
                    <p>Tento email byl odeslán automaticky z LPA systému.</p>
                    <p>Pro přístup do systému použijte: <a href="{FRONTEND_URL}">{FRONTEND_URL}</a></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Nový audit byl přidělen
    
    Dobrý den {auditor_name},
    
    byl Vám přidělen nový audit k provedení:
    
    Linka: {line_name}
    Kategorie: {category_name}
    Termín: {deadline}
    
    Prosím, proveďte audit do stanoveného termínu.
    
    Pro zobrazení detailu přejděte na: {FRONTEND_URL}/assignments/{assignment_id}
    
    ---
    Tento email byl odeslán automaticky z LPA systému.
    """

    return EmailService.send_email(to_email, subject, html_body, text_body)


def send_issue_assignment_email(
    to_email: str,
    solver_name: str,
    issue_description: str,
    line_name: str,
    category_name: str,
    severity: str,
    deadline: str,
    issue_id: int,
) -> bool:
    """Odešle email o přidělení neshody k řešení"""

    severity_labels = {
        "low": "🟢 Nízká",
        "medium": "🟡 Střední",
        "high": "🔴 Vysoká",
    }
    severity_text = severity_labels.get(severity, severity)

    subject = f"Neshoda k řešení: {line_name}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #dc2626;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9fafb;
                padding: 30px;
                border: 1px solid #e5e7eb;
            }}
            .info-box {{
                background-color: white;
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid #dc2626;
            }}
            .issue-description {{
                background-color: #fef2f2;
                padding: 15px;
                margin: 15px 0;
                border-radius: 5px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #dc2626;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚠️ Neshoda vyžaduje řešení</h1>
            </div>
            <div class="content">
                <p>Dobrý den <strong>{solver_name}</strong>,</p>
                
                <p>byla Vám přidělena neshoda k řešení:</p>
                
                <div class="info-box">
                    <p><strong>📍 Linka:</strong> {line_name}</p>
                    <p><strong>📋 Kategorie:</strong> {category_name}</p>
                    <p><strong>⚡ Závažnost:</strong> {severity_text}</p>
                    <p><strong>📅 Termín řešení:</strong> {deadline}</p>
                </div>
                
                <div class="issue-description">
                    <strong>Popis neshody:</strong>
                    <p>{issue_description}</p>
                </div>
                
                <p>Prosím, řešte tuto neshodu do stanoveného termínu.</p>
                
                <a href="{FRONTEND_URL}/neshody/{issue_id}" class="button">
                    Zobrazit detail neshody
                </a>
                
                <div class="footer">
                    <p>Tento email byl odeslán automaticky z LPA systému.</p>
                    <p>Pro přístup do systému použijte: <a href="{FRONTEND_URL}">{FRONTEND_URL}</a></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Neshoda vyžaduje řešení
    
    Dobrý den {solver_name},
    
    byla Vám přidělena neshoda k řešení:
    
    Linka: {line_name}
    Kategorie: {category_name}
    Závažnost: {severity_text}
    Termín řešení: {deadline}
    
    Popis neshody:
    {issue_description}
    
    Prosím, řešte tuto neshodu do stanoveného termínu.
    
    Pro zobrazení detailu přejděte na: {FRONTEND_URL}/neshody/{issue_id}
    
    ---
    Tento email byl odeslán automaticky z LPA systému.
    """

    return EmailService.send_email(to_email, subject, html_body, text_body)


def send_password_reset_email(
    to_email: str,
    user_name: str,
    new_password: str,
    is_new_user: bool = False,
) -> bool:
    """Odešle email s novým heslem"""

    if is_new_user:
        subject = "Vítejte v LPA systému - Přístupové údaje"
        greeting = f"Vítejte v LPA systému, <strong>{user_name}</strong>!"
        intro = (
            "byl Vám vytvořen účet v LPA systému. Níže naleznete Vaše přístupové údaje:"
        )
    else:
        subject = "LPA systém - Nové heslo"
        greeting = f"Dobrý den <strong>{user_name}</strong>,"
        intro = "Vaše heslo bylo resetováno. Níže naleznete nové přístupové údaje:"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #059669;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9fafb;
                padding: 30px;
                border: 1px solid #e5e7eb;
            }}
            .credentials-box {{
                background-color: white;
                padding: 20px;
                margin: 20px 0;
                border: 2px solid #059669;
                border-radius: 5px;
            }}
            .credential-item {{
                margin: 10px 0;
            }}
            .credential-label {{
                color: #6b7280;
                font-size: 12px;
                text-transform: uppercase;
            }}
            .credential-value {{
                font-size: 18px;
                font-weight: bold;
                color: #059669;
                font-family: monospace;
            }}
            .warning {{
                background-color: #fef3c7;
                padding: 15px;
                margin: 20px 0;
                border-left: 4px solid #f59e0b;
                border-radius: 3px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #059669;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Přístupové údaje</h1>
            </div>
            <div class="content">
                <p>{greeting}</p>
                
                <p>{intro}</p>
                
                <div class="credentials-box">
                    <div class="credential-item">
                        <div class="credential-label">Email</div>
                        <div class="credential-value">{to_email}</div>
                    </div>
                    <div class="credential-item">
                        <div class="credential-label">Heslo</div>
                        <div class="credential-value">{new_password}</div>
                    </div>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Důležité:</strong> Doporučujeme Vám po prvním přihlášení změnit heslo na vlastní.
                </div>
                
                <a href="{FRONTEND_URL}/login" class="button">
                    Přihlásit se do systému
                </a>
                
                <div class="footer">
                    <p>Tento email byl odeslán automaticky z LPA systému.</p>
                    <p>Pokud jste o tento email nežádali, kontaktujte prosím administrátora.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    {"Vítejte v LPA systému" if is_new_user else "Nové heslo"}
    
    Dobrý den {user_name},
    
    {intro}
    
    Email: {to_email}
    Heslo: {new_password}
    
    DŮLEŽITÉ: Doporučujeme Vám po prvním přihlášení změnit heslo na vlastní.
    
    Pro přihlášení přejděte na: {FRONTEND_URL}/login
    
    ---
    Tento email byl odeslán automaticky z LPA systému.
    Pokud jste o tento email nežádali, kontaktujte prosím administrátora.
    """

    return EmailService.send_email(to_email, subject, html_body, text_body)
