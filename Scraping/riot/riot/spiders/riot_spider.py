#https://docs.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Response
import scrapy

from ..item_data import User_data, Match_data

class RiotSpider(scrapy.Spider):
    name = 'riot'

    start_urls = ["https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/scarletbloody?api_key=RGAPI-cc34b06e-be77-4b02-acc5-a4d455c5123e"]

    '''
    def __init__ (self, *a, **kw): 
        super(RiotSpider, self).__init__(*a, **kw)
        
    
        self.api_url = {
                "data by_account" : lambda account_name : f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{account_name}?api_key={key}",
                "matches by accountID" : lambda accountID : f"https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/{accountID}?api_key={key}",
                "match info by matchID" : lambda matchID : f"https://euw1.api.riotgames.com/lol/match/v4/matches/{matchID}?api_key={key}"
            }
    '''

#---------------------------------------- PARSE SUMMONER
    def parse(self, response):
        print("\n-----------------------------------------------------------------------------PARSE USER\n")
       
        #trasformo in dict una stringa che contiene un dizionario/json
        summoner_data = eval(response.text)
        item = User_data()
        item['level'] = summoner_data['summonerLevel']
        item['accountId'] = summoner_data['accountId']
        item['puuid'] = summoner_data['puuid']
        yield item

        request_matches = scrapy.Request(
                #url = self.api_url["matches by accountID"](accountId),
                url = self._getUrl(1,  item['accountId']),
                callback= self.parse_matches
            )
        
        yield request_matches

        


#---------------------------------------- PARSE LISTA MATCH
    def parse_matches(self, response): 
        print("\n-----------------------------------------------------------------------------PARSE LIST MATCH\n")
        summoner_matches = eval(response.text)['matches']
        #todo: paginazione
        for match in summoner_matches:            
            request_match = scrapy.Request(
                #url = self.api_url["match info by matchID"](matchID))
                url = self._getUrl(2, match['gameId']),
                callback=self.parse_match)

            yield request_match
        
#---------------------------------------- PARSE Singolo MATCH
    def parse_match(self, response): 
        print("\n-----------------------------------------------------------------------------PARSE SINGLE MATCH\n")
    
        single_match = eval(response.text.replace('true', 'True').replace('false', 'False'))

        item = Match_data()
        item['gameId'] = single_match['gameId']
        
        item['queueid'] = single_match['queueId']  #http://static.developer.riotgames.com/docs/lol/queues.json
        item['platformId'] =  single_match['platformId']
        item['seasonId'] = single_match['seasonId']
 
        item['game_duration'] = single_match['gameDuration']
        item['timestamp'] = single_match['gameCreation']

        item['partecipants_list'] = [x['player']['accountId'] for x in single_match['participantIdentities']]

        yield item
        
        for accountId in item['partecipants_list'] :
            request_matches = scrapy.Request(
                url = self._getUrl(3, accountId)
            )
            #yield request_matches
       

    def _getUrl(self, type, id):
        #key = "RGAPI-cc34b06e-be77-4b02-acc5-a4d455c5123e"
        if type == 0: return f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{id}?api_key={key}"
        if type == 1: return f"https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/{id}?api_key={key}"
        if type == 2: return f"https://euw1.api.riotgames.com/lol/match/v4/matches/{id}?api_key={key}"
        if type == 3: return f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-account/{id}?api_key={key}"
