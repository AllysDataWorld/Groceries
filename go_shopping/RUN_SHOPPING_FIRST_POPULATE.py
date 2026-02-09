
from go_shopping.populate_smart_shopping import populate_smart_shopping
from app import app

# In your Flask app or script
with app.app_context():
    populate_smart_shopping()
    
    
    
# THIS DOESN"T REALLY HLEP BUT KEEPING THE CODE    
# from smart_shopping_utils import update_single_item_smart_shopping
#
# # After saving a new grocery item
# new_item = Grocery_Items(myItem='milk', ...)
# db.session.add(new_item)
# db.session.commit()
#
# # Update Smart_Shopping for this item
# update_single_item_smart_shopping('milk')