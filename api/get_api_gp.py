from xml.dom.minidom import Element
from flask import Flask , render_template
from flask_mysqldb import MySQL
from Base import *
import re
import glob
import os
import shutil
from datetime import date , datetime , timedelta
import time
from flask import request , url_for , send_file , jsonify , json
from flask_api import FlaskAPI , status , exceptions
from operator import itemgetter
from lxml import html
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor , wait
from operator import itemgetter


def getPrice(codeAsin):
    link = 'https://www.amazon.com/gp/product/{}/'.format(codeAsin)
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
    # delivery = htmlTest.find('span', id="a-offscreen")
    # if(delivery):
    #     print(delivery.text.strip())
    element = htmlTest.find('span', class_="a-offscreen")
    if(element):
        print(element.text.strip())
        return element.text.strip()
    return None

def getname(codeAsin):
    link = 'https://www.amazon.com/gp/product/{}/'.format(codeAsin)
    codeHTML = CodeHTML(link)
    htmlTest = codeHTML.beautifulSoup()
    delivery = htmlTest.find('span', id="productTitle")
    if(delivery):
        print(delivery.text.strip())
        return delivery.text.strip()
    element = htmlTest.find('span', class_="a-size-large product-title-word-break")
    if(element):
        print(element.text.strip())
        return element.text.strip()
    return None

def getype(codeAsin):
    link = 'https://www.amazon.com/gp/product/{}/'.format(codeAsin)
    codeHTML = CodeHTML(link)
    htmlTest = codeHTML.beautifulSoup()
    link={}
    codeasins = htmlTest.findAll("li" , class_ ="swatchAvailable")
    codeasin = htmlTest.findAll("li" , class_="swatchSelect")
    
    for code in codeasin:
        texts_asin = str(code['id']+"_codeasin")
        texts_color = str(code['id']+"_color")
        texts_price = str(code['id']+"_price")
        texts_option = str(code['id']+"_option")
        st = str(code['title'])
        name_color = st[15:]
        link[texts_asin]= code['data-defaultasin']
        link[texts_color]= name_color
        element = htmlTest.find('span', id=texts_price)
        stt = element.text.strip()
        if "option" in stt:
            link[texts_option] = stt[:9]
            link[texts_price]= stt[14:]
        else:
            link[texts_price] = element.text.strip()

    for codes in codeasins:
        texts_asin = str(codes['id']+"_codeasin")
        texts_color = str(codes['id']+"_color")
        texts_price = str(codes['id']+"_price")
        texts_option = str(codes['id']+"_option")
        st = str(codes['title'])
        name_color = st[15:]
        link[texts_asin]= codes['data-defaultasin']
        link[texts_color]= name_color
        element = htmlTest.find('span', id=texts_price)
        tt = element.text.strip()
        if "option" in tt:
            link[texts_option] = tt[:9]
            link[texts_price]= tt[14:]
        else:
            link[texts_price] = element.text.strip()

    return link
def getInfos():
    pass


