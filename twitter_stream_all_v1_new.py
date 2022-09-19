import time
import pymongo
import pytz
import tweepy
import re
import traceback
import requests
import urllib3
import zmq
import threading
from datetime import datetime
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
db_crypto = db["crypto"]
db_keywords = db["keywords"]
api_url = keys.api_url
list_statuses = []

# endregion


class StreamListener(tweepy.Stream):

    global list_statuses

    def on_status(self, status):

        if status.user.followers_count > 100:

            list_statuses.append(status)
            is_retweet = hasattr(status, "retweeted_status")

            if not is_retweet and status.user.followers_count > 300000:

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

                text = Utils.deEmojify(text)

                if Utils.contains(lists.crypto_words_list, text, False):

                    db_crypto.insert_one({
                        "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                        "text": text,
                        "source": status.user.screen_name,
                        "time": Utils.fix_time(),
                        "fow": str(status.user.followers_count)[:-3],
                        "likes": str(status.favorite_count),
                        "retweet": str(status.retweet_count),
                        "eng_score": 0
                    })
                    requests.get(api_url + "ren_crypto", verify=False)

    def on_exception(self, exception):
        print_exception(exception)

    def on_error(self, status_code):
        print_exception(status_code)

    def on_disconnect(self, notice):
        print_exception(notice)
        return


def print_exception(message):

    print("=========================================")
    print("Encountered streaming error (", message, ")")
    print("=========================================")
    time.sleep(120)
    with open("logs/log.txt", "a") as myfile:
        myfile.write('\n' + "=========================================")
        myfile.write('\n' + "Titter All - ERROR:")
        myfile.write('\n' + str(message))
        myfile.write('\n' + str(traceback.format_exc()))
        myfile.write('\n' + "=========================================")

    main()


def get_time_stamp():

    global time_stamp

    tz = pytz.timezone("Europe/Sofia")
    cur_time = tz.localize(datetime.now(), is_dst=None)

    cur_time = str(cur_time)
    cur_time = cur_time[:-18] + "00"
    cur_time = re.sub(':', '', cur_time)
    cur_time = re.sub('-', '', cur_time)
    cur_time = re.sub(' ', '', cur_time)

    return cur_time


def send_keywords_count():

    cur_time_stamp, last_time_stamp = get_time_stamp()

    while True:

        time.sleep(60)
        cur_time_stamp = get_time_stamp()

        if last_time_stamp != cur_time_stamp:   # =======================    NEW CANDLE

            last_time_stamp = cur_time_stamp
            try:
                for c in lists.acc_list_words:
                    db_keywords.update_one({'name': c.get("name")}, {'$push': {'trend':  c.get('num')}})
                    db_keywords.update_one({'name': c.get("name")}, {'$push': {'time': cur_time_stamp}})
                    c['num'] = 0
                requests.get(api_url + "ren_trends", verify=False)

            except Exception as e:
                print_exception(e)

        else:   # =======================================================    REFRESH LAST CANDLE

            try:
                for c in lists.acc_list_words:

                    cursor_trend = db_keywords.find_one({"name": c.get("name")}, {"trend"})
                    size = len(cursor_trend.get("trend")) - 1

                    db_keywords.update_one({'name': c.get("name")}, {
                        '$set': {"trend." + str(size): c.get('num') + cursor_trend.get("trend")[size]}})

                    c['num'] = 0

                requests.get(api_url + "ren_trends", verify=False)

            except Exception as e:
                print_exception(e)


def process_statuses():

    global list_statuses

    while True:

        time.sleep(2)

        for status in list_statuses:

            if hasattr(status, "extended_tweet"):
                text = status.extended_tweet["full_text"].lower()
            else:
                text = status.text.lower()

            for c in lists.acc_list_words:
                for i in c.get("list"):
                    if i in text:
                        c['num'] = c.get("num") + 1

            # ===================   COUNT DIFFERENT WORDS TWEETS

            # if status.user.followers_count > 100000:
            #
            #     for c in lists.crypto_words_list:
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

    t1 = threading.Thread(target=send_keywords_count)
    t1.start()

    t2 = threading.Thread(target=process_statuses)
    t2.start()

    stream = StreamListener(keys.consumer_key_b, keys.consumer_secret_b,
                            keys.access_token_b, keys.access_token_secret_b)

    stream.filter(languages=["en"], track=lists.search_q, stall_warnings=True)




