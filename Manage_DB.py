import threading
import traceback
import pytz as pytz
import pymongo
import tweepy
import time
import datetime
from datetime import datetime as dt
import keys.keys as keys
import Firebase_manager as fcm
import Utils
import requests

client = pymongo.MongoClient(keys.mongo_url, ssl=True)
db = client.SentencesDatabase
counter = 14

client_tweepy = tweepy.Client(bearer_token=keys.bear_token, consumer_key=keys.consumer_key,
consumer_secret=keys.consumer_secret,access_token=keys.access_token,access_token_secret=keys.access_token_secret)

api_url = keys.api_url
db_track = db["track"]
db_track_a = db["track_a"]
db_average = db["track_average"]
db_filter = db["track_filter"]
db_sym = db["sym"]


def delete():

    try:
        db_ = db["1"]
        db_size = db_.estimated_document_count()
        if db_size > 60:
            all_users = db_.find().limit(db_size - 60)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["10"]
        db_size = db_.estimated_document_count()
        if db_size > 60:
            all_users = db_.find().limit(db_size - 60)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["500"]
        db_size = db_.estimated_document_count()
        if db_size > 60:
            all_users = db_.find().limit(db_size - 60)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["100"]
        db_size = db_.estimated_document_count()
        if db_size > 60:
            all_users = db_.find().limit(db_size - 60)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["rep"]
        db_size = db_.estimated_document_count()
        if db_size > 60:
            all_users = db_.find().limit(db_size - 60)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["rep_f"]
        db_size = db_.estimated_document_count()
        if db_size > 60:
            all_users = db_.find().limit(db_size - 60)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["sym"]
        db_size = db_.estimated_document_count()
        if db_size > 60:
            all_users = db_.find().limit(db_size - 60)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["sym_f"]
        db_size = db_.estimated_document_count()
        if db_size > 60:
            all_users = db_.find().limit(db_size - 60)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["news"]
        db_size = db_.estimated_document_count()
        if db_size > 60:
            all_users = db_.find().limit(db_size - 60)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["news_f"]
        db_size = db_.estimated_document_count()
        if db_size > 50:
            all_users = db_.find().limit(db_size - 20)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["videos"]
        db_size = db_.estimated_document_count()
        if db_size > 60:
            all_users = db_.find().limit(db_size - 60)
            for usr in all_users:
                db_.delete_one({"_id": usr['_id']})

        db_ = db["events"]

        cursor = db_.find({})
        for doc in cursor:

            doc_date = doc.get("date")
            doc_date = doc_date.replace(" (or earlier)", "")
            end_date = dt.strptime(doc_date, "%d %b %Y")

            now = datetime.datetime.now()
            now = str(now)
            now = now.split(" ", 1)[0]
            now = now + " 00:00:00"
            now = dt.strptime(now, '%Y-%m-%d %H:%M:%S')
            margin = (end_date - now).days

            if margin < 0:
                db_.delete_one({"link": doc.get("link")})

    except Exception as e:

        print("=============================manage_db_delete")
        print('exception', e)
        print("=========================================")
        time.sleep(10)
        with open("logs/manage.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Manage Db Delete - EXEPTION:")
            myfile.write('\n' + str(e))
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")

def update():

    global counter

    while True:

        time.sleep(30)
        counter +=1

        # ================  UPDATE ALL TWEETS

        update_tweets("1")

        update_tweets("10")

        update_tweets("100")

        update_tweets("500")

        update_tweets("sym")

        update_tweets("sym_f")

        # ================  UPDATE TRACKED TWEETS

        try:
            tz = pytz.timezone("Europe/Sofia")
            tim = tz.localize(datetime.datetime.now(), is_dst=None)
            tim = tim.replace(tzinfo=None)

            tweet_IDs = db_track.find().distinct('link')
            tweet_IDs = [word.replace("https://twitter.com/twitter/statuses/", "") for word in tweet_IDs]

            if 0 < len(tweet_IDs) < 99:

                tweets = client_tweepy.get_tweets(ids=tweet_IDs, tweet_fields=["public_metrics"])
                for tweet in tweets.data:
                    db_track.update_one({'link': "https://twitter.com/twitter/statuses/" + str(tweet["id"])},
                                        {'$push': {'likes': tweet["public_metrics"].get("like_count"),
                                                   'retweet':  tweet["public_metrics"].get("retweet_count"), 'time': tim}})

        except Exception as e:

            print("=============================manage_db_track")
            print('exception', e)
            print("=========================================")
            with open("logs/manage.txt", "a") as myfile:
                myfile.write('\n' + "=========================================")
                myfile.write('\n' + "Manage DB Track - EXEPTION:")
                myfile.write('\n' + str(e))
                myfile.write('\n' + str(traceback.format_exc()))
                myfile.write('\n' + "length of list: " + str(len(tweet_IDs)))
                myfile.write('\n' + "=========================================")

        # ================  CHECK FOR TRENDING TWEETS

        check_for_trending_tweets()

        # ================  MOVE 100 + TO ARCHIVE AND CLEAR INACTIVE

        try:
            if counter > 6:

                counter = 0
                statuses = db_track.find()

                for status in statuses:
                    if len(status.get("retweet")) > 100:
                        db_track_a.insert_one({
                            "link": status.get("link"),
                            "source": status.get("source"),
                            "time": status.get("time"),
                            "text": status.get("text"),
                            "likes": status.get("likes"),
                            "retweet": status.get("retweet")
                        })
                        db_track.delete_one({"link": status['link']})

                # tweet_IDs = db_track.find().distinct('link')
                # tweet_IDs = [word.replace("https://twitter.com/twitter/statuses/", "") for word in tweet_IDs]

                if 0 < len(tweet_IDs) < 99:

                    status_ids = []
                    for tweet in tweets.data:
                        status_ids.append(str(tweet["id"]))
                    for tweet in tweet_IDs:
                        if str(tweet) not in status_ids:
                            db_track.delete_one({"link": "https://twitter.com/twitter/statuses/" + str(tweet)})

        except Exception as e:

            print("=============================move to archive and  clear inactive")
            print('exception', e)
            print("================================================================")
            with open("logs/manage.txt", "a") as myfile:
                myfile.write('\n' + "=========================================")
                myfile.write('\n' + "Manage DB Track - EXEPTION:")
                myfile.write('\n' + str(e))
                myfile.write('\n' + str(traceback.format_exc()))
                myfile.write('\n' + "=========================================")

def update_tweets(db_name):

    try:

        db_ = db[db_name]
        tweet_IDs = db_.find().distinct('link')
        tweet_IDs = [word.replace("https://twitter.com/twitter/statuses/", "") for word in tweet_IDs]

        if len(tweet_IDs) > 0:
            tweets = client_tweepy.get_tweets(ids=tweet_IDs, tweet_fields=["public_metrics"])
            for tweet in tweets.data:
                db_.update_one({"link": "https://twitter.com/twitter/statuses/" + str(tweet["id"])},
                               {"$set": {"likes": tweet["public_metrics"].get("like_count"),
                                         "retweet": tweet["public_metrics"].get("retweet_count")}})

    except Exception as e:

        print("=============================manage_db_update")
        print('exception', e)
        print("=========================================")
        with open("logs/manage.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Manage DB Update - EXEPTION:")
            myfile.write('\n' + str(e))
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")

def leave_last_200_in_trends_array():

    db_ = db["trend"]
    db_trend_a = db["trend_a"]
    cursor_a = db_.find_one({"name": "ada"}).get("trend")
    lenght = len(cursor_a)
    num = 50

    if lenght > 200:

        cursor = db_.find()

        for c in cursor:

            trend = c.get("trend")
            trend_end = trend[-(lenght -num):]
            db_.update_one({'name': c.get("name")}, {'$set': {'trend': trend_end}})
            trend_start = trend[:(num)]
            arch_trend = db_trend_a.find_one({"name":c.get("name")}).get("trend")
            db_trend_a.update_one({'name': c.get("name")}, {'$set': {'trend':arch_trend + trend_start}})

            trend = c.get("trend_vol")
            trend_end = trend[-(lenght -num):]
            db_.update_one({'name': c.get("name")}, {'$set': {'trend_vol': trend_end}})
            trend_start = trend[:(num)]
            arch_trend = db_trend_a.find_one({"name":c.get("name")}).get("trend_vol")
            db_trend_a.update_one({'name': c.get("name")}, {'$set': {'trend_vol': arch_trend + trend_start}})

            trend = c.get("time")
            trend_end = trend[-(lenght - num):]
            db_.update_one({'name': c.get("name")}, {'$set': {'time': trend_end}})
            trend_start = trend[:(num)]
            arch_trend = db_trend_a.find_one({"name":c.get("name")}).get("time")
            db_trend_a.update_one({'name': c.get("name")}, {'$set': {'time': arch_trend + trend_start}})

def update_trend_av_del_above_500_trend_a():

    db_trend_a = db["trend_a"]
    cursor_a = db_trend_a.find_one({"name": "ada"}).get("trend")
    lenght = len(cursor_a)

    if lenght > 600:

        db_trend = db["trend"]
        cursor = db_trend.find()

        for c in cursor:
            try:
                trend_only = db_trend_a.find_one({"name": c.get("name")}).get("trend")
                trend = trend_only + c.get("trend")
                trend_vol_only = db_trend_a.find_one({"name": c.get("name")}).get("trend_vol")
                trend_vol = trend_vol_only + c.get("trend_vol")

                db_trend.update_one({'name': c.get("name")}, {'$set': {'trend_av': int(sum(trend) / len(trend))}})
                db_trend.update_one({'name': c.get("name")},
                                    {'$set': {'trend_vol_av': int(sum(trend_vol) / len(trend_vol))}})

                db_trend_a.update_one({'name': c.get("name")}, {'$set': {'trend': trend_only[-500:]}})
                db_trend_a.update_one({'name': c.get("name")}, {'$set': {'trend_vol': trend_vol_only[-500:]}})
            except Exception as e:

                print("=============================pinned_tweets")
                print(c.get("name"))
                print('exception', e)
                print("=========================================")
                with open("logs/manage.txt", "a") as myfile:
                    myfile.write('\n' + "=========================================")
                    myfile.write('\n' + "Manage DB PINNED TWEETS - EXEPTION:")
                    myfile.write('\n' + str(e) + c.get("name"))
                    myfile.write('\n' + str(traceback.format_exc()))
                    myfile.write('\n' + "=========================================")

def check_for_trending_tweets():

    bnb_accs = {'BNBCHAIN', 'binance', 'cz_binance'}

    try:

        cursor = db_track.find()
        cursor_average = db_average.find()

        for c in cursor:
            try:
                lenght = len(c.get("likes"))
                if lenght < 60:
                    score = int(c.get("likes")[lenght-1]) + int(c.get("retweet")[lenght-1])
                    for av in cursor_average:
                        if av.get("name") == c.get("source"):

                            db_sym.update_one({'link': c.get('link')},
                                                   {'$set': {'eng_score': str(score/av.get("list")[lenght-1])[:4]}},upsert=True)

                            if score > int(av.get("list")[lenght-1] * 1.3) and score > (lenght-1) * 10 and av.get("name") not in bnb_accs \
                                    or score > int(av.get("list")[lenght-1] * 2):

                                exists = db_filter.find_one({'link': c.get("link")})
                                if not exists:
                                    db_filter.insert_one(c)

                                    with open("logs/trending_tweets.txt", "a", encoding='utf-8') as myfile:
                                        myfile.write('\n' + "=======================================")
                                        myfile.write('\n' + av.get("name") + " NEW ")
                                        myfile.write('\n' + "text" + c.get("text"))
                                        myfile.write('\n' + "score" + str(score) + " len: " + str(lenght - 1))
                                        myfile.write('\n' + "score_average" + str(int(av.get("list")[lenght-1] * 2)))
                                        myfile.write('\n' + "array" + str(av.get("list")))
                                        myfile.write('\n' + "above_protect" + str((lenght-1) * 10))
                                        myfile.write('\n' + "=======================================")
                cursor_average.rewind()

            except Exception as e:
                with open("logs/manage.txt", "a") as myfile:
                    myfile.write('\n' + "=========================================")
                    myfile.write('\n' + "Manage DB TRENDING TWEETS - EXEPTION:")
                    myfile.write('\n' + str(e))
                    myfile.write('\n' + str(traceback.format_exc()))
                    myfile.write('\n' + "=========================================")



        requests.get(api_url + "ren_sym", verify=False)

    except Exception as e:

        print("=============================manage_db_check_trending_tweets")
        print('exception', e)
        print("=========================================")
        with open("logs/manage.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Manage DB TRENDING TWEETS - EXEPTION:")
            myfile.write('\n' + str(e))
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")

def pinned_tweets():

    try:

        alt_list = []
        db_sym_f = db["sym_f"]
        cursor = db_average.find()

        for c in Utils.acc_list:
            for i in c.get("list"):
                alt_list.append(i)

        users = client_tweepy.get_users(ids=alt_list, user_fields=['pinned_tweet_id','public_metrics'])

        for c in cursor:
            for user in users.data:
                if user.username == c.get('name'):
                    if user.pinned_tweet_id is not None and user.pinned_tweet_id != c.get('pinned_tweet_id'):

                        db_average.update_one({'name': user.username},
                                            {'$set': {'pinned_tweet_id': user.pinned_tweet_id}})

                        tweet = client_tweepy.get_tweets(ids=user.pinned_tweet_id, tweet_fields=["public_metrics"])

                        text = Utils.deEmojify(tweet.data[0].get('text'))

                        time2 = Utils.fix_time()

                        exists = db_sym_f.find_one({'link': "https://twitter.com/twitter/statuses/" + str(user.pinned_tweet_id)})
                        if not exists:

                            fcm.sendPush_twitter("Pinned tweet from " + user.username, text,
                                                 "https://twitter.com/twitter/statuses/" + str(user.pinned_tweet_id), "alts")

                            db_sym_f.insert_one({
                                "link": "https://twitter.com/twitter/statuses/" + str(user.pinned_tweet_id),
                                "text": text,
                                "source": user.username,
                                "time": time2,
                                "fow": str(user.public_metrics.get('followers_count'))[:-3],
                                "likes": 0,
                                "retweet": 0,
                                "eng_score": 0
                            })

                            requests.get(api_url + "ren_sym_f", verify=False)
    except Exception as e:

        print("=============================pinned_tweets")
        print('exception', e)
        print("=========================================")
        with open("logs/manage.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "Manage DB PINNED TWEETS - EXEPTION:")
            myfile.write('\n' + str(e))
            myfile.write('\n' + str(traceback.format_exc()))
            myfile.write('\n' + "=========================================")

def run():

    print("ONLINE MANAGE DB")

    t1 = threading.Thread(target=update)
    t1.start()

    while True:

        try:
            delete()
            time.sleep(60)
            delete()
            time.sleep(60)
            leave_last_200_in_trends_array()
            time.sleep(60)
            update_trend_av_del_above_500_trend_a()
            time.sleep(60)
            pinned_tweets()
            time.sleep(60)

        except Exception as e:

            print("=============================manage_db_track")
            print('exception', e)
            print("=========================================")
            time.sleep(30)
            with open("logs/manage.txt", "a") as myfile:
                myfile.write('\n' + "=========================================")
                myfile.write('\n' + str(e))
                myfile.write('\n' + str(traceback.format_exc()))
                myfile.write('\n' + "=========================================")
