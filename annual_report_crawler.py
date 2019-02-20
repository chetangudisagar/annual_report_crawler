#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
---------------Annual Reports Crawler---------------
This script can be used to crawl annual reports from public repositories.
Example website used is http://www.annualreports.com
This program takes in a Excel File as an input with "Company Name" containing the company names whose reports will be generated. 
Make sure you have python library installers like pip and install dependencies such as all the imports and 'lxml' -
	pip install lxml


Usage:
  annual_report_crawler.py -f companiesList.xlsx
  annual_report_crawler.py (-h | --help)
  annual_report_crawler.py --version
"""

__author__ = "Chetan Gudisagar"
__copyright__ = ""
__credits__ = ["Himanshu Choudhary"]
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Chetan Gudisagar"
__email__ = "chetangudisagar@gmail.com"
__status__ = "Development"


from bs4 import BeautifulSoup
import pandas as pd
import requests
from pathlib import Path
import argparse

domainURL = 'http://www.annualreports.com' #company domain url
chunkSize = 20000 #Size in Bytes to download part by part and save
localPath = 'D:/Codes/crawler/output/' #Local system path to store the output


def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Optional arguments
    parser.add_argument("-f","--companiesListfile", help="Excel file name", type=str, default='companiesList.xlsx')
    parser.add_argument("-chsize", "--chunkSize", help="Size in Bytes to download part by part and save", type=int, default=20000)
    parser.add_argument("-lpath", "--localPath", help="Local system path to store the output", type=str, default='D:/Codes/crawler/output/')
    parser.add_argument("-d", "--domain", help="Company Domain URL", type=str, default='http://www.annualreports.com')
    parser.add_argument("-c", "--companyName", help="Company Name", type=str, default='___')

    # Print version
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    # Parse arguments
    args = parser.parse_args()

    return args

def fetchYearWiseReports(fileLinkWithOutYear, companyName):

	for i in range(2014,2015):
		reportURL = fileLinkWithOutYear + str(i) + '.pdf'
		print("reportURL " + reportURL)

		#crate path if not exists
		filePath = localPath + companyName
		p = Path(filePath)
		p.mkdir(parents=True, exist_ok=True)


		fileName = str(Path(filePath + '/' + reportURL.split('/')[-1]))

		#get the file and print it
		responseData = requests.get(reportURL, stream=True)
		print("responseData.status_code -" +str(responseData.status_code))
		if(responseData.status_code == 200):
			print("fileName - " + fileName)
			with open( fileName , 'wb') as file:
			    for chunk in responseData.iter_content(chunkSize):
			        file.write(chunk)
			    file.close()

def fetchYearWiseReportsLinks(companyURL, companyName):
	print("Fetching report for " + companyURL)
	URL = domainURL + companyURL

	#hit a get request
	responseData = requests.get(URL)
	
	#format to BeautifulSoup
	soupData = BeautifulSoup(responseData.text,"lxml")
	#print(soupData)

	flag=0

	#Begin the Party!!
	for link in soupData.find_all('a'):
		#print(link.get('href'))
		if (link.get('href')!=None and '/HostedData/AnnualReportArchive/' in link.get('href') and flag==0 ) :
			print(link.get('href'))
			fileLinkWithOutYear = link.get('href')[:-8]
			print('fileLinkWithOutYear - '+fileLinkWithOutYear)
			fetchYearWiseReports(domainURL + fileLinkWithOutYear, companyName)
			flag=1


def crawl(companyName):
	print("Crawling " + companyName)

	#split by spaces
	companyNameParts = companyName.split(' ') 
	#print(companyNameParts)

	#construct URL
	URL = domainURL+"/Companies?search="
	for companyNamePart in companyNameParts:
		URL = URL + companyNamePart + '+'
	URL = URL[:-1] #remove additional + in the end
	URL = URL + '&submit=Search'
	#print(URL)

	#hit a get request
	responseData = requests.get(URL)
	
	#format to BeautifulSoup
	soupData = BeautifulSoup(responseData.text,"lxml")
	#print(soupData)

	#Begin the Party!!
	for link in soupData.find_all('a'):
		if(link.get('href')!=None and '/Company' in link.get('href')):
			print(link.get('href'))
			fetchYearWiseReportsLinks(link.get('href'), companyName)
	#r = requests.get('https://www.google.com')



# Parse the arguments
args = parseArguments()

chunkSize = args.chunkSize
localPath = args.localPath
domainURL = args.domainURL

if args.companyName != "___" :
	crawl(companyName)
else:
	companiesListfile = args.companiesListfile
	companiesList = pd.read_excel(companiesListfile)
	companiesNamesList = companiesList['Company Name']
	for companyName in companiesNamesList:
		crawl(companyName)
# crawl("JPMorgan Chase")
# crawl("google")
# crawl("la la land")
