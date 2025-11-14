import sys
import os

# Add project root (one folder up) to PYTHONPATH
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from config import API_KEY
import moondream as md

# Connect to Moondream Station
model = md.vl(api_key=API_KEY)

# Load prompt from project root
PROMPT_PATH = os.path.join(ROOT, "prompt.txt")
with open(PROMPT_PATH, "r") as f:
    PROMPT = f.read()

def MoonModel(img):
    result = model.query(img, PROMPT)
    return result.get("answer")
