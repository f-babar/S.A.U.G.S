import pymongo
import json
import constants
from pymongo import MongoClient
client = MongoClient()

client = MongoClient(constants.MONGO_URL)

db = client.saugs
countries_collection = db.countries

with open('data/countries.json', encoding='utf-8-sig', errors='ignore') as json_file:
  countries_data = json.load(json_file)
  result = countries_collection.insert_many(countries_data)
  print('Inserted....')




