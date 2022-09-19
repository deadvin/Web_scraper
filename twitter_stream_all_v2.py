import time
import pymongo
import pytz
import tweepy
import re
import Firebase_manager as fcm
import traceback
import requests
import urllib3
import zmq
import threading
from datetime import datetime, timedelta
import keys.keys as keys
import Utils
import json

# region VARS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
client = pymongo.MongoClient(keys.mongo_url, ssl=True)
db = client.SentencesDatabase
db_100 = db["100"]
db_500 = db["500"]
db_1m = db["1"]
db_10m = db["10"]
db_spam = db["spam"]
db_words = db["words"]
db_word_trend = db["trend"]
language = 'en'
api_url = keys.api_url
ban_list = [1324465509417574402, 1305904514487083008, 1266613947458699264, 1034478294677250048,
            1003400207357366272, 968796006576947200, 905778654503940096, 896499601745731585, 814084607347920896,
            3306286357, 2768661213, 121158213, 42213904, 17340970]
list_statuses = []
crypto_keywords = []
time_stamp = 0
cur_time_stamp = 0
# endregion

# region WORDS LIST

sym_list = []
search_q = []

sym_list.append({'name': 'ADA', "list": ["ada", "cardano"]})
sym_list.append({'name': 'SOL', "list": ["solana", "sol"]})
sym_list.append({'name': 'DOGE', "list": ["doge", "dogecoin", "doge coin"]})
sym_list.append({'name': 'MATIC', "list": ["matic", "polygon"]})
sym_list.append({'name': 'SLP', "list": ["slp", "small love potion"]})
sym_list.append({'name': 'LUNA', "list": ["luna", "terra"]})
sym_list.append({'name': 'DOT', "list": ["polkadot", "dot"]})
sym_list.append({'name': 'INJ', "list": ["inj", "injective protocol"]})
sym_list.append({'name': 'AVAX', "list": ["avax", "avalanche"]})
sym_list.append({'name': 'EOS', "list": ["eos", "eosio", "block one"]})
sym_list.append({'name': 'THETA', "list": ["theta"]})
sym_list.append({'name': 'IOTA', "list": ["iota", "miota"]})
sym_list.append({'name': 'CHZ', "list": ["chz", "chiliz"]})
sym_list.append({'name': 'ONE', "list": ["harmony"]})
sym_list.append({'name': 'KSM', "list": ["ksm", "kusama"]})
sym_list.append({'name': 'NEAR', "list": ["nearprotocol", "near protocol"]})
sym_list.append({'name': 'XTZ', "list": ["xtz", "tezos"]})
sym_list.append({'name': 'ALGO', "list": ["algo", "algorand"]})
sym_list.append({'name': 'EGLD', "list": ["egld", "elrond"]})
sym_list.append({'name': 'AR', "list": ["arweave", "ar"]})
sym_list.append({'name': 'AXS', "list": ["axs", "axieinfinity", "axie infinity"]})
sym_list.append({'name': 'XRP', "list": ["xrp", "ripple"]})
sym_list.append({'name': 'FIL', "list": ["filecoin", "file coin", "fil"]})
sym_list.append({'name': 'VET', "list": ["vechain", "ve chain", "vet"]})
sym_list.append({'name': 'UNI', "list": ["uniswap", "uni swap", "uni"]})
sym_list.append({'name': 'CAKE', "list": ["pancakeSwap"]})
sym_list.append({'name': 'ICP', "list": ["icp", "internet computer"]})
sym_list.append({'name': 'ETC', "list": ["etc", "ethereum classic"]})
sym_list.append({'name': 'ZIL', "list": ["zil", "zilliqa"]})
sym_list.append({'name': 'XLM', "list": ["xlm", "stellar"]})
sym_list.append({'name': 'XMR', "list": ["xmr", "monero"]})
sym_list.append({'name': 'SAND', "list": ["sand", "sandbox", "The Sandbox Game"]})
sym_list.append({'name': 'RVN', "list": ["rvn", "ravencoin"]})
sym_list.append({'name': 'MANA', "list": ["decentraland", "mana"]})
sym_list.append({'name': 'LTC', "list": ["ltc", "litecoin"]})
sym_list.append({'name': 'GALA', "list": ["gala", "galagames"]})
sym_list.append({'name': 'BNB', "list": ["bnb", "binance coin"]})
sym_list.append({'name': 'AAVE', "list": ["aave"]})
sym_list.append({'name': 'ANKR ', "list": ["ankr"]})
sym_list.append({'name': '1INCH', "list": ["1inch", "one inch"]})
sym_list.append({'name': 'COTI', "list": ["coti"]})
sym_list.append({'name': 'ENJ', "list": ["enjin", "enj"]})
sym_list.append({'name': 'ATOM', "list": ["atom", "cosmos"]})
sym_list.append({'name': 'ETH', "list": ["eth", "etherium"]})
sym_list.append({'name': 'FTM', "list": ["ftm", "fantom"]})

acc_list_words = []
acc_list_words.append(
    {'name': 'btc', "list": ["btc", "bitcoin", "crypto", "cryptocurrencies", "cryptocurrency"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'ada', "list": ["ada", "cardano", "adausdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append(
    {'name': 'luna', "list": ["#luna", "terra", "lunausdt", "terra luna", "terraluna"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'eth', "list": ["ethetium", "eth", "ethusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append(
    {'name': 'near', "list": ["NEARProtocol", "nearusdt", "#near", "NEAR Protocol"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'atom', "list": ["cosmos", "atomusdt", "#atom"], 'num': 0, 'num_vol': 0})  # - 1
acc_list_words.append({'name': 'avax', "list": ["avax", "avaxusdt"], 'num': 0, 'num_vol': 0})  # - 1
acc_list_words.append({'name': 'ftm', "list": ["ftm", "#fantom", "ftmusdt"], 'num': 0, 'num_vol': 0})  # - 1
acc_list_words.append({'name': 'one', "list": ["harmonyone", "oneusdt", "harmony one"], 'num': 0, 'num_vol': 0})  # - 1
acc_list_words.append({'name': 'ksm', "list": ["ksm", "kusama", "ksmusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'matic', "list": ["polygon", "matic", "maticusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'sol', "list": ["sol", "solana", "solusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append(
    {'name': 'inj', "list": ["inj", "injectiveprotocol", "injusdt", "injective protocol"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'vet', "list": ["vet", "vechain", "vetusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'iota', "list": ["iota", "miota", "iotaust"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'theta', "list": ["theta", "thetausdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'enj', "list": ["enj", "enjin", "enjusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'dot', "list": ["polkadot", "dotusdt"], 'num': 0, 'num_vol': 0})  # - 1
acc_list_words.append({'name': 'coti', "list": ["coti", "cotiusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': '1inch', "list": ["1inch", "1inchusdt", "#oneinch"], 'num': 0, 'num_vol': 0})
acc_list_words.append(
    {'name': 'axs', "list": ["axs", "axsusdt", "AxieInfinity", "Axie Infinity"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'ankr', "list": ["ankr", "ankrusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'algo', "list": ["#algo", "algousdt", "algorand"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'aave', "list": ["aave", "aaveusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'ar', "list": ["arusdt", "arweave"], 'num': 0, 'num_vol': 0})  # - 1
acc_list_words.append({'name': 'bnb', "list": ["bnb", "bnbusdt", "binance"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'chz', "list": ["chz", "chzusdt", "chiliz"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'eos', "list": ["eos", "eosusdt", "EOSIO"], 'num': 0, 'num_vol': 0})
acc_list_words.append(
    {'name': 'etc', "list": ["etc", "etcusdt", "ethereumclassic", "ethereum classic"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'egld', "list": ["elrond", "egld", "egldusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'fil', "list": ["file coin", "filusdt", "filecoin"], 'num': 0, 'num_vol': 0})  # - 1
acc_list_words.append(
    {'name': 'gala', "list": ["gala coin", "gala games", "galausdt", "galagames"], 'num': 0, 'num_vol': 0})  # - 1
acc_list_words.append({'name': 'icp', "list": ["icp", "icpusdt", "dfinity"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'ltc', "list": ["ltc", "ltcusdt", "litecoin", "lite coin"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'mana', "list": ["mana coin", "manausdt", "decentraland"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'rvn', "list": ["#rvn", "rvnusdt", "ravencoin"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'sand', "list": ["#sandbox", "sandusdt", "sand crypto"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'uni', "list": ["uniusdt", "uniswap"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'xrp', "list": ["xrp", "xrpusdt", "ripple"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'xmr', "list": ["xmr", "xmrusdt", "monero"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'xlm', "list": ["#stellar", "xlm", "xlmusdt"], 'num': 0, 'num_vol': 0})
acc_list_words.append({'name': 'zil', "list": ["#zil", "zilusdt", "zilliqa"], 'num': 0, 'num_vol': 0})
acc_list_words.append(
    {'name': 'ape', "list": ["apeusdt", "apecoin", "bored ape", "ape coin"], 'num': 0, 'num_vol': 0})  # - 1

alt_word_list = []

for c in acc_list_words:
    for i in c.get("list"):
        alt_word_list.append(i)

for c in sym_list:
    for i in c.get("list"):
        search_q.append(i)

crypto_word_list = ["btc", "bitcoin", "crypto", "cryptocurrencies", "cryptocurrency"]
search_q = alt_word_list + crypto_word_list


# endregionF

class tweet_object:
    def __init__(self, data):

        new_data = json.loads(data)

        self.text = Utils.deEmojify(new_data.get('data').get("text").lower())
        self.id = new_data.get('data').get("id")
        self.author_id = new_data.get('data').get("author_id")
        self.screen_name = new_data.get('includes').get("users")[0].get('name')
        self.followers_count = new_data.get('includes').get("users")[0].get('public_metrics').get('followers_count')

        if self.text[:4] == "RT @":
            self.retweet = True
        else:
            self.retweet = False

class StreamListener(tweepy.StreamingClient):
    global list_statuses

    def on_connect(self):
        print("Twitter ALl V2 Online")

    def on_data(self, raw_data):

        tweet = tweet_object(raw_data)
        list_statuses.append(tweet)

        if tweet.followers_count > 10000:

            # ====================== FILTER SPAM =========================

            if tweet.author_id in ban_list:
                return

            if len(tweet.screen_name) > 25:
                return

            if tweet.text.count('@') > 7:
                return

            if not tweet.retweet and tweet.followers_count > 100000:

                time2 = Utils.fix_time()

                if Utils.contains(crypto_word_list, tweet.text, False):
                    db_100.insert_one({
                        "link": "https://twitter.com/twitter/statuses/" + str(tweet.id),
                        "text": tweet.text,
                        "source": tweet.screen_name,
                        "time": time2,
                        "fow": str(tweet.followers_count)[:-3],
                        "likes": 0,
                        "retweet": 0,
                        "eng_score": 0
                    })
                    requests.get(api_url + "ren_100", verify=False)

                if tweet.followers_count > 500000:

                    if Utils.contains(crypto_word_list, tweet.text, False):
                        db_500.insert_one({
                            "link": "https://twitter.com/twitter/statuses/" + str(tweet.id),
                            "text": tweet.text,
                            "source": tweet.screen_name,
                            "time": time2,
                            "fow": str(tweet.followers_count)[:-3],
                            "likes": 0,
                            "retweet": 0,
                            "eng_score": 0
                        })
                        requests.get(api_url + "ren_500", verify=False)

                if tweet.followers_count > 1700000:

                    if Utils.contains(crypto_word_list, tweet.text, False):
                        # fcm.sendPush_twitter("Tweet from " + tweet.screen_name, tweet.text,
                        #                      "https://twitter.com/twitter/statuses/" + str(tweet.id), "t2m")

                        db_1m.insert_one({
                            "link": "https://twitter.com/twitter/statuses/" + str(tweet.id),
                            "text": tweet.text,
                            "source": tweet.screen_name,
                            "time": time2,
                            "fow": str(tweet.followers_count)[:-3],
                            "likes": 0,
                            "retweet": 0,
                            "eng_score": 0
                        })
                        requests.get(api_url + "ren_1", verify=False)

                if tweet.followers_count > 10000000:

                    if Utils.contains(crypto_word_list, tweet.text, False):
                        fcm.sendPush_twitter("Tweet from " + tweet.screen_name, tweet.text,
                                             "https://twitter.com/twitter/statuses/" + str(tweet.id), "t10m")

                        print("==============  TWEET 10M+ ==============")
                        print(tweet.screen_name + " fow:" + str(tweet.followers_count))
                        print(tweet.text)

                        db_10m.insert_one({
                            "link": "https://twitter.com/twitter/statuses/" + str(tweet.id),
                            "text": tweet.text,
                            "source": tweet.screen_name,
                            "time": time2,
                            "fow": str(tweet.followers_count)[:-3],
                            "likes": 0,
                            "retweet": 0,
                            "eng_score": 0
                        })

                        requests.get(api_url + "ren_10", verify=False)



    def on_disconnect(self):

        print("=========================================")
        print("DISCONECT")
        print("=========================================")
        time.sleep(60)
        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Titter All - DISCONECT:")
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")

        run_stream()

    def on_connection_error(self):
        print("=========================================")
        print("Connection Error")
        print("=========================================")
        time.sleep(60)
        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Titter All - Connection Error:")
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")

        run_stream()

    def on_closed(self, response):

        print("=========================================")
        print("CONNECTION CLOSED (", response, ")")
        print("=========================================")
        time.sleep(60)
        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Titter All - CONNECTION CLOSED:")
            myfile.write('\n' + str(response))
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")

    def on_exception(self, exception):

        print("=========================================")
        print("Encountered streaming exception (", exception, ")")
        print("=========================================")
        time.sleep(60)
        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Titter All - EXEPTION:")
            myfile.write('\n' + str(exception))
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")

        run_stream()

    def on_error(self, errors):

        print("=========================================")
        print("Encountered streaming error (", errors, ")")
        print("=========================================")
        time.sleep(60)
        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Titter All - ERROR:")
            myfile.write('\n' + str(errors))
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")

        run_stream()

def get_time_stamp():
    global time_stamp

    tz = pytz.timezone("Europe/Sofia")
    tim = tz.localize(datetime.now(), is_dst=None)
    tim = str(tim)
    tim = tim[:-15]
    tim = re.sub(':', '', tim)
    tim = re.sub('-', '', tim)
    tim = re.sub(' ', '', tim)
    timi = tim[-2:]
    timi = int(timi)

    if 0 <= timi < 15:
        time_stamp = int(tim[:-2] + "15")
    elif 15 <= timi < 30:
        time_stamp = int(tim[:-2] + "30")
    elif 30 <= timi < 45:
        time_stamp = int(tim[:-2] + "45")
    elif timi > 45:
        tz = pytz.timezone("Europe/Sofia")
        tim = tz.localize(datetime.now() + timedelta(hours=1), is_dst=None)
        # tim = datetime.now() + timedelta(hours=1)
        tim = str(tim)
        tim = tim[:-15]
        tim = re.sub(':', '', tim)
        tim = re.sub('-', '', tim)
        tim = re.sub(' ', '', tim)

        time_stamp = int((tim[:-2]) + "00")

def send_key_trend():
    global time_stamp, cur_time_stamp

    get_time_stamp()
    cur_time_stamp = time_stamp

    while True:

        time.sleep(60)
        get_time_stamp()

        if cur_time_stamp != time_stamp:  # =============================    NEW CANDLE

            cur_time_stamp = time_stamp
            try:

                for c in acc_list_words:
                    db_word_trend.update_one({'name': c.get("name")}, {'$push': {'trend': c.get('num')}})
                    db_word_trend.update_one({'name': c.get("name")}, {'$push': {'trend_vol': c.get('num_vol')}})
                    db_word_trend.update_one({'name': c.get("name")}, {'$push': {'time': cur_time_stamp}})
                    c['num'] = 0
                    c['num_vol'] = 0

                requests.get(api_url + "ren_trends", verify=False)

            except Exception as e:

                print("=============================TWITTER ALL KEYWORDS NEW CANDLE")
                print('exception', e)
                print("======================================================")

                with open("logs/twitter_keywords_trend.txt", "a") as myfile:
                    myfile.write('\n' + "=========================================")
                    myfile.write('\n' + " TREND  KEYWORDS SEND - EXEPTION:")
                    myfile.write('\n' + str(e))
                    myfile.write('\n' + str(traceback.format_exc()))
                    myfile.write('\n' + "=========================================")

        else:  # =============================    REFRESH LAST CANDLE

            try:
                for c in acc_list_words:
                    cursor_trend = db_word_trend.find_one({"name": c.get("name")}, {"trend"})
                    cursor_trend_vol = db_word_trend.find_one({"name": c.get("name")}, {"trend_vol"})

                    # cursor_trend_vol = [0 if v is None else v for v in cursor_trend_vol['trend_vol']]
                    # cursor_trend = [0 if v is None else v for v in cursor_trend['trend']]

                    size = len(cursor_trend.get("trend")) - 1
                    size_vol = len(cursor_trend_vol.get("trend_vol")) - 1

                    db_word_trend.update_one({'name': c.get("name")}, {
                        '$set': {"trend." + str(size): c.get('num') + cursor_trend.get("trend")[size]}})
                    db_word_trend.update_one({'name': c.get("name")}, {
                        '$set': {"trend_vol." + str(size_vol): c.get('num_vol') + cursor_trend_vol.get("trend_vol")[
                            size_vol]}})
                    c['num'] = 0
                    c['num_vol'] = 0

                requests.get(api_url + "ren_trends", verify=False)

            except Exception as e:

                print("=============================TWITTER ALL KEYWORDS SEND")
                print('exception', e)
                print("======================================================")

                with open("logs/twitter_keywords_trend.txt", "a") as myfile:
                    myfile.write('\n' + "=========================================")
                    myfile.write('\n' + " TREND  KEYWORDS SEND - EXEPTION:")
                    myfile.write('\n' + str(e))
                    myfile.write('\n' + str(traceback.format_exc()))
                    myfile.write('\n' + "=========================================")

                # cursor = db_word_trend.find()
                # size = size - 2
                #
                # for c in cursor:
                #
                #     trend = c.get("trend")
                #     trend = trend[-size:]
                #     db_word_trend.update_one({'name': c.get("name")}, {'$set': {'trend': trend}})
                #
                #     trend = c.get("trend_vol")
                #     trend = trend[-size:]
                #     db_word_trend.update_one({'name': c.get("name")}, {'$set': {'trend_vol': trend}})
                #
                #     trend = c.get("time")
                #     trend = trend[-size:]
                #     db_word_trend.update_one({'name': c.get("name")}, {'$set': {'time': trend}})

def process_statuses():
    global list_statuses

    while True:

        time.sleep(2)

        for tweet in list_statuses:

            #  ==================  COUNT CRYPTO KEYWORDS

            for c in acc_list_words:
                for i in c.get("list"):
                    if i in tweet.text:
                        c['num'] = c.get("num") + 1
                        c['num_vol'] = c.get("num_vol") + int(tweet.followers_count / 1000)

            # ===================   COUNT WORDS IN CRYPTO TWEETS

            if tweet.followers_count > 100000:

                for c in crypto_word_list:
                    if c in tweet.text:
                        text2 = re.sub(r'[^\w]', ' ', tweet.text)
                        text2 = text2.split()
                        for w in text2:
                            exists = db_words.find_one({'name': w})
                            if exists:
                                db_words.update_one({'name': w}, {'$set': {'count': exists.get("count") + 1}})
                            else:
                                db_words.insert_one({"name": w, "count": 1})

                        break

            list_statuses.remove(tweet)

def run_stream():

    stream = StreamListener(bearer_token=keys.bear_token, wait_on_rate_limit=True)

    rule = ""
    for w in search_q:
        rule = rule + ' OR ' + '"' + w + '"'
    rule = rule[4:]
    rule = "' " + rule + " lang:en'"
    print(rule)

    stream.add_rules(tweepy.StreamRule(rule))

    stream.filter(expansions=['author_id'], user_fields=["public_metrics"], tweet_fields=["public_metrics"])

def main():

    t1 = threading.Thread(target=send_key_trend)
    t1.start()

    t2 = threading.Thread(target=process_statuses)
    t2.start()

    run_stream()
