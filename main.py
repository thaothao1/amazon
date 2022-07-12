from copyreg import dispatch_table
from xml.dom.minidom import Element
from flask import Flask, render_template
from flask_mysqldb import MySQL
from Base import *
import re
import glob
import os
import shutil
from datetime import date, datetime, timedelta
import time
from flask import request, url_for, send_file, jsonify, json
from flask_api import FlaskAPI, status, exceptions
from operator import itemgetter
from lxml import html
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor, wait
from operator import itemgetter
from api.get_api import getAsin, getHTML, getInfos, getInfosThread, getlink, getPrice2, getSizes, loadImages
from api.get_api_gp import getPrice, getname, getype
from api.get_price_asin import stype_link

app = FlaskAPI(__name__)
# app.config["MYSQL_HOST"] = 'localhost'
# app.config["MYSQL_USER"] = 'root'
# app.config["MYSQL_PASSWORD"] = ''
# app.config['MYSQL_DB'] ='amazon'
# mysql = MySQL(app)
FORDER_IMAGE = os.path.join('tmp', '')
# FORDER_IMAGE_UPLOAD = os.path.join('uploads', '')
urlEntry = None
spEntry = None
nColor = 0
imageFolder = "./tmp"
executor = ThreadPoolExecutor(max_workers=10)
futures = []
data = {}
entryUrls = []
test = []


def main():
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

    @app.route("/get_product_amazon", methods=['POST'])
    def getAllImage():
        global data
        data = {}
        url = str(request.data.get('link_ref', ''))
        productDir = getAsin(url)
        codeHTML = CodeHTML(url)
        html = codeHTML.getPage()
        sizes = getSizes(html)
        data["asinCode"] = productDir
        data["linkRoot"] = url
        price = getPrice2(productDir)
        loadImages(productDir, html, codeHTML)
        info_sort = []
        try:
            info = getInfos(sizes, html, codeHTML, productDir)
            info_sort = sorted(info, key=itemgetter('indexSort'))
        except:
            info_sort = []
        data["price"] = price
        data["info"] = info_sort
        response = jsonify({"data": data})
        # response = jsonify({"data": data})
        # Enable Access-Control-Allow-Origin
        return response

    @app.route("/get_amazon", methods=['POST'])
    def get_all():
        global data
        data = {}
        url = str(request.data.get('link_ref', ''))
        productDir = getAsin(url)
        codeHTML = CodeHTML(url)
        html = codeHTML.getPage()
        stype = getype(productDir)
        name = getname(productDir)
        data["asinCode"] = productDir
        data["linkRoot"] = url
        data["name"] = name
        data["stype"] = stype
        # response = jsonify({"data" : data})
        return {"response": data}

    @app.route("/get_price_codeasin", methods=['POST'])
    def get_price_codeasin():
        response = []
        url = request.data.get('data', '')
        for i in url:
            codeasin = i["codeasin"]
            stype = i["stype"]
            price_old = i["price"]
            data1 = stype_link(codeasin, stype, price_old)
            response.append(data1)
        return {"data": response}

    if __name__ == '__main__':
        app.run(debug=True, host="0.0.0.0", port="5000")


main()
