# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 08:03:25 2024

@author: after
"""


import logging
from bulk_code.bulk_upload import bulk_upload


PATH = r'\receipts\one\wip'

BASE = r'C:\Users\after\OneDrive\Desktop\code_from_HD\Groceries\Groceries\FLASK\final_versions'
thisStore = "Metro"

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S',
                    filename='log.log', encoding='utf-8', level=logging.DEBUG)

folder = BASE +"\\"+ PATH
logger.info('\n-----------------------------\nBULK UPLOAD PROCESS using V12 Metro Code\n-----------------------------\n')


bulk_upload(True, folder, logger, thisStore) #fuzzy matching is off
