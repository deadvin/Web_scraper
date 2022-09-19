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
import keys.lists as lists
import Utils

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
list_statuses = []
crypto_keywords = []
time_stamp = 0
cur_time_stamp = 0

# endregion




class StreamListener(tweepy.Stream):

    global list_statuses

    def on_status(self, status):

        list_statuses.append(status)

        if status.user.followers_count > 10000:

            # ====================== SPAM =========================

            # name = db_spam.find_one({"name": status.user.screen_name})
            # if not name:
            #     db_spam.insert_one({
            #         "name": status.user.screen_name,
            #         "numb": 1,
            #     })
            # else:
            #     db_spam.update_one({"name": status.user.screen_name},
            #                        {"$set": {"numb": name.get("numb") + 1}})

            if status.user.id in lists.twitter_ban_accs:
                return

            if len(status.user.screen_name) > 25:
                return

            if hasattr(status, "extended_tweet"):
                text = status.extended_tweet["full_text"].lower()
            else:
                text = status.text.lower()

            if text.count('@') > 7:
                return

            # ====================== FORMAT TEXT =========================

            time2 = Utils.fix_time()
            text = Utils.deEmojify(text)
            is_retweet = hasattr(status, "retweeted_status")

            # =============   SEND WORD
            # wo = ''
            # for word in search_q:
            #     if contains_help(word)(text):
            #         wo = word
            #         print(str(word))
            #
            # for s in sym_list:
            #     for i in s.get("list"):
            #         if wo == i:
            #             name = s.get("name")
            #             print(str(name))

            if not is_retweet and status.user.followers_count > 100000:

                if Utils.contains(lists.crypto_words_list, text, False):

                    db_100.insert_one({
                        "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                        "text": text,
                        "source": status.user.screen_name,
                        "time": time2,
                        "fow": str(status.user.followers_count)[:-3],
                        "likes": str(status.favorite_count),
                        "retweet": str(status.retweet_count),
                        "eng_score": 0
                    })
                    requests.get(api_url + "ren_100", verify=False)

                if status.user.followers_count > 500000:

                    if Utils.contains(lists.crypto_words_list, text, False):

                        db_500.insert_one({
                            "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                            "text": text,
                            "source": status.user.screen_name,
                            "time": time2,
                            "fow": str(status.user.followers_count)[:-3],
                            "likes": str(status.favorite_count),
                            "retweet": str(status.retweet_count),
                        })
                        requests.get(api_url + "ren_500", verify=False)

                if status.user.followers_count > 1700000:

                    if Utils.contains(lists.crypto_words_list, text, False):

                        # fcm.sendPush_twitter("Tweet from " + status.user.screen_name, text,
                        #                      "https://twitter.com/twitter/statuses/" + str(status.id), "t2m")

                        db_1m.insert_one({
                            "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                            "text": text,
                            "source": status.user.screen_name,
                            "time": time2,
                            "fow": str(status.user.followers_count)[:-3],
                            "likes": str(status.favorite_count),
                            "retweet": str(status.retweet_count),
                            "eng_score": 0
                        })
                        requests.get(api_url + "ren_1", verify=False)

                if status.user.followers_count > 10000000:

                    if Utils.contains(lists.crypto_words_list, text, False):

                        fcm.sendPush_twitter("Tweet from " + status.user.screen_name, text, "https://twitter.com/twitter/statuses/" + str(status.id), "t10m")

                        db_10m.insert_one({
                            "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                            "text": text,
                            "source": status.user.screen_name,
                            "time": time2,
                            "fow": str(status.user.followers_count)[:-3],
                            "likes": str(status.favorite_count),
                            "retweet": str(status.retweet_count),
                            "eng_score": 0
                        })
                        requests.get(api_url + "ren_10", verify=False)

    def on_exception(self, exception):
         print("=============================twitter_stream_exe")
         print('exception', exception)
         print("=========================================")
         time.sleep(120)
         with open("logs/log.txt", "a") as myfile:
             myfile.write('\n' + "=========================================")
             myfile.write('\n' + "Titter All - EXEPTION:")
             myfile.write('\n' + str(exception))
             myfile.write('\n' + str(traceback.format_exc()))
             myfile.write('\n' + "=========================================")
         main()

    def on_error(self, status_code):
        print("=========================================")
        print("Encountered streaming error (", status_code, ")")
        print("=========================================")
        time.sleep(120)
        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Titter All - ERROR:")
            myfile.write('\n' + str(status_code))
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")
        main()

    def on_disconnect(self, notice):
        print("=========================================")
        print(notice)
        print("DISCONECTO MAI FRENDO ")
        print("=========================================")
        time.sleep(120)
        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' +"=========================================")
            myfile.write('\n' + "Titter All - DISCONECT:")
            myfile.write('\n' + str(notice))
            myfile.write('\n' + "=========================================")

        main()

        return

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

    global time_stamp,cur_time_stamp

    get_time_stamp()
    cur_time_stamp = time_stamp

    while True:

        time.sleep(60)
        get_time_stamp()

        if cur_time_stamp != time_stamp:   #     =============================    NEW CANDLE

            cur_time_stamp = time_stamp
            try:

                for c in lists.acc_list_words:

                    db_word_trend.update_one({'name': c.get("name")}, {'$push': {'trend':  c.get('num')}})
                    db_word_trend.update_one({'name': c.get("name")}, {'$push': {'trend_vol':  c.get('num_vol')}})
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

        else:   # =============================    REFRESH LAST CANDLE

            try:
                for c in lists.acc_list_words:

                    cursor_trend = db_word_trend.find_one({"name": c.get("name")}, {"trend"})
                    cursor_trend_vol = db_word_trend.find_one({"name": c.get("name")}, {"trend_vol"})

                    # cursor_trend_vol = [0 if v is None else v for v in cursor_trend_vol['trend_vol']]
                    # cursor_trend = [0 if v is None else v for v in cursor_trend['trend']]

                    size = len(cursor_trend.get("trend")) - 1
                    size_vol = len(cursor_trend_vol.get("trend_vol")) - 1

                    db_word_trend.update_one({'name': c.get("name")}, {
                        '$set': {"trend." + str(size): c.get('num') + cursor_trend.get("trend")[size]}})
                    db_word_trend.update_one({'name': c.get("name")}, {
                        '$set': {"trend_vol." + str(size_vol): c.get('num_vol') + cursor_trend_vol.get("trend_vol")[size_vol]}})
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

        for status in list_statuses:

            if hasattr(status, "extended_tweet"):
                text = status.extended_tweet["full_text"].lower()
            else:
                text = status.text.lower()

            #  ==================  COUNT CRYPTO KEYWORDS

            for c in lists.acc_list_words:
                for i in c.get("list"):
                    if i in text:
                        c['num'] = c.get("num") + 1
                        c['num_vol'] = c.get("num_vol") + int(status.user.followers_count / 1000)

            # ===================   COUNT WORDS IN CRYPTO TWEETS

            # if status.user.followers_count > 100000:
            #
            #     for c in lists.crypto_word_list:
            #         if c in text:
            #             text2 = re.sub(r'[^\w]', ' ', text)
            #             text2 = text2.split()
            #             for w in text2:
            #                 exists = db_words.find_one({'name': w})
            #                 if exists:
            #                     db_words.update_one({'name': w}, {'$set': {'count': exists.get("count") + 1}})
            #                 else:
            #                     db_words.insert_one({"name": w, "count": 1})
            #
            #             break

            list_statuses.remove(status)

def main():

    print("Twitter ALl Online")

    t1 = threading.Thread(target=send_key_trend)
    t1.start()

    t2 = threading.Thread(target=process_statuses)
    t2.start()

    stream = StreamListener(keys.consumer_key_b, keys.consumer_secret_b,
                            keys.access_token_b, keys.access_token_secret_b)

    stream.filter(languages=["en"], track=lists.search_q, stall_warnings=True)




