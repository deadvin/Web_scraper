import Twitter_stream_acc as Twitter_stream_acc
import twitter_stream_all as twitter_stream_all
import Scraper_videos as Scraper_videos
import Manage_DB as Manage_DB
import Binance_prices as Binance_script
import Scraper_news_events as Scraper_news_events
import threading


def twitter_all():
    twitter_stream_all.main()

def twitter_acc():
    Twitter_stream_acc.main()

def videos():
    Scraper_videos.main()

def web_news_events():
    Scraper_news_events.main()

def manage_db():
    Manage_DB.run()

def binance_scripts():
    Binance_script.run()

def main():

    t1 = threading.Thread(target=twitter_all)
    t1.start()

    t2 = threading.Thread(target=twitter_acc)
    t2.start()

    t3 = threading.Thread(target=videos)
    t3.start()

    t4 = threading.Thread(target=web_news_events)
    t4.start()

    t5 = threading.Thread(target=manage_db)
    t5.start()

    t6 = threading.Thread(target=binance_scripts)
    t6.start()


if __name__ == "__main__":

    main()






