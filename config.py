import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"

COMPANY_NAME = "Carinfo.app"
COMPANY_CONTEXT = """
Carinfo.app is a digital platform that generates insurance leads for vehicles (cars and two-wheelers).
- Leads are transferred to partners: Policybazaar and Acko for policy conversion.
- Primary lead source: Organic channels (Google SEO, content blogs, YouTube).
- Secondary: CRM retargeting (email, WhatsApp, SMS campaigns).
- Target markets: Pan-India, focus on metro and tier-2 cities.
- Policy types offered: Comprehensive and Third Party.
"""

DEPARTMENTS = ["Sales", "Marketing", "Product", "Tech"]

LEADS_FILE = "data/leads.csv"
BOOKINGS_FILE = "data/bookings.csv"
REPORTS_DIR = "reports"
