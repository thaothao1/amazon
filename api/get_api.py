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

def getAsin(link):
    codeAsin = None
    mask = """.*/dp/([^/]+)/.*"""
    m = re.match(mask, link)
    if m:
        codeAsin = m.group(1).strip()
    if codeAsin is None:
        mask = """.*/gp/product/([^/]+)/.*"""
        m = re.match(mask, link)
        if m:
            codeAsin = m.group(1).strip()
            codeAsin = codeAsin[0:10]
    if codeAsin is None:
        mask = """.*/gp/product/([^/]+)?pf_rd_r.*"""
        m = re.match(mask, link)
        if m:
            codeAsin = m.group(1).strip()
            codeAsin = codeAsin[0:10]
    print(codeAsin)
    return codeAsin


def getHTML(url):
    codeHTML = CodeHTML(url)
    html = codeHTML.getPage()
    return html


def getSizes(html):
    html = html.replace(';\n', ';<--hoa-->')
    html = html.replace('; //', ';<--hoa-->')
    html = html.replace('\n', ' ')
    html = html.replace('    ', '')
    html = html.replace('  ', ' ')
    html = html.replace(' +', ' ')
    html = html.replace('var ', '\nvar ')
    html = html.replace(';<--hoa-->', ';\n')

    mask = """var dataToReturn = (.+);"""
    matchs = re.findall(mask, html, re.M)
    sizes = []
    for m in matchs:
        json_string = m.replace("\'", '"')
        json_string = json_string.replace('\t', '')
        json_string = json_string.replace(', ]', ']')
        json_string = json_string.replace(',]', ']')

        obj = json.loads(json_string)
        color_names = []
        size_names = []
        asinVariationValues = []

        if 'variationValues' in obj:
            variationValues = obj['variationValues']
            if 'color_name' in variationValues:
                a = variationValues['color_name']
            if 'size_name' in variationValues:
                size_names = variationValues['size_name']
                sizes = size_names
    return sizes


def loadImages(productDir, html, codeHTML):
    global data
    global executor
    global future
    global futures
    future = executor.submit(downloadImageInThread, productDir, html, codeHTML)
    futures.append(future)
    # print("Add new thread download: {}".format(productDir))
    wait(futures)
    print("DONE Images")


def download(pathFile, link, optimize=True):
    # print("download: link = {}".format(link))
    if optimize == True:
        foundFiles = glob.glob("{}.*".format(pathFile))
        if len(foundFiles) > 0:
            # print('download exist path = {}'.format(foundFiles[0]))
            head, tail = os.path.split(foundFiles[0])
    imageTypes = {"image/png": "png", "image/jpeg": "jpg", "image/jpg": "jpg"}
    r = request.get(link, stream=True)
    if r.status_code == 200:
        contentType = r.headers['Content-Type']
        if contentType in imageTypes:
            filePath = "{}.{}".format(pathFile, imageTypes[contentType])
            data["images"].append(filePath)
            with open(filePath, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
    pass


def downloadImageInThread(productDir, html, codeHTML):
    global data
    # tkMessageBox.showinfo( "Error!", "Step 1")
    try:
        # print("downloadImageInThread: {}".format(productDir))
        mask = """var obj = jQuery.parseJSON\\('(.+)'\\);"""
        isFound = False
        matchs = re.findall(mask, html, re.M)
        # print("CHECK ", html)

        for m in matchs:
            if m:
                json_string = m
                obj = json.loads(json_string.replace("\\'", "'"))
                if "colorImages" not in obj:
                    continue
                landingAsinColor = None
                if "landingAsinColor" in obj:
                    landingAsinColor = obj["landingAsinColor"]
                data["images"] = []
                # print(landingAsinColor, obj["colorImages"])
                data["landingAsinColor"] = landingAsinColor
                # print("CHECK ", obj["colorImages"])
                for key, images in obj["colorImages"].items():  # python 3
                    if landingAsinColor != None and key != landingAsinColor:
                        # if key == None:
                        continue
                    title = key.replace('\\/', '-')
                    title = re.sub(
                        '[!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~]', '-', title)
                    title = title.replace('\n', '')
                    title = title.replace(' ', '-')
                    while(title.find('--') != -1):
                        title = title.replace('--', '-')
                    title = title.strip()
                    data["title"] = title
                    isFound = True
                    if "/" in productDir:
                        path = "{}/{}".format(productDir, title)
                        if not os.path.exists(path):
                            os.makedirs(path)
                        # data[url]['pathFolder'] = path
                    else:
                        path = "{}/{}/{}".format(imageFolder,
                                                 productDir, title)
                        if not os.path.exists(path):
                            os.makedirs(path)
                        # data[url]['pathFolder'] = path
                    for idx, image in enumerate(images):
                        # print("image =", image)
                        if "hiRes" in image:
                            linkImage = image["hiRes"]
                        elif "large" in image:
                            linkImage = image["large"]
                        else:
                            continue
                        # print("image = {}".format(linkImage))
                        pathFile = "{}/image_{}".format(path, idx)
                        download(pathFile, linkImage)
                print("DONE")
        if isFound == False:
            print("Tiep tuc tim kiem!")
            productColor = codeHTML.elementWithXpath(
                '//*[contains(text(),"Color:")]/../following-sibling')
            title = None
            # print("----", productColor)
            if productColor != None:
                # print("productColor = ", productColor)
                title = productColor.text.strip()
                title = title.replace('Color: ', '')
                title = title.replace(' +', ' ')
                title = title.strip()
                data["title"] = title
            # html = re.sub(' +', ' ', html)
            # html = re.sub(', \n }', '}', html)
            # html = html.replace(' +', ' ')
            # html = html.replace('\n+', '\n')
            # html = html.replace('{\n', '{')
            # html = html.replace(',\n', ',')
            # html = html.replace(', \n }', '}')

            # solution 1
            # print(html.find('{                '))
            # html = html.replace('{\n                ','{')
            # html = html.replace(',\n                ',',')
            # html = html.replace(')\n                ',')')
            # html = html.replace('\n                ','')
            # solution 2
            array = [line.strip() for line in html.split('\n')]
            html = ('').join(array)
            mask = """var data = (.+),'airyConfig'"""
            test = """\"hiRes\":(.+),\"thumb\":\"https://images-na.ssl-images-amazon.com/images/I/41jPqOjIfPL._AC_US40_.jpg"""
            matchs = re.findall(mask, html, re.M)
            for m in matchs:
                # print("m = ", m)
                if m:
                    json_string = m.replace("\'", '"')
                    json_string = json_string + "}"
                    # print("json_stringB = ",json_string)
                    obj = json.loads(json_string)
                    if "colorImages" not in obj:
                        continue
                    # print("json_stringJSON = ", obj)

                    landingAsinColor = None
                    if "landingAsinColor" in obj:
                        landingAsinColor = obj["landingAsinColor"]
                        data["landingAsinColor"] = landingAsinColor
                    # 	updateColorName(url, landingAsinColor)
                    data["images"] = []
                    for key, images in obj["colorImages"].items():  # python 3
                        # if landingAsinColor != None and key == None:
                        # if key == None:
                        if landingAsinColor != None and key != landingAsinColor:
                            continue
                        if title == None:
                            title = key.replace('\\/', '-')
                            title = re.sub(
                                '[!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~]', '-', title)
                            title = title.replace('\n', '')
                            title = title.replace(' ', '-')
                            while(title.find('--') != -1):
                                title = title.replace('--', '-')
                                title = title.strip()
                                data["title"] = title
                        isFound = True
                        path = "{}/{}/{}".format(imageFolder,
                                                 productDir, title)
                        if not os.path.exists(path):
                            os.makedirs(path)
                        for idx, image in enumerate(images):
                            if "hiRes" in image and image["hiRes"] != None:
                                linkImage = image["hiRes"]
                            elif "large" in image and image["large"] != None:
                                linkImage = image["large"]
                            else:
                                continue
                            # print("image = {}".format(linkImage))
                            pathFile = "{}/image_{}".format(path, idx)
                            download(pathFile, linkImage)

                    print("DONE")
        if isFound == False:
            print('Error Found')
    except:
        print('Error Try')
    pass


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
    # if(delivery):
    #     print(delivery.text.strip())
    element = htmlTest.find('span', class_="a-offscreen")
    if(element):
        # print(element.text.strip())
        return element.text.strip()
    return None

def getlink(html):
    pass

def getInfosThread(codeASIN, size_name, infos, indexSort):
    isFind = False
    isSoldOut = False
    product = None
    # print(f"START {codeASIN} - {size_name}")
    # products = Product.objects(amazon_codeASIN=codeASIN)
    # if products.count() > 0:
    # 	isFind = True
    # 	if products.count() > 1:
    # 		print("Loi dupliacation database: amazon_codeASIN= {}".format(codeASIN))
    # 	product = products[0]
    price = getPrice2(codeASIN)
    # print(f"END {price}")
    # if price == None:
    # 	isSoldOut = True
    # 	if isFind == True:
    # 		price = product.amazon_price
    # else:
    # 	if isFind == True:
    # 		product.amazon_price = price
    # 		product.save()
    # 	else:
    # 		product = Product(title="N/A", amazon_codeASIN=codeASIN)
    # 		product.amazon_price = price
    # 		product.save()
    info = {'codeASIN': codeASIN, 'sizeName': size_name,
            'isSoldOut': isSoldOut, 'price': price, 'indexSort': indexSort}
    infos.append(info)


def getInfos(sizes, html, codeHTML, productDir):
    print("START")
    executor = ThreadPoolExecutor(max_workers=30)
    futures = []
    infos = []
    html = html.replace(';\n', ';<--hoa-->')
    html = html.replace('; //', ';<--hoa-->')
    html = html.replace('\n', ' ')
    html = html.replace('    ', '')
    html = html.replace('  ', ' ')
    html = html.replace(' +', ' ')
    html = html.replace('var ', '\nvar ')
    html = html.replace(';<--hoa-->', ';\n')

    mask = """var dataToReturn = (.+);"""
    matchs = re.findall(mask, html, re.M)

    for m in matchs:
        json_string = m.replace("\'", '"')
        json_string = json_string.replace('\t', '')
        json_string = json_string.replace(', ]', ']')
        json_string = json_string.replace(',]', ']')

        obj = json.loads(json_string)
        color_names = []
        size_names = []
        asinVariationValues = []

        if 'variationValues' in obj:
            variationValues = obj['variationValues']
            if 'color_name' in variationValues:
                a = variationValues['color_name']
            if 'size_name' in variationValues:
                size_names = variationValues['size_name']
        if 'asinVariationValues' in obj:
            asinVariationValues = obj['asinVariationValues']
        selectedColorName = 0
        if "selectedVariationValues" in obj:
            selectedVariationValues = obj['selectedVariationValues']
            if "color_name" in selectedVariationValues:
                selectedColorName = selectedVariationValues["color_name"]
        if asinVariationValues == []:
            continue
        for key, value in asinVariationValues.items():
            code_size = value['size_name']
            code_color = value['color_name']
            size_name = size_names[int(code_size)]
            if selectedColorName != int(code_color):
                continue
            if sizes != [] and size_name not in sizes:
                continue
            codeASIN = value['ASIN']
            # print(sizes)
            # print("A", value['ASIN'], size_name)
            indexSort = sizes.index(size_name)
            # print("B", indexSort)
            future = executor.submit(
                getInfosThread, codeASIN, size_name, infos, indexSort)
            futures.append(future)
    wait(futures)
    if infos == []:
        priceElement = codeHTML.elementWithXpath(
            '//*[@id="priceblock_ourprice"]')
        # print("priceElement = ", priceElement)
        if priceElement != None:
            price = priceElement.text.strip()
            codeASIN = productDir
            isSoldOut = True
            if price != None:
                isSoldOut = False
            info = {'codeASIN': codeASIN, 'sizeName': None,
                    'isSoldOut': isSoldOut, 'price': price}
            infos.append(info)
    print("END")
    return infos
