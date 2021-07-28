#author : Emilien Romulus

import boto3
import json
import os
from shutil import copyfile
import tempfile
from office365.sharepoint.client_context import ClientContext

import logging
LOG_FILENAME = r"C:/SharePoint-API/Log/SharePoint-Download.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.ERROR)

#backup existing non-empty file
filePath = r"C:/SharePoint-API/myfile.xlsx"
archivePath = r"C:/SharePoint-API/Archive/myfile.xlsx"

if os.stat(filePath).st_size > 0 :
    print("Backing up current file to Archive...")
    copyfile(filePath, archivePath)


#Retrieve credentials from SSM parameter store
try:
    secret_name = "aws-ssm-secret-name"
    ssm = boto3.client('ssm', region_name="eu-west-1")
    parameter = ssm.get_parameter(Name=secret_name,WithDecryption=True)
    credentials=json.loads(parameter.get('Parameter').get('Value'))
except:
    response = boto3.resource('sns',region_name="eu-west-1").Topic('ARN:exception-catch-SNS-topic').publish(Message='There was an error running the SharePoint-Download.py script')
    print('[Ko] an error occured')
    logging.exception('Error getting credentials')
    raise

#Download file from SharePoint using credentials
try:
    ctx = ClientContext("https://company.sharepoint.com/sites/sitename/")
    username = credentials.get('username')
    password = credentials.get('password')
    
    ctx.with_user_credentials(username,
                              password)
    web = ctx.web.get().execute_query()
    
    file_url = "/sites/sitename/folder/myfile.xlsx"
    download_path = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
    download_path = filePath


    with open(download_path, "wb") as local_file:
        file = ctx.web.get_file_by_server_relative_path(file_url).download(local_file).execute_query()
    print("[Ok] file has been downloaded: {0}".format(download_path))
except:
    response = boto3.resource('sns',region_name="eu-west-1").Topic('ARN:exception-catch-SNS-topic').publish(Message='There was an error running the SharePoint-Download.py script')
    print('[Ko] an error occured')
    logging.exception('Error downloading file')
    raise


#Check if the final file is not empty, replace if Archive otherwise
if os.stat(ledgerPath).st_size == 0 :
    print("filesize=0 ; rollback with Archive")
    copyfile(archivePath, filePath)
