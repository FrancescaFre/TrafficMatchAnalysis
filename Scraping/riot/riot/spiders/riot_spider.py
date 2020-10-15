# documentazione response di scrapy
# https://docs.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Response

# documentazione per i parametri di count_documents di pymongo: 
# https://api.mongodb.com/python/current/api/pymongo/collection.html?highlight=count_documents#pymongo.collection.Collection.count_documents
      
import scrapy
import itertools
import logging
from pymongo import MongoClient
from ..item_data import User_data, Match_data

class RiotSpider(scrapy.Spider):
    name = 'riot'
    riot_db = 'riot_db'

    #devo fare l'init perchè altrimenti al reload del crawler non fa il bind con il db da start_requests, giustamente direi
    def __init__(self, *a, **kw):
        super(RiotSpider, self).__init__(*a, **kw)
        print("start bind db:")
        #collego il db con il crawler (collego la porta data in input)
        client = MongoClient('localhost', int(self.port)) 
        #carico i dati del db nella var riot_db
        global riot_db
        riot_db = client.riots_data_second

    def start_requests(self):
        print("start request batch")
        
       # self.state['first'] = 0
        
        #per ogni match prendo tutti gli utenti
        set_p= set(itertools.chain.from_iterable(((uid for uid in match['partecipants_list'] if uid!="0") for match in riot_db.match.find() )))
        
        print(len(set_p)) #stampo il numero di player unici 
        #per ogni utente genero una richiesta: si tratta del pool iniziale di richieste. 
        for accountId in set_p:
            request_summoner = scrapy.Request(
                url = self._getUrl("summoner", accountId),
                priority = 3 
                # priorità più alta così queste richieste vengono fatte subito, 
                # non ho capito se in caso di interruzione e ripresa del crawler viene ripreso anche il ciclo, 
                # nel dubbio metto priorità più alta così vengono generate almeno le richieste. 
            )
            yield request_summoner
        print("end request batch")

    #---------------------------------------- PARSE SUMMONER
    #controllo le informazioni del summoner
    def parse(self, response):
        #trasformo in dict una stringa che contiene un dizionario/json
        summoner_data = eval(response.text)
        item = User_data()
        item['level'] = summoner_data['summonerLevel']
        item['accountId'] = summoner_data['accountId']
        item['puuid'] = summoner_data['puuid']
        item['number_matches'] = 0
        item['banned'] = True
        logging.info(f"START parse matchlist userId: {item['accountId']}")

        request_matches = scrapy.Request(
            url = self._getUrl("matchlist", item['accountId']),
            callback= self.get_all_matches, 
            cb_kwargs = dict(args = [], count = 0, item = item),
            priority = 2
            )
        yield request_matches

    #---------------------------------------- PARSE ALL MATCHES
    #ciclo tutti i match raccogliendoli
    def get_all_matches(self, response, args, count, item): 
        accountId = item['accountId']
        index = count + 100
        list_matches = args

        summoner_matches = eval(response.text)['matches']
        
        list_matches += [x['gameId'] for x in summoner_matches] #sono liste di numeri, posso farlo
        if len(summoner_matches) != 0:
            request_matches = scrapy.Request(
                url = self._getUrl_(1,accountId,index),
                callback = self.get_all_matches, 
                priority = 2,
                cb_kwargs = dict(args = list_matches, count = index, item = item)
            ) 
            yield request_matches

        else: 
            item['banned'] = False
            item['number_matches'] = len(list_matches)
            yield item #salvo nel db l'utente 

            #ciclo tutti i match per ottenerne una chiama per ogni match da controllare con parse_match
            logging.info(f"END parse matchlist userId: {accountId} - matches: {len(list_matches)}")
            for matchId in list_matches: 
                #CHECK: SE IL MATCH è GIà NEL DB skip: 
                if riot_db.match.find_one({"gameId": matchId}) == None:
                    request_match = scrapy.Request(
                        url = self._getUrl("match", matchId),
                        callback=self.parse_match, 
                        priority = 1
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
            #CHECK: SE IL SUMMONER è GIà NEL DB, cioè ha già visto tutti i match parsati, skip
            if riot_db.user.find_one({"accountId":accountId}) == None:
                request_summoner = scrapy.Request(
                    url = self._getUrl("summoner", accountId)
                )
                yield request_summoner
       

    def _getUrl(self, type, id):
        if type == "summoner by name" : return f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{id}?api_key={self.riot_key}"
        if type == "matchlist": return f"https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/{id}?api_key={self.riot_key}"
        if type == "match": return f"https://euw1.api.riotgames.com/lol/match/v4/matches/{id}?api_key={self.riot_key}"
        if type == "summoner": return f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-account/{id}?api_key={self.riot_key}"

#Crea gli URL per la ricerca paginata della lista di match 
    def _getUrl_(self, type, id, index):
        return f"https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/{id}?beginIndex={index}&api_key={self.riot_key}"