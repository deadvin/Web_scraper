import time
import pymongo
import pytz
import tweepy
import datetime
import re
import Firebase_manager as fcm
import requests
import traceback
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import zmq
import keys.keys as keys
import Utils


context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

client = pymongo.MongoClient(keys.mongo_url, ssl=True)

db = client.SentencesDatabase
db_rep = db["rep"]
db_rep_f = db["rep_f"]
db_sym = db["sym"]
db_sym_f = db["sym_f"]
db_500 = db["500"]
db_track = db["track"]
api_url = keys.api_url
alt_list = []
alt_list_int = []
rep_list_int = []

auth = tweepy.OAuthHandler(keys.consumer_key_b,  keys.consumer_secret_b)
auth.set_access_token(keys.access_token_b, keys.access_token_secret_b)
api = tweepy.API(auth, wait_on_rate_limit=True, timeout=60)

elon_list = [44196397]

rep_list = ["865624663841320960", "3295423333", "2704294333", "381696140", "59393368", "44196397", "15971805","34713362", "1395670265103851520", "2361601055","31064165"]
key_words_sym = ["partnership","partners", "partner"]
key_words_all = ["nft", "fan token", "ada", "cardano",
                 "xrp", "ripple", "theta", "ethereum", "eth", "chiliz", "chz", "doge", "dogecoin", "solana", "sol", "polkadot", "uniswap", "terra", "luna", "binance","bnb", "chainlink", "litecoin", "ltc", "internet computer", "icp",
                 "polygon","matic", "ethereum classic", "vechain", "vet", "stellar", "xlm", "filecoin", "fil", "tron", "trx", "avalanche", "avax", "aave", "eos", "monero", "xmr", "pancakeswap",
                 "axie infinity", "axs"]
ban = ["bitcoin rises to the highest since", "greed index", "for early access to our free", "major crypto price update",
       "has been transferred from", "crypto updates:", "rt @breakingcrypto5"]
key_words_crypto = ["nft","btc", "bitcoin", "crypto", "cryptocurrencies", "cryptocurrency", "blockchain", "digital currency", "virtual currency","digital currencies","virtual currencies"]


for c in Utils.acc_list:
    for i in c.get("list"):
        alt_list.append(i)

for element in alt_list:
    alt_list_int.append(int(element))

for element in rep_list:
    rep_list_int.append(int(element))

merged_list = alt_list + rep_list


class StreamListener(tweepy.Stream):

    def on_status(self, status):

        # =================================    ELON TUSK

        if False and status.user.id in elon_list:

            if status.in_reply_to_status_id is not None:

                statuses = api.get_status(status.in_reply_to_status_id)
                if hasattr(statuses, "extended_tweet"):
                    text = statuses.extended_tweet["full_text"].lower()
                else:
                    text = statuses.text.lower()

                if Utils.contains(key_words_crypto, text, False) or Utils.contains(key_words_all, text, True):

                    fcm.sendPush_twitter("E: " + status.user.screen_name, text, "https://twitter.com/twitter/statuses/" + str(status.id), "breaking")

                    time2 = Utils.fix_time()

                    db_rep_f.insert_one({
                        "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                        "text": text,
                        "source": status.user.screen_name,
                        "time": time2,
                        "fow": str(status.user.followers_count)[:-3],
                        "likes": str(status.favorite_count),
                        "retweet": str(status.retweet_count),
                        "eng_score": 0
                    })
                    requests.get(api_url + "ren_rep_f", verify=False)
            else:

                if hasattr(status, "extended_tweet"):
                    text = status.extended_tweet["full_text"].lower()
                else:
                    text = status.text.lower()

                if Utils.contains(key_words_crypto, text, False) or  Utils.contains(key_words_all, text, True):

                    if hasattr(status, "extended_tweet"):
                        text = status.extended_tweet["full_text"].lower()
                    else:
                        text = status.text.lower()

                    time2 = Utils.fix_time()

                    fcm.sendPush_twitter("E: " + status.user.screen_name, text,  "https://twitter.com/twitter/statuses/" + str(status.id), "breaking")

                    db_rep_f.insert_one({
                        "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                        "text": text,
                        "source": status.user.screen_name,
                        "time": time2,
                        "fow": str(status.user.followers_count)[:-3],
                        "likes": str(status.favorite_count),
                        "retweet": str(status.retweet_count),
                        "eng_score": 0
                    })
                    requests.get(api_url + "ren_rep_f", verify=False)

        #   ===============================    BREAKING

        if status.user.id in rep_list_int and status.in_reply_to_status_id is None:

            if hasattr(status, "extended_tweet"):
                text = status.extended_tweet["full_text"].lower()
            else:
                text = status.text.lower()

            text = Utils.breaking_text(text)
            exists = db_rep.find_one({'text': text})

            print("=========  BREAKING  =============")
            print(status.user.screen_name)
            print(text)
            print("  ")

            if not exists and len(text) > 13:

                time2 = Utils.fix_time()

                db_rep.insert_one({
                    "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                    "text": text,
                    "source": status.user.screen_name,
                    "time": time2,
                    "fow": str(status.user.followers_count)[:-3],
                    "likes": str(status.favorite_count),
                    "retweet": str(status.retweet_count),
                    "eng_score": 0
                })
                requests.get(api_url + "ren_rep", verify=False)

            if Utils.contains(key_words_crypto, text, False) or Utils.contains(key_words_all, text, True):

                if not Utils.contains(ban, text, False):

                    exists = db_rep_f.find_one({'text': text})

                    if not exists and len(text) > 13 and text.count('@') < 6:

                        text = Utils.breaking_text(text)

                        fcm.sendPush_twitter("Breaking News: ", text,
                                          "https://twitter.com/twitter/statuses/" + str(status.id), "breaking")

                        db_rep_f.insert_one({
                            "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                            "text": text,
                            "source": status.user.screen_name,
                            "time": time2,
                            "fow": str(status.user.followers_count)[:-3],
                            "likes": str(status.favorite_count),
                            "retweet": str(status.retweet_count),
                            "eng_score": 0
                        })

                        requests.get(api_url + "ren_rep_f", verify=False)


        #   ===============================    ALTCOIN OFFICIAL ACCOUNTS

        if status.user.id in alt_list_int:

            is_retweet = hasattr(status, "retweeted_status")

            if hasattr(status, "extended_tweet"):
                text = status.extended_tweet["full_text"].lower()
            else:
                text = status.text.lower()

            text = Utils.deEmojify(text)

            if is_retweet or text.count('@') > 5 or db_sym.find_one({'text': text}) or len(text) < 14 or status.in_reply_to_status_id is not None:
                return

            tz = pytz.timezone("Europe/Sofia")
            tim = tz.localize(datetime.datetime.now(), is_dst=None)
            tim = tim.replace(tzinfo=None)
            time2 = Utils.fix_time()

            db_track.insert_one({
                "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                "source": status.user.screen_name,
                "time": [tim],
                "time2": time2,
                "text": text,
                "fow": str(status.user.followers_count)[:-3],
                "likes": [str(status.favorite_count)],
                "retweet": [str(status.retweet_count)]
            })

            print(status.user.screen_name + "   ")
            print("https://twitter.com/twitter/statuses/" + str(status.id))
            print(text)
            print("   ")

            # for s in acc_list:
            #     for i in s.get("list"):
            #         if status.user.id == int(i):
            #             name = s.get("name")
            #
            # # =====================    SOCKET SEND
            # try:
            #     socket.send_string(name)
            #     message = socket.recv()
            # except:
            #     pass

            db_sym.insert_one({
                "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                "text": text,
                "source": status.user.screen_name,
                "time": time2,
                "fow": str(status.user.followers_count)[:-3],
                "likes": str(status.favorite_count),
                "retweet": str(status.retweet_count),
                "eng_score": 0
            })
            requests.get(api_url + "ren_sym", verify=False)

            if Utils.contains(key_words_sym, text, False):
                fcm.sendPush_twitter("Tweet from " + status.user.screen_name, text,
                                     "https://twitter.com/twitter/statuses/" + str(status.id), "alts")

                db_sym_f.insert_one({
                    "link": "https://twitter.com/twitter/statuses/" + str(status.id),
                    "text": text,
                    "source": status.user.screen_name,
                    "time": time2,
                    "fow": str(status.user.followers_count)[:-3],
                    "likes": str(status.favorite_count),
                    "retweet": str(status.retweet_count),
                    "eng_score": 0
                })
                requests.get(api_url + "ren_sym_f", verify=False)

    def on_exception(self, exception):
        print("=======================================exe")
        print('exception', exception)
        print("=========================================")
        time.sleep(60)
        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Titter Acc - EXEPTION:")
            myfile.write('\n' + str(exception))
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")
        main()

    def on_error(self, status_code):
        print("=========================================")
        print("Encountered streaming error (", status_code, ")")
        print("=========================================")
        time.sleep(60)
        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Titter Acc - ERROR:")
            myfile.write('\n' + str(status_code))
            myfile.write('\n' + "=========================================")
        main()

    def on_disconnect(self, notice):

        print("=========================================")
        print(notice)
        print("DISCONNECT")
        print("=========================================")
        time.sleep(60)
        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Titter Acc - DISCONNECT:")
            myfile.write('\n' + str(notice))
            myfile.write('\n' + "=========================================")

        main()







def main():

    print("Twitter ACCS Online")


    stream = StreamListener(
        keys.consumer_key_b, keys.consumer_secret_b,
        keys.access_token_b, keys.access_token_secret_b
    )

    stream.filter(follow=merged_list, stall_warnings=True)




