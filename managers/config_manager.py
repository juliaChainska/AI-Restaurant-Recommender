import os
from dotenv import load_dotenv

load_dotenv()

def get_config(key: str, default=None):
    return os.getenv(key, default)

