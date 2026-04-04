from datetime import datetime
from models import Grocery_Items, Smart_Shopping
from database import db
import statistics


def populate_smart_shopping():
    """
    Populate/refresh the Smart_Shopping table with aggregated data from Grocery_Items.
    This function should be called whenever Grocery_Items is updated.
    """

    # Clear existing Smart_Shopping data
    Smart_Shopping.query.delete()
    db.session.commit()

    # Get all distinct items (group by myItem)
    distinct_items = db.session.query(Grocery_Items.myItem) \
        .filter(Grocery_Items.myItem.isnot(None)) \
        .distinct() \
        .all()

    print(f"Processing {len(distinct_items)} distinct items...")

    for item_tuple in distinct_items:
        item_name = item_tuple[0]

        # Get all purchases of this item, ordered by date
        purchases = Grocery_Items.query \
            .filter_by(myItem=item_name) \
            .order_by(Grocery_Items.recepitDate.asc()) \
            .all()

        if not purchases:
            continue

        # Basic data
        purchase_count = len(purchases)
        first_purchase = purchases[0].recepitDate
        last_purchase = purchases[-1].recepitDate

        # my_category = purchases[0].myCategory #replace the code below.
        # Get myCategory (use most recent non-null value)
        my_category = None
        for p in reversed(purchases):
            if p.myCategory:
                my_category = p.myCategory
                break

        # Calculate average interval and standard deviation
        average_interval = None
        std_deviation = None

        if purchase_count >= 2: # Calculate intervals between 2 consecutive purchases
            intervals = []
            for i in range(1, len(purchases)):
                prev_date = purchases[i - 1].recepitDate
                curr_date = purchases[i].recepitDate
                interval_days = (curr_date - prev_date).days
                intervals.append(interval_days)

            # Calculate statistics
            average_interval = statistics.mean(intervals)

            if len(intervals) >= 2:
                std_deviation = statistics.stdev(intervals)

        # Calculate typical price (median or average of non-null prices)
        prices = [p.price for p in purchases if p.price is not None]
        typical_price = statistics.median(prices) if prices else None

        # Calculate typical quantity (most common count per receipt, default 1)
        # For now, we'll use 1 as we don't track quantity per item
        typical_quantity = 1

        # Find preferred store (most frequent store)
        store_counts = {}
        for p in purchases:
            store = p.storeName
            store_counts[store] = store_counts.get(store, 0) + 1

        #preferred_store = max(store_counts, key=store_counts.get) if store_counts else 'Metro'
        preferred_store = 'Metro'

        # Create Smart_Shopping entry
        smart_item = Smart_Shopping(
            myItem=item_name,
            myCategory=my_category,
            first_purchase_date=first_purchase,
            last_purchase_date=last_purchase,
            purchase_count=purchase_count,
            average_interval=average_interval,
            std_deviation=std_deviation,
            typical_quantity=typical_quantity,
            typical_price=typical_price,
            preferred_store=preferred_store,
            last_updated=datetime.utcnow()
        )

        db.session.add(smart_item)

    # Commit all changes
    try:
        db.session.commit()
        print(f"Successfully populated Smart_Shopping with {len(distinct_items)} items: {distinct_items}")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error populating Smart_Shopping: {e}")
        return False


def update_single_item_smart_shopping(item_name):
    """
    Update Smart_Shopping for a single item (more efficient for single updates).

    Args:
        item_name: The myItem value to update
    """

    # Get all purchases of this item
    purchases = Grocery_Items.query \
        .filter_by(myItem=item_name) \
        .order_by(Grocery_Items.recepitDate.asc()) \
        .all()

    if not purchases:
        # Item was deleted, remove from Smart_Shopping
        Smart_Shopping.query.filter_by(myItem=item_name).delete()
        db.session.commit()
        return

    # Calculate all statistics (same logic as above)
    purchase_count = len(purchases)
    first_purchase = purchases[0].recepitDate
    last_purchase = purchases[-1].recepitDate

    my_category = None
    for p in reversed(purchases):
        if p.myCategory:
            my_category = p.myCategory
            break

    average_interval = None
    std_deviation = None

    if purchase_count >= 2:
        intervals = []
        for i in range(1, len(purchases)):
            prev_date = purchases[i - 1].recepitDate
            curr_date = purchases[i].recepitDate
            interval_days = (curr_date - prev_date).days
            intervals.append(interval_days)

        average_interval = statistics.mean(intervals)

        if len(intervals) >= 2:
            std_deviation = statistics.stdev(intervals)

    prices = [p.price for p in purchases if p.price is not None]
    typical_price = statistics.median(prices) if prices else None

    typical_quantity = 1

    store_counts = {}
    for p in purchases:
        store = p.storeName
        store_counts[store] = store_counts.get(store, 0) + 1

    preferred_store = max(store_counts, key=store_counts.get) if store_counts else 'Metro'

    # Update or create Smart_Shopping entry
    smart_item = Smart_Shopping.query.filter_by(myItem=item_name).first()

    if smart_item:
        # Update existing
        smart_item.myCategory = my_category
        smart_item.first_purchase_date = first_purchase
        smart_item.last_purchase_date = last_purchase
        smart_item.purchase_count = purchase_count
        smart_item.average_interval = average_interval
        smart_item.std_deviation = std_deviation
        smart_item.typical_quantity = typical_quantity
        smart_item.typical_price = typical_price
        smart_item.preferred_store = preferred_store
        smart_item.last_updated = datetime.utcnow()
    else:
        # Create new
        smart_item = Smart_Shopping(
            myItem=item_name,
            myCategory=my_category,
            first_purchase_date=first_purchase,
            last_purchase_date=last_purchase,
            purchase_count=purchase_count,
            average_interval=average_interval,
            std_deviation=std_deviation,
            typical_quantity=typical_quantity,
            typical_price=typical_price,
            preferred_store=preferred_store,
            last_updated=datetime.utcnow()
        )
        db.session.add(smart_item)

    try:
        db.session.commit()
        print(f"Updated Smart_Shopping for '{item_name}'")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error updating Smart_Shopping for '{item_name}': {e}")
        return False