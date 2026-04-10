import os
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# --- WORDPRESS CONFIGURATION ---
WP_URL = os.environ.get("WP_URL", "https://uma.infinityfreeapp.com")
WP_USERNAME = os.environ.get("WP_USERNAME", "admin") # Kept admin as it's not a secret usually
WP_PASSWORD = os.environ.get("WP_PASSWORD")

# The REST API endpoint
WP_API_ENDPOINT = f"{WP_URL.rstrip('/')}/wp-json/wp/v2"

# --- GROQ API CONFIGURATION ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# Recommended model for text generation: Llama 3 70b or 8b (it's fast and highly capable)
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# --- BLOG SETTINGS ---
# Optional: Specific categories or tags if you have their IDs.
# Leave empty for default.
WP_CATEGORY_IDS = [] 
WP_TAG_IDS = []

# Status can be 'publish' or 'draft'
POST_STATUS = "publish"
