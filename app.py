
# Install application: Tesseract-OCR
# Adjust two hard coded paths (for DB, and for OCR)
# pip install pytesseract flask_sqlalchemy flask_migrate opencv-python


import pytz
import sqlite3
import secrets
import logging
from dateutil.relativedelta import relativedelta
from werkzeug.utils import secure_filename
from pytesseract import pytesseract

import os
import csv
import re
import secrets
import logging
from datetime import datetime

from config import Config
from database import db

from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy as sa
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, sessionmaker

# Custom imports
from code_helpers.parse_process_df import parse_process_df
from code_helpers.text_mining_metro import text_mining_metro
from code_helpers.OCR_metro import OCR_metro
from code_helpers.levenshtein_distance import levenshtein_distance
from code_helpers.create_metro_df import create_metro_df


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



# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = Config.OUTPUT_FOLDER
app.config['TEMP_FOLDER'] = Config.TEMP_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DB_PATH

# Initialize extensions
#db = SQLAlchemy(app)
db.init_app(app)  # Use init_app instead of passing app directly
migrate = Migrate(app, db)

# Configure Tesseract
pytesseract.tesseract_cmd = Config.TESSERACT_CMD

# Database setup
engine = sa.create_engine(Config.DB_PATH)
connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()

logger.info('\n' + '='*50)
logger.info('Started Running the Flask App')

print ("\n"+"-"*10 +"\n ✅ start app.py:Verbose Messages:" , Config.VERBOSE)

# Import models after db.init_app to register them
import models


