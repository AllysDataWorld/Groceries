
	------------INITIAL COMMIT--------
running on new environment: conda activate ai
organized the code into appropriate files; instead of ai.py containing everything.
    log file in log folder
    send_to_ai csv in OUTPUT folder
    OCR_text.csv in TEMP folder
    Bulk Processing files located in folder: bulk_code 
		Bulk Processing uses the same functions are the main processing
    main code excludes the bulk upload code

BUG: There was a 'Change Date' button on Items_temp.html that was not working. Simply removed it. 
     reorganized Items_temp.html so that the picture and table are side-by-side; to make it easier on the user

	------------SECOND COMMIT--------

Set VERBOSE within CONFIG:
VERBOSE = Config.VERBOSE

DEFINED IN TWO PLACES: FIXED:
text_mining_metro.py and create_metro_df.py 
metro_headings = ['GROCERY', 'PRODUCE', 'DAIRY', 'DELI','SEAFOOD', 'GENERAL','COMM']
subtotal_list = ['SUBTOTAL.' ,'SUBTOTAL', 'SUBTOT']
total_list = ['TOTAL.' ,'TOTAL', 'TOT']


------------Third COMMIT--------

Used Claud to create a link "Export Distinct Items" currently in the Delete.HTML
that exports the items and their labels to dir:OUTPUT

------------COMMIT:AI--------
	
Route.py has code to create updated.csv that has the orig row and updated row. 
TODO: The code is copy/pasted and could be improved probably. CSV is in OUTPUT folder.
MOVED OCR_TEXT.csv into OUTPUT folder
MOVED ai code to their own folder
Added: agent_main.py
upload_date = uts.get_upload_date()
list_of_items = uts.get_upload_items() 
	
Commit Message: Two AI agents called sequentially. One gets the list of uploaded items, the other classifies them and assigns use_before dates.
	
------------COMMIT:Bulk & Web--------
Commit Message: Completed the Bulk_Upload code. Added MutliDelete Option. Update shows picture of receipt.

- renamed /bulk_insert/ to /save_grocery_item/
- split /bulk_insert/ into two functions: One that receives BULK_CODE (bulk_upload_qa())  and one that receives from the HTML website(save_grocery_item(). The bulk_add_grocery_item() is shared
    --> bulk_upload_qa() does a QA, and allows the HUMAN to fix the labels on the website.
- make a new DIR where I can process ALL the receipts	
- Added Button to Item_Temp.html to be able to delete a few rows at the same time on the Updated Last Upload page
- Fixed Bug: guess_label_for_new_items only returned a filename picture when there are guesses for items.
- When I click on UPDATE, the picture of the receipt should be in the update_html because I keep forgetting what the correct value should be.
	
------------COMMIT:Bulk & Web---------
Commit Message: Fixed Critical Bug. Try using Date on receipt. Created 'Fake Populate All' button.
- Fixed Critical bug in uploading receipt by website.
- Updated website + bulk behaviour to try an use the receipt date.
- Created a 'Fake Populate All' button for testing, so I dont have to us the update button just to save the rows.

Commited out code:
- Bulk upload gives user three options for upload date: 
  1) use today's date
  2) use the date found on recipt 
  3) The filename is the date
  4) Enter a new date

------------COMMIT:Bulk & Web---------
Commit Message "Fixed behavior for getting Receipt Date from OCR, otherwise use today(). Added option to enlarge/pan the picture."
Fixed bug: if it can't find the receipt date from the OCR text then set it as today's date.
If its a bulk process then user will stay in the QA Loop until they say YES this is correct.
On the website, user can change the date.
NEXT: website users should also be alerted.
Removed the option to change the date on "UPLOAD.HTML" and added it to "ITEMS_TEMP.HTML"
Updated UPDATE_ITEMS_TEMP.HTML so that you can't update the date from there (recepit date should only be updated for all rows)
Picture of Receipt: Click to enlarge pan around the image

Examples of Troublesome files:
2020-05-05.jpg  - This picture is an example of when OCR fails - However its a BADLY taken picture.
all_new.jpg     - date isn't on receipt


------------COMMIT:Bulk/Web---------
git commit -m  "Fixed Bugs. Added modal for website users to be alerted when todays date is autopopulated"

        modified:   bulk_code/bulk_upload.py        --> bulk_upload(): nicer print statement
        modified:   bulk_code/bulk_utls.py          --> bulk_upload_qa(): Fixed buggy behaviour
        modified:   routes.py                       --> upload(): updated to include new alert modal
        modified:   templates/Items_temp.html       --> updated to include new alert modal
        new file:   templates/Items_temp_now.html
        modified:   utils.py                        --> bulk_add_grocery_item(): db.session.expunge_all()  # Add this line
                                                        get_upload_date_from_OCRText(): nicer print statement


------------COMMIT:Bulk & Web---------
git commit -m  "Fixed Bugs. Added modal for website users to be alerted when todays date is autopopulated. WIP Alternative LastUpload View"

Add 'total price' to make it easier to see that all the items on the receipt were accounted for.
Bug Fix: Previous comment Removed the option to change the date on "UPLOAD.HTML" and added it to "ITEMS_TEMP.HTML" - The HTML tables also needed to be updated
The order of the receipt items should remain the same as original receipt
Minor changes reducing sum_price_list() calls in order to eventually eliminate the function.
Added Alternative View for Last_Upload page (WIP): End goal is for users to be able to select their own views; Future: defaults can be set based on their devices.

Changes to be committed:
        modified:   bulk_code/bulk_upload.py            --> uts.process_uploaded_file(): returns total price
        modified:   bulk_code/bulk_utls.py              --> cosmetic changes
        modified:   templates/update_items_temp.html    --> See 'Bug Fix'

        modified:   code_helpers/create_metro_df.py     --> sort order code
        modified:   utils.py                            --> sort order code + See 'Minor Change'
        modified:   routes.py                           --> sort order code + total price included in all routes that return Items_temp.html + Bug fix

        modified:   templates/Items_temp.html               --> CSS + JS moved to separate files. date model code
        new file:   static/css/date_warning.css             --> CSS + JS moved to separate files.
        new file:   static/js/date_warning.js               --> CSS + JS moved to separate files.

        modified:   templates/base.html                     --> WIP Alternative LastUpload View
        new file:   templates/grocery_shared_content.html   --> WIP Alternative LastUpload View
        new file:   templates/Items_temp_view2.html         --> WIP Alternative LastUpload View
        new file:   static/js/grocery_common.js             --> WIP Alternative LastUpload View

------------COMMIT:Web---------
git commit -m  "Alternative LastUpload View + organizational and cosmetic changes"
MAIN CHANGE:
Items_temp.html was renamed to 'Last_Upload.html'
Created two views of the Last_Upload HTML (see TwoViews.png)
NEXT if user makes changes in view1 they should return back to view1
OTHER CHANGES:
Organizational Updates: created template/archive folder and added it to gitignore.
    This includes previous versions of HTML files. And Claud examples of changes.
cosmetic update: Deleting TEMP DB Items will give the user a flash message of the items deleted

        modified:   .gitignore                              -> organizational changes
        modified:   routes.py                               -> Items_temp.html was renamed + delete_multiple_items_TempDB() gives flash messages of items deleted
        modified:   static/css/button.css                   -> Fake population button is now purple
        modified:   static/css/main.css                     -> filename modal is now centered on the page
        modified:   static/js/date_warning.js               -> BugFix
        modified:   static/js/grocery_common.js             -> Pop up now has the file image centered

        new file:   templates/Last_upload.html
        new file:   templates/Last_upload__side_by_side.html
        new file:   templates/Last_upload_filename.html
        new file:   templates/Last_upload_footer.html
        new file:   templates/Last_upload_itemtable.html
        new file:   templates/Last_upload_middleButtons.html
        new file:   templates/Last_upload_header.html
        new file:   templates/TwoViews.png

        deleted:    templates/Items_temp - Copy (2).html     -> Moved to archives
        deleted:    templates/Items_temp - Copy.html         -> Moved to archives
        deleted:    templates/Items_temp.html                -> Moved to archives
        deleted:    templates/Items_temp_newversion.html     -> Moved to archives
        modified:   templates/Items_temp_view2.html          -> Moved to archives

------------COMMIT:GUESSING--------
git commit -m  "Fixed Bug and updated logic for two guessing functions and updated print statements"
MAIN CHANGE: In preparation for next step (get first guesses from the Distinct_Grocery_Items.txt
             (so that users don't have to start from scratch when uploading the first few reciepts,
             and also if the database needs to be re-created, this will make that critical error a seemless fix)
FIXED BUG in Guessing uts.clean_produce() was running for produce and non-produce items.
Updated logic for guessing functions: Only guess when there's something to guess. Don't use PRODUCE function for Grocery items
Created print_log function that has a nice header/footer.

        modified:   routes.py                   -> Updated logic '/guess_label_for_new_items/'
        modified:   utils.py                    -> Updated logic guess_labels()

        modified:   code_helpers/create_metro_df.py         -> Updated print statements
        modified:   code_helpers/parse_process_df.py        -> Updated print statements
        modified:   code_helpers/text_mining_metro.py       -> Updated print statements

        deleted:    templates/Items_temp_view2.html         -> Moved to archives
        deleted:    templates/grocery_shared_content.html   -> Moved to archives

        modified:   bulk_code/bulk_upload.py                -> Updated a comment

	------------COMMIT:Bulk--------
git commit -m  "Bulk Uploaded all the recipts into DB. Fixed bugs."
*POPULATED THE DB WITH ALL RECEIPTS IN THE FOLDER*
UserInput BUG: in Bulk Upload when the user type'd YES they still wouldn't exit the loop
Date BUG: When I did the second upload, the 'date on receipt' would become today's date. Fixed that by changing model.py: removed the default date value, instead make it nullable=False.
Try/Catch: When there's an issue with the OCR, the extract date function failed and crashed the program
GUI Update: Removed the ability to accidently delete a row.

        modified:   bulk_code/bulk_utls.py                  -> Cosmetic & userinput bug
        modified:   models.py                               -> Fixed a date bug
        modified:   routes.py                               -> Cosmetic (nicer print statements & renamed functions)
        modified:   utils.py                                -> Added Try/Catch & Cosmetic (nicer print statements & renamed functions)

        deleted:    static/js/date_warning.js                -> this was an exact duplicate of grocery_common.js
        modified:   static/js/grocery_common.js             -> Added warning to user before deleting a row

        modified:   templates/Last_upload__side_by_side.html                            -> Made the side-by-side view the main view
        renamed:    templates/Last_upload.html -> templates/Last_upload__updown.html    -> Made the side-by-side view the main view
        modified:   templates/Last_upload_header.html       -> Added a refresh button to make bulk load easier

        modified:   templates/base.html                     -> Added Search Tab
        modified:   templates/items.html                    -> Cosmetic (Added note for user)

	------------COMMIT:Web--------
git commit -m  "Added Autocomplete to help data quality when updating items. Included jQuery_index.HTML into base.HTML"
TODO BAD CODE: Currently three HTML files should be sharing code
                "update_items_temp.html" and "update_items.html" and "jQuary_index.html"
                "update_items_temp.html" and "update_items.html" have exact duplicate JS code
                I've tried to call the JS through search.js, but it did not work.
                Issue: The search functionality does not work, and in Developer Tools, I get an error.

        modified:   routes.py                           -> added search routes
        modified:   templates/update_items.html         -> added autopopution/search & cleanup code
        modified:   templates/update_items_temp.html    -> added autopopution/search
        modified:   templates/jQuery_index.html         -> Updated to include BASE.HTML
        new file:   static/js/search.js                 -> created the file that should be shared
        modified:   templates/base.html                 -> removed JQuery code

	------------COMMIT:Cleanup--------
git commit -m  "clean up GUI and organized ai output files"

-Cleaned up GUI: "Last_upload.html" and "Last_upload__side_by_side.html" and "Last_upload_header.html"
-Moved 'ai output files' into its own folder: output/out_ai/

        modified:   agent_main.py                               -> using AI_OUT folder
        modified:   config.py                                   -> using AI_OUT folder
        modified:   utils.py                                    -> using AI_OUT folder

        modified:   templates/Last_upload__side_by_side.html    -> Clean up for if no file uploaded
        modified:   templates/Last_upload__updown.html          -> Clean up for if no file uploaded
        modified:   templates/Last_upload_header.html           -> Clean up for if no file uploaded

        modified:   routes.py                                   -> added else print statement

	------------COMMIT:Shopping & Search--------
git commit -m  "Initial commit for Smart Shopping. Updated Search code."
WIP Go Shopping Code
Created a new shopping database and HTML with a new route. Created code for the first population of shopping database.
Created code to convert entire db into a dataframe (code not used)
Search HTML now has an option for an exact search. (This helps fix data quality issues as well)
TODO: WORKFLOW: Upload a receipt will update GROCERY_ITEMS. Only the new uploaded item's frequency should be updated.
TODO: WORKFLOW: Update a single row in GROCERY_ITEMS. Only the new uploaded item's frequency should be updated.
TODO: WORKFLOW: Manually Add new item to GROCERY_ITEMS. Only the new uploaded item's frequency should be updated.

        modified:   templates/base.html                         -> added shopping tab
        new file:   templates/shopping.html                     -> added shopping tab
        new file:   go_shopping/RUN_SHOPPING_FIRST_POPULATE.py  -> populate the new database
        new file:   go_shopping/populate_smart_shopping.py      -> populate the new database
        new file:   go_shopping/__init__.py                     -> na
        new file:   go_shopping/shopping_functions.py           -> function not used
        modified:   models.py                                   -> created new table: Smart_Shopping
        modified:   routes.py                                   -> added shopping() and updated ajax_live_search()
        modified:   templates/jQuery_index.html                 -> Updated to include exact search option
        modified:   utils.py                                    -> updated print statements


	------------COMMIT:Shopping--------
git commit -m  "Smart Shopping add the main functionality"
Worked on the bulk of the shopping code. Created three HTMLs and their routes:
New features:
    smart shopping list calculations based on average interval
    smart shopping summary: give most important items
    under the settings tab, the user can opt out certain categories
    TODO: let users adjust the thresholds. Add an HTML that shows the predicted date calculated, the threashold. And ultimately be able to set different thresholds for specific categories. IE I want my eggs when running low, but pasta after I'm at 0%

        new file:   go_shopping/get_shopping.py            -> main code is called from the website
        new file:   go_shopping/RUN_SHOPPING.py                 -> CLI version: Prints shopping list and summary
        new file:   go_shopping/populate_shop_settings.py       -> called once - to populate the database: Shopping_List_Settings
        modified:   go_shopping/populate_smart_shopping.py      -> updated to simply - category will always be populated
        modified:   models.py                                   -> created new table: Shopping_List_Settings
        modified:   routes.py                                   -> created shopping routes: shopping_settings(), update_shopping_settings(), shopping_list_summary(), shopping_list_page()
        modified:   templates/base.html                         -> added shopping tabs
        modified:   templates/shopping.html                     -> removed edit table features from GUI (user should only update the Grocery_Items table)
        new file:   templates/shopping_list.html->
        new file:   templates/shopping_list_summary.html->
        new file:   templates/shopping_settings.html->


	------------COMMIT:Refactor--------
git commit -m  "Refactored Code"
        modified:   routes.py
        renamed:    templates/Last_upload__updown.html -> templates/Last_upload_phone.html
        renamed:    templates/Last_upload__side_by_side.html -> templates/Last_upload_web.html
        modified:   templates/base.html
        renamed:    templates/update_items.html -> templates/update_item.html


	------------COMMIT:AI--------
git commit -m  "AI works again after website code changed"

receipt_date is no longer being written to OCR_text.csv
creating file for AI to read:
    When GROCERY_ITEMS is bulk uploaded, myItems are being stored in a list with the upload_date.
    Then myItems and Upload_date are writen to file: send_to_ai.txt
    aka
    The AI reads this file, cateorgizes it as perishable or not, calculates expiry_date,
    The AI resposne is stored in a text file with the timestamp in its name.
Added the line "app.config.from_object(Config)" because CONFIG wasn't getting all the keys.

        modified:   agent_main.py   -> fixing bugs that occured because the Website funcations have changed.
        modified:   utils.py        -> updated: get_upload_items(), bulk_add_grocery_item()



	------------COMMIT:AI--------
git commit -m  "Saving AI response to later read from the website"
The main commit is the grumpy_agent.py; it called a helloworld agent and saves the response, and uses code from google's website to read parts of the response.
This is a toy example to be used for agent_main. Ran into my 'daily requests limits'
bulk_code/bulk_upload.py: Added the line "app.config.from_object(Config)" because CONFIG wasn't getting all the keys.

        new file:   GIT_COMMITS.md                          -> commiting all my historical comments
        new file:   ai/grumpy_agent.py                      -> working example of a simple agent json dump with additioanl example code
        modified:   bulk_code/bulk_upload.py                -> to be safe, added config code

        moved:    agent_main.py -> ai/agent_main.py         
        moved:    ai/agent_web.py -> ai/testing/agent_web.py
        moved:    ai/agents.py -> ai/testing/agents.py
        moved:    ai/my_agent.py -> ai/testing/my_agent.py

	------------COMMIT:AI--------
git commit -m  "Agent retrieves facts about food items and displays it on the website"
User Uploads new receipt. Once that receipt is saved to the Database, user clicks on Predict Expiry Tab:
route /ai_response/ calls ai_predictedExpiry() in ai_predictedExpiry.py and then brings up 'ai_predictedExpiry.html'

        modified:   .gitignore
        modified:   GIT_COMMITS.md
        modified:   README.md
        modified:   ai/agent_main.py                        -> call AI Agent and write JSON file
        new file:   ai/ai_predictedExpiry.py                -> read JSON file and send to router
        modified:   config.py
        modified:   routes.py
        new file:   templates/ai_predictedExpiry.html       -> shows food facts from AI in table form
        modified:   templates/base.html

	------------COMMIT:AI--------
git commit -m  "refactored ai"
        renamed:    ai/agent_main.py -> ai/agent_predictedExpiry.py
        modified:   ai/ai_predictedExpiry.py



	------------COMMIT:AI--------
git commit -m  "Updated NavBar, Created new model, AI Logic, fixed ai bug"
First Fix the BUG: ai_food_facts.csv was only saving the last item.
Updated NavBar to include dropdowns.
Created a new database table, to capture the food and its expiry dates
Removed the old functionality of ai_predictedExpiry() being called from NavBar

Changes to AI logic: Only new items that were not previously classified go to the AI
OOPS: accidently deleted all rows from the database by running the code:
    with app.app_context():
        db.drop_all()
        db.create_all()

        modified:   models.py                   --> Added a new model: Food_Expiry
        modified:   ai/ai_predictedExpiry.py    --> Updated logic to reduce AI calls
        modified:   config.py                   --> new JSON and text files
        modified:   utils.py                    --> four new functions
                                                    get_EST_WEEKS(search)
                                                    parse_date(date_str: str | None) 
                                                    populate_food_expiry_from_json() 
                                                    populate_food_expiry_existing_items(existing_item_dic, upload_date)
        modified:   routes.py                   --> no longer called from the NavBar: ai_predictedExpiry() 
        modified:   go_shopping/shopping_functions.py   --> import statement
        new file:   templates/ai.html
        modified:   templates/base.html         --> Add DropDown to NavBar
        new file:   templates/food_exp.html
        deleted:    ai/grumpy_agent.py


	------------COMMIT:GENERAL--------
git commit -m  "Bug Fixes"
Update bug - Website crashed if item was updated.
Filename bug - the picture kept disappearing. this was because the get_filename() needed to be updated
Delete Food_Expiry: created routes and links in Delete.html to delete the table. Updated other delete routes to be more consistant.

        modified:   routes.py							--> Update Temp Item bug + Added Delete Food_Expiry
        modified:   templates/Last_upload_phone.html	--> Update Temp Item bug
        modified:   templates/Last_upload_web.html		--> Update Temp Item bug
        modified:   templates/update_items_temp.html	--> Update Temp Item bug
        modified:   templates/base.html					--> labels updated
        modified:   utils.py							--> filename bug
        modified:   templates/delete.html

	------------COMMIT:GENERAL--------
git commit -m  "Cosmetic GUI Updates"
GUI updates: Delete page was split into delete.html and settings.html

        modified:   utils.py                            --> temp commented ai call when user saves
        modified:   routes.py                           --> created new route for settings.html
        modified:   templates/Last_upload_phone.html    --> h1 updates
        modified:   templates/Last_upload_web.html      --> h1 updates
        modified:   templates/home.html                 --> added links in boxes
        modified:   templates/base.html                 --> updated labels for links
        modified:   templates/delete.html               --> delete tabel links only
        new file:   templates/settings.html             --> save CSV link only: "Distinct_Grocery_Items.csv"


	------------COMMIT:MONSTER COMMIT:--------
git commit -m  "MAJOR UPDATES in Logic: Bulk_Add, Guess_Labels, New DB table: CurrentFood New HTMLs and Routes"
NEW DATABASE: CurrentFood -> Purchase Date, Item, classification, EST_WEEKS, ExpiryDate
        Remove items from Food_Expiry that have expired
User is able to correct EST_WEEKS received from AI, and it also updates the FOOD_FACTS DB
ROUTE UPDATES: 
        added route for: current_food(), update_foodexp(id), export_food_facts()
        , delete_all() deletes 7 tables, 
        fixed bugs
        removed home(), and now index.html points to homepage('/')
            temp routes to be merged later '/' & '/index/' & '/index2/' & '/all_tables/'
bulk_add_grocery_item UPDATES: 
    after Grocery_Items is updated, get EST_WEEKS from Food_Expiry or AI
    populate the Food_Expiry, current_food, Smart Shopping, Shopping Settings
guess_labels_from_DB UPDATES:
    if label is not in GROCERY_ITEMS database table, then read CSV: Distinct_Grocery_Items(storeItem) 


        modified:   README.md                                       --> formatted and more detailed.
        modified:   models.py                                       --> Added CurrentFood
        modified:   ai/agent_predictedExpiry.py                     --> Changed {Items_Bought} to {+Items_Bought+} 
        modified:   ai/ai_predictedExpiry.py                        --> save_food_facts() now saves a JUMP and CSV
        new file:   ai/populate_current_food.py                     --> run once to populate db
        modified:   config.py
        modified:   go_shopping/RUN_SHOPPING_FIRST_POPULATE.py      --> note updated TODO: update one row code
        modified:   go_shopping/get_shopping.py                     --> updated to Config.MIN_PURCHASE
        modified:   go_shopping/populate_shop_settings.py           
        modified:   go_shopping/populate_smart_shopping.py          --> fixed a bug: purchases[0]
        modified:   routes.py                                       --> See NOTES above
        modified:   templates/base.html                             --> Added and updates links
        new file:   templates/current_food.html                     --> new page for new table
        new file:   templates/update_food_exp.html                  --> new page for new table
        modified:   templates/delete.html                           --> link to delete 5 or 7? tables (CONFIRM THIS)
        new file:   templates/groceries.html                        --> this was index.html; standardized: if no rows message
        deleted:    templates/home.html 
        modified:   templates/index.html                            --> now the homepage
        new file:   templates/index2.html                           --> now the homepage v2
        new file:   templates/wha.html                              --> now the homepage v3
        modified:   templates/food_exp.html                         --> standardized: if no rows message
        modified:   templates/items.html                            --> standardized: if no rows message
        modified:   templates/shopping.html                         --> standardized: if no rows message
        modified:   templates/update_item.html                      --> bug fix in submit link
        modified:   utils.py                                        --> MAJOR UPDATES: see notes



	------------COMMIT:AI SCOPE BUG--------
git commit -m  "FIXED AI BUG & changed log settings"

The AI BUG: I called both the files below, and it only printed 
--- UNCOMMITED OUT---> call AI
--- UNCOMMITED OUT---> call AI
without actually calling the AI - no print statements inside ai_predictedExpiry.py were executed and the following
FILES were NOT UPDATED:
ai_response.json
ai_food_facts_dump_2026-03-31_16-27-55.json
ai_food_facts.csv

THE REASON was that since the AGENT was being executed upon import - the first time python imports, it caches everything.
The second time the same imports are run, it just runs from cache. So it was getting the AGENT call from CACHE! 

agent_predictedExpiry.py
the runner and prompt definition needs to be called inside the function, otherwise, the agent will be called upon import, instead of when I call the function.
async def run_agent_query():
    runner = InMemoryRunner(agent=combined_flow)
    my_prompt = "get the classification for the list of items and then calculate the predicted_expiry_date for each item"

ai_predictedExpiry.py
the 
    import importlib
    import ai.agent_predictedExpiry as agent_module
    importlib.reload(agent_module)  # reloads the module
    asyncio.run(agent_module.run_agent_query())  # calls the fresh function. Also this blocks until the agent finishes

        modified:   ai/agent_predictedExpiry.py             --> fix scoping bug (see notes)
        modified:   ai/ai_predictedExpiry.py                --> fix scoping bug (see notes)
        modified:   app.py                                  --> updated log settings to remove extra lines (Called CSS, or JS each time a webpage propagates)
        modified:   go_shopping/populate_shop_settings.py   --> cosmetic (better print error statement)
        modified:   go_shopping/populate_smart_shopping.py  --> cosmetic (better print error statement)
        modified:   routes.py                               --> removing unnecessary ai routes

	------------COMMIT:Created DEV vs PROD code:--------
git commit -m  "Updated CONFIG file to create a separate DEV and PROD codebase"
git cloned onto RaspberryPi, and now I need to have DEV code (in Windows) and a PROD code (for Linux)
config file now has 3 classes in a hierarchy: Config -> DevConfig, ProdConfig

            modified:   config.py                           --> Major updates here (See notes)
            modified:   app.py                              --> Updated to use the new CONFIG file structure
            modified:   ai/testing/agent_web.py             --> file note used: removed error just to get ride of pycharm's red line




	------------COMMIT:<NEXT>--------
git commit -m  "Nonetnch"



Tasks:
## TODO: when you upload a new receipt, it should fill empty (secondary) by looking up the txt file.
-Guessing: Use the CSV to help guess. Think about the priority: exact matches with your database, fuzzy with your db, then other csv?
## TODO: tried to have the agent get receips too but had Agent broke.
## TODO: have website display AI results
-Understand where I was last time: agent_main.py
-Get receipes based on the last receipt bought.



	------------NEXT COMMIT--------
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

NEXT:
• 	AI connection to Google Calendar. If meeting happens at dinner time, then assume you're eating out. Adjust this weeks freq.
• 	AI search for a receipe based on your last receipt.
• 	Replenishment reminders — “You typically run out of coffee every 23 days.”
• 	Price-drop alerts — notify when an item they buy frequently is cheaper at another store.
• 	Meal planning suggestions — based on what they already bought and what’s expiring soon.


NICE TO HAVES:
- When hit the back button - and I've already uploaded a receipt and it hasn't been deleted or saved, and I click on Upload Receipt again - It doesn't give user a message why its not working.
- Create a "TEST_MODE" where I can upload to the database and not message up actual historical record.
- VERBOSE is currently for everything; offer options where it can be for some features.




