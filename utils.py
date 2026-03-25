import os
import re
import pytz
import csv
from datetime import datetime, date, timedelta

from database import db
from app import app, logger
from ai.ai_predictedExpiry import ai_predictedExpiry
from models import Groceries, Grocery_Items, Grocery_TEMP_Items, Food_Expiry

from config import Config
app.config.from_object(Config)

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
    elif isinstance(date_input, date):
        return date_input
    else:
        return datetime.strptime(date_input, '%d-%m-%Y').date()

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
        temp_ocr = os.path.join(app.config['OUTPUT_FOLDER'], 'OCR_text.csv')
        with open(temp_ocr, 'r') as fin:
            content = fin.read()
            filename = content.split(',')[1]
        return filename if filename else "get_filename() FAILED"
    except FileNotFoundError:
        return "get_filename() File Note Found"


def get_upload_date():
    """DONT THINK THIS WORKS: The date is no longer in OCR_text.csv.
    Get date of upload from OCR_text.csv. This is the date the user input on the website"""
    from app import app
    try:
        temp_ocr = os.path.join(app.config['OUTPUT_FOLDER'], 'OCR_text.csv')
        with open(temp_ocr, 'r') as fin:
            content = fin.read()
            upload_date = content.split(',')[0].split(' ')[0]
        return upload_date if upload_date else "get_upload_date() FAILED"
    except FileNotFoundError:
        return "get_upload_date() File Note Found"

def get_upload_items_for_AI():
    ''''send_to_ai file contains the list of items uploaded with their upload date as the last element of the str'''
    temp = os.path.join(app.config['OUT_AI'], 'send_to_ai.txt')
    with open(temp, 'r') as fin:
        list_of_items = fin.read().split(',')
    upload_date = list_of_items.pop()
    return list_of_items, upload_date

def get_VERBOSE():
    #used in route /guess_label_for_new_items/ because I dont want to pass a parameter
    return Config.VERBOSE

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


#########################
# Database Operations
#########################
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


def bulk_add_grocery_item(temp_items):
    # Save to Grocery_Items and Grocery tables
    VERBOSE = True
    total_price = sum([item.price for item in temp_items])
    store_name = temp_items[0].storeName
    upload_date = temp_items[0].recepitDate

    all_food_items = []
    item_dic = {}

    temp_ocr = os.path.join(app.config['OUTPUT_FOLDER'], 'OCR_text.csv')
    with open(temp_ocr, 'r') as f:
        raw_text = f.read()
    
    receipt_id = add_raw_receipt(raw_text, store_name, total_price, get_filename())
       
    # Bulk insert items
    grocery_items = []
    for temp_item in temp_items:
        all_food_items.append(temp_item.myItem)
        item_data = {
            'storeItem': temp_item.storeItem,
            'myCategory': temp_item.myCategory,
            'storeCategory': temp_item.storeCategory,
            'myItem': temp_item.myItem,
            'storeName': temp_item.storeName,
            'price': temp_item.price,
            'filename': temp_item.filename,
            'recepitDate': temp_item.recepitDate,
            'groceries_id': receipt_id
        }
        grocery_items.append(Grocery_Items(**item_data))
    db.session.bulk_save_objects(grocery_items)
    db.session.commit()
    
    # Clear temp table
    Grocery_TEMP_Items.query.delete()
    db.session.commit()
    db.session.expunge_all()  # Add this line


    for line in all_food_items:
        item_EST_WEEKS = get_EST_WEEKS(line) #from DB
        item_dic[line] = item_EST_WEEKS
        if VERBOSE:  print(f"food_item:{line} -> DB found {item_EST_WEEKS} EST_WEEKS")


    new_item = []
    for item, wks in item_dic.items():
        if  wks == 0:
            new_item.append(item)

    if VERBOSE:  print(f"There are {len(new_item)} new times (that are not currently in the db)")
    output_ai = os.path.join(app.config['OUT_AI'], 'send_to_ai.txt')
    f = open(output_ai, 'w')
    for line in new_item:
        print("Send to ai:", line)
        f.write(str(line))
        f.write(",")
    f.write(upload_date.strftime('%Y/%m/%d'))
    f.close()

    if len(new_item) > 0:
        response, error = ai_predictedExpiry() #no file given
        print(f"response:{response}, error:{error}")

        summary = populate_food_expiry_from_json()
        if VERBOSE:
            print("Added New Food Items to Food Expiry DB:")
            print(f"Added:   {summary['added']}")
            print(f"Skipped: {summary['skipped']}")
            print(f"Errors:  {summary['errors']}")

    print(f"Add {len(item_dic)} Existing Food Items to Food Expiry DB:")
    populate_food_expiry_existing_items(item_dic, upload_date)

    return grocery_items, item_dic


def get_EST_WEEKS(search):
    """Decide if db already has the EST_WEEKS for item"""
    item_EST_WEEKS = db.session.query(Food_Expiry.EST_WEEKS)\
        .distinct()\
        .filter(Food_Expiry.item.like(f'%{search}%'))\
        .limit(1)\
        .all()
    if len(item_EST_WEEKS) != 0:
        WKS = item_EST_WEEKS[0][0]
    else:
        WKS = 0
    return WKS
# item_EST_WEEKS = get_EST_WEEKS(search)


def parse_date(date_str: str | None) -> datetime:
    DATE_FMT = "%Y/%m/%d"
    if not date_str:
        return datetime.utcnow()
    try:
        return datetime.strptime(date_str, DATE_FMT)
    except ValueError:
        return datetime.utcnow()

def populate_food_expiry_from_json() -> dict:
    """
    Reads a flat JSON array of food items and populates the Food_Expiry table.

    Expected JSON structure (one object per item):
        [
            {
                "item":                  "eggs",
                "classification":        "perishable",
                "upload_date":           "2026/03/16",
                "EST_WEEKS":             4,
                "predicted_expiry_date": "2026/04/13"
            },
            ...
        ]

    Args:
        json_path:  Path to the JSON file.

    Returns:
        A dict with keys "added", "skipped", and "errors".
    """
    import json

    food_facts = os.path.join(app.config['OUT_AI'], app.config['AI_FOOD_FACTS_DUMP'])
    with open(food_facts, "r") as f:
        items: list[dict] = json.load(f)

    results = {"added": [], "skipped": [], "errors": []}

    print(f"populate foodexp db from JSON -> ITEMS:{items}")
    for item_data in items:
        item_name = item_data.get("item")

        if not item_name:
            results["errors"].append({"data": item_data, "reason": "Missing 'item' field"})
            continue

        # Skip if already in the DB (item column is unique)
        # if Food_Expiry.query.filter_by(item=item_name).first():
        #     print("skipped:", item_name)
        #     results["skipped"].append(item_name)
        #     continue

        record = Food_Expiry(
            item                  = item_name,
            classification        = item_data.get("classification", "unknown"),
            EST_WEEKS             = int(item_data.get("EST_WEEKS", 0)),
            purchase_date         = parse_date(item_data.get("upload_date")),
            predicted_expiry_date = parse_date(item_data.get("predicted_expiry_date")),
        )

        db.session.add(record)
        results["added"].append(item_name)

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise RuntimeError(f"Database commit failed: {exc}") from exc

    return results
# ---------------------------------------------------------------------------
# Example usage inside a Flask app context
# ---------------------------------------------------------------------------
# from app import app, db
# from models import Food_Expiry
#
# with app.app_context():
#     summary = populate_food_expiry_from_json("ai_food_facts_dump.json")
#     print(f"Added:   {summary['added']}")
#     print(f"Skipped: {summary['skipped']}")
#     print(f"Errors:  {summary['errors']}")



def populate_food_expiry_existing_items(existing_item_dic, upload_date) -> dict:
    """
    reads items from Food_Expiry db and Food_Expiry table.
    """

    print(f"There are {len(existing_item_dic)} items in the existing_item_list")
    for item, wks in existing_item_dic.items():
        record = Food_Expiry(
            item                  = item,
            classification        = "perishable",
            EST_WEEKS             = int(wks),
            purchase_date         = upload_date,
            predicted_expiry_date = upload_date + timedelta(days=7*wks)
        )
        db.session.add(record)
    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise RuntimeError(f"Database commit failed: {exc}") from exc

    return None
# ---------------------------------------------------------------------------
# Example usage inside a Flask app context
# ---------------------------------------------------------------------------
# from app import app, db
# from models import Food_Expiry
#
# with app.app_context():
#     summary = populate_food_expiry_from_json("ai_food_facts_dump.json")
#     print(f"Added:   {summary['added']}")
#     print(f"Skipped: {summary['skipped']}")
#     print(f"Errors:  {summary['errors']}")
















def find_store_item_matches(item):
    """Find matching items in Grocery_Items table."""
    return Grocery_Items.query.filter(
        Grocery_Items.storeItem.like(f"%{item}%")
    ).order_by(Grocery_Items.recepitDate.desc()).all()

def get_unlabeled_items():
    """Get items from temp table that need labeling."""
    from database import db
    
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


def get_date_from_TEMP_ITEMS_DB():
    """Get the current date from Grocery_TEMP."""
    from database import db
    #Get the first item's date
    result = db.session.execute(
        select(Grocery_TEMP_Items.recepitDate).limit(1)
    ).scalar()
    return convert_date(result)

def get_totalPrice_from_TEMP_ITEMS_DB():
    """Get the total price from Grocery_TEMP."""
    from database import db
    #Get the first item's date
    result = db.session.execute(
        select(Grocery_TEMP_Items.price)
    ).scalars().all()

    total_price =sum(result)
    return total_price

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



def get_OCRtext():
    """Helper function for Get_Upload_date_from_OCRText: Get text from OCR.csv"""
    from app import app
    import os
    try:
        OCR_FILE = os.path.join(app.config['OUTPUT_FOLDER'], 'OCR_text.csv')
        all_text = open(OCR_FILE).readlines()
        text_list = []
        for text in all_text:
            if text == "\n":
                pass
            else:
                text = text.split('\n')[0]
                text_list.append(text)
    except FileNotFoundError:
        return "get_OCRtext() File Note Found"
    return text_list

def convert_date_to_format(thisdate):
    # Convert to your desired format
    from datetime import datetime
    date_obj = datetime.strptime(thisdate, '%Y-%m-%d')
    newdate = date_obj.strftime('%d-%m-%Y')
    return newdate


def get_upload_date_from_OCRText():
    possible_list = []
    found_date = False
    text_list = get_OCRtext()

    matches = [(i, element) for i, element in enumerate(text_list)
               if element.startswith("Date")]

    num_matches = len(matches)

    if num_matches == 0:
        dt = ""
        found_date = False
        print ("Receipt Date was not found")
    elif num_matches == 1:
        dt = matches[0][1].split(' ')[1]  # one match
        found_date = True
    else:
        possible_list = [dt_m[1] for dt_m in matches]
        dt = possible_list[0][0]
        found_date = True
        print(f"Look for Date in OCR Text -> matches: {matches}")
        print(f"Look for Date in OCR Text -> possible_list: {possible_list}")
        print(f"Look for Date in OCR Text -> suggested dt: {dt}")

    try:
        if len(dt.split('/')) == 3: # Expecting the format '24/11/21'
            year = int("20" + dt.split('/')[0])
            month = int(dt.split('/')[1])
            day = int(dt.split('/')[2])
            OCR_dt = date(year, month, day)
            OCR_dt = convert_date(OCR_dt)
            human_readable = OCR_dt.strftime("%B %d, %Y")
            print(f"The date on the receipt was {human_readable}")
            return OCR_dt
        else:
            #print(f"Date is not in the expected format YEAR/MO/DAY")
            print("Please confirm receipt date")
            return None

    except Exception as e:
        print(f"Exception {e} occured with exracting the date from OCR ")








def process_uploaded_file(file_path, store, filename, receipt_date, bulk_process):
    import pandas as pd
    # Process receipt
    raw_text, new_rows, total_price = process_receipt_text(file_path, store, filename)

    Grocery_TEMP_Items.query.delete()
    db.session.commit()

    temp_ocr = os.path.join(app.config['OUTPUT_FOLDER'], 'OCR_text.csv')
    with open(temp_ocr, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([filename, store, raw_text])

    df_sortorder = pd.read_csv(os.path.join(app.config['OUTPUT_FOLDER'], 'sortorder_df.csv'))
    item_to_sort = {row['item']: row['sort_order'] for _, row in df_sortorder.iterrows() if row['CAT'] == 'ITEM'}
    sorted_items = sorted(new_rows, key=lambda x: item_to_sort.get(x[1], 9999))
    new_rows = sorted_items

    receipt_date = convert_date(get_upload_date_from_OCRText())

    # Add items to Grocery_TEMP_Items table
    for item in new_rows:
        item_data = {
            'storeItem': item[1],
            'storeCategory': item[0],
            'price': item[2],
            'storeName': store,
            'filename': filename,
            'recepitDate':receipt_date,
            'myCategory': '',
            'myItem': ''
        }
        add_temp_item(item_data)
    
    # Attempt to label items automatically
    bought_once, frequent_items = guess_labels(logger, Config.VERBOSE)
    return bought_once, frequent_items, total_price





def print_log(mystr, logger, header=False, footer=False):
    if header:
        header_len = (len(mystr)+10) *'-'
        mystr = f"{header_len} \n START {mystr.upper()} \n{header_len}\n"
    elif footer:
        footer_len = (len(mystr)+10) *'-'
        mystr = f"{footer_len} \n END {mystr.upper()} \n{footer_len}\n"
    else:
        pass
    logger.info(mystr)
    print(mystr)
    return None

def guess_labels(logger, VERBOSE):
    """Guess labels for uploaded items based on purchase history."""
    if VERBOSE: print_log("guess_labels", logger, header=True, footer=False)

    bought_once = {}
    frequent_items = {}
    
    temp_items = Grocery_TEMP_Items.query.all()
    num_items = len(temp_items)
    if num_items == 0:
        print("NO ITEMS IN Grocery_TEMP_Items")
        return {}, {}

    if VERBOSE:
        print_log(f"Guessing the labels all items uploaded (aka Grocery_TEMP_Items):\n",
                  logger, header=False, footer=False)

    for i, temp_item in enumerate(temp_items):
        storeItem = temp_item.storeItem
        storeCat = temp_item.storeCategory

        if VERBOSE:
            print_log(f'\n{i} of {num_items} \nFor {storeCat} Item: {storeItem}', logger, header=False, footer=False)

        #processing for produce items only
        if storeCat == "PRODUCE":
            storeItem = clean_produce(storeItem)
            if VERBOSE:print_log(f"Cleaning Produce item: {storeItem}", logger, header=False, footer=False)
            if not storeItem: #was updated afte clean_produce()
                if VERBOSE:print_log(f"XXX-> Produce was updated after calling clean_produce()... {storeItem}",
                          logger, header=False, footer=False)
                continue
            else:
                if VERBOSE:print_log(f"XXX-> Produce was NOT changed after cleaning... {storeItem}",
                          logger, header=False, footer=False)
        else: #not produce item
            pass


        matches = find_store_item_matches(storeItem)
        if VERBOSE:
            print_log(f"Found {len(matches)} matches:", logger, header=False, footer=False)

        if not matches:
            pass
            
        elif len(matches) == 1:
            # Bought once before
            match = matches[0]
            keep = temp_item.storeItem
            temp_item.myItem = match.myItem
            temp_item.myCategory = match.myCategory
            bought_once[temp_item.myItem] = match.recepitDate.date()
            if VERBOSE: print_log(f"Bought ONCE - ORIG:{keep} \nUpdated:{match.myItem}",
                                  logger, header=False, footer=False)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating item: {e}")
        else:
            # Frequent item
            if VERBOSE:
                for m in matches:
                    print("> Matches:", m.storeItem)
            match = matches[0]  # Use most recent
            keep = temp_item.storeItem
            temp_item.myItem = match.myItem
            temp_item.myCategory = match.myCategory
            frequent_items[len(matches)] = temp_item.myItem
            if VERBOSE: print_log(f"Bought MANY TIMES - ORIG:{keep} \nUpdated:{match.myItem}",
                                  logger, header=False, footer=False)
 
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating item: {e}")

    if VERBOSE: print_log("guess_labels", logger, header=False, footer=True)
    return bought_once, frequent_items


def uploaded_items_to_ai():
    """ DELETE THIS LATER? NOT USED
        Export distinct items from Grocery_Items_TEMP to CSV."""
    try:
       # Get distinct combinations of all fields
        distinct_items = db.session.query(
            Grocery_TEMP_Items.storeName,
            Grocery_TEMP_Items.storeCategory,
            Grocery_TEMP_Items.storeItem,
            Grocery_TEMP_Items.myItem,
            Grocery_TEMP_Items.myCategory
        ).distinct().order_by(
            Grocery_TEMP_Items.storeName,
            Grocery_TEMP_Items.myCategory,
            Grocery_TEMP_Items.myItem
        ).all() 
        
        # Create CSV filename 
        csv_filename = "Uploaded_Items_for_AI.csv"
        csv_path = os.path.join(app.config['OUTPUT_FOLDER'], csv_filename)
        
        # Ensure output folder exists
        os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
        
        # Write to CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['storeName', 'storeCategory', 'storeItem', 'myItem', 'myCategory'])  # Header
            for item in distinct_items:
                # Only write rows where at least myItem has a value (or adjust condition as needed)
                if item.myItem:  # Skip rows with null myItem
                    writer.writerow([
                        item.storeName,
                        item.storeCategory,
                        item.storeItem,
                        item.myItem,
                        item.myCategory
                    ])

    except Exception as e:
        logger.error(f"Error uploaded_items_to_ai: {e}")
        print(f"Error uploaded_items_to_ai: {e}")
    return None

