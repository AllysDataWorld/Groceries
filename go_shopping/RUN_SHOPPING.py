
from go_shopping.get_shopping import get_shopping_list, get_shopping_list_summary
from app import app

# In your Flask app or script
with app.app_context():
    # Get items that are 80% through their cycle
    shopping_list = get_shopping_list()


    for item in shopping_list:
        print(f"{item['urgency']}: {item['item']} - Last bought {item['days_since_last']} days ago")


    summary = get_shopping_list_summary()

    print(f"Shopping List Summary:")
    print(f"  Total items: {summary['total_items']}")
    print(f"  Overdue: {summary['overdue_count']}")
    print(f"  Buy now: {summary['buy_now_count']}")
    print(f"  Estimated cost: ${summary['estimated_cost']}")

    print("\nOVERDUE ITEMS:")
    for item in summary['overdue_items']:
        print(f"  - {item['item']} (should have bought {item['days_since_last'] - item['average_interval']:.0f} days ago)")