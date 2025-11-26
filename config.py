import os

ZAKUPKI_TOKEN = os.getenv('ZAKUPKI_TOKEN', '')

AI_URL = os.getenv('AI_URL', '')
AI_API_KEY = os.getenv('AI_API_KEY', '')
MODEL = os.getenv('MODEL', '')
MAX_TOKENS = 127000
COST_INPUT_TOKENS = 0.00015
COST_OUTPUT_TOKENS = 0.0006

DB_NAME = os.path.join(os.path.dirname(__file__), 'db/db/tender_t.db')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN = int(os.getenv('ADMIN', ''))
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', '')
