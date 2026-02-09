


#     matches = uts.find_store_item_matches(storeItem)
#
#     for match in matches:
#         print(f"Matches for {storeItem}: {match.storeItem}")

from models import Grocery_Items, Smart_Shopping

def print_n_log(mystr, logger, header=False, footer=False):  # See print_log in utils
    logger.info(mystr)
    print(mystr)


def convert_db_to_df(logger, thisStore, VERBOSE):
    grocery_db_items = Grocery_Items.query.all()
    num_items = len(grocery_db_items)
    if num_items == 0:
        print("NO ITEMS IN Grocery_TEMP_Items")
        return None

    storeItem, storeCat, myCat, myItm, dat, myPrice = [], [], [], [], [], []

    for i, temp_item in enumerate(grocery_db_items):
        storeItem.append(temp_item.storeItem)
        storeCat.append(temp_item.storeCategory)
        myCat.append(temp_item.myCategory)
        myItm.append(temp_item.myItem)
        dat.append(temp_item.recepitDate)
        myPrice.append(temp_item.price)

    df = pd.DataFrame({
        "storeItem": storeItem,
        "storeCat": storeCat,
        "myCat": myCat,
        "myItm": myItm,
        "dat": dat,
        "myPrice": myPrice
    })

    df.to_csv("df.csv")

    return df