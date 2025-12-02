import re
import pandas as pd

from code_helpers.levenshtein_distance import levenshtein_distance


# metro_headings = ['GROCERY', 'PRODUCE', 'DAIRY', 'DELI','SEAFOOD', 'GENERAL','COMM']
# subtotal_list = ['SUBTOTAL.' ,'SUBTOTAL', 'SUBTOT']
# total_list = ['TOTAL.' ,'TOTAL', 'TOT']


def create_metro_df(text_list, VERBOSE=True):
    import utils as uts
    from config import Config
    
    if VERBOSE:
        CM_PRNSTMT = False
    else:
        CM_PRNSTMT = True

    metro_headings = Config.METRO_CATEGORY
    subtotal_list = Config.SUBTOTALS
    total_list = Config.TOTALS

    text_list = text_list[3:]
    
    col_length = []
    lev_arr = []
    distance = []
    header_lst, h_found = [], []
    cln_txt = []
    a, b, c = [],[],[]

    if CM_PRNSTMT: print("Start create_metro_df. Number of Items Received: ", len(text_list))

    for text in text_list:    
        text = re.sub(r'[?|$|:|*|!]',r'',text).strip()
        if CM_PRNSTMT: print("\nstep one - the token is: ", text)

        if text.split('.')[0] =='COMM':
            text ='BAKERY'
        elif text.split(' ')[0] =='GENERAL':
            text ='GENERAL'
        elif text.split(' ')[0] =='DELI':
            text ='DELI'
            
        col_len = len(text.split(' '))
        col_length.append(col_len)
        cln_txt.append(text)
        
        if CM_PRNSTMT: print(">> step two: ", text, col_len == 1 , len(text)==1, col_len, len(text))
        
        if col_len == 1 or len(text)==1:
            lev_arr = []
            if CM_PRNSTMT: print(">>> step three (len=1): ", text)
            for head in metro_headings:
                dis = levenshtein_distance(text, head)
                lev_arr.append(dis)
            match_header = min(lev_arr) #the min LEV distance is the closest matching header 
            loc = lev_arr.index(match_header) #find the location of the closest header
            header = metro_headings[loc] #find the header
            head_dis = levenshtein_distance(text, header)
            
            #create df_debug
            a.append(text)
            b.append(header)
            c.append(head_dis)
            
            if head_dis < 5:
                distance.append(head_dis)
                header_lst.append("STORE_CATEGORY")
                if CM_PRNSTMT: print("!FOUND CAT:", text, header)  
                h_found.append(header)

            else:
                distance.append(100) 
                header_lst.append("ITEM TOK")   
                h_found.append("ITEM TOK")

        else:
            distance.append(100)
            header_lst.append("ITEM") 
            h_found.append("ITEM")
            
      
    total_arr = []
    sav_arr = []
    for text in text_list:  
        thisTok = text.split(" ")
        if thisTok[0] in subtotal_list or thisTok[0].upper() in total_list:
            total_arr.append(1)
        else:
            total_arr.append(0)
        if thisTok[0].upper() == 'SAVING' or thisTok[0].upper() == 'AVING':
            sav_arr.append(1)
        else:
            sav_arr.append(0)
          
    #len is 51
    df = pd.DataFrame({
        "ORIG": cln_txt,
        "LEN": col_length,
        "CAT": header_lst,
        "CAT_MATCH": h_found,
        "DIS": distance,
        "TOTAL": total_arr, 
        "SAV": sav_arr
    })
    
    df_lev = pd.DataFrame({
        "tok": a,
        "header": b,
        "lev": c
    })
        
   
    # Condition to flag rows (e.g., values greater than 3 in column 'A')
    flag_condition = df['TOTAL'] == 1
    
    # Find the index of the first occurrence of the flag
    first_flag_index = flag_condition.idxmax()
    
    # Drop rows after the first flag
    df_receipt = df.iloc[:first_flag_index + 1] #[['ORIG', "LEN", "SAV"]]
    
    price_arr = []
    item_arr=[]
    for row in df_receipt.ORIG:
        t = row.split(" ")
        if t[-1].replace('.','',1).isdigit():
            price = uts.convert_price(t[-1])
            item = ' '.join(t[0:len(t)-1])
            price_arr.append(price)
            item_arr.append(item) 
            if CM_PRNSTMT: print("ORIG: DIGIT: ", t)
        else:
            price = 0.0
            item = row
            price_arr.append(price)
            item_arr.append(item)
            if CM_PRNSTMT: print("ORIG: ELSE: ", t)

    
    df_receipt.loc[:, 'price'] = price_arr
    df_receipt.loc[:, 'item'] = item_arr
    
    item_arr=[]
    weight_arr=[]
    for row in df_receipt.item:
        tok0 = row.split(' ')
        tok = row.split('.')
        if 'kg' in tok or 'kg' in tok0:
            item_arr.append(row)
            weight_arr.append(1)
        else:
            item = ' '.join(tok)
            tok = item.split('  ')
            item = ' '.join(tok)
            item_arr.append(item)
            weight_arr.append(0)
    
   
    df_receipt.loc[:, 'produce_cost'] = weight_arr
    df_receipt.loc[:, 'itemCLN'] = item_arr
    
    df_cln = df_receipt[df_receipt['SAV']==0]
    df_cln = df_cln[df_cln['TOTAL']==0]
   
    df_cln[df_cln['LEN']<7].shape[0]==df_cln.shape[0]
    
    if CM_PRNSTMT: print("End of Create_metro_df:")
    return df_receipt, df_cln, df_lev

#########################################################################

#USED THE WEBSITE TO UPLOAD. THEN DELETE THE UPLOADED ROWS.
#UPLOADING CREATES A TEMP CSV FILE THAT HAS THE RAW OCR OUTPUT AS A CSV FILE
# FILE = 'OCR_text_DATRY.csv'
# FILE = "OCR_text_Metro_8_ORIG.csv"
# FILE = 'metro_5_GPD_15.63.csv'

# def TEST_CONVERT_CSV_TO_df(FILE):
#     all_text = open(FILE).readlines()
#     text_list = []
#     for text in all_text:
#         if text == "\n":
#             pass
#         else:
#             text = text.split('\n')[0]
#             text_list.append(text)
#     df_receipt, df_cln, df_lev = create_metro_df(text_list)
#     df_cln.to_csv("df_cln.csv", index=0)
#     df_receipt.to_csv("df_flags.csv", index=0)
#     return df_receipt, df_cln, df_lev
 
 
#TESTING: UPLOAD a recept using GUI: this will create the OCR_text.csv
#FILE = r'C:\Users\after\OneDrive\Desktop\code_from_HD\Groceries\Groceries\FLASK\final_versions\v9\OCR_text.csv'
#df_receipt, df_cln, df_lev =  TEST_CONVERT_CSV_TO_df(FILE)
