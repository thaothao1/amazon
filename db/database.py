from flask import Flask
from flask_restful import Api , Resource , abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/amazon'
db = SQLAlchemy(app)
