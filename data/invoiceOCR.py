# -*- coding: utf-8 -*-
"""OCR

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Sa_ytvT9MT7yECCCv-dsiEenyUGpZc57
"""

!pip install pytesseract
!sudo apt install tesseract-ocr
!pip install openpyxl

from google.colab import files
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from openpyxl.workbook import Workbook

# Image handling libraries
from PIL import Image
import cv2
import pytesseract
from pytesseract import image_to_string

#Text preprocessing libraries
import nltk
import re
from nltk.corpus import stopwords

#Logging libraries
import logzero         
from logzero import logger

def get_image(directory):
    
    image_path=os.path.join(directory, filename)
    image =cv2.imread(image_path) #read image present in directory
    return image  
            
def clean_image(img):
    img = cv2.resize(img, None, fx=1.45, fy=1.25, interpolation=cv2.INTER_CUBIC) #scaling the image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)# get grayscale image
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 85, 11) #thresholding
    return img
    
def extract_text(cleaned_image):
    custom_config = r'-l eng --psm 3'
    extracted_Information = pytesseract.image_to_string(cleaned_image,config=custom_config)
    extracted_Information = extracted_Information.replace(",", "")
    extracted_Information = extracted_Information.split("\n")
    logger.info("-----Readin Extracted Text-----------")
    logger.info("%s Extracted Text : ", extracted_Information)
    
    
    return extracted_Information

def clean_text(sentence_id,filename,extracted_text):
    extracted_text =[ text.lower() for text in extracted_text]

    # Remove unicode characters
    extracted_text = [asci.encode('ascii', 'ignore').decode() for asci in extracted_text]
    extracted_text = [re.sub('[^a-z0-9.$/-]+', " ", text) for text in extracted_text]
    extracted_text = [word for word in extracted_text if word not in stopwords.words('english') ]
    cleaned_text = []
    for sentences in extracted_text:
        sentences = sentences.split(" ")
        for words in sentences:
            if words not in [' ',"",'.','-']:
                cleaned_text.append(words)
    logger.info("-----Reading cleaned Text-----------")          
    logger.info("%s Cleaned Text for %d sentence_id : ", cleaned_text)
      
    temp_df =pd.DataFrame()         
    temp_df['Word'] = cleaned_text
    temp_df['SentenceID'] = sentence_id
    temp_df['Filename'] = filename
    
    
    return temp_df

directory = r'/content/Invoices/'
invoice_data = pd.DataFrame(columns = ['SentenceID','Filename','Word'])
sentence_id = 0

logzero.logfile("logfile.log",maxBytes=1e6)
pytesseract.pytesseract.tesseract_cmd = ( r'/usr/bin/tesseract')

for filename in os.listdir(directory):

        if filename.endswith(".tif") and sentence_id<=8 :     #For reading image file
            sentence_id +=1
            image = get_image(directory)
            cleaned_image = clean_image(image)
            extracted_text = extract_text(cleaned_image)
            invoice_data_df = clean_text(sentence_id,filename, extracted_text)
            invoice_data = invoice_data.append(invoice_data_df,ignore_index=True)

invoice_data.to_excel("ner_dataset.xlsx", index=False)