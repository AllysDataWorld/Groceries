# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 18:16:18 2024
@author: Aila Ansari
SOURCE:
    https://circuitdigest.com/microcontroller-projects/optical-character-recognition-ocr-using-tesseract-on-raspberry-pi
    https://www.datacamp.com/tutorial/optical-character-recognition-ocr-in-python-with-pytesseract
Tested on: 
    \\Groceries\FLASK\final versions\v3\receipts\Metro.jpg
            
"""

import cv2
from pytesseract import pytesseract 
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.tesseract_cmd = path_to_tesseract 

def OCR_metro(imageFile):
    img = cv2.imread(imageFile,cv2.IMREAD_COLOR) #Open the image from which charectors has to be recognized
    #img = cv2.resize(img, (620,480) ) #resize the image if required 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grey to reduce detials 
    gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise
    original = pytesseract.image_to_string(gray, config='')
    return original
    
    #test = (pytesseract.image_to_data(gray, lang=None, config='', nice=0) ) #get confidence level if required
    #print(pytesseract.image_to_boxes(gray))

    
'''required = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

Final = ''

for c in original:

    for ch in required:

        if c==ch:

         Final = Final + c 

         break

print (test)

for a in test:
    if a == "\n":
        print("found")'''

 
