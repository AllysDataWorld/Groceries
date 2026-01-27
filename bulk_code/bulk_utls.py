# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 05:19:52 2024

@author: after
"""

from datetime import date
from models import Grocery_TEMP_Items
import utils as uts


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
                return None # exit out of this process
            
            continue  # Restart the process

        # if receipt_date is today's date, then user has to say 'yes' to continue
        current_date = uts.get_date_from_db().date()
        today_date = date.today().strftime('%Y-%m-%d')

        if today_date == today_date:
            user_input = input("The receipt date was automattically set to today's date. If this is correct please say YES\n")
            if user_input != 'YES':
                continue  # Restart the process


        temp_items = Grocery_TEMP_Items.query.all()
        if not temp_items:
            print("No items to save")
            return None # exit out of this process

        # If we reach here, everything is valid
        return temp_items




def get_date_for_bulk(filename):
    import sys
    OCR_dt, human_readable_date, num_matches, possible_list = uts.get_upload_date_from_OCRText()

    print("Upload date is blank. Please select the following options, and enter 1,2, or 3. Use the Website to view the receipt being processed\n")
    print(f"1) use today's date\n2) use the date found on recipt {human_readable_date} \n3) The filename is the date, \n4) Enter a new date")
    user_option = int(input())
        
    match user_option:
        case 1:
            receipt_date = uts.get_toronto_time()
        case 2:
            receipt_date = OCR_dt
        case 3:
            file_date = filename.split(".")[0]
            year, month, day = [int(item) for item in file_date.split('-')]
            receipt_date = date(year, month, day)
        case 4:
            date_components = input('Enter a date formatted as YYYY-MM-DD: ').split('-')
            year, month, day = [int(item) for item in date_components]
            receipt_date = date(year, month, day)
        case _:
            print("ERR Entry")
            sys.exit(0)
    print("Continue using date:", receipt_date)
