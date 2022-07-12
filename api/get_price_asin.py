from flask import Flask, render_template
from flask_mysqldb import MySQL
from Base import *
from flask_api import FlaskAPI
from api.get_api import getAsin, getHTML, getname_t, getInfos_sz, getInfosThread_sz, getPrice_sz, getPrice_t, getSizes_sz, getstype_sz, getype_t

from operator import itemgetter

app = FlaskAPI(__name__)


def stype_link(CodeAsin, stype, price_old):
    # tyle_link1 :
    if stype == "gp":
        link1 = 'https://www.amazon.com/gp/product/{}?th=1'.format(CodeAsin)
        stype1 = "gp"
        codeasin = CodeAsin
        price_old = price_old
        return getdata(link1, stype1, codeasin, price_old)
    else:
        # type_link2
        if stype == "dp":
            link2 = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(CodeAsin)
            stype2 = "dp"
            codeasin = CodeAsin
            price_old = price_old
        return getdata(link2, stype2, codeasin, price_old)


def getdata(link, stype, codeasin, price_old):
    codeHTML = CodeHTML(link)
    html = codeHTML.getPage()
    htmlTest = codeHTML.beautifulSoup()
    price_old = price_old
    type = htmlTest.find('div', class_="a-row a-spacing-micro")
    if (type):
        st = type.text.strip()

        if "Size:" in st:
            sizes = getSizes_sz(html)
            info_sort = []
            try:
                info = getInfos_sz(sizes, html, codeHTML, codeasin)
                info_sort = sorted(info, key=itemgetter('indexSort'))
            except:
                info_sort = []
            data = info_sort
        else:
            data = getype2(codeasin, price_old)
    else:
        data = getype2(codeasin, price_old)
    return data


def getype2(codeasin, price_old):
    link = 'https://www.amazon.com/gp/product/{}/'.format(codeasin)
    codeHTML = CodeHTML(link)
    htmlTest = codeHTML.beautifulSoup()
    codeasin = htmlTest.findAll("li", class_="swatchSelect")
    links = {}
    for code in codeasin:
        texts_price = str(code['id']+"_price")
        st = str(code['title'])
        name_color = st[15:]
        links["codeasin"] = code['data-defaultasin']
        links["color"] = name_color
        links["stype"] = "gp"
        links["price_old"] = price_old
        # links["stype"]= "gp"
        element = htmlTest.find('span', id=texts_price)
        stt = element.text.strip()
        if "option" in stt:
            links["option"] = stt[:9]
            links["price_new"] = stt[14:]
        else:
            links["price_new"] = element.text.strip()
    return links


def getype1(codeasin, price_old):
    link = 'https://www.amazon.com/dp/{}?th=1&psc=1'.format(codeasin)
    codeHTML = CodeHTML(link)
    htmlTest = codeHTML.beautifulSoup()
    links = {}
    links['codeasin'] = codeasin
    links['stype'] = "dp"
    color = htmlTest.find('span', class_='selection')
    links['color'] = color.text.strip()
    size = htmlTest.find('span', class_='a-dropdown-prompt')
    links['size'] = size.text.strip()
    links["price_old"] = price_old
    price = htmlTest.find('span', class_='a-offscreen')
    links["price_new"] = price.text.strip()
    return links
