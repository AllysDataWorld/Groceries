# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 09:27:08 2024

@author: after
"""


def text_mining_metro(text, metro_logger, VERBOSE):
    from config import Config
    import utils as uts
    
    if VERBOSE:
        TM_PRNSTMT = False
    else:
        TM_PRNSTMT = True    
        metro_logger.info("\nstart text_mining_metro:" + str(text))
        print("\nstart text_mining_metro:\n")

    metro_headings = Config.METRO_CATEGORY
    subtotal_list = Config.SUBTOTALS
    total_list = Config.TOTALS

    headings = {}
    produce_arr = []
    insert_row = []

    iteration = True #does this mean stop when you've found total or subtotal?
    insert_new_rows = True ##False means stop adding items to database (past total/subtotal))
    found = 0
    pop = False

    category= ""
    subtotal_price = 0.0
    total_price = 0.0
    newtok = ""
    
    text = text[3:]

    
    for i, tok in enumerate(text):
        thisTok = tok.split(" ")
        
        if iteration:
            metro_logger.info("PROCESS tok: " + str(tok))
            if thisTok[0] in subtotal_list:
                insert_new_rows = False #stop adding items to database
                price=0.0
                item = ""
                t = tok.split(' ')
                subtotal_price = uts.convert_price(t[-1])
                metro_logger.debug("> found subtotal_price: " + str(subtotal_price))

            elif thisTok[0].upper() in total_list:
                iteration = False
                price=0.0
                item = ""
                t = tok.split(' ')                
                total_price = uts.convert_price(t[-1])
                metro_logger.debug("> found total_price: " + str(total_price))

            elif thisTok[0].upper() in metro_headings:
                 headings[tok] = i
                 for h in metro_headings:
                     if thisTok[0].upper() == h:
                         if h == 'COMM.': h ='BAKERY'
                         category=h
                         price=0.0
                         item = ""
                         metro_logger.info("> Update Category: " + str(h))
                         
            elif thisTok[0].upper() == 'SAVING'or thisTok[0].upper() == 'AVING':
                metro_logger.debug("SKIPPED Savings") # + thisTok[0])
                price=0.0
                item = ""
             
            else: 
                if insert_new_rows:
                     if category == 'PRODUCE':
                         produce_arr.append(tok)
                         price=0.0
                         item = ""
                         metro_logger.debug("Added tok to PRODUCE array: " + str(tok))
                                          
                     else:       
                         t = tok.split(' ')
                         if t[-1].replace('.','',1).isdigit():
                             price = uts.convert_price(t[-1])
                             item = ' '.join(t[0:len(t)-1])
                             #metro_logger.debug("Item has Price: " + str(item) +" - "+ str(price))
                         else:
                             price = 0.0
                             item = tok 
                             #metro_logger.info("Item price not found:" + str(item) +" - "+ str(price))
                             
                         insert_row.append((category, item, price))
                                                 
                         if TM_PRNSTMT:
                            metro_logger.info(f"->PROCESSED: The item {item} is from category:{category} and it cost {price}")
                            print(f"PROCESSED: The item {item} is from category:{category} and it cost {price}")

        # else:
        #     print('iteration complete')
    if len(produce_arr) > 0:  
        metro_logger.info(f"----PRODUCE PROCESSING on array len {len(produce_arr)}---->\n"+ str(produce_arr))
    
    if len(produce_arr) == 1: #if bag of fruit: example ['APP MCINTOSH BAG']
        t = produce_arr[0].split(' ')
        if t[-1].replace('.','',1).isdigit():
            price = uts.convert_price(t[-1])
            item = ' '.join(t[0:len(t)-1])
            insert_row.append(("PRODUCE", item, price)) 
        else:
            price = 0.0
            item = produce_arr[0]            
            insert_row.append(("PRODUCE", item, price)) 
                
    else:   
        for i in range(len(produce_arr)):
            metro_logger.debug("PROCESS PRODUCE>> " + str(produce_arr[i]))
            t = produce_arr[i].split(' ')
            
            if t[0]=="HASS" and t[1]=="AVOCADO": #bought a bag of avocados
                found = i
                if t[-1].replace('.','',1).isdigit():
                    price = uts.convert_price(t[-1])
                    item = ' '.join(t[0:len(t)-1])
                    insert_row.append(("PRODUCE", item, price)) 
                    pop = True
                else:
                    item = produce_arr[i]
                    price = 0.0
                    insert_row.append(("PRODUCE", item, price)) 
                    pop = True
            else:
                pass

        if pop:
            metro_logger.info (f"Will POP OUT: {produce_arr[found]}")
            produce_arr.pop(found)        
        
        iteration = True 
        metro_logger.debug (f'produce_arr: {produce_arr}')
        
        if len(produce_arr)!=0:
            metro_logger.debug(f'produce_arr Loop Range: {range(len(produce_arr)-1)}')

        if len(produce_arr)==2:
            newtok = " ".join([produce_arr[0], produce_arr[1]])
            metro_logger.debug (f'One Produce Item: {newtok}')

        
        for i in range(len(produce_arr)-1):
            if len(produce_arr)>2 and i == 0:
                pass
            else:
                if iteration:
                    if newtok=="":
                        newtok = " ".join([produce_arr[i-1], produce_arr[i]])
                    t = newtok.split(' ')
                    price = uts.convert_price(t[-1])
                    item = ' '.join(t[0:len(t)-1])
                    category = 'PRODUCE'

                    metro_logger.debug(f"Start - i:{i}, i:{i-1}, t:{i+1} ")
                    metro_logger.debug(f"join - {produce_arr[i-1]}, and {produce_arr[i]}")
                    metro_logger.debug(f"Loop:{i}, netok:{newtok}, t:{t}")
                    metro_logger.info(f"{category} The item is {item} and it cost {price}")
                    
                    insert_row.append((category, item, price))
                    iteration = False
                else:
                    iteration = True


    if total_price == 0.0:
        total_price = subtotal_price

    myLen = len(insert_row)
    
    if TM_PRNSTMT:
        metro_logger.info(f"OUTPUT of text_mining_metro: {insert_row}")
        metro_logger.info('END text_mining_metro--------------')    
        
        print(f"SEND OUPTPUT to app: row/s: \n{insert_row}")
        print('End text_mining_metro')
          
    return insert_row, total_price


# def HARD_CODED_TEST(file): 
#     from app import logger
#     from pytesseract import pytesseract 
#     pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
#     from OCR_metro import OCR_metro
#     new_recepit = 'static/uploads/' + file
#     print("\n--------------HARD CODED TEST CALLED on FILE: ", new_recepit)
#     text =  OCR_metro(new_recepit)
#     text_list = text.split('\n')
#     text_list = list(filter(None, text_list))
#     insert_row, total_price = text_mining_metro(text_list, logger)
#     return insert_row, text_list

#insert_row, text_list = HARD_CODED_TEST('metro_1_Produce_dup2.jpg')