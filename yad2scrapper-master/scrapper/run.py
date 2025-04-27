# Import necessary modules
from modules.indexParser import *
from modules.reportMaker import *
from argparse import ArgumentParser
from datetime import datetime
from modules.sendEmail import sendEmail
import os
import time
import re
import logging

# Configure logger
LOG_FILENAME = 'webScrapper.log'
format = '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s[%(process)d]%(funcName)10s: %(message)s'
logging.basicConfig(filename=LOG_FILENAME, format=format, level=logging.DEBUG)
logger = logging.getLogger('webScrapper')

# Regex pattern for URL validation
urlMatcher = re.compile(r'https?://[^/]+')

# Create a timestamp for file naming
ts = time.time()
timeStamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H:%M:%S')

# Function to validate if a URL is correct
def validateUrl(url):
    if urlMatcher.search(url):
        return True
    return False

# Parse command line arguments
parser = ArgumentParser(description='Scrap data from YAD')
parser.add_argument('filename', help='Output filename')
parser.add_argument('-u', '--url', dest='inputUrl', help='Custom input URL for scraping')
parser.add_argument('-s', '--start-page', type=int, dest='sPageNum', default=1, help='Start page number')
parser.add_argument('-e', '--end-page', type=int, dest='ePageNum', help='End page number')
parser.add_argument('-p', '--use-proxy', dest='useProxy', action='store_true', help='Enable proxy usage')
parser.add_argument('-t', '--use-delay', dest='delayInterval', type=int, help='Set delay (in seconds) between HTTP requests')
parser.add_argument('-C', '--cleanup', dest='cleanup', action='store_true', help='Cleanup temporary files after scraping')

# Define mutually exclusive scraping types
group = parser.add_mutually_exclusive_group()
group.add_argument('-r', '--residential', dest='isResidential', action='store_true', help="Scrap default residential listings")
group.add_argument('-c', '--commercial', dest='isCommercial', action='store_true', help="Scrap default commercial listings")

# Parse the arguments
args = parser.parse_args()
filename = args.filename
sPageNum = args.sPageNum
ePageNum = args.ePageNum
useProxy = args.useProxy
delayInterval = args.delayInterval
inputUrl = args.inputUrl
doCleanup = args.cleanup
isResidential = args.isResidential
isCommercial = args.isCommercial

# Validate if necessary options are provided
if (not inputUrl) and (not (isCommercial or isResidential)):
    print("[!]. Please provide scrapping type either -r or -c\n")
    exit(1)

# Validate custom URL if provided
if inputUrl:
    inputUrl = inputUrl.strip()
    if not validateUrl(inputUrl):
        print("[ERROR]. URL pattern doesn't seem right")
        exit(1)

print("\n")

# Validate start and end page numbers
if not inputUrl:
    if sPageNum and (not ePageNum):
        print("[!]. End page number is not mentioned, only starting page will be scraped\n")
        ePageNum = sPageNum

    if sPageNum > ePageNum:
        print("[ERROR]. Start page number should be less than end page number\n")
        exit(1)

    if ePageNum and (not sPageNum):
        print("[!]. Please provide start page number as well\n")
        exit(1)
elif inputUrl:
    print("[!]. Start and End page ranges are ignored when using a custom URL\n")

# Display proxy usage
if useProxy:
    print("[>]. Firefox proxy profile enabled\n")

# Display delay info
if delayInterval:
    print("[>]. Configured a {} seconds delay for each HTTP request\n".format(delayInterval))

# Create output filename with timestamp
outFile = "{}-{}.csv".format(filename, timeStamp)

print("[!]. Task launched at '{}'".format(timeStamp))

# Initialize variables
targetUrl = None
isFirstPage = True
exceptionCount = 0

# Initialize necessary output directories
initDirs()

# Default URL templates for residential and commercial scraping
rawTargetUrl = "http://www.yad2.co.il/Nadlan/sales.php?multiSearch=1&AreaID=&City=&HomeTypeID=&fromRooms=&untilRooms=&fromPrice=50000&untilPrice=&PriceType=1&fromSquareMeter=&untilSquareMeter=&FromFloor=&ToFloor=&Info=&PriceOnly=1&Order=price&Page={}"

if isCommercial:
    rawTargetUrl = "http://www.yad2.co.il/Nadlan/business.php?AreaID=&City=&Sale=&HomeTypeID=&fromSquareMeter=&untilSquareMeter=&fromPrice=1000&untilPrice=&PriceType=1&fromRooms=&untilRooms=&Info=&PriceOnly=1&Page={}"
elif isResidential:
    rawTargetUrl = "http://www.yad2.co.il/Nadlan/sales.php?multiSearch=1&AreaID=&City=&HomeTypeID=&fromRooms=&untilRooms=&fromPrice=50000&untilPrice=&PriceType=1&fromSquareMeter=&untilSquareMeter=&FromFloor=&ToFloor=&Info=&PriceOnly=1&Order=price&Page={}"

# Track exceptions
exceptionIDs = []

# Start scraping pages if no custom URL provided
if not inputUrl:
    for pageNum in range(sPageNum, ePageNum + 1):
        targetUrl = rawTargetUrl.format(pageNum)
        print("[>]. Scraping Page {}: {}\n".format(pageNum, targetUrl))

        try:
            outputData = scrapUrlData(targetUrl, useProxy, delayInterval)
        except Exception as e:
            exceptionCount += 1
            exceptionIDs.append(pageNum)
            print(e)
            print("[!]. Exception happened at page {}".format(pageNum))
            outputData = None  # <-- важно явно установить None


        if outputData:
            print("[!]. Dumping data into output file")
            fileGenerated = dumpDataFile(outputData, pageNum, outFile=outFile)
        else:
            print(f"[!] Skipping page {pageNum} due to error.\n")

    # Prepare final report after scraping
    prepareReport(outFile, sPageNum, ePageNum)

    # Optionally cleanup temporary data
    if doCleanup:
        print("[!]. Performing cleanup operations at path: {}".format(backDir))

# If a custom URL was provided
elif inputUrl:
    targetUrl = inputUrl
    print("[>]. Scraping URL: {}\n".format(targetUrl))

    try:
        outputData = scrapUrlData(targetUrl, useProxy, delayInterval)
    except Exception as e:
        print(e)

    print("[!]. Dumping data into output file")
    fileGenerated = dumpDataFile(outputData, -1, outFile=outFile)

# End timestamp
endTime = time.time()
endTimeStamp = datetime.fromtimestamp(endTime).strftime('%Y-%m-%d-%H:%M:%S')

# Send email with the final file
if os.path.exists(outFile):
    if inputUrl:
        sendEmail(outFile, 1, 1, timeStamp, endTimeStamp)
    else:
        sendEmail(outFile, sPageNum, ePageNum, timeStamp, endTimeStamp)

# Final logs
print("[!]. Task finished at '{}'\n".format(endTimeStamp))
print("[!]. Total encountered Exceptions: {}".format(exceptionCount))
print("[!]. Encountered Exception IDs: {}".format(', '.join(str(x) for x in exceptionIDs)))
