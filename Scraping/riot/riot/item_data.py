import scrapy

class User_data(scrapy.Item):
    accountId = scrapy.Field()
    level = scrapy.Field()
    puuid = scrapy.Field()


class Match_data(scrapy.Item):
    gameId = scrapy.Field()
    queueid = scrapy.Field()

    platformId = scrapy.Field()
    seasonId = scrapy.Field()
    
    game_duration = scrapy.Field()
    timestamp = scrapy.Field()
    
    partecipants_list = scrapy.Field()