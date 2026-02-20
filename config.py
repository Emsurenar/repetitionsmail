"""
Configuration for Repetitionsmail.
Loads secrets from environment variables (set in .env locally, GitHub Actions secrets in CI).
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env if present (local dev)
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Gmail
GMAIL_SENDER    = os.getenv('GMAIL_SENDER', 'emre.b.sunar@gmail.com')
GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', '')
GMAIL_RECIPIENT = os.getenv('GMAIL_RECIPIENT', 'emre.b.sunar@gmail.com')

# LLM
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
OPENAI_API_KEY    = os.getenv('OPENAI_API_KEY', 'dummy')  # CrewAI requires it

# Paths
PROJECT_ROOT = Path(__file__).parent
DATABASE_PATH = PROJECT_ROOT / 'topics.db'
TEMPLATE_DIR  = PROJECT_ROOT / 'templates'
LOG_DIR       = PROJECT_ROOT / 'logs'

LOG_DIR.mkdir(exist_ok=True)

# LLM model
LLM_MODEL = "anthropic/claude-opus-4-6"


def validate_config() -> bool:
    required = {
        'ANTHROPIC_API_KEY': ANTHROPIC_API_KEY,
        'GMAIL_SENDER':      GMAIL_SENDER,
        'GMAIL_APP_PASSWORD':GMAIL_APP_PASSWORD,
        'GMAIL_RECIPIENT':   GMAIL_RECIPIENT,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        logger.error(f"Missing config: {', '.join(missing)}")
        return False
    return True


if __name__ == '__main__':
    print("Config status:")
    print(f"  Anthropic key : {'✓' if ANTHROPIC_API_KEY else '✗'}")
    print(f"  Gmail sender  : {GMAIL_SENDER}")
    print(f"  Gmail password: {'✓' if GMAIL_APP_PASSWORD else '✗'}")
    print(f"  Recipient     : {GMAIL_RECIPIENT}")
    print()
    print("✅ OK" if validate_config() else "❌ Missing fields")
