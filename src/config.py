import os
import json

# Root directories
WORKSPACE_DIR = r"c:\scratch"
RAW_DIR = r"C:\BoothIQ\data\raw"


# Specific data paths (DR1: Standardized Storage Mapping)
DIRS = {
    "eci_2025": os.path.join(RAW_DIR, "eci_2025"),
    "eci_2020": os.path.join(RAW_DIR, "eci_2020"),
    "candidate_affidavits": os.path.join(RAW_DIR, "candidate_affidavits"),
    "census": os.path.join(RAW_DIR, "census"),
    "schemes": os.path.join(RAW_DIR, "schemes"),
    "news": os.path.join(RAW_DIR, "news"),
    "spatial": os.path.join(RAW_DIR, "spatial"),
    "social_media": os.path.join(RAW_DIR, "social_media"),
    "caste_survey": os.path.join(RAW_DIR, "caste_survey"),
    "nfhs_5": os.path.join(RAW_DIR, "nfhs_5"),
    "electoral_roll": os.path.join(RAW_DIR, "electoral_roll"),
    "economic_indicators": os.path.join(RAW_DIR, "economic_indicators"),
    "infrastructure": os.path.join(RAW_DIR, "infrastructure"),
    "flood_vulnerability": os.path.join(RAW_DIR, "flood_vulnerability"),
    "latest": os.path.join(RAW_DIR, "latest"),
    "latest1": os.path.join(RAW_DIR, "latest1"),
    "latest2": os.path.join(RAW_DIR, "latest2"),
}

# Ensure directories exist (DR1)
def ensure_directories():
    for name, path in DIRS.items():
        os.makedirs(path, exist_ok=True)
    os.makedirs(os.path.join(WORKSPACE_DIR, "logs"), exist_ok=True)

# Master lookup table (FR7)
LOOKUP_PATH = os.path.join(WORKSPACE_DIR, "constituency_lookup.json")

def load_constituencies():
    if not os.path.exists(LOOKUP_PATH):
        raise FileNotFoundError(f"Master constituency lookup file not found at {LOOKUP_PATH}")
    with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# Anti-blocking configurations (NFR1: 2.0 to 5.0 seconds delay)
MIN_DELAY = 2.0
MAX_DELAY = 5.0

# News API configuration (TC2)
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
