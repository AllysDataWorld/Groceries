# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 05:19:52 2024

@author: after
"""
import os
import time
from pytesseract import pytesseract
start = time.time()


# Imports from main application (project root)
from app import app
from database import db
from config import Config
import utils as uts   

from bulk_code import bulk_utls as b_uts

# Push application context and create tables
app.app_context().push()
db.create_all()

# Your bulk upload code here...

# Defining paths to tesseract.exe and the image we would be using 
pytesseract.tesseract_cmd =  Config.TESSERACT_CMD
VERBOSE = Config.VERBOSE
thisDate = "" 

def print_n_log(mystr, logger):
    logger.info(mystr)                        
    print(mystr)                        

def bulk_upload(folder_path, logger, thisStore, VERBOSE):
    
    UPLOAD_FOLDER = os.listdir(folder_path) 
    total_files = len(UPLOAD_FOLDER)

    #myNOTE = folder_path.split('\\')[-1]
    if VERBOSE: print_n_log(f"*******\nThere are {len(UPLOAD_FOLDER)} files to BULK UPLOAD in folder {folder_path}\n*******\n", logger)

    #file the upload date from the filename or from the OCR Text:
        


    for filenumber, filename in enumerate(UPLOAD_FOLDER):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            if VERBOSE: print_n_log("-"*100, "\nNEW RECEIPT\n", "Uploading Filename", filename, "-"*100)
            if VERBOSE: print_n_log(f"\n\nPROCESS: {filename}: {filenumber} of {total_files}", logger)
            
#-----------Process receipt: Update Grocery_TEMP_Items DB
            bought_once, frequent_items = uts.process_uploaded_file(file_path, thisStore, filename, "") #Upload date is blank
            temp_items = b_uts.bulk_upload_qa()
            if temp_items: uts.bulk_add_grocery_item(temp_items) #if return None then user existed and do not execute this function

    print("END:", round(time.time()- start,0), " secs")