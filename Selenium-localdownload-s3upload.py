"""
Author : Emilien Romulus
"""

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import os
import pandas as pd
import boto3
import logging

LOG_FILENAME = r"C:\Selenium-POC\log\Selenium-POC.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.ERROR)

rootpath=r'C:\Selenium-POC'
savepath=r'C:\Selenium-POC\data'
archivepath=r'C:\Selenium-POC\archive'

#Clean up any existing downloaded files
while os.path.exists(savepath  +  '\myfile.csv'):
    os.remove(savepath  +  '\myfile.csv')

try:
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : savepath}
    chromeOptions.add_experimental_option("prefs",prefs)
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument('--disable-gpu')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chromeOptions)
    driver.get("http://www.website.com")
    time.sleep(0.5)
except:
    logging.exception('Selenium error accessing the web page')
    raise
    
#Find element and click
elem = driver.find_element_by_xpath('//*XPATH')
elem.click()

#Input in format d/m/y
elem.send_keys(dt.strftime('%d/%m/%Y'))

#Wait for the downloaded file to exist
while not os.path.exists(savepath  +  r'\myfile.csv'):
    time.sleep(1)

#rename the file
newname=r'\myfile-'+ dt.strftime("%Y-%m-%d") +r'.csv'

i=1
while os.path.exists(savepath  + newname):
    oldname=r'\myfile-'+ dt.strftime("%Y-%m-%d") +r' ('+ str(i) + r').csv'
    if os.path.exists(archivepath + oldname):
        time.sleep(0.5)
        #an archive i ealready exists, go to next loop
    else:
        os.rename(savepath + newname,archivepath + oldname)
    i=i+1
os.rename(savepath + r'\myfile.csv',savepath + newname)

#close the browser and process
driver.quit()
time.sleep(0.5)

#Open the csv with Pandas
df = pd.read_csv(savepath + newname)

#Timestamp with today's date
df['Date of Execution'] = datetime.datetime.today().strftime("%Y-%m-%d")

#Re-write the csv
df.to_csv(savepath + newname, index=False)

#Upload a copy to S3 Standard IA
s3 = boto3.client('s3')
targetBucket = 'my-bucket-name'
sourceFile = savepath+newname

try:
	with open(sourceFile, "rb") as f:
		s3.upload_fileobj(f, targetBucket, "Selenium-POC/data/"+newname[1:], ExtraArgs = {
		'StorageClass': 'STANDARD_IA'
	  })
except:
    logging.exception('AWS S3 Error')
    raise

#Upload a copy to S3 Standard IA
sourceFile = savepath+newname
try:
    with open(sourceFile, "rb") as f:
        s3.upload_fileobj(f, targetBucket, "VEU/totalwithdrawn/"+newname[1:], ExtraArgs = {
        'StorageClass': 'STANDARD_IA'
      })
except:
    logging.exception('AWS S3 Error')
    raise
