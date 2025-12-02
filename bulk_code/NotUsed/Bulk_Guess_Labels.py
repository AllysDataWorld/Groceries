from database import db
from models import Grocery_Items
from app import logger
from sqlalchemy import or_, select
import utils as uts

"""The difference between this code and the main code is that 
    one gets the bought items as a list, and the other gets it as ...something else"""

def guess_labels_bulk(db_items): 
    """     
    query GroceryItems for labels
    for each row in GroceryItems
      get the storeItem
      query GroceryItems for that storeItem
      populate the GroceryItems
    """
    
    bought_once_dic = {}
    freq_item_dic = {}
    item_and_cat = {}
    
    user_input = input(f'Guess Labels: Verbose Press 1:    ')
    if int(user_input) == 1:
        GL_PRNSTMT = True
    else:
        GL_PRNSTMT = False
        
    
    if GL_PRNSTMT: print("start guess_labels_bulk: ?GLB")
  
    for i, this_item in enumerate(db_items):
        if GL_PRNSTMT: print(f"\n?GLB****** {i}:{this_item} ******\n"  )    
        
        if this_item == "":
            if GL_PRNSTMT: print(f"?GLB BLANK ITEM found @ index:{i}, item name:{this_item}")
        else:        
            queried_tasks = uts.find_store_item_matches(this_item)
            
            if len(queried_tasks) == 0:
                if GL_PRNSTMT: print("?GLB No Guesses; This is a new item")
                #new_item_dic = find_possible_matches(this_item, i, new_item_dic)
                pass
              
            elif len(queried_tasks) == 1:
                if GL_PRNSTMT: print(f"\n?GLB Bought this once before {this_item}")
                for finditem in queried_tasks:
                    if GL_PRNSTMT: print("?GLB Table Row:", finditem.id, finditem.storeItem, finditem.myItem, finditem.myCategory)
                    myItem = finditem.myItem
                    myCategory = finditem.myCategory
                    boughtDT = finditem.recepitDate.date()
                    bought_once_dic[myItem] = boughtDT
                    item_and_cat[finditem.storeItem] = (myItem, myCategory)
                                        
            else:
                if GL_PRNSTMT: print(f"\n?GLB Bought {this_item} - {len(queried_tasks)} times before!")
                for finditem in queried_tasks:
                    if GL_PRNSTMT: print("?GLB Many Times:", finditem.id, finditem.storeItem, finditem.myItem, finditem.myCategory)
                    myItem = finditem.myItem
                    myCategory = finditem.myCategory   
                    item_and_cat[finditem.storeItem] = (myItem, myCategory)
                    freq_item_dic[len(queried_tasks)] = myItem


    if GL_PRNSTMT: print("\n\t?GLB SUMMARY\n")
        
    for key, value in item_and_cat.items():
        my_message = f"?GLB {key} was found in db with: {value}, aka def:how_long_ago(boughtDT) days ago!"
        if GL_PRNSTMT: print(my_message)
        logger.info(my_message)
              
    if len(bought_once_dic) == 0 and len(freq_item_dic) == 0:
        if GL_PRNSTMT: print("?GLB All new items")
        if GL_PRNSTMT: print (f"?GLB *****************\n All new items \n**********************")

    else:        
        if len(bought_once_dic) > 0:
            if GL_PRNSTMT: print (f"?GLB *****************\n {len(bought_once_dic)} items have been bought once\n**********************")
            for key, value in bought_once_dic.items():
                my_message = f"{key} was bought once before on {value}, aka def:how_long_ago(boughtDT) days ago!"
                if GL_PRNSTMT: print(my_message)
                logger.info(my_message)

            
        if len(freq_item_dic) > 0:
            if GL_PRNSTMT: print(f"?GLB *****************\n {len(freq_item_dic)} items have been bought frequently\n**********************")
            for key, value in freq_item_dic.items():
                my_message = f"{value} is a FREQUENT ITEM, and has been bought {key} times before!"
                if GL_PRNSTMT: print(my_message)
                logger.info(my_message)

    if GL_PRNSTMT: print("?GLB end guess_labels_bulk")
    with open('GuessedItems.txt', 'w') as f:
        print(item_and_cat, file=f)
    return item_and_cat




def guess_label_for_new_items():
   
    new_item_dic = {}
    all_items = uts.find_store_item_matches("") #get all Grocery_ITEM items   
    unlabeled_items = get_unlabeled_items()
    
    for rownum, tempRow in enumerate(unlabeled_items):
        this_item = clean_produce(tempRow.storeItem)
        logger.info(f"\n\n********\nPOSSIBLE MATCH for item: {rownum}:{this_item}\n***********************\n")
        distance = 0
        tempDic = {}
        for grItem in all_items:
            gr_storeItem = clean_produce(grItem.storeItem)
            distance = levenshtein_distance(this_item, gr_storeItem)
            tempDic[distance] = (gr_storeItem, grItem.storeItem)
            logger.info(f"Distance:{distance}: {this_item} -> {gr_storeItem}")
        
        min_key = min(tempDic.keys())
        logger.info(f"The minimum key is: {min_key} which is {tempDic[min_key][1]}") 
        
        if min_key < 10:
            query_min = uts.find_store_item_matches(tempDic[min_key][1])
            for founditem in query_min:                
                logger.info(f"Min Difference Item: ID:{founditem.id}, ITEM:{founditem.storeItem}, MyItem:{founditem.myItem}, MyCat:{founditem.myCategory}")
            
            tempRow.myItem = founditem.myItem
            tempRow.myCategory = founditem.myCategory   
            new_item_dic[this_item] = founditem.myItem 
                 
    logger.info(f"\n\tSUMMARY - guess_label_for_new_items\n")
    if len(new_item_dic) > 0:
        if GL_PRNSTMT: print (f"*****************\n {len(new_item_dic)} items are new\n**********************")
        for key, value in new_item_dic.items():
            my_message = f"The best match for {key} was {value}"
            if GL_PRNSTMT: print(my_message)
            logger.info(my_message)  


