# config.py
import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Dr. Well - AI Medical Assistant"
APP_ICON = "🤖"
APP_VERSION = "1.0.0"

# Google API Key - Get from https://aistudio.google.com/
# Option 1: From environment variable (.env file)
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Option 2: If not found in .env, set directly (uncomment and add your key)
# if not GOOGLE_API_KEY:
#     GOOGLE_API_KEY = "paste_your_actual_api_key_here"

# Check if API key is set
if not GOOGLE_API_KEY:
    print("⚠️ WARNING: GOOGLE_API_KEY not found!")
    print("Please either:")
    print("1. Create a .env file with: GOOGLE_API_KEY=your_key_here")
    print("2. Or set GOOGLE_API_KEY directly in config.py")
    print("\nGet your API key from: https://aistudio.google.com/")

MEDICAL_SPECIALTIES = [
    "Cardiologist", "Dermatologist", "Neurologist", "Orthopedic Surgeon",
    "Pediatrician", "Psychiatrist", "Ophthalmologist", "ENT Specialist",
    "Gynecologist", "General Physician", "Dentist", "Physiotherapist"
]

