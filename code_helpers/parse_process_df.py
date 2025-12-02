import warnings
from pandas.errors import SettingWithCopyWarning
# warnings.simplefilter(action="ignore", category = FutureWarning)
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

import pandas as pd
from code_helpers.create_metro_df import create_metro_df
 

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


def parse_process_df(text_list, log, VERBOSE):
    if VERBOSE:
        PPDF_PRNSTMT = True
        log.info("\nstart parse_process_df:\n")
        print("\nstart parse_process_df:\n")
        
    else:
        PPDF_PRNSTMT = False    

    insert_row = []

    df_orig, df, df_debug = create_metro_df(text_list)
    df = df.reset_index()
    
    #Create DF_CAT:
    df_cat = df[df['CAT']=="STORE_CATEGORY"]
    df_cat.loc[:,'Produce_start'] = df_cat.index.to_series() # Get the index of the next row
    df_cat.loc[:,'Produce_stop'] = df_cat.index.to_series().shift(-1) # Get the index of the next row
    df_cat.Produce_stop = df_cat.Produce_stop.fillna(0).astype('int')

    if df_cat.iloc[-1,-1]==0 and df_cat.shape[0]>0:
        df_cat.iloc[-1,-1] = df.shape[0]


    
    # df_cat.to_csv("df_cat.csv")
    # df.to_csv("df.csv")
    # df_orig.to_csv("df_orig.csv")
    # df_debug.to_csv("df_debug.csv")

    if PPDF_PRNSTMT: 
        print(f"\ndf: {df}")
        print(f"\ndf_cat: {df_cat}")

        log.info(f"df:\n {df}\n-----\n")
        log.info(f"df_cat:\n {df_cat}\n-----\n")
        log.info(f"df_debug:\n {df_debug}\n-----\n")
    
    
    #Create Produce_DF and OTHER_DF
    produce_index = 0
    for index, row in df_cat.iterrows():
        if row['CAT'] == "STORE_CATEGORY" and row['item'] == 'PRODUCE':
            produce_index=row
            break
    
    if PPDF_PRNSTMT: print(f"produce_index: {produce_index}")
    if isinstance(produce_index, int):
        other_df = df
    else:
        strt = convert_to_int(produce_index.Produce_start)
        stp = convert_to_int(produce_index.Produce_stop)
        if PPDF_PRNSTMT:print("qa: Produce start:", strt)
        if PPDF_PRNSTMT:print("qa Produce Stop:", stp)
    
        produce_df = df.iloc [strt+1:stp, :] #remove the first row
        before = df.iloc[:strt, :]
        after = df.iloc[stp:, :]
        other_df = pd.concat([before, after])
  
        if PPDF_PRNSTMT:
            print(f"\nproduce_df {produce_df.columns} \n: {produce_df}")
            print(f"\nother_df: {other_df.columns} \n {other_df}")
            log.info(f"produce_df:{produce_df.columns}\n {produce_df}\n-----\n")
            log.info(f"other_df:{other_df.columns}\n {other_df}\n-----\n")
        
        price_idx = produce_df.columns.get_loc("price")  
        da_item = produce_df.item.to_list()
        
        #########################
        # INSERT ROWS: PRODUCE  #
        #########################

        for i, cost in enumerate(produce_df.produce_cost):
            if cost==1:
                cost_str = produce_df.iloc[i,-1]
                item_str = produce_df.iloc[i-1,-1]
                price = produce_df.iloc[i,price_idx]
                item = item_str# + " " + cost_str
                da_item[i] = 0
                da_item[i-1] = 0
                if PPDF_PRNSTMT:print("insert_row: PRODUCE", item,"------->", price)
                log.info("insert_row:" + str(item) + str(price))
    
                insert_row.append(("PRODUCE", item, price))
            else:
                pass
                #if PPDF_PRNSTMT: print("ELS:", i, cost, produce_df.iloc[i,-3])
        
               
        produce_extra_items = [("PRODUCE", k, produce_df.iloc[i,price_idx]) for i,k in enumerate(da_item) if k!=0]
        insert_row = insert_row + produce_extra_items


    ################
    # INSERT ROWS  #
    ################
    category=""
    for index, row in other_df.iterrows():
        if row.CAT == "STORE_CATEGORY" and row.item != 'PRODUCE':
            category= row['CAT_MATCH']
        else:
            insert_row.append((category, row['item'], row['price']))
            print("insert_row:", category, row['item'] ,"------->", row['price'])
            log.info("insert_row:" + str(category) + str(row['item']) +"------->"+ str(row['price']))


    if PPDF_PRNSTMT:
        log.info("\n end parse_process_df:\n")
        print("-------------\n", insert_row, ": insert_row")
        print("\n end parse_process_df:\n")

    
    total = 0.0
    for row in insert_row:
        total = row[2] + total

    total = round(total, 2)
    return insert_row, total

# TESTING:
# from create_df import TEST_CONVERT_CSV_TO_df
# df_orig, df = TEST_CONVERT_CSV_TO_df(FILE)

# metro_headings = ['GROCERY', 'PRODUCE', 'DAIRY', 'DELI','SEAFOOD', 'GENERAL','COMM']
# subtotal_list = ['SUBTOTAL.' ,'SUBTOTAL', 'SUBTOT']
# total_list = ['TOTAL.' ,'TOTAL', 'TOT']

#USED THE WEBSITE TO UPLOAD a receipt THEN DELETE THE UPLOADED ROWS.
#UPLOADING CREATES A TEMP CSV FILE THAT HAS THE RAW OCR OUTPUT AS A CSV FILE
# FILE = 'OCR_text_DATRY.csv'
# FILE = "OCR_text_Metro_8_ORIG.csv"
#FILE = 'metro_5_GPD_15.63.csv'
