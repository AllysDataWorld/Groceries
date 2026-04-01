

from models import Grocery_Items, Shopping_List_Settings
from database import db

def populate_shop_settings():
    """
    Populate/refresh the Shopping Settings table categories from Grocery_Items.
    Calling this function should then update the shopping list.
    """

    # Clear existing Smart_Shopping data
    Shopping_List_Settings.query.delete()
    db.session.commit()

    # Get all distinct items (group by myItem)
    distinct_Category = db.session.query(Grocery_Items.myCategory) \
        .filter(Grocery_Items.myCategory.isnot(None)) \
        .distinct() \
        .all()

    print(f"Processing {len(distinct_Category)} distinct categories...")

    cat_list = [myCat for myCat in distinct_Category]

    # Bulk insert items
    cat_items = []
    for temp_item in cat_list:
        item_data = {
            'myCategory': temp_item.myCategory,
            'include_in_shopping_list': True,
        }
        cat_items.append(Shopping_List_Settings(**item_data))
    try:
        db.session.bulk_save_objects(cat_items)
        db.session.commit()
        print(f"Successfully populated Smart_Shopping with {len(cat_list)} items")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error populating Smart_Shopping: {e}")
        return False


