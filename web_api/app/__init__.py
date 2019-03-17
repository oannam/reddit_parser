from flask import Flask
from flasgger import Swagger
from flask_pymongo import PyMongo

app = Flask(__name__)
swagger = Swagger(app)
app.config['MONGO_URI'] = 'mongodb://mongodb:27017/reddit'
mongo = PyMongo(app)

from app import routes