import Twitter_stream_acc as Twitter_stream_acc
import twitter_stream_all_v1 as twitter_stream_all_v1
import Scraper_videos as Scraper_videos
import Manage_DB as Manage_DB
import Binance_script as Binance_script
import Scraper_news_events as Scraper_news_events
import threading


def twitter_all_f():
    twitter_stream_all_v1.main()

def twitter_acc_f():
    Twitter_stream_acc.main()

def screapers_f():
    Scraper_videos.main()

def web_f():
    Scraper_news_events.main()

def manage():
    Manage_DB.run()

def price():
    Binance_script.run()


if __name__ == "__main__":

    t1 = threading.Thread(target=twitter_all_f)
    t1.start()

    t2 = threading.Thread(target=twitter_acc_f)
    t2.start()

    t3 = threading.Thread(target=screapers_f)
    t3.start()

    t4 = threading.Thread(target=web_f)
    t4.start()

    t5 = threading.Thread(target=manage)
    t5.start()

    t6 = threading.Thread(target=price)
    t6.start()




