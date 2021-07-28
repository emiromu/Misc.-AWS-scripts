# -*- coding: utf-8 -*-
"""
Author : Emilien Romulus
"""

import json
import requests
import csv
import datetime
from datetime import timedelta
import boto3
import logging

LOG_FILENAME = r"C:\REST-API-JSON\log\rest-api-json.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.ERROR)

rootpath='C:\REST-API-JSON'
savepath='D:\REST-API-JSON\data'

#The REST API in this example used to accept requests with date attribute ?date=
### GENERATE THE LIST OF DAYS WE WANT REC INFORMATION FROM
sdate = datetime.date.today() - datetime.timedelta(days = 1)   # start date
#edate = date(2019, 10, 24)   # end date
edate = datetime.date.today() - datetime.timedelta(days = 1)   # end date

delta = edate - sdate       # as timedelta
datelist = []
jsonlist = []
list_results = []

### query the start date to generate jsondict

try:
    url = 'https://website/api-url?date='
    jsondict = json.loads(requests.get(url + str(sdate)).text)
except:
    logging.exception('Error querying the API')
    raise

for i in range(delta.days + 1):
    day = sdate + timedelta(days=i)
    datelist.append(str(day))

for j in range(len(datelist)):
    print('Fetching JSON for date : '+datelist[j])
    data = json.loads(requests.get(url + datelist[j]).text)
    jsondict.update(data)
    jsonlist.append(jsondict.get('result'))

### GENERATE THE LISTS TO STORE AND PARSE RESULTS
### The Json sent by the web app are nested lists and dictionaries
ci=0
cj=0

for i in jsonlist :
    for j in jsonlist[ci] :
        list_results.append(jsonlist[ci][cj])
        cj=cj+1
    ci=ci+1
    cj=0
ci=0


list_output = []
ci=1

for row in list_results :
    print('')
    print('Parsing row '+str(ci)+' of list_results')
    
    topblist=[]
    topblist=row.get('certificateRanges')
    for subrow in topblist :
        sublist = []
        
        sublist.append(subrow.get('row1'))
        sublist.append(subrow.get('row2'))
                
        list_output.append(sublist)
        
    ci=ci+1
    


list_headers = [
                'row1',
                'row2'
                ]
        
### WRITE TO CSV (OVERWRITE IF ALREADY EXISTS)
with open(savepath + r'\rest-api-json-'+str(sdate)+'-'+str(edate)+'.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(list_headers)
    writer.writerows(list_output)

#Upload a copy to S3 Standard IA
try:
	s3 = boto3.client('s3')
	targetBucket = 'my-bucket-name'
	sourceFile = savepath + r'\rest-api-json-'+str(sdate)+'-'+str(edate)+'.csv'

	with open(sourceFile, "rb") as f:
		s3.upload_fileobj(f, targetBucket, "rest-api-json/data/"+ r'rest-api-json-'+str(sdate)+'-'+str(edate)+'.csv', ExtraArgs = {
		'StorageClass': 'STANDARD_IA'
	  })

except:
    logging.exception('Error uploading to S3')
    raise

