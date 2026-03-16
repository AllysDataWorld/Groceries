# Groceries
How to use Groceries App

FLASK website: Upload the receipt
or
BULK Upload -> Searches receipt files in specified folder (within RUN_BULK_UPLOAD.py)
>> If using Bulk version, it will upload the receipt and ask the user to label all empty cells using the website
 
AI: 
User Uploads new receipt. Once that receipt is saved to the Database, user clicks on Predict Expiry Tab:
route /ai_response/ calls ai_predictedExpiry() in ai_predictedExpiry.py and then brings up 'ai_predictedExpiry.html'
ai_predictedExpiry(): calls [agent_main.py](ai/agent_main.py) the Agent that writes a JSON file:
    The grocery item, [perishable or non-perishable], upload_date, estimated number of weeks item will last, predicted_expiry_date.
    ai_predictedExpiry() read this JSON file and sends it back to HTML.


