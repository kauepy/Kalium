from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"

load_dotenv(ENV_PATH, override=True)


import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


MODEL = "openrouter/free"

BASE_URL = "https://openrouter.ai/api/v1"

TEMPERATURE = 0.3
MAX_TOKENS = 1000
TIMEOUT = 60