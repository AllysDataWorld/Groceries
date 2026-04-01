# Groceries App
### How to use Groceries App
1. FLASK website: Upload the receipt
2. BULK Upload -> Searches receipt files in specified folder (within `RUN_BULK_UPLOAD.py`)
   - Bulk will upload the receipt and ask the user to label all empty cells using the website
   - If the date is not found on the receipt, it'll will assume todays date, and alert/confirm with the user. 
 
### How UPLOAD works:
1. OCR extracts text from receipt and then writes to 'OCR_text.csv': [filename, store, raw_text]
2. bought_once, frequent_items = guess_labels_from_DB() --> (Grocery_Items DB)
   - find_store_item_matches_from_DB(storeItem) --> (Grocery_Items DB)
   - if not found --> read_Distinct_Grocery_Items(storeItem) --> (Distinct_Grocery_Items.csv)
3. Last Upload WEBSITE has a Button that calls: guess_label_for_new_items(): 
   - get_unlabeled_items
   - do fuzzy matching based on lev dist. --> TODO: on save, update the Distinct_Grocery_Items.csv
 
### bulk_add_grocery_item:
User saves to database after they have uploaded and made their edits:
1. update Grocery_Items: transfer all rows from Grocery_TEMP_Items 
   - delete all rows from Grocery_TEMP_Items
2. update Food_Expiry:
   - get_EST_WEEKS_via_Food_Expiry -> if not known ask AI (send_to_ai.txt)
   - if AI was called: populate_food_expiry_from_json(item_dic, response_table, upload_date)
        - There is COMMENTED OUT CODE that skips exiting items: #TODO: use this code, however it will impact populate_current_food(); update accordingly
   - else #AI was NOT called: populate_food_exiry_db(item_dic, upload_date)
3. update CurrentFood
    - populate_current_food: insert all non-expired items from Food_Expiry
4. update Smart_Shopping:
5. update Shopping_List_Settings


### AGENT CODE:
User Experience: User Uploads new receipt and saves to the Database:

###### Call AGENT:
agent_predictedExpiry(): calls Google ADK
  - INPUT: reads send_to_ai.txt by calling get_upload_items_for_AI()
  - PROCESSING: categorizes item and predicts end date.
  - OUTPUT: (JSON DUMP) app.config['AI_RESPONSE']
    - The grocery item, [perishable or non-perishable], upload_date, estimated number of weeks item will last, predicted_expiry_date.

###### Extract Info from JUMP:
ai_predictedExpiry(): recevies dump & sends to HTML:
  - INPUT: (JSON DUMP) app.config['AI_RESPONSE']
  - PROCESSING: extracts ai answer (massive JSON drump) into a small JSON dump
  - OUTPUT:
    - #TODO save answer as a JSON dump: app.config['AI_FOOD_FACTS_DUMP'] with datetime in filename
    - #TODO? save as a dataframe: app.config['AI_FOOD_FACTS']

# Backlog TODO: 
Clean up: 
1. does it make sense to combine functions: 
    - uts.convert_date_to_format(thisdate)
    - uts.parse_date(date_str: str | None)
    - uts.convert_date
1. consoliate '/' and '/all_tables/' and '/index2/' 
2. Possible Bug: I don't think upload date is a part of OCR; and are these dups? 
    - get_upload_date_from_OCRText
    - get_upload_date()
    - get_date_from_TEMP_ITEMS_DB()

3. Refactor: Possibly put these into their own files, as they are doing a lot:
   - process_uploaded_file
   - bulk_add_grocery_item

4. Update Settings.HTML
   - add a button to export food_facts db into ai_food_facts.csv

5. Add to 'install.py':
   - os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

6. Add Item -> currnetly only populates only Groceries and GroceryItems