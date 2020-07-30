#https://docs.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Response
import scrapy
import logging
from ..item_data import User_data, Match_data

class RiotSpider(scrapy.Spider):
    name = 'riot'
    
    def start_requests(self):
        #gli argomenti passati con -a sono messi di default a self.nome_arg 
        logging.basicConfig(filename='file_info.log',level=logging.INFO)
        yield scrapy.Request(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{self.user}?api_key={self.riot_key}")
        yield scrapy.Request(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/wicked%20symphony?api_key={self.riot_key}")

    #---------------------------------------- PARSE SUMMONER
    #controllo le informazioni del summoner
    def parse(self, response):
        #trasformo in dict una stringa che contiene un dizionario/json
        summoner_data = eval(response.text)
        item = User_data()
        item['level'] = summoner_data['summonerLevel']
        item['accountId'] = summoner_data['accountId']
        item['puuid'] = summoner_data['puuid']
        logging.info(f"START parse matchlist userId: {item['accountId']}")
        yield item

        request_matches = scrapy.Request(
            url = self._getUrl("matchlist", item['accountId']),
            callback= self.get_all_matches, 
            cb_kwargs = dict(args = [], count = 0, accountId = item['accountId'])
            )
        yield request_matches

    #---------------------------------------- PARSE ALL MATCHES
    #ciclo tutti i match raccogliendoli
    def get_all_matches(self, response, args, count, accountId): 
        index = count + 100
        list_matches = args

        summoner_matches = eval(response.text)['matches']
        list_matches += [x['gameId'] for x in summoner_matches] #sono liste di numeri, posso farlo
        if len(summoner_matches) != 0:
            request_matches = scrapy.Request(
                url = self._getUrl_(1,accountId,index),
                callback = self.get_all_matches, 
                cb_kwargs = dict(args = list_matches, count = index, accountId = accountId)
            ) 
            yield request_matches
        else: 
            #ciclo tutti i match per ottenerne una chiama per ogni match da controllare con parse_match
            logging.info(f"END parse matchlist userId: {accountId} - matches: {len(list_matches)}")
            for matchId in list_matches: 
                request_match = scrapy.Request(
                    url = self._getUrl("match", matchId),
                    callback=self.parse_match
                )
                yield request_match  
                        
    #---------------------------------------- PARSE Singolo MATCH
    def parse_match(self, response): 
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
            request_summoner = scrapy.Request(
                url = self._getUrl("summoner", accountId)
            )
            yield request_summoner
       

    def _getUrl(self, type, id):
        
        if type == "summoner by name": return f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{id}?api_key={self.riot_key}"
        if type == "matchlist": return f"https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/{id}?api_key={self.riot_key}"
        if type == "match": return f"https://euw1.api.riotgames.com/lol/match/v4/matches/{id}?api_key={self.riot_key}"
        if type == "summoner": return f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-account/{id}?api_key={self.riot_key}"

    def _getUrl_(self, type, id, index):
        return f"https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/{id}?beginIndex={index}&api_key={self.riot_key}"