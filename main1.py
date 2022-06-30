from xml.dom.minidom import Element
from flask import Flask , render_template
from flask_mysqldb import MySQL
from Base import *
import re
import glob
import os
import shutil
import json
from datetime import date , datetime , timedelta
import time
from flask import request , url_for , send_file , jsonify
from flask_api import FlaskAPI , status , exceptions
from operator import itemgetter
from lxml import html
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor , wait
from operator import itemgetter


# app = Flask(__name__)
# app.config["MYSQL_HOST"] = 'localhost'
# app.config["MYSQL_USER"] = 'root'
# app.config["MYSQL_PASSWORD"] = ''
# app.config['MYSQL_DB'] ='amazon'
# mysql = MySQL(app)
futures =[]
executor = ThreadPoolExecutor(max_workers=10)
imageFolder ="./tmp"
data={}

def getAsin(url):
    codeAsin = None
    mask = """.*/dp/([^/]+)/.*"""
    m = re.match(mask,url)
    if m:
        codeAsin = m.group(1).strip()
    if codeAsin is None:
        mask = """.*/gp/product/([^/]+)/.*"""
        m = re.match(mask , url)
        if m:
            codeAsin = m.group(1).strip()
            codeAsin = codeAsin[0:10]
    if codeAsin is None:
        mask = """.*/gp/product/([^/]+)?pf_rd_r.*"""
        m = re.match(mask,url)
        if m:
            codeAsin = m.group(1).strip()
            codeAsin = codeAsin[0:10]
    print(codeAsin)
    return codeAsin

def getPrice2(codeAsin):
    link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeAsin)
    codeHTML = CodeHTML(link)
    root = codeHTML.tree()
    elements = root.xpath(
        '//*/td[@class="a-span12"]/span[@id="priceblock_ourprice"]')
    if elements != None and len(elements) != 0:
        return elements[0].text.strip()
    elements = root.xpath(
        '//*/td[@class="a-span12"]/span[@id="priceblock_saleprice"]')
    if elements != None and len(elements) != 0:
        return elements[0].text.strip()

    elements = root.xpath(
        '//*/div[@class="a-section a-spacing-small a-spacing-top-small"]/div[@id="olp-upd-new"]/span/a')
    if elements != None and len(elements) != 0:
        element = elements[0]
        str = html.tostring(element, encoding='utf-8').decode("utf-8")
        mask = """(\\$[0-9\\.]+)"""
        matchs = re.findall(mask, str)
        for m in matchs:
            return m
    htmlTest = codeHTML.beautifulSoup()
    delivery = htmlTest.find('span', id="contextualIngressPtLabel")
    if(delivery):
        print(delivery.text.strip())
    element = htmlTest.find('span', class_="a-size-medium a-color-price")
    if(element):
        print(element.text.strip())
        return element.text.strip()
    return None   

def main():
    app = FlaskAPI(__name__)
    @app.after_request
    def after_request(response):
        # Add and remove custom headers for Security reasons
        # https://github.com/shieldfy/API-Security-Checklist/blob/master/README-de.md
        # and after Astra Security Check
        ContentSecurityPolicy = ''
        ContentSecurityPolicy += "default-src 'self'; "
        ContentSecurityPolicy += "script-src 'self' 'unsafe-inline'; "
        ContentSecurityPolicy += "style-src 'self' 'unsafe-inline'; "
        ContentSecurityPolicy += "img-src 'self' data:; "
        ContentSecurityPolicy += "connect-src 'self';"
        response.headers.add('Content-Security-Policy',  ContentSecurityPolicy)
        response.headers.add('X-Content-Type-Options', 'nosniff')
        response.headers.add('Strict-Transport-Security',
                             'max-age=86400; includeSubDomains')
        response.headers.add('X-Frame-Options', 'deny')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('X-XSS-Protection', '1; mode=block')
        response.headers.set('Server', '')

        # This is neccessary for a project partner
        response.headers.add('Access-Control-Allow-Origin', '*')
        # header = response.headers
        # header['Access-Control-Allow-Origin'] = '*'
        # header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        # header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
        return response
    @app.route("/get_price_product_amazon" , methods=['POST'])
    def get_price():
        global data
        data = {}
        url = str(request.data.get('link_ref', ' '))
        productDir = getAsin(url)
        price = getPrice2(productDir)
        data["price"] = price
        response = jsonify({"data" : data})
        return {"mess" : response}

    if __name__=='__main__':
        app.run(debug=True)

main()