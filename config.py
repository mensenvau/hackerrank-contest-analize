import os
import sys
from dotenv import load_dotenv

load_dotenv()

class Config:
    CONTEST_SLUG = os.getenv("CONTEST_SLUG")
    HACKERRANK_COOKIE = os.getenv("HACKERRANK_COOKIE")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    REQUEST_DELAY_SECONDS = float(os.getenv("REQUEST_DELAY_SECONDS", 2.0))
    OUTPUT_DIR = "results"

    @classmethod
    def get_headers(cls):
        return {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36",
            "Cookie": cls.HACKERRANK_COOKIE,
            "Accept": "application/json"
        }

    @classmethod
    def validate(cls):
        errors = []
        if not cls.CONTEST_SLUG: errors.append("CONTEST_SLUG missing")
        if not cls.HACKERRANK_COOKIE: errors.append("HACKERRANK_COOKIE missing")
        
        if errors:
            print(f"❌ Config Errors: {', '.join(errors)}")
            sys.exit(1)
