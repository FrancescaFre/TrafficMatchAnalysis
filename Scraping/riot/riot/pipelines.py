# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from . import item_data

class RiotPipeline(object):

    def __init__(self):
 
        self.mongo_uri = ["localhost", 27017]
        self.mongo_db = "riots_data"


    def open_spider(self, spider):
    #connessione al database
        self.client = pymongo.MongoClient('localhost',27017)
    #crezione database
        self.db = self.client[self.mongo_db]
    
    def close_spder(self, spider):
        self.client.close()


    def process_item(self, item, spider):
        if (isinstance(item, item_data.Match_data)):
          self.db['match'].insert_one(dict(item))
        if (isinstance(item, item_data.User_data)):
          self.db['user'].insert_one(dict(item))
        return item
