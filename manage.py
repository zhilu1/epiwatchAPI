#!/usr/bin/env python
from pprint import pprint
import json
from pymongo import MongoClient
import os
import sys


# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string

# Test function

def tempTest():
    myclient = MongoClient(
        'mongodb+srv://NULLUSER:unsw123@cluster0-ycp9i.mongodb.net/test?retryWrites=true')
    mydb = myclient["NULLDB"]
    mycol = mydb["NULLDB"]
    """
    with open('result1.json', 'r') as myfile:
        data=myfile.read()
    mydict = json.loads(data)
    """
    test_dir = {}
    test_dir["Eric"] = "E"
    test_dir["Frank"] = "F"
    print(type(test_dir))
    x = mycol.insert_one(test_dir)


# Connect the database
def dbConnect(authorUrl, dbName, collectionName):
    myclient = MongoClient(authorUrl)
    mydb = myclient[dbName]
    collection = mydb[collectionName]
    return collection

# Import the Json file and store the data into the database


def storeJson(jsonFile, collection):
    with open(jsonFile, 'r') as myfile:
        data = myfile.read()
    mydict = json.loads(data)
    collection.insert_many(mydict)

# Get all the data (Json) from the database


def getAllData(collection):
    data = collection.find()
    # for i in data:
    #    print(i)
    return data

    # print(type(db.collection.find()))

# Example to use database tool-funcitons


def main():
    authorUrl = 'mongodb+srv://frankjunyulin:unsw123@cluster0-ycp9i.mongodb.net/test?retryWrites=true'
    dbName = "NULLDB"
    collectionName = "NULLDB"
    collection = dbConnect(authorUrl, dbName, collectionName)

    #storeJson('WHO_scraping/result1.json', collection)
    data = getAllData(collection)
    for i in data:
        print(i)


"""
mydb = myclient["seng3011"]
mycol = mydb["scraping_result"]
with open('result1.json', 'r') as myfile:
    data=myfile.read()
mydict = json.loads(data)
print (mydict)
"""


if __name__ == '__main__':
    print("sss")
    main()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seng3011.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
    print("aaa")
# pprint library is used to make the output look more pretty
