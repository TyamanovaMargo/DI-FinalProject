#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from modules.indexParser import *
from modules.reportMaker import *
from argparse import ArgumentParser
from datetime import datetime
from modules.sendEmail import sendEmail
import os
import time
import re
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

# Setup logging configuration to log errors, info, etc.
LOG_FILENAME = 'webScrapper.log'
format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s[%(process)d]%(funcName)10s: %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=format, level=logging.DEBUG)
logger = logging.getLogger('webScrapper')

# Regex pattern to match URLs
urlMatcher = re.compile(r'https?://[^/]+')

# Get the current timestamp in a readable format
ts = time.time()
timeStamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')

# Function to validate URL format
def validateUrl(url):
    if urlMatcher.search(url):
        return True
    return False

# Initialize temporary directories for storing data if they do not exist
def initDirs():
    if not os.path.exists('./tmp'):
        os.mkdir('./tmp')

# Function to scrape data from a URL, with an option for proxy and delay between requests
def scrapUrlData(outFile, useProxy, delayInterval):
    options = Options()
    
    # Set proxy settings if the useProxy flag is enabled
    if useProxy:
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.http", "45.6.18.232")
        options.set_preference("network.proxy.http_port", 8080)

    # Initialize Firefox driver with specified options
    driver = webdriver.Firefox(options=options)
    driver.get(outFile)

    # Delay between requests if specified
    if delayInterval:
        time.sleep(delayInterval)

    # Collect data from the page
    data = collectData(driver)
    driver.quit()

    return data

# Function to collect data from the webpage by searching for listing items
def collectData(driver):
    data = []
    
    try:
        # Find all listing items on the page by their class name
        items = driver.find_elements(By.CLASS_NAME, 'listing-item')

        # Loop through each item and extract name and price
        for item in items:
            try:
                name = item.find_element(By.CLASS_NAME, 'title').text
                price = item.find_element(By.CLASS_NAME, 'price').text
                data.append({"name": name, "price": price})
            except Exception as e:
                print(f"Error extracting data from item: {e}")
                continue

    except Exception as e:
        print(f"Error extracting items from the page: {e}")
    
    return data

# Function to dump collected data into a CSV file
def dumpDataFile(data, pageNum, outFile):
    if data:
        with open(outFile, 'a') as f:
            for entry in data:
                f.write(f"{entry['name']},{entry['price']}\n")
    else:
        print(f"[ERROR]. No data collected for page {pageNum}")

# Function to prepare the final report after scraping
def prepareReport(outFile, sPageNum, ePageNum):
    print(f"[>]. Preparing report from {sPageNum} to {ePageNum}")

# Function to send an email with the output file and report
def sendEmail(outFile, sPageNum, ePageNum, startTime, endTime):
    print(f"[>]. Sending email with file {outFile} and report")

# Main logic for argument parsing
parser = ArgumentParser(description='Scrap data from YAD')
parser.add_argument('filename', help='output filename')
parser.add_argument('-u', '--url', dest='inputUrl', help='Provide a custom input URL for scraping')
parser.add_argument('-s', '--start-page', type=int, dest='sPageNum', default=1, help='Provide the start page number')
parser.add_argument('-e', '--end-page', type=int, dest='ePageNum', help='Provide the last page number')
parser.add_argument('-p', '--use-proxy', dest='useProxy', action='store_true', help='Enable proxy support')
parser.add_argument('-t', '--use-delay', dest='delayInterval', type=int, help='Provide a delay for each HTTP request')
parser.add_argument('-C', '--cleanup', dest='cleanup', action='store_true', help='Perform a cleanup operation to remove temporary files')

# Exclusive arguments for residential or commercial scraping
group = parser.add_mutually_exclusive_group()
group.add_argument('-r', '--residential', dest='isResidential', action='store_true', help="Scrap residential listings")
group.add_argument('-c', '--commercial', dest='isCommercial', action='store_true', help="Scrap commercial listings")

# Parse the arguments
args = parser.parse_args()

# Extract parsed values
filename = args.filename
sPageNum = args.sPageNum
ePageNum = args.ePageNum
useProxy = args.useProxy
delayInterval = args.delayInterval
inputUrl = args.inputUrl
doCleanup = args.cleanup
isResidential = args.isResidential
isCommercial = args.isCommercial

# Validate input and ensure that required arguments are provided
if (not inputUrl) and (not (isCommercial or isResidential)):
    print("[!]. Please provide scrapping type either -r or -c\n")
    exit(1)

# Validate URL if provided
if inputUrl:
    inputUrl = inputUrl.strip()
    if not validateUrl(inputUrl):
        print("[ERROR]. URL pattern doesn't seem right")
        exit(1)

# Handle start and end page number logic
if not inputUrl:
    if sPageNum and (not ePageNum):
        print("[!]. End page number is not mentioned")
        ePageNum = sPageNum
    if sPageNum > ePageNum:
        print("[ERROR]. Start page number should be less than end page number")
        exit(1)

# Initialize the URL based on the scraping type
rawTargetUrl = "https://www.yad2.co.il/realestate/forsale?Page={}"
if isCommercial:
    rawTargetUrl = "http://www.yad2.co.il/Nadlan/business.php?Page={}"
elif isResidential:
    rawTargetUrl = "http://www.yad2.co.il/Nadlan/sales.php?Page={}"

# Prepare for scraping by initializing directories
initDirs()

# Loop through pages and collect data
exceptionCount = 0
exceptionIDs = []
if not inputUrl:
    for pageNum in range(sPageNum, ePageNum + 1):
        targetUrl = rawTargetUrl.format(pageNum)
        print(f"[>]. Scraping Page {pageNum}: {targetUrl}")
        try:
            outputData = scrapUrlData(targetUrl, useProxy, delayInterval)
        except Exception as e:
            exceptionCount += 1
            exceptionIDs.append(pageNum)
            print(e)
            print(f"[!]. Exception happened at page {pageNum}")
        
        print("[!]. Dumping data into output file")
        dumpDataFile(outputData, pageNum, outFile=outFile)

    # Prepare a final report
    prepareReport(outFile, sPageNum, ePageNum)

    # Perform cleanup if needed
    if doCleanup:
        print("[!]. Performing a cleanup operation")

elif inputUrl:
    # Scraping a single custom URL
    targetUrl = inputUrl
    print(f"[>]. Scraping URL: {targetUrl}")
    try:
        outputData = scrapUrlData(targetUrl, useProxy, delayInterval)
    except Exception as e:
        print(e)
    
    print("[!]. Dumping data into output file")
    dumpDataFile(outputData, -1, outFile=outFile)

# Send an email after completion
endTime = time.time()
endTimeStamp = datetime.fromtimestamp(endTime).strftime('%Y-%m-%d-%H:%M:%S')
if os.path.exists(outFile):
    sendEmail(outFile, sPageNum, ePageNum, timeStamp, endTimeStamp)

print(f"[!]. Task completed at '{endTimeStamp}'")
print(f"[!]. Total encountered Exceptions: {exceptionCount}")
print(f"[!]. Encountered Exception IDs: {', '.join(exceptionIDs)}")
