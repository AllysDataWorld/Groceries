# Groceries
How to use Groceries App

FLASK website: Upload the receipt
or
BULK Upload -> Searches receipt files in specified folder (within RUN_BULK_UPLOAD.py)
>> If using Bulk version, it will upload the receipt and ask the user to label all empty cells using the website
 
AI: 
User Experience: User Uploads new receipt. Once that receipt is saved to the Database, user clicks on Predict Expiry Tab:
BACKEND ROUTE: /ai_response/ calls ai_predictedExpiry() in ai_predictedExpiry.py and then brings up 'ai_predictedExpiry.html'
LOGIC: ai_predictedExpiry(): calls [agent_main.py](ai/agent_predictedExpiry.py) the Agent that writes a JSON file:
    The grocery item, [perishable or non-perishable], upload_date, estimated number of weeks item will last, predicted_expiry_date.
    ai_predictedExpiry() read this JSON file and sends it back to HTML.

agent creates a JSON DUMP:
INPUT: reads send_to_ai.txt by calling get_upload_items_for_AI()
PROCESSING: categorizes item and predicts end date.
OUTPUT: (JSON DUMP) app.config['AI_RESPONSE']

ai calls agent & sends to HTML:
    INPUT: (JSON DUMP) app.config['AI_RESPONSE']
    PROCESSING: extracts ai answer from JSON dump
    OUTPUT: 
        return to HTML: table
        DELETE? save as a dataframe: app.config['AI_FOOD_FACTS']
        DELETE? if answer is in a unexpected data structure: 
        save answer as a temp JSON dump: app.config['AI_FOOD_FACTS_DUMP']



LOGIC: 
Save to Grocery_Items creates file: send_to_ai.txt
    At this point, call ai to calculate the end_dates and save to database
    Add database clean up, when the end date has passed, remove item from database

    Save the original(maybe?) AI dump with timedate: app.config['SAVE_DUMP']

For each item thats being saved to the grocery database, 
    example: BREAD
    see if BREAD exists in the previous Resposnes
    if not, put in array to call AI
    otherwise, get information for this item.
Now each item should have dates.
    NEW DATABASE: Time_DB -> Purchase Date, Item, Category, classification, EST_WEEKS, ExpiryDate
    BULK_INSERT into a new database (items we currently have in the fridge): FridgeDB
        Purchase Date, Item, Category, classification, EST_WEEKS, ExpiryDate
    New Function: Remove items from FridgeDB that have expired
    NEW DATABASE: Time_DB -> Item, Category, classification, EST_WEEKS



