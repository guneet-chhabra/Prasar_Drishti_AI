"""Central application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()

ROOT = os.path.dirname(os.path.abspath(__file__))


class Config:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/sports_ai",
    )

    NEWSONAIR_BASE_URL = os.getenv("NEWSONAIR_BASE_URL", "https://newsonair.gov.in")
    SCRAPE_DELAY = float(os.getenv("SCRAPE_DELAY", "1.5"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", "1000"))

    DATA_DIR = os.path.join(ROOT, "data")
    RAW_DIR = os.path.join(DATA_DIR, "raw")
    PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
    LABELLED_DIR = os.path.join(DATA_DIR, "labelled")

    MODELS_DIR = os.path.join(ROOT, "models")
    SENTIMENT_MODEL_DIR = os.path.join(MODELS_DIR, "sentiment")
    SPORTS_MODEL_DIR = os.path.join(MODELS_DIR, "sports")
    FIFA_MODEL_DIR = os.path.join(MODELS_DIR, "fifa")

    BERT_MODEL_NAME = os.getenv("BERT_MODEL_NAME", "distilbert-base-uncased")
    MAX_SEQ_LENGTH = int(os.getenv("MAX_SEQ_LENGTH", "512"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "16"))
    NUM_EPOCHS = int(os.getenv("NUM_EPOCHS", "3"))
    LEARNING_RATE = float(os.getenv("LEARNING_RATE", "2e-5"))

    SENTIMENT_LABELS = {0: "Anti-Govt", 1: "Neutral", 2: "Pro-Govt"}
    NUM_LABELS = 3

    SDI_SENTIMENT_WEIGHT = 0.30
    SDI_MEDAL_WEIGHT = 0.40
    SDI_FUNDING_WEIGHT = 0.30

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    FRONTEND_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000/api")
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8050"))

    @classmethod
    def create_dirs(cls) -> None:
        for directory in [
            cls.RAW_DIR,
            cls.PROCESSED_DIR,
            cls.LABELLED_DIR,
            cls.SENTIMENT_MODEL_DIR,
            cls.SPORTS_MODEL_DIR,
            cls.FIFA_MODEL_DIR,
        ]:
            os.makedirs(directory, exist_ok=True)
