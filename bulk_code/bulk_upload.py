# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 05:19:52 2024

@author: after
"""

import time
start = time.time()

import sys
import os
from datetime import date
from datetime import datetime

from pytesseract import pytesseract
from models import Grocery_TEMP_Items


# Imports from main application (project root)
from app import app
from database import db
from config import Config
import utils as uts  # for get_toronto_time, sum_price_list, RAWTEXT_Database_Add

# Push application context and create tables
app.app_context().push()
db.create_all()

# Your bulk upload code here...

# Defining paths to tesseract.exe and the image we would be using 
pytesseract.tesseract_cmd =  Config.TESSERACT_CMD
VERBOSE = Config.VERBOSE
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

def bulk_upload_qa():
    """Save all temp items to main database."""
    while True:  # Loop to allow user to retry after fixing errors
        unpopulated = uts.get_unpopulated_items()
        
        if unpopulated:
            print("Please complete all required fields on the website before saving:")
            
            for  item in (unpopulated):
                print(f"> My_Label or My_Category is missing: {item.storeItem}")
            
            # Give user a chance to fix and retry
            user_input = input("Press Enter after fixing the errors on the website, to try again, or type 'xxx' to abort: ").strip().lower()
            if user_input.lower() == 'xxx':
                print("Bulk upload cancelled.")
                return None
            continue  # Restart the process
        
        temp_items = Grocery_TEMP_Items.query.all()
        if not temp_items:
            print("No items to save")
            
            # Give user a chance to add items and retry
            user_input = input("Press Enter after adding items on the website, to try again, or type 'xxx' to abort: ").strip().lower()
            if user_input.lower() == 'xxx':
                print("Bulk upload cancelled.")
                return None
            continue  # Restart the process
        
        # If we reach here, everything is valid
        return temp_items 



def bulk_upload(fuzzy, folder_path, logger, thisStore, VERBOSE):
    
    UPLOAD_FOLDER = os.listdir(folder_path) 
    total_files = len(UPLOAD_FOLDER)

    #myNOTE = folder_path.split('\\')[-1]
    if VERBOSE: print_n_log(f"*******\nThere are {len(UPLOAD_FOLDER)} files to BULK UPLOAD in folder {folder_path}\n*******\n", logger)

    for filenumber, filename in enumerate(UPLOAD_FOLDER):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            
            if VERBOSE: print_n_log("-"*100, "NEW RECEIPT", "-"*100)

            file_date = filename.split(".")[0]
            if VERBOSE: print_n_log ("Uploading Filename", filename)
            
            if sum([1 for i in filename.split("-") if i.isnumeric()]) == 3:
                if VERBOSE: print_n_log("Receipt Date is: ", filename)
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
                    thisDate = uts.get_toronto_time()
                    user_input = input(f'No date was set: Press 1 to end process or Press any number to continue uploading receipt with todays date {thisDate} ')
                    if int(user_input) == 1:
                        exit()
                print ("Date on receipt is",  thisDate, "\n")

                        
            if VERBOSE: print_n_log(f"\n\nPROCESS: {filename}: {filenumber} of {total_files}", logger)
            #new_recepit = os.path.join(folder_path, filename)
            
#-----------Process receipt: Update Grocery_TEMP_Items DB
            bought_once, frequent_items = uts.process_uploaded_file(file_path, thisStore, filename, thisDate)
            temp_items = bulk_upload_qa(VERBOSE)
            uts.bulk_add_grocery_item(temp_items)

    print("END:", round(time.time()- start,0), " secs")