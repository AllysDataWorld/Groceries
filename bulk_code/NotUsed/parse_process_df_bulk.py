import warnings
from pandas.errors import SettingWithCopyWarning
# warnings.simplefilter(action="ignore", category = FutureWarning)
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

import pandas as pd
from code_helpers.create_metro_df import create_metro_df
from bulk_code.Bulk_Guess_Labels import guess_labels_bulk
from app import logger


def convert_to_int(num):
    """."""    
    if isinstance(num, str):
        if num.replace('.','',1).isdigit():
            num = int(num)
        else:
            num = 0
    else:            
        num = int(num)
    return num


def parse_process_df_bulk(text_list, log):
    PRNT_PP = True
    user_input = input(f'Parse_Process_df_bulk: Verbose Press 1:    ')
    if int(user_input) == 1:
        PP_PRNSTMT = True
    else:
        PP_PRNSTMT = False
        
 
    insert_row = []
    other_df = pd.DataFrame(insert_row)
    produce_df = pd.DataFrame(insert_row) 
    item_list= []

    log.info("Create DF:")
    df_orig, df, df_debug = create_metro_df(text_list)
    df = df.reset_index()
    
    if PP_PRNSTMT: print("\n\n\n//start parse_process_df_bulk: PPDB")
    
    #CREATE DF for GUESS_LABEL: 
    item_list = df[df.CAT != "STORE_CATEGORY"]['item'].to_list()
    if PP_PRNSTMT: print("PPDB: Guess Labels for DF: >>>", item_list)
    guess_dic = guess_labels_bulk (item_list)
    if PP_PRNSTMT: print("\nPPDB: Guessed Items: >>>", guess_dic, "\n")
    
    df["myItem"] = ""
    df["myCat"] = ""
    dfitem_index = df.columns.get_loc("myItem")
    dfcat_index = df.columns.get_loc("myCat")

    if PP_PRNSTMT: print("\nPPDB Updating DF with found items:")
    for i, guessed_item in enumerate(guess_dic):
        for index, row in df.iterrows():
            if (row['item'] == guessed_item):
                if PP_PRNSTMT: print("PPDB RowItem: ", row['item'], ": FOUND:", guessed_item)
                df.iloc[index, dfitem_index] = guess_dic[guessed_item][0]
                df.iloc[index, dfcat_index] = guess_dic[guessed_item][1]
                break

    df.to_csv("df.csv")

    #Create DF_CAT:
    df_cat = df[df['CAT']=="STORE_CATEGORY"]
    df_cat.loc[:,'Produce_start'] = df_cat.index.to_series() # Get the index of the next row
    df_cat.loc[:,'Produce_stop'] = df_cat.index.to_series().shift(-1) # Get the index of the next row
    df_cat.Produce_stop = df_cat.Produce_stop.fillna(0).astype('int')

    if df_cat.iloc[-1,-1]==0 and df_cat.shape[0]>0:
        df_cat.iloc[-1,-1] = df.shape[0]

    if PP_PRNSTMT: print("\n\nPPDB: Dataframes")
    if PP_PRNSTMT: print(f"\ndf\n {df}")
    if PP_PRNSTMT: print(f"\ndf_cat\n {df_cat}")
    if PP_PRNSTMT: print("QA above:", df_cat.iloc[-1,-1]==0, df_cat.shape[0]>0, df_cat.shape[0])
    
    #Create Produce_DF and OTHER_DF
    produce_index = 0
    for index, row in df_cat.iterrows():
        if row['CAT'] == "STORE_CATEGORY" and row['item'] == 'PRODUCE':
            produce_index=row
            break
    
    if PP_PRNSTMT: print(f"PPDB: produce_index: {produce_index}")
    if isinstance(produce_index, int):
        other_df = df
    else:
        strt = convert_to_int(produce_index.Produce_start)
        stp = convert_to_int(produce_index.Produce_stop)
        #if PP_PRNSTMT: print("PPDB: qa: Produce start:", strt)
        #if PP_PRNSTMT: print("PPDB: qa Produce Stop:", stp)
    
        produce_df = df.iloc [strt+1:stp, :] #remove the first row
        before = df.iloc[:strt, :]
        after = df.iloc[stp:, :]
        other_df = pd.concat([before, after])
        
        log.info(f"PPDB: produce_df:{produce_df.columns}\n {produce_df}\n-----\n")
        log.info(f"PPDB: other_df:{other_df.columns}\n {other_df}\n-----\n")
    
        if PP_PRNSTMT: print(f"\nPPDB: produce_df {produce_df.columns} \n: {produce_df}")
        if PP_PRNSTMT: print(f"\nPPDB: other_df: {other_df.columns} \n {other_df}")
 
        price_idx = produce_df.columns.get_loc("price")  
        da_item = produce_df.item.to_list()
        
        #NEW PART
        # if PP_PRNSTMT: print("PPDB: Guess Labels for Produce Items: >>>", da_item)

        # for i, guessed_item in enumerate(guess_dic):
            # for row in da_item:
                # if (row == guessed_item):
                    # if PP_PRNSTMT: print("PPDB RowItem: ", row, ": FOUND:", guessed_item)
                    # produce_df.iloc[index, dfitem_index] = guess_dic[guessed_item][0]
                    # produce_df.iloc[index, dfcat_index] = guess_dic[guessed_item][1]
                    # break

        
        #########################
        # INSERT ROWS: PRODUCE  #
        #########################
        produce_item = produce_df.columns.get_loc("itemCLN")  
        my_produce_item = produce_df.columns.get_loc("myItem")  
        my_produce_cat = produce_df.columns.get_loc("myCat")  

        for i, cost in enumerate(produce_df.produce_cost):
            if cost==1:                
                cost_str = produce_df.iloc[i, produce_item]
                my_item = produce_df.iloc[i-1, my_produce_item]
                price = produce_df.iloc[i,price_idx]
                item = produce_df.iloc[i-1, produce_item]
                my_Cat = produce_df.iloc[i-1, my_produce_cat]
                da_item[i] = 0
                da_item[i-1] = 0
                my_message = f"insert_row: PRODUCE, {item}--> {price}"
                my_message = "insert_row: PRODUCE", item, "-->", price, my_item, my_Cat
                if PP_PRNSTMT: print(my_message)
                logger.info(my_message)
                insert_row.append(("PRODUCE", item, price, my_item, my_Cat))
            else:
                pass
                #if PP_PRNSTMT: print("ELS:", i, cost, produce_df.iloc[i,-3])
        
        produce_extra_items = [("PRODUCE", k, produce_df.iloc[i,price_idx], "", "") for i,k in enumerate(da_item) if k!=0]
        insert_row = insert_row + produce_extra_items
    
    print("-"*40, "BEFORE:", "-"*40)
    print(insert_row)


    ################
    # INSERT ROWS  #
    ################
    category=""
    for index, row in other_df.iterrows():
        if row.CAT == "STORE_CATEGORY" and row.item != 'PRODUCE':
            category= row['CAT_MATCH']
            print("category:", category)
        else:
            insert_row.append((category, row['item'], row['price'], row["myItem"], row['myCat']))
            my_message = "PPDB: insert_row:", category, row['item'], "-->", row['price'], row['myItem'], row['myCat']
            if PP_PRNSTMT: print(my_message)
            logger.info(my_message)
        
    total = 0.0
    for row in insert_row:
        total = row[2] + total

    print("-"*40, "AFTER:", "-"*40)
    print(insert_row)

    total = round(total, 2)
    return insert_row, total
    
# metro_headings = ['GROCERY', 'PRODUCE', 'DAIRY', 'DELI','SEAFOOD', 'GENERAL','COMM']
# subtotal_list = ['SUBTOTAL.' ,'SUBTOTAL', 'SUBTOT']
# total_list = ['TOTAL.' ,'TOTAL', 'TOT']

# USED THE WEBSITE TO UPLOAD a receipt THEN DELETE THE UPLOADED ROWS.
# UPLOADING CREATES A TEMP CSV FILE THAT HAS THE RAW OCR OUTPUT AS A CSV FILE

def TEST_process(FILE, lg):
    all_text = open(FILE).readlines()
    text_list = []
    for text in all_text:
        if text == "\n":
            pass
        else:
            text = text.split('\n')[0]
            text_list.append(text)
            
    #new_rows, total = parse_process_df_bulk(text_list, lg)
    return text_list
    
# from ai import logger as lg
# import create_metro_df as CM
# import ast
# import bulk_upload_helpers as HP

# FILE = 'OCR_text.csv'
# text_list = TEST_process(FILE, lg)
# df_orig, df, df_debug = CM.create_metro_df(text_list)

# df = df.reset_index()
# item_list = df[df.CAT != "STORE_CATEGORY"]['item'].to_list()
# #guess_dic = HP.guess_labels_bulk (item_list)
# out = TEST_process("GuessedItems.txt", lg)[0]    
# guess_dic = ast.literal_eval(out)

    
# df["myItem"] = ""
# df["myCat"] = ""
# dfitem_index = df.columns.get_loc("myItem")
# dfcat_index = df.columns.get_loc("myCat")

# PP_PRNSTMT = True