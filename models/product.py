import datetime
from mongoengine import *


class Product(Document):
    codeasin = StringField(required=True , max_length=200) 
    color = StringField(required=True , max_length=200) 
    describe_color = StringField( max_length=200)
    hide_show = BooleanField(default= True)
    image = StringField(max_length=200)



