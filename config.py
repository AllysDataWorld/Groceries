# Configuration
class Config:
    TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    UPLOAD_FOLDER = 'static/uploads/'
    OUTPUT_FOLDER = 'output/'
    TEMP_FOLDER = 'temp/'
    DB_PATH = 'sqlite:///groceries.db'
    DATABASE_NAME = 'groceries.db'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    VERBOSE = False
    
    METRO_CATEGORY = ['GROCERY', 'PRODUCE', 'DAIRY', 'DELI','SEAFOOD', 'GENERAL','COMM']
    SUBTOTALS = ['SUBTOTAL.' ,'SUBTOTAL', 'SUBTOT']
    TOTALS = ['TOTAL.' ,'TOTAL', 'TOT']
