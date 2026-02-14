"""
Konfigurace pro odesílání emailů
"""

import os
from dotenv import load_dotenv

# Načtení .env souboru
load_dotenv()

# SMTP nastavení
SMTP_HOST = os.getenv("SMTP_HOST", "mailin.endora.cz")
SMTP_PORT = int(os.getenv("SMTP_PORT","587"))
SMTP_USER = os.getenv("SMTP_USER","info@safecompas.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD","Semi2583")
SMTP_FROM = os.getenv("SMTP_FROM","info@safecompas.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME","LPA ")

# URL frontendu pro odkazy v emailech
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
