
# Install application: Tesseract-OCR
# Adjust two hard coded paths (for DB, and for OCR)
# pip install pytesseract flask_sqlalchemy flask_migrate opencv-python


import os
import secrets
import logging
from pytesseract import pytesseract

from config import Config
from config import DevConfig, ProdConfig

from database import db
from flask import Flask

from flask_migrate import Migrate
import sqlalchemy as sa

from sqlalchemy.orm import Session, sessionmaker #remove Session import

# Custom imports


import werkzeug
werkzeug.serving._log_add_style = False

log_file = 'logs/log.log'

# Configure logging
logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S',
    filename=log_file,
    encoding='utf-8',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# LOG prints out each webpage the user clicks on (which I want to keep) and also prints out each time the CSS/JS was called, which I want to remove.
# This disable = True code below removes routes + CSS + JS
# log = logging.getLogger('werkzeug')
# log.disabled = True

# This code below removes just the 'ANSI colors from Werkzeug logs'
# "[36mGET /static/css/date_warning.css HTTP/1.1[0m" 304 -
class NoStaticFilter(logging.Filter):
    def filter(self, record):
        # Exclude requests for static files or specific extensions
        message = record.getMessage()
        return "/static/" not in message and ".css" not in message
logging.getLogger("werkzeug").addFilter(NoStaticFilter())


# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = Config.OUTPUT_FOLDER
#app.config['TEMP_FOLDER'] = Config.TEMP_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH


env = os.getenv("FLASK_ENV", "development")

if env == "production":
    app.config.from_object(ProdConfig)
    app.config['SQLALCHEMY_DATABASE_URI'] = ProdConfig.DB_PATH
    pytesseract.tesseract_cmd = ProdConfig.TESSERACT_CMD # Configure Tesseract
else:
    app.config.from_object(DevConfig)
    app.config['SQLALCHEMY_DATABASE_URI'] = DevConfig.DB_PATH
    pytesseract.tesseract_cmd = DevConfig.TESSERACT_CMD  # Configure Tesseract


# Initialize extensions
#db = SQLAlchemy(app)
db.init_app(app)  # Use init_app instead of passing app directly
migrate = Migrate(app, db)


# Database setup - Suggested to Remove all of this too
engine = sa.create_engine(app.config['DB_PATH'])
connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()

logger.info('\n' + '='*50)
logger.info('Started Running the Flask App')
logger.info( """WARNING MESSAGE below is a Flask's built-in warning that fires whenever you use app.run(), regardless of environment.
 It means you're using Flask's built-in server, not a production WSGI server like Gunicorn.""")
logger.info(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
logger.info(f'OCR: {pytesseract.tesseract_cmd}')


print ("\n"+"-"*10 +"\n ✅ start app.py:Verbose Messages:" , Config.VERBOSE , "\n")
mode = "prod" if os.getenv("FLASK_ENV") == "production" else "dev"
print(f"🚀 Starting Flask in {mode} mode")

# Import models after db.init_app to register them
import models
import routes


