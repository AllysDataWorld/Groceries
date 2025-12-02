import csv
import os
from datetime import datetime

from app import app, logger, session
from models import Groceries, Grocery_Items, Grocery_TEMP_Items
import utils as uts
from database import db

from flask import render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from code_helpers.levenshtein_distance import levenshtein_distance


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
    
    filename = uts.get_filename() if new_matches else ''
    temp_items = Grocery_TEMP_Items.query.order_by(Grocery_TEMP_Items.recepitDate.desc()).all()
    return render_template('Items_temp.html', filename=filename, tasks=temp_items)

@app.route('/bulk_insert/')
def bulk_insert():
    """Save all temp items to main database."""
    unpopulated = uts.get_unpopulated_items()
    if unpopulated:
        flash("Please complete all required fields before saving:")
        for i, item in enumerate(unpopulated):
            flash(f"Row {i+1}: Missing required information")
        return redirect('/last_upload/')
    
    temp_items = Grocery_TEMP_Items.query.all()
    if not temp_items:
        flash("No items to save")
        return redirect('/upload/')
    
    # Calculate totals and create main receipt record
    total_price = uts.sum_price_list([item.price for item in temp_items])
    store_name = temp_items[0].storeName

    temp_ocr = os.path.join(app.config['TEMP_FOLDER'], 'OCR_text.csv')
    with open(temp_ocr, 'r') as f:
        raw_text = f.read()
    
    receipt_id = uts.add_raw_receipt(raw_text, store_name, total_price, uts.get_filename())
       

    send_to_ai = [temp_item.myItem for temp_item in temp_items]
    output_ai = os.path.join(app.config['OUTPUT_FOLDER'], 'send_to_ai.csv')
    with open(output_ai, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(send_to_ai)
    
    # Bulk insert items
    grocery_items = []
    for temp_item in temp_items:
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
    
    logger.info(f"Inserted {len(grocery_items)} items into Grocery_Items")
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

# Routes - Updates and Deletes
# @app.route('/update_date/')
# def update_date():
#     """Update receipt date for all temp items."""
#     new_date = uts.get_toronto_time()
#     session.query(Grocery_TEMP_Items).update({
#         Grocery_TEMP_Items.recepitDate: new_date
#     })
#     session.commit()
    
#     temp_items = Grocery_TEMP_Items.query.order_by(Grocery_TEMP_Items.recepitDate.desc()).all()
#     return render_template('Items_temp.html', filename=uts.get_filename(), tasks=temp_items)

# Delete routes
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

# Update routes
@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def update_receipt(id):
    """Update a receipt."""
    receipt = Groceries.query.get_or_404(id)
    
    if request.method == 'POST':
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
        item.storeName = request.form['updated_storeName']
        item.storeCategory = request.form['updated_storeCategory']
        item.storeItem = request.form['updated_storeItem']
        item.myCategory = request.form['updated_myCategory']
        item.myItem = request.form['updated_myItem']
        item.price = uts.convert_price(request.form['updated_price'])
        
        new_date = uts.convert_date(request.form['updated_date'])
        if item.recepitDate.date() > new_date:
            item.recepitDate = new_date
        
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
    
    if request.method == 'POST':
        item.storeName = request.form['updated_storeName']
        item.storeCategory = request.form['updated_storeCategory']
        item.storeItem = request.form['updated_storeItem']
        item.myCategory = request.form['updated_myCategory']
        item.myItem = request.form['updated_myItem']
        item.price = uts.convert_price(request.form['updated_price'])
        
        new_date = uts.convert_date(request.form['updated_date'])
        if item.recepitDate.date() > new_date:
            item.recepitDate = new_date
        
        try:
            db.session.commit()
            return redirect('/last_upload/')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating temp item: {e}")
            return 'Error updating temp item'
    
    return render_template('update_items_temp.html', task=item)

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
    temp_items = Grocery_TEMP_Items.query.order_by(Grocery_TEMP_Items.recepitDate.desc()).all()
    filename = uts.get_filename() if temp_items else ''
    return render_template('Items_temp.html', filename=filename, tasks=temp_items)

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
    receipt_date = request.form.get('recepitDate')

    logger.info(f"\nUploaded: {filename}")
    print(f"\nUploaded: {filename}")
    flash(f"Uploaded: {filename}")
    
    bought_once, frequent_items = uts.process_uploaded_file(file_path, store, filename, receipt_date)
    
    if bought_once:
        flash(f"{len(bought_once)} items bought once before")
        for item, date in bought_once.items():
            days_ago = uts.how_long_ago(date)
            flash(f"{item} was bought {days_ago} ago")
    
    if frequent_items:
        flash(f"{len(frequent_items)} frequent items found")
        for count, item in frequent_items.items():
            flash(f"{item} bought {count} times before")

    temp_items = Grocery_TEMP_Items.query.order_by(Grocery_TEMP_Items.recepitDate.desc()).all()
    return render_template('Items_temp.html', filename=filename, tasks=temp_items)
