# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 05:19:52 2024

@author: after
"""

import time
start = time.time()


import sys
import os
from datetime import datetime, date
import pandas as pd
from pytesseract import pytesseract

# Imports from main application (project root)
from app import app
from database import db
from models import Grocery_Items
import utils as uts  # for get_toronto_time, sum_price_list, RAWTEXT_Database_Add

# Imports from bulk_code folder (same directory)
#from bulk_code.parse_process_df_bulk import parse_process_df_bulk
from code_helpers.text_mining_metro import text_mining_metro
from code_helpers.OCR_metro import OCR_metro


# Push application context and create tables
app.app_context().push()
db.create_all()

# Your bulk upload code here...





# from app import RAWTEXT_Database_Add
# from app import get_toronto_time, sum_price_lst
# from app import Grocery_Items
# from parse_process_df_bulk import parse_process_df_bulk
# from text_mining_metro import text_mining_metro
# from OCR_metro import OCR_metro

# import pandas as pd

# import os
# import sys

# from pytesseract import pytesseract 

# from app import app, db
# app.app_context().push()
# db.create_all()

# Defining paths to tesseract.exe and the image we would be using 
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


thisDate = "" 

def check4issues_forBulkUpload(price, file):
    """."""     
    ISSUES = False
    if isinstance(price, str):
        if price.replace('.','',1).isdigit():
            # print(" PRICE IS STR and FINE")
            pass
        else:
            # print(" PRICE IS STR and NOT FINE", price)
            ISSUES = True
    else:
        try:            
            price = float(price)
        except:
            # print(" PRICE IS DIGIT and NOT FINE", price)
            ISSUES = True
    if ISSUES:
        sys.exit("Bulk Upload - ISSUE WITH PRICE {price} within {filename})")
    return None

def print_n_log(mystr, logger):
    logger.info(mystr)                        
    print(mystr)                        

def bulk_upload(fuzzy, folder_path, logger, thisStore):
    
    UPLOAD_FOLDER = os.listdir(folder_path) 
    total_files = len(UPLOAD_FOLDER)

    myNOTE = folder_path.split('\\')[-1]
    print_n_log(f"*******\nThere are {len(UPLOAD_FOLDER)} files to BULK UPLOAD in folder {folder_path}\n*******\n", logger)

    for filenumber, filename in enumerate(UPLOAD_FOLDER):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            
            print("-"*250, "NEW RECEIPT", "-"*250)

            file_date = filename.split(".")[0]
            print ("Uploading Filename", filename)
            
            if sum([1 for i in filename.split("-") if i.isnumeric()]) == 3:
                print("Receipt Date is: ", filename)
                # filename = "file-123-abc-456-789"
                # Split: ["file", "123", "abc", "456", "789"]
                # Numeric parts: ["123", "456", "789"]
                # Count: 3
                # Result: True (3 == 3)
                
            else:
                user = input(f"Confirm Date(YYYY-MM-DD): {file_date} \n Enter 1 if this is correct, or any number to enter a new date ")
                if int(user) == 1:
                    year, month, day = [int(item) for item in file_date.split('-')]
                    thisDate = date(year, month, day)
                else:
                    date_components = input('Enter a date formatted as YYYY-MM-DD: ').split('-')
                    year, month, day = [int(item) for item in date_components]
                    thisDate = date(year, month, day)
                
                if thisDate=="":
                    thisDate = get_toronto_time()
                    user_input = input(f'No date was set: Press 1 to end process or Press any number to continue uploading receipt with todays date {thisDate} ')
                    if int(user_input) == 1:
                        exit()
                        
            print_n_log(f"\n\nPROCESS: {filename}: {filenumber} of {total_files}", logger)
            new_recepit = os.path.join(folder_path, filename)
            
#-----------Process receipt
            bought_once, frequent_items = uts.process_uploaded_file(file_path, thisStore, filename, "")
            
            
            # raw_text = OCR_metro(new_recepit) #comment starts here
                       
            # text_list = raw_text.split('\n')
            # text_list = list(filter(None, text_list))

            # new_rows, total = parse_process_df_bulk(text_list, logger)      
            # print("-" * 40)
            # logger.info("-" * 40)
            
            # #I'm not sure why rows should not be less than 3:
            # # for rows in new_rows:
                # # if len(rows) != 3:
                    # # print("new rows:", new_rows)
                    # # sys.exit(f"bulk_upload.py: New rows is not 3:  {len(new_rows)} != 3")  
            # # print("-" * 40)

            # for rows in new_rows:
                # check4issues_forBulkUpload(rows[2], filename)
            
            # total_price_lst = [
                    # receipt_item[2]
                # for receipt_item in new_rows
            # ]
            
            # totalPrice = uts.sum_price_list(total_price_lst)

            # new_id = RAWTEXT_Database_Add(rawtext=raw_text, store=thisStore, 
                                          # price=totalPrice, file=filename)

            # print("-"*40, "new_rows", "-"*40)
            # print(new_rows)

            # # Create a list of Grocery_Items objects based on the temp_items
            # grocery_items = [
                # Grocery_Items(
                    # storeItem=receipt_item[1],
                    # filename = filename,
                    # myCategory=receipt_item[4],
                    # storeCategory=receipt_item[0],
                    # myItem =receipt_item[3],
                    # storeName=thisStore,
                    # price=receipt_item[2],
                    # recepitDate=thisDate,
                    # groceries_id = new_id
                # ) for receipt_item in new_rows #for receipt_item in new_rows if len (receipt_item) == 3  
            # ] #receipt_item[0] = ('BAKERY', 'COUNTRY HARV. SOU', 4.79)
    
            # if len(new_rows) != len(grocery_items):
                # sys.exit(f"{len(new_rows)} != {len(grocery_items)}")  
    

        # try: # Bulk insert into Grocery_Items table
            # db.session.bulk_save_objects(grocery_items)
            # db.session.commit()
            # print("SUCCESS: Added grocery_items to Item DB", )
            # logger.info("SUCCESS: Added Receipt to Grocery_Items DB:" + str(len(grocery_items)))                        
    
        # except Exception as e:
            # db.session.rollback()
            # logger.info("FAIL: Receipt Not Added to Grocery_Items DB:" + str(len(grocery_items)))                        
            # logger.info("Error occurred:" + e + '\n')                        
    
            # print("FAIL: Receipt Not Added to Grocery_Items DB")
            # print(f"Error occurred: {e}")
    
    print("END:", round(time.time()- start,0), " secs")
    
# groceries_id = insert_groceries(temp_items)
# raw_text, new_rows, total_price = text_mining(new_recepit, store)
# bulk_insert()

#text_orig, new_rows, total_price = text_mining(new_recepit, thisStore)
#delete_all_Grocery_TEMP_Items()
