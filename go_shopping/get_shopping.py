from datetime import datetime
from models import Smart_Shopping, Shopping_List_Settings
from database import db


def get_shopping_list(threshold=0.8, min_purchases=3):
    """
    Generate a smart shopping list based on purchase patterns and depletion prediction.
    Filters out categories based on user settings.

    Args:
        threshold: Float between 0-1. Suggest items when (days_since_last / avg_interval) >= threshold
                   Default 0.8 means suggest when 80% of typical interval has passed
        min_purchases: Minimum number of purchases needed to include item in predictions
                       Default 3 ensures we have reliable data

    Returns:
        List of dictionaries containing shopping list items with priority scores
    """

    today = datetime.now().date()
    shopping_list = []

    # Get excluded categories from settings
    excluded_categories = db.session.query(Shopping_List_Settings.myCategory) \
        .filter(Shopping_List_Settings.include_in_shopping_list == False) \
        .all()
    excluded_categories = [cat[0] for cat in excluded_categories]

    # Get all items with sufficient purchase history
    query = Smart_Shopping.query.filter(
        Smart_Shopping.purchase_count >= min_purchases,
        Smart_Shopping.average_interval.isnot(None)
    )

    # Filter out excluded categories
    if excluded_categories:
        query = query.filter(~Smart_Shopping.myCategory.in_(excluded_categories))

    items = query.all()

    for item in items:
        # Calculate days since last purchase
        last_purchase = item.last_purchase_date.date() if isinstance(item.last_purchase_date,
                                                                     datetime) else item.last_purchase_date
        days_since_last = (today - last_purchase).days

        # Calculate priority score
        if item.average_interval > 1:
            priority_score = days_since_last / item.average_interval
        else:
            priority_score = 0

        # Only suggest items that meet the threshold
        if priority_score >= threshold:
            # Calculate predicted need date
            from datetime import timedelta
            predicted_need_date = last_purchase + timedelta(days=int(item.average_interval))

            # Determine urgency level
            if priority_score >= 1.2:
                urgency = "OVERDUE"
            elif priority_score >= 1.0:
                urgency = "BUY NOW"
            elif priority_score >= 0.9:
                urgency = "BUY SOON"
            else:
                urgency = "CONSIDER"

            shopping_list.append({
                'item': item.myItem,
                'category': item.myCategory,
                'priority_score': round(priority_score, 2),
                'urgency': urgency,
                'days_since_last': days_since_last,
                'average_interval': round(item.average_interval, 1),
                'last_purchase_date': last_purchase,
                'predicted_need_date': predicted_need_date,
                'preferred_store': item.preferred_store,
                'typical_price': item.typical_price,
                'typical_quantity': item.typical_quantity,
                'purchase_count': item.purchase_count
            })

    # Sort by priority score (highest first)
    shopping_list.sort(key=lambda x: x['priority_score'], reverse=True)

    return shopping_list



def get_shopping_list_summary(threshold=0.8, min_purchases=3):
    """
    Get a summary of the shopping list with statistics.

    Returns:
        Dictionary with summary stats and categorized items
    """

    shopping_list = get_shopping_list(threshold=threshold, min_purchases=min_purchases)

    # Categorize by urgency
    overdue = [item for item in shopping_list if item['urgency'] == 'OVERDUE']
    buy_now = [item for item in shopping_list if item['urgency'] == 'BUY NOW']
    buy_soon = [item for item in shopping_list if item['urgency'] == 'BUY SOON']
    consider = [item for item in shopping_list if item['urgency'] == 'CONSIDER']

    # Calculate estimated total cost
    total_cost = sum([item['typical_price'] * item['typical_quantity']
                      for item in shopping_list
                      if item['typical_price'] is not None])

    # Group by category
    by_category = {}
    for item in shopping_list:
        cat = item['category'] or 'Uncategorized'
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)

    return {
        'total_items': len(shopping_list),
        'overdue_count': len(overdue),
        'buy_now_count': len(buy_now),
        'buy_soon_count': len(buy_soon),
        'consider_count': len(consider),
        'estimated_cost': round(total_cost, 2),
        'overdue_items': overdue,
        'buy_now_items': buy_now,
        'buy_soon_items': buy_soon,
        'consider_items': consider,
        'by_category': by_category,
        'full_list': shopping_list
    }


