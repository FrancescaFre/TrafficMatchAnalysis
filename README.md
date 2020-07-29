# TrafficMatchAnalysis
Little project to undestand Riot Api and collect data about players, i would check the distribution of player during the day to identify the avg traffic. 
I need to catch data (full anonymized) about duration and time of the day, then draw graph about elaborated data. 
The data will be stored in my pc and shared with at least my professor (btw i think only the results will be shared).

The API used are:
* match: to collect timestamp and duration
* summoner: to label some statistics (like "how many match a challenger usually play? And players between 1-30?")


___
RUN

source activate

scrapy activate riot_py38

scrapy crawl riot -s JOBDIR=crawls/leolouchsly-1 -a riot_key=$RIOT_KEY -a port=27017 -a user="lelouchsly"


ULTERIORI COMANDI: 
--logfile FILE_NAME: Overrides LOG_FILE=FILE_NAME

--loglevel/-L LEVEL: Overrides LOG_LEVEL

--nolog: Sets LOG_ENABLED to False

-a: aggiunge gli argomenti 
port = porta per mongodb
user = utente da cui iniziare il crawl
riot_key = key per usare le api 