
from go_shopping.populate_smart_shopping import populate_smart_shopping
from go_shopping.populate_shop_settings import populate_shop_settings
from app import app


# In your Flask app or script
with app.app_context():
    populate_smart_shopping()
    populate_shop_settings()
    

    
# UPDATE FOR ONE ITEM:
# from smart_shopping_utils import update_single_item_smart_shopping
#
# # After saving a new grocery item
# new_item = Grocery_Items(myItem='milk', ...)
# db.session.add(new_item)
# db.session.commit()
#
# # Update Smart_Shopping for this item
# update_single_item_smart_shopping('milk')