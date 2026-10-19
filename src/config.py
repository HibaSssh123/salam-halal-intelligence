from pathlib import Path

APP_NAME = "SALAM HALAL INTELLIGENCE"
APP_SUBTITLE = "Plateforme intelligente de suivi industriel et d'aide à la décision"
APP_NOTICE = "PROTOTYPE ACADÉMIQUE — DONNÉES SIMULÉES"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "salam_halal_intelligence.db"

BATCH_STATUSES = ["Planifié", "En production", "Terminé", "Bloqué", "Expiré"]
INCOMING_TYPES = {"entrée", "production"}
OUTGOING_TYPES = {"sortie"}
