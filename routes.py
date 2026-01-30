import csv
import os
from datetime import date

from app import app, logger
from models import Groceries, Grocery_Items, Grocery_TEMP_Items
import utils as uts
from database import db

from flask import render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from code_helpers.levenshtein_distance import levenshtein_distance


@app.route('/fake_populate_all/')
def fake_populate_all():
    """fake_populate_all - use for testing."""

    all_items = uts.find_store_item_matches("")  # Get all items
    unlabeled_items = uts.get_unlabeled_items()
    total_price = uts.get_totalprice_from_db()

    for row_num, temp_item in enumerate(unlabeled_items):
        clean_item = uts.clean_produce(temp_item.storeItem)

        temp_item.myItem = "myItem"
        temp_item.myCategory = 'myCategory'

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    flash(f"DUMMY Values Populated")
    filename = uts.get_filename()
    temp_items = Grocery_TEMP_Items.query.order_by(Grocery_TEMP_Items.recepitDate.desc()).all()
    return render_template('Items_temp.html',
                           total_price = total_price,
                           current_date=uts.get_date_from_db().date(),
                           filename=filename, tasks=temp_items)






@app.route('/guess_label_for_new_items/')
def guess_label_for_new_items():
    """Use Levenshtein distance to guess labels for new items."""
    
    new_matches = {}
    
    all_items = uts.find_store_item_matches("")  # Get all items
    unlabeled_items = uts.get_unlabeled_items()
    
    for row_num, temp_item in enumerate(unlabeled_items):
        clean_item = uts.clean_produce(temp_item.storeItem)
        logger.info(f"Finding match for item {row_num}: {clean_item}")
        
        distances = {}
        for grocery_item in all_items:
            clean_grocery = uts.clean_produce(grocery_item.storeItem)
            distance = levenshtein_distance(clean_item, clean_grocery)
            distances[distance] = (clean_grocery, grocery_item)
        
        if distances:
            min_distance = min(distances.keys())
            logger.info(f"Best match distance: {min_distance}")
            
            if min_distance < 10:  # Threshold for acceptable match
                best_match = distances[min_distance][1]
                temp_item.myItem = best_match.myItem
                temp_item.myCategory = best_match.myCategory
                new_matches[clean_item] = best_match.myItem
                
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error updating item: {e}")
    
    # Display results
    if new_matches:
        flash(f"{len(new_matches)} new items matched")
        for original, matched in new_matches.items():
            flash(f"{original} → {matched}")
    
    filename = uts.get_filename()
    total_price = uts.get_totalprice_from_db()
    temp_items = Grocery_TEMP_Items.query.order_by(Grocery_TEMP_Items.recepitDate.desc()).all()
    return render_template('Items_temp.html',
                           total_price = total_price,
                           current_date=uts.get_date_from_db().date(),
                           filename=filename, tasks=temp_items)


@app.route('/save_grocery_item/')
def save_grocery_item():
    """Save all temp items to main database."""
    unpopulated = uts.get_unpopulated_items()
    if unpopulated:
        flash("Please complete all required fields before saving:")
        for  item in (unpopulated):
            flash(f"> My_Label or My_Category is missing: {item.storeItem}")
        return redirect('/last_upload/')
    
    temp_items = Grocery_TEMP_Items.query.all()
    if not temp_items:
        flash("No items to save")
        return redirect('/upload/')
  
    grocery_items = uts.bulk_add_grocery_item(temp_items)

    message = f"Inserted {len(grocery_items)} items into Grocery_Items"
    logger.info(message)
    print (message)
    flash(f"Successfully saved {len(grocery_items)} items")
    
    items = Grocery_Items.query.order_by(Grocery_Items.recepitDate.desc()).all()
    return render_template('items.html', tasks=items)



# Routes - Search
@app.route('/search/')
def search():
    """Search page."""
    return render_template('jQuery_index.html')

@app.route("/ajaxlivesearch", methods=["POST"])
def ajax_live_search():
    """AJAX endpoint for live search."""
    search_word = request.form.get('query', '')
    search_pattern = f"%{search_word}%"
    
    if not search_word:
        results = Grocery_Items.query.order_by(Grocery_Items.recepitDate.desc()).limit(5).all()
    else:
        results = Grocery_Items.query.filter(
            or_(
                Grocery_Items.storeName.like(search_pattern),
                Grocery_Items.storeItem.like(search_pattern),
                Grocery_Items.myCategory.like(search_pattern),
                Grocery_Items.myItem.like(search_pattern)
            )
        ).order_by(Grocery_Items.recepitDate.desc()).limit(5).all()
    
    return jsonify({
        'htmlresponse': render_template(
            'jQuery_response.html',
            employee=results,
            numrows=len(results)
        )
    })

# Routes - Manual Entry
@app.route('/add_item/')
def add_item():
    """Manual item entry form."""
    return render_template('add_item.html')

@app.route('/manual_add_receipt/', methods=['GET', 'POST'])
def manual_add_receipt():
    """Handle manual receipt entry."""
    if request.method == 'POST':
        form_data = {
            'storeName': request.form['manual_storeName'],
            'receiptItem': request.form['manual_receiptitem'],
            'price': request.form['manual_price'],
            'myCategory': request.form['manual_my_category'],
            'storeCategory': request.form['manual_StoreCategory'],
            'myItem': request.form['manual_my_item']
        }
        
        # Add to main receipt table
        uts.add_raw_receipt(
            form_data['receiptItem'],
            form_data['storeName'],
            form_data['price'],
            "Manual Entry"
        )
        
        # Add to items table
        item_data = {
            'storeItem': form_data['receiptItem'],
            'myCategory': form_data['myCategory'],
            'storeCategory': form_data['storeCategory'],
            'myItem': form_data['myItem'],
            'storeName': form_data['storeName'],
            'price': uts.convert_price(form_data['price']),
            'recepitDate': uts.get_toronto_time(),
            'filename': "MANUAL ENTRY"
        }
        uts.add_grocery_item(item_data)
        
        return redirect('/items/')
    
    return render_template('add_item.html')


    
########################################################
# Delete routes
########################################################

@app.route('/delete_multiple_items_TempDB/', methods=['POST'])
def delete_multiple_items_TempDB():
    """Delete multiple temp items from the database."""
    item_ids = request.form.getlist('item_ids')
    
    if not item_ids:
        flash('No items selected for deletion', 'warning')
        return redirect('/items_temp/')
    
    try:
        # Convert IDs to integers and delete each item
        deleted_count = 0
        for item_id in item_ids:
            item = Grocery_TEMP_Items.query.get(int(item_id))
            if item:
                db.session.delete(item)
                deleted_count += 1
        
        # Commit all deletions at once
        db.session.commit()
        flash(f'Successfully deleted {deleted_count} item(s)', 'success')
        
    except ValueError:
        db.session.rollback()
        flash('Invalid item ID format', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting items: {str(e)}', 'error')
    
    return last_upload()

@app.route('/delete_all/')
def delete_all():
    """Delete all data from all tables."""
    try:
        Grocery_Items.query.delete()
        Groceries.query.delete()
        Grocery_TEMP_Items.query.delete()
        db.session.commit()
        return render_template('upload.html')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting all data: {e}")
        return 'Error deleting data'

@app.route('/delete_all_Grocery_TEMP_Items/')
def delete_all_temp_items():
    """Delete all temporary items."""
    try:
        Grocery_TEMP_Items.query.delete()
        db.session.commit()
        return redirect('/upload/')
    except Exception as e:
        db.session.rollback()
        return 'Error deleting temp items:', e

@app.route('/delete/<int:id>/')
def delete_receipt(id):
    """Delete a specific receipt."""
    receipt = Groceries.query.get_or_404(id)
    try:
        db.session.delete(receipt)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        db.session.rollback()
        return 'Error deleting receipt:', e

@app.route('/delete_item/<int:id>/')
def delete_item_route(id):
    """Delete a specific grocery item."""
    item = Grocery_Items.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/items/')
    except Exception as e:
        db.session.rollback()
        return 'Error deleting item:', e

@app.route('/delete_temp_item/<int:id>/')
def delete_temp_item(id):
    """Delete a specific temp item."""
    item = Grocery_TEMP_Items.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/last_upload/')
    except Exception as e:
        db.session.rollback()
        return 'Error deleting temp item:',e
    
    
########################################################
# Update routes
########################################################
@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def update_receipt(id):
    """Update a receipt."""
    receipt = Groceries.query.get_or_404(id)
    
    if request.method == 'POST':   
        
        updated = os.path.join(app.config['OUTPUT_FOLDER'], 'Updated_Rows.csv')
        with open(updated, 'a', newline='') as csvfile:
                updatewriter = csv.writer(csvfile)
                updatewriter.writerow("")
                updatewriter.writerow(["ROUTE: /update/"])
        
                updatewriter.writerow(["Update Groceries ORIG ROW", 
                    receipt.storeName,
                    receipt.receiptText,
                    receipt.filename,
                    receipt.subtotal ])
                updatewriter.writerow(["Update Groceries UPDATED ROW", 
                    request.form['updated_storeName'],
                    request.form['updated_receiptText'],
                    request.form['updated_filename'],
                    uts.convert_price(request.form['updated_price'])])        
        
        receipt.storeName = request.form['updated_storeName']
        receipt.receiptText = request.form['updated_receiptText']
        receipt.filename = request.form['updated_filename']
        receipt.subtotal = uts.convert_price(request.form['updated_price'])
        
        new_date = uts.convert_date(request.form['updated_upload_date'])
        if receipt.upload_date.date() > new_date:
            receipt.upload_date = new_date
        

        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating receipt: {e}")
            return 'Error updating receipt'
    
    return render_template('update.html', task=receipt)

@app.route('/update_items/<int:id>/', methods=['GET', 'POST'])
def update_items_route(id):
    """Update a grocery item."""
    item = Grocery_Items.query.get_or_404(id)
    
    if request.method == 'POST':
        
        updated = os.path.join(app.config['OUTPUT_FOLDER'], 'Updated_Rows.csv')
        with open(updated, 'a', newline='') as csvfile:
                updatewriter = csv.writer(csvfile)
                updatewriter.writerow("")
                updatewriter.writerow(["ROUTE: /update_items/"])
        
                updatewriter.writerow(["Update GroceriesITEMS ORIG ROW",
                    item.storeName,
                    item.storeCategory,
                    item.storeItem,
                    item.myCategory,
                    item.myItem,
                    item.price
                    ])
                updatewriter.writerow(["Update GroceriesITEMS UPDATED ROW",
                    request.form['updated_storeName'],
                    request.form['updated_storeItem'],
                    request.form['updated_myCategory'],
                    request.form['updated_myItem'],
                    uts.convert_price(request.form['updated_price'])])          

        item.storeName = request.form['updated_storeName']
        item.storeCategory = request.form['updated_storeCategory']
        item.storeItem = request.form['updated_storeItem']
        item.myCategory = request.form['updated_myCategory']
        item.myItem = request.form['updated_myItem']
        item.price = uts.convert_price(request.form['updated_price'])

        new_date = uts.convert_date_to_format(request.form['updated_date'])
        item.recepitDate = uts.convert_date(new_date)

        try:
            db.session.commit()
            return redirect('/items/')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating item: {e}")
            return 'Error updating item'
    
    return render_template('update_items.html', task=item)

@app.route('/update_items_temp_db/<int:id>/', methods=['GET', 'POST'])
def update_temp_item_route(id):
    """Update a temporary item."""
    item = Grocery_TEMP_Items.query.get_or_404(id)
    filename = uts.get_filename()   
    
    if request.method == 'POST':
        
        updated = os.path.join(app.config['OUTPUT_FOLDER'], 'Updated_Rows.csv')
        with open(updated, 'a', newline='') as csvfile:
                updatewriter = csv.writer(csvfile)
                updatewriter.writerow("")
                updatewriter.writerow(["ROUTE: /update_items_temp_db/"])
        
                updatewriter.writerow(["Update GroceriesITEMS ORIG ROW",
                    item.storeCategory,
                    item.storeItem,
                    item.myCategory,
                    item.myItem,
                    item.price
                    ])
                updatewriter.writerow(["Update GroceriesITEMS UPDATED ROW",
                    request.form['updated_storeItem'],
                    request.form['updated_myCategory'],
                    request.form['updated_myItem'],
                    uts.convert_price(request.form['updated_price'])])           

        item.storeCategory = request.form['updated_storeCategory']
        item.storeItem = request.form['updated_storeItem']
        item.myCategory = request.form['updated_myCategory']
        item.myItem = request.form['updated_myItem']
        item.price = uts.convert_price(request.form['updated_price'])
        

        try:
            db.session.commit()
            return redirect('/last_upload/')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating temp item: {e}")
            return 'Error updating temp item'
        
          
    return render_template('update_items_temp.html', filename=filename, task=item)
    




# Utility routes
@app.route('/home/')
def home():
    """Home page."""
    return render_template('home.html')

@app.route('/delete_page/')
def delete_page():
    """Delete operations page."""
    return render_template('delete.html')


# Routes - Display
@app.route('/')
def index():
    """Main page showing all receipts."""
    receipts = Groceries.query.order_by(Groceries.upload_date.desc()).all()
    return render_template('index.html', tasks=receipts)

@app.route('/items/')
def items():
    """Show all grocery items."""
    items = Grocery_Items.query.order_by(Grocery_Items.recepitDate.desc()).all()
    return render_template('items.html', tasks=items)

@app.route('/last_upload/')
def last_upload():
    """Show items from last upload."""
    temp_items = Grocery_TEMP_Items.query.all()
    filename = uts.get_filename() if temp_items else ''
    curr_date = uts.get_date_from_db().date() if temp_items else ''
    total_price = uts.get_totalprice_from_db()
    return render_template('Items_temp.html',
                           total_price=total_price,
                           current_date=curr_date,
                           filename=filename, tasks=temp_items)


@app.route('/last_upload_view2/')
def last_upload_view2():
    """Show items from last upload."""
    temp_items = Grocery_TEMP_Items.query.all()
    filename = uts.get_filename() if temp_items else ''
    curr_date = uts.get_date_from_db().date() if temp_items else ''
    total_price = uts.get_totalprice_from_db()
    return render_template('Items_temp_view2.html',
                           total_price=total_price,
                           current_date=curr_date,
                           filename=filename, tasks=temp_items)





@app.route('/display/<filename>')
def display_image(filename):
    """Display uploaded image."""
    return redirect(url_for('static', filename=f'uploads/{filename}'), code=301)

# Routes - Upload and Processing
@app.route('/check_last_upload/')
def check_last_upload():
    """Check if there are unsaved temp items."""
    temp_count = len(Grocery_TEMP_Items.query.all())
    if temp_count == 0:
        return redirect('/upload/')
    else:
        flash("You must delete or save the existing rows first")
        return redirect('/last_upload/')


@app.route('/export_distinct_items/')
def export_distinct_items():
    """ MODULE written by Claud
        Export distinct items from Grocery_Items to CSV."""
    try:
      
       # Get distinct combinations of all fields
        distinct_items = db.session.query(
            Grocery_Items.storeName,
            Grocery_Items.storeCategory,
            Grocery_Items.storeItem,
            Grocery_Items.myItem,
            Grocery_Items.myCategory
        ).distinct().order_by(
            Grocery_Items.storeName,
            Grocery_Items.myCategory,
            Grocery_Items.myItem
        ).all() 
        
        # Create CSV filename with timestamp
        #timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        #csv_filename = f'distinct_items_{timestamp}.csv'
        csv_filename = "Distinct_Grocery_Items.csv"
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
        logger.info(f"Exported {len(distinct_items)} distinct items to {csv_filename}")
        flash(f"Successfully exported {len(distinct_items)} distinct items to {csv_filename}")
        return redirect('/delete_page/')
        
    except Exception as e:
        logger.error(f"Error exporting distinct items: {e}")
        flash(f"Error exporting items: {str(e)}")
        return redirect('/delete_page/')


@app.route('/change_recepit_date/', methods=['GET', 'POST'])
def change_recepit_date():
    receipt_date = request.form.get('recepitDate') # This will be 'YYYY-MM-DD'
    if receipt_date:
        # Convert to your desired format
        formatted_date = uts.convert_date_to_format(receipt_date)
        formatted_date = uts.convert_date(formatted_date)

        db.session.query(Grocery_TEMP_Items).update({
            Grocery_TEMP_Items.recepitDate: formatted_date
        })
        db.session.commit()
    else:
        flash("Date Field is empty")

    total_price = uts.get_totalprice_from_db()
    filename = uts.get_filename()
    temp_items = Grocery_TEMP_Items.query.order_by(Grocery_TEMP_Items.recepitDate.desc()).all()
    return render_template('Items_temp.html',
                           total_price = total_price,
                           current_date=uts.get_date_from_db().date(),
                           filename=filename, tasks=temp_items)





########################################################
# UPLOAD routes
########################################################

@app.route('/upload/', methods=['GET', 'POST'])
def upload():

    """Handle file upload and processing."""
    if request.method == 'GET':
        return render_template('upload.html')
    
    # Validate file upload
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if not (file and uts.allowed_file(file.filename)):
        flash('Invalid file type')
        return redirect(request.url)
    
    # Process upload
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Get form data
    store = request.form.get('storeName') or request.form.get('store_name_options')

    logger.info(f"\nUploaded: {filename}")
    print(f"\nUploaded: {filename}")
    flash(f"Uploaded: {filename}")
    
    bought_once, frequent_items, total_price = uts.process_uploaded_file(file_path, store, filename, "", False)
    
    if bought_once:
        flash(f"{len(bought_once)} items bought once before")
        for item, thisdate in bought_once.items():
            days_ago = uts.how_long_ago(thisdate)
            flash(f"{item} was bought {days_ago} ago")
    
    if frequent_items:
        flash(f"{len(frequent_items)} frequent items found")
        for count, item in frequent_items.items():
            flash(f"{item} bought {count} times before")

    #uts.uploaded_items_to_ai()

    current_date = uts.get_date_from_db().date()
    today_date = uts.convert_date(date.today())
    show_date_warning = (current_date == today_date)
    #print(f"current_date: {current_date} \ntoday_date: {today_date} \nif statement is {show_date_warning}")

    temp_items = Grocery_TEMP_Items.query.order_by(Grocery_TEMP_Items.recepitDate.desc()).all()
    return render_template('Items_temp.html',
                           current_date=current_date,
                           total_price = total_price,
                           show_date_warning=show_date_warning,
                           filename=filename, tasks=temp_items)