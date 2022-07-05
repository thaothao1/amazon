import datetime
from mongoengine import *

class Category_size(Document):
    codeasin_product = StringField(max_length=200)
    codeasin_size = StringField(max_length=200)
    type = StringField(max_length=200)
    price_amazon = StringField(max_length=200)
    price_sell = StringField(max_length=200)
    supplier = StringField(max_length=200)
    amount = IntField()
    