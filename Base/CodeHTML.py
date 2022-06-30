import time, io, os, re
import hashlib
from bs4 import BeautifulSoup
from lxml import html
from html.parser import HTMLParser 
import datetime
import xlsxwriter
import requests
import json
import progressbar
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
def remove_element(el):
    parent = el.getparent()
    if el.tail.strip():
        prev = el.getprevious()
        if prev is not None:
            prev.tail = (prev.tail or '') + el.tail
        else:
            parent.text = (parent.text or '') + el.tail
    parent.remove(el)

class CodeHTML:
	link = None
	page = None
	def __init__(self, link):
		self.link = link
		software_names = [SoftwareName.CHROME.value]
		operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
		user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
		self.user_agent = user_agent_rotator.get_random_user_agent()

	def getPage(self):
		if self.page == None:
			# headers = {
			# 	"authority": "www.amazon.com",
			# 	# "upgrade-insecure-requests": 1,
			# 	"sec-fetch-user": "?1",
			# 	"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
			# 	# "sec-fetch-mode": "navigate",
			# 	# "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
			# 	# "sec-fetch-site": "none",
			# 	# "accept-encoding": "gzip, deflate, br",
			# 	'cookie': 'session-id=133-8332163-5703405; i18n-prefs=USD; ubid-main=130-0598328-8755668; aws-ubid-main=620-2337503-8840722; regStatus=registered; s_fid=2F707522184EF1B5-12E58032342F4197; aws-target-data=%7B%22support%22%3A%221%22%7D; s_vnum=2042701943008%26vn%3D3; s_nr=1610948212299-Repeat; s_dslv=1610948212301; lc-main=en_US; remember-account=false; aws-userInfo-signed=eyJ0eXAiOiJKV1MiLCJrZXlSZWdpb24iOiJ1cy1lYXN0LTEiLCJhbGciOiJFUzM4NCIsImtpZCI6ImYzZjk4MmNhLTlhNWUtNGY4OC1hMTc1LTVlNTYxMDMwNWQ4NSJ9.eyJzdWIiOiIiLCJzaWduaW5UeXBlIjoiUFVCTElDIiwiaXNzIjoiaHR0cDpcL1wvc2lnbmluLmF3cy5hbWF6b24uY29tXC9zaWduaW4iLCJrZXliYXNlIjoiXC9SN0tVa3kzM0pMRHFlMmtcL0hZNjFpVlBuMUpvR0IxQ2xQWmF1SDBNQm80PSIsImFybiI6ImFybjphd3M6aWFtOjo1OTYyODQ2MzU4MTA6cm9vdCIsInVzZXJuYW1lIjoiVGVzdGVyJTIwYXdzJTIwVGVhbSUyMEROIn0.0K3Q5LYbOBkkPICrqOY1Kd5pORKgNzCD5n7019O0A6m5fKdpIGAelhSZ3eKoDgc78H6NrhgNV1pSqpcPaxv86vCU2UUG3ogZ-74r4RIV28ShYW3LIywFDaM9CMLzwQcn; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A596284635810%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22Tester%2520aws%2520Team%2520DN%22%2C%22keybase%22%3A%22%2FR7KUky33JLDqe2k%2FHY61iVPn1JoGB1ClPZauH0MBo4%5Cu003d%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D; x-amz-captcha-1=1612258766686024; x-amz-captcha-2=cLGEthV+RbtldPPS+5g/fQ==; s_cc=true; aws_lang=en; aws-target-session-id=1612338189875-619315; aws-target-visitor-id=1610448581531-398124.38_0; session-token=Mynnysj3WgYqP2vK9YglLs6Jeo/qxomQ6BpLteIOLpmzOw7hUpWKFiyVSHNEYBYyUOsfW8BzESCQEXXmq2MZNryCUj5eNm8FrDcx2Lhr7SkjH3h28j7q7bLROwMH5oHNSCxKwfvIfWtQOnVO6+Jpk5zHmuwVLHBcZR5GIqPaZdWQnxNTWdLQ+o55qjZo0/vv; skin=noskin; session-id-time=2082787201l; csm-hit=tb:s-CRCBQS0X2996ZTGD6Z1Q|1612339847983&t:1612339852616&adb:adblk_no',
			# 	"accept-language": "en-US,en;q=0.9"
			# }
			# request = urllib2.Request(self.link, headers=headers)
			# self.page = urllib2.urlopen(request).read()
			# response = requests.get(self.link, headers=headers)
			# response.encoding = 'utf-8'
			# self.page = response.text

			headers = {
				'authority': 'www.amazon.com',
				'pragma': 'no-cache',
				'cache-control': 'no-cache',
				'upgrade-insecure-requests': '1',
				'user-agent': self.user_agent,
				'sec-fetch-mode': 'navigate',
				'sec-fetch-user': '?1',
				'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
				'sec-fetch-site': 'none',
				'sec-fetch-user': '?1',
				'sec-fetch-dest': 'document',
				# 'referer': 'https://www.amazon.com/s?k=Shoe&ref=nb_sb_noss',
				'accept-encoding': 'gzip, deflate, br',
				'accept-language': 'en-US,en;q=0.9',
				# 'cookie': 's_fid=294CC7CD90F34247-007CD949B05CD739; regStatus=pre-register; session-id=136-6362132-5998706; session-id-time=2082787201l; i18n-prefs=USD; sp-cdn="L5Z9:VN"; ubid-main=131-5245671-0008925; x-wl-uid=1UZHij9RxCu1dFkcFEuNsXeRBNFOIUxfxS7Q6966EOBqljco1w7iy6I8vMyuLWgN8VFE1GiRlWR0=; aws-priv=eyJ2IjoxLCJldSI6MCwic3QiOjB9; aws-target-static-id=1570455712715-457242; aws-target-data=%7B%22support%22%3A%221%22%7D; aws-target-visitor-id=1570455712737-136140.22_13; s_vn=1601117125209%26vn%3D5; s_pers=%20s_vnum%3D2002699742224%2526vn%253D2%7C2002699742224%3B%20s_invisit%3Dtrue%7C1570729456311%3B%20s_nr%3D1570727656320-New%7C1578503656320%3B; s_nr=1570870740319-Repeat; s_vnum=2002785061057%26vn%3D4; s_dslv=1570870740322; session-token=xXfPNrPGe+wE0fApj5UtKnE3GlyNEs6a0kXo6XwzlGfy0DZRMZmQXdiPEgEDy5p8Mudowh0xPuW20t12tWOJbN4bR4IdOom/ctnSNbZIcOBiNbqpaJQ9IFFiSUP/OKVwg3tFuFBaRZDZIE+xQP08by7CIWpheGaRaV8W7nqpLpB7QeATy4DObpuzuMSlpN72; csm-hit=tb:2EWWPPQF35P11WVNZXGB+sa-2EWWPPQF35P11WVNZXGB-HJY2N6MT78TMH76AG53V|1571568932722&t:1571568932722&adb:adblk_yes'
				# 'CloudFront-Viewer-Country-Name': 'United States',
				# 'CloudFront-Viewer-Country-Region': 'MI',
				# 'CloudFront-Viewer-Country-Region-Name': 'Michigan',
				# 'CloudFront-Viewer-City': 'Ann Arbor',
				# 'CloudFront-Viewer-Postal-Code': '48105',
				# 'CloudFront-Viewer-Time-Zone': 'America/Detroit',
				# 'CloudFront-Viewer-Latitude': '42.30680',
				# 'CloudFront-Viewer-Longitude': '-83.70590',
				# 'CloudFront-Viewer-Metro-Code': '505',
				'cookie': 'session-id=131-1220769-3364415; session-id-time=2082787201l; i18n-prefs=USD; ubid-main=134-4184894-3235025; lc-main=en_US; session-token=xh/Dy3NQd7T0020SZD1o/nXkZsqf1XkYIi/tMGMXlPCZC5MRW9Rlxwkmfyz6S62caARnEB1FXchVfT+7YgrZ/9n6tbTPwmIbk85gemaP9RpGySLyqv9QtCoDKRIxCUj3XT6e9NEMf0UaNVlkkUP21QIN6mBINu3jsFsKGN9f4JOZaADmc290sAXzuFF+1HJN; skin=noskin; csm-hit=tb:s-JYVJJVD7VSKMRF7MNH82|1614201311322&t:1614201313760&adb:adblk_yes'
			}
			s = requests.session()
			response = s.get(self.link, headers=headers)
			self.page = response.text 

		return self.page
	def editPage(self, str1,str2):
		self.page = self.page.replace(str1, str2)
	def beautifulSoup(self):
		self.getPage()
		if self.page!= None:
			
			return BeautifulSoup(self.page)
		else:
			return None
	def tree(self):
		self.getPage()
		if self.page!= None:
			# print(self.page)
			myparser = html.HTMLParser(encoding="utf-8")
			return html.fromstring(self.page, parser=myparser)
		else:
			return None
	def elementsWithXpath(self, xpath):
		tree = self.tree()
		if tree!=None:
			return tree.xpath(xpath)
		else:
			return []
	def elementWithXpath(self, xpath):
		elements = self.elementsWithXpath(xpath)
		if elements == None or len(elements) == 0:
			return None
		else:
			return elements[0]

def readLines(fileName):
	arrayDataOut = []
	if not os.path.exists(fileName):
		file = open(fileName, "w")
	with open(fileName) as file:
		arrayData = file.readlines()
	for data in arrayData:
		if len(data.strip())>0:
			arrayDataOut.append(data.strip())
	return arrayDataOut

def writeLine(fileName, line):
	with open(fileName, "a") as myfile:
		myfile.write("%s\n" %line)

def writeFile(fileName, data):
	with io.open(fileName, mode="w", encoding="utf-8") as myfile:
		myfile.write(u'{}'.format(data))
def createFolderIfNotExists(pathFolder):
	print ('pathFolder =', pathFolder)
	if not os.path.exists(pathFolder):
		os.makedirs(pathFolder)