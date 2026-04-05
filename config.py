# Configuration
import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")
    DB_FOLDER = os.path.join(BASE_DIR, "instance")
    UPLOAD_FOLDER = os.path.join("static", "uploads") #'static/uploads/'
    OUT_AI = os.path.join(OUTPUT_FOLDER, "out_ai") #OUT_AI = 'output/out_ai/'
    AI_RESPONSE = "ai_response.json"
    AI_FOOD_FACTS = "ai_food_facts.csv"
    SAVE_DUMP = os.path.join(OUT_AI, "save_ai_dumps") #timestamp added
    AI_FOOD_FACTS_DUMP = "ai_food_facts_dump" #.json
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MIN_PURCHASE = 2
    VERBOSE = False

    METRO_CATEGORY = ['GROCERY', 'PRODUCE', 'DAIRY', 'DELI','SEAFOOD', 'GENERAL','COMM']
    SUBTOTALS = ['SUBTOTAL.' ,'SUBTOTAL', 'SUBTOT']
    TOTALS = ['TOTAL.' ,'TOTAL', 'TOT']

class DevConfig(Config):
    DEBUG = True
    ENV = "development"
    TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    DB_PATH = f"sqlite:///{os.path.join(Config.DB_FOLDER, 'groceries_dev.db')}"


class ProdConfig(Config):
    DEBUG = False
    ENV = "production"
    TESSERACT_CMD = "/usr/bin/tesseract"
    DB_PATH = f"sqlite:///{os.path.join(Config.DB_FOLDER, 'groceries_prod.db')}"

