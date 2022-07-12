from unittest import result
from Base import *
import re
import requests
import glob
import os
import shutil
import json
from datetime import date, datetime, timedelta
import time

from flask import request, url_for, send_file, jsonify
from flask_api import FlaskAPI, status, exceptions
from operator import itemgetter
from lxml import html

from concurrent import futures
from concurrent.futures import ThreadPoolExecutor, wait
from operator import itemgetter
from api.get_api import getAsin, getHTML, getInfos_sz, getInfosThread_sz, getname_t, getPrice_sz, getPrice_t, getSizes_sz, getstype_sz, getype_t, loadImages_sz
from api.get_api_gp import getPrice, getname, getype, getInfos, getInfosThread, getPrices, getSizes, getstype, loadImages, getHTML1
from api.get_price_asin import stype_link
from api.get_zip_code import zip_code


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
db = {}


def main():
    app = FlaskAPI(__name__)

    app.config["FORDER_IMAGE"] = FORDER_IMAGE

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

    @app.route("/amazon/api/getImage", methods=['POST'])
    def getAllImage():
        global data
        data = {}
        url = str(request.data.get('link_ref', ''))
        res = zip_code(url)
        productDir = getAsin(res)
        codeHTML = CodeHTML(res)
        html = codeHTML.getPage()
        st = getstype_sz(productDir)
        if st == "size":
            sizes = getSizes_sz(html)
            data["asinCode"] = productDir
            data["linkRoot"] = res
            price = getPrice_sz(productDir)
            loadImages_sz(productDir, html, codeHTML)
            info_sort = []
            try:
                info = getInfos_sz(sizes, html, codeHTML, productDir)
                info_sort = sorted(info, key=itemgetter('indexSort'))
            except:
                info_sort = []
            data["price"] = price
            data["info"] = info_sort
            response = jsonify({"data": data})
            return response
        else:
            stype = getype_t(productDir)
            name = getname_t(productDir)
            db["asinCode"] = productDir
            db["linkRoot"] = res
            db["name"] = name
            db["stype"] = stype
            # response = jsonify({"data" : data})
            return {"response": db}
        # response = jsonify({"data": data})
        # Enable Access-Control-Allow-Origin

    @app.route("/get_amazon", methods=['POST'])
    def get_all():
        # global db
        db = {}
        url = str(request.data.get('link_ref', ''))
        result = zip_code(url)
        productDir = getAsin(result)
        codeHTML = CodeHTML(result)
        html = codeHTML.getPage()
        st = getstype_sz(productDir)
        if st == "size":
            sizes = getSizes(html)
            data["asinCode"] = productDir
            data["linkRoot"] = result
            price = getPrices(productDir)
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
            return response
        else:
            stype = getype(productDir)
            name = getname(productDir)
            db["asinCode"] = productDir
            db["linkRoot"] = result
            db["name"] = name
            db["stype"] = stype
            # response = jsonify({"data" : data})
            return {"response": db}

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
