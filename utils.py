import os
import re
import pytz
import csv
from datetime import datetime

from database import db
import utils as uts
from app import app, logger
from config import Config
from models import Groceries, Grocery_Items, Grocery_TEMP_Items


from dateutil.relativedelta import relativedelta
from sqlalchemy import or_, select

# Custom imports
from code_helpers.parse_process_df import parse_process_df
from code_helpers.OCR_metro import OCR_metro

# Utility Functions
def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def get_toronto_time():
    """Get current time in Toronto timezone."""
    utc_time = datetime.utcnow()
    toronto_tz = pytz.timezone('America/Toronto')
    utc_time = pytz.utc.localize(utc_time)
    return utc_time.astimezone(toronto_tz)

def convert_date(date_input):
    """Convert various date inputs to datetime object."""
    if not date_input:
        return get_toronto_time()
    elif isinstance(date_input, datetime):
        return date_input
    else:
        return datetime.strptime(date_input, '%Y-%m-%d').date()

def convert_price(price):
    """Convert price input to float."""
    if isinstance(price, str):
        if price.replace('.','',1).isdigit():
            price = float(price)
        else:
            price = 0.00
    else:            
        price = float(price)
    return price

def get_filename():
    """Get filename from OCR_text.csv."""
    from app import app
    try:
        temp_ocr = os.path.join(app.config['TEMP_FOLDER'], 'OCR_text.csv')
        with open(temp_ocr, 'r') as fin:
            content = fin.read()
            filename = content.split(',')[1] if ',' in content else "get_filename() FAILED: Can't Open File"
        return filename if filename else "get_filename() FAILED"
    except FileNotFoundError:
        return "get_filename() File Note Found"



def sum_price_list(price_list):
    """Calculate sum of prices in list."""
    return sum(convert_price(price) for price in price_list)

def clean_produce(item):
    """Clean produce item names by removing unwanted patterns."""
    # Keep all words
    words = re.findall(r'\b[A-Za-z]+\b', item, flags=re.IGNORECASE)
    clean_item = " ".join(words)
    
    # Remove words starting with 'k' (like KG)
    filtered_words = re.findall(r'\b(?!k\w+)\w+\b', clean_item, flags=re.IGNORECASE)
    return " ".join(filtered_words)

def how_long_ago(date):
    """Calculate how long ago a date was."""
    today = datetime.today().date()
    difference = today - date
    
    if 30 < difference.days < 360:
        diff = relativedelta(today, date)
        months_ago = diff.months + (diff.years * 12)
        return f"{months_ago} months"
    elif difference.days > 360:
        diff = relativedelta(today, date)
        return f"{diff.years} years"
    return f"{difference.days} days"

# Database Operations
def add_raw_receipt(raw_text, store, price, filename):
    """Add receipt to main Groceries table."""
    from database import db
    from app import logger
    
    new_receipt = Groceries(
        receiptText=raw_text,
        storeName=store,
        filename=filename,
        subtotal=price
    )
    
    try:
        db.session.add(new_receipt)
        db.session.commit()
        logger.info(f"SUCCESS: Added receipt to DB for {filename}")
        return new_receipt.id
    except Exception as e:
        db.session.rollback()
        logger.error(f"FAIL: Receipt not added to DB for {filename}: {e}")
        return None

def add_temp_item(item_data):
    """Add item to temporary table."""
    from database import db
    from app import logger
    
    new_item = Grocery_TEMP_Items(**item_data)
    
    try:
        db.session.add(new_item)
        db.session.commit()
        logger.info(f"SUCCESS: Added temp item for {item_data.get('filename')}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"FAIL: Temp item not added: {e}")

def add_grocery_item(item_data):
    """Add item to main Grocery_Items table."""
    from database import db
    from app import logger
    
    new_item = Grocery_Items(**item_data)
    
    try:
        db.session.add(new_item)
        db.session.commit()
        logger.info(f"SUCCESS: Added grocery item for {item_data.get('filename')}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"FAIL: Grocery item not added: {e}")

def find_store_item_matches(item):
    """Find matching items in Grocery_Items table."""
    return Grocery_Items.query.filter(
        Grocery_Items.storeItem.like(f"%{item}%")
    ).order_by(Grocery_Items.recepitDate.desc()).all()

def get_unlabeled_items():
    """Get items from temp table that need labeling."""
    from database import db
    from app import logger
    
    return db.session.execute(
        select(Grocery_TEMP_Items).where(
            or_(
                Grocery_TEMP_Items.myItem.is_(None),
                Grocery_TEMP_Items.myItem == ""
            )
        )
    ).scalars().all()

def get_unpopulated_items():
    """Get items with missing required fields."""
    from database import db
    from app import logger
    
    return db.session.execute(
        select(Grocery_TEMP_Items).where(
            or_(
                Grocery_TEMP_Items.myItem.is_(None),
                Grocery_TEMP_Items.myItem == "",
                Grocery_TEMP_Items.myCategory.is_(None),
                Grocery_TEMP_Items.myCategory == "",
                Grocery_TEMP_Items.price.is_(None),
                Grocery_TEMP_Items.price == ""
            )
        )
    ).scalars().all()

# OCR and Text Processing
def process_receipt_text(image_path, store, filename):
    """Process receipt image and extract text."""
    from app import logger
    
    match store:
        case 'Food Basics' | 'Bulk Barn':
            logger.info(f"{store} OCR processing")
            raw_text = OCR_metro(image_path)
            new_rows = []
            total_price = 0
        case 'Metro':
            raw_text = OCR_metro(image_path)
            text_list = [line for line in raw_text.split('\n') if line.strip()]
            logger.info(f"Processing {filename} with parse_process_df")
            new_rows, total_price = parse_process_df(text_list, logger, Config.VERBOSE)
        case _:
            raw_text = OCR_metro(image_path)
            new_rows = []
            total_price = 0
            logger.info(f"Unknown store {store}, using basic OCR")
    
    return raw_text, new_rows, total_price


def process_uploaded_file(file_path, store, filename, receipt_date):
    
    if receipt_date=="":
        receipt_date = get_toronto_time()
    
    # Process receipt
    raw_text, new_rows, total_price = process_receipt_text(file_path, store, filename)
    
    # Clear temp table and save OCR result
    Grocery_TEMP_Items.query.delete()
    db.session.commit()
    

    temp_ocr = os.path.join(app.config['TEMP_FOLDER'], 'OCR_text.csv')
    with open(temp_ocr, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.today().date(), filename, store, raw_text])
    
    # Add items to temp table
    for item in new_rows:
        item_data = {
            'storeItem': item[1],
            'storeCategory': item[0],
            'price': item[2],
            'storeName': store,
            'filename': filename,
            'recepitDate': uts.convert_date(receipt_date),
            'myCategory': '',
            'myItem': ''
        }
        uts.add_temp_item(item_data)
    
    # Attempt to label items automatically
    bought_once, frequent_items = guess_labels(Config.VERBOSE)
    return bought_once, frequent_items


def guess_labels(VERBOSE):
    """Guess labels for uploaded items based on purchase history."""
    bought_once = {}
    frequent_items = {}
    
    temp_items = Grocery_TEMP_Items.query.all()
    if VERBOSE:
        message = f"Processing {len(temp_items)} items for label guessing"
        print(message)
        logger.info(message)
    
    for i, temp_item in enumerate(temp_items):
        clean_item = uts.clean_produce(temp_item.storeItem)
        if not clean_item:
            continue
        
        matches = uts.find_store_item_matches(clean_item)
        if VERBOSE:
            message = f"Processing item {i}: {clean_item}"
            print(message)
            logger.info(message)        
            
        
        if not matches:
            pass
            
        elif len(matches) == 1:
            # Bought once before
            match = matches[0]
            temp_item.myItem = match.myItem
            temp_item.myCategory = match.myCategory
            bought_once[temp_item.myItem] = match.recepitDate.date()

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating item: {e}")
        else:
            # Frequent item
            match = matches[0]  # Use most recent
            temp_item.myItem = match.myItem
            temp_item.myCategory = match.myCategory
            frequent_items[len(matches)] = temp_item.myItem
 
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating item: {e}")

    return bought_once, frequent_items