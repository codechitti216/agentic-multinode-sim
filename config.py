from dotenv import load_dotenv
import os

# Load environment variables from .env if available
load_dotenv()

# -------------------------------
# LLM Config
# -------------------------------
LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
LMSTUDIO_API_KEY  = os.getenv("LMSTUDIO_API_KEY", "lm-studio")

# -------------------------------
# Ports for all microservices
# (override via .env if needed)
# -------------------------------
PORTS = {
    "auth":         int(os.getenv("AUTH_PORT", 8001)),
    "user":         int(os.getenv("USER_PORT", 8002)),
    "database":     int(os.getenv("DATABASE_PORT", 8003)),
    "payment":      int(os.getenv("PAYMENT_PORT", 8004)),
    "notification": int(os.getenv("NOTIFICATION_PORT", 8005)),
    "networking":   int(os.getenv("NETWORKING_PORT", 8006)),   # ✅ Networking runs on 8006
    "commander":    int(os.getenv("COMMANDER_PORT", 9080)),
}

# -------------------------------
# Port validation - ensure networking is on 8006
# -------------------------------
if PORTS["networking"] != 8006:
    print(f"⚠️  WARNING: Networking port is {PORTS['networking']}, expected 8006")
    print(f"   Check your .env file for NETWORKING_PORT setting")

# -------------------------------
# Data / logs storage location
# -------------------------------
DATA_DIR = os.getenv("DATA_DIR", "./data")
