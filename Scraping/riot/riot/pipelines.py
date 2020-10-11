# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from . import item_data

class RiotPipeline(object):

    def __init__(self):
        self.mongo_db = "riots_data_second"
        #self.mongo_db = "riots_data_test"

    def open_spider(self, spider):
    #connessione al database
        self.client = pymongo.MongoClient('localhost',int(spider.port))
    #crezione database
        self.db = self.client[self.mongo_db]
    
    def close_spder(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        #inserimento di un match
        if (isinstance(item, item_data.Match_data)):
          self.db['match'].update_one({'gameId':item['gameId']}, {'$set': item}, upsert=True)

        #inserimento di un utente
        if (isinstance(item, item_data.User_data)):
          self.db['user'].update_one({'puuid':item['puuid']}, {'$set': dict(item)}, upsert=True)

        return item

#UPSERT: impedisce che venga inserito un valore se esiste già con quella chiave/index
#upsert (optional): If True, perform an insert if no documents match the filter.
#https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.update_one
