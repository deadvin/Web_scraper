import time
import pytz
import re
import random
import datetime
import pymongo
from selenium.webdriver.common.by import By
import Firebase_manager as fcm
from selenium import webdriver
import requests
import keys.keys as keys

client = pymongo.MongoClient(keys.mongo_url,
    ssl=True)
db = client.SentencesDatabase
news_db = db["news"]
db_news_f = db["news_f"]
event_db = db["events"]
tube_db = db["videos"]
api_url = keys.api_url

chrome_options = webdriver.ChromeOptions()


chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')

driver1 = webdriver.Chrome(keys.chromepath, options=chrome_options)
driver2 = webdriver.Chrome(keys.chromepath, options=chrome_options)


words = ["btc", "eth", "ada", "bnb",
                 "xrp", "sol", "dot", "doge", "eth", "uni", "luna", "link", "avax", "ltc", "bch",
                 "algo", "icp", "matic", "fil", "ftt","trx",
                 "xlm", "vet", "etc", "atom", "theta",
                 "xtz","aave", "egld", "cake", "eos", "xmr", "hbar", "qnt", "grt", "axs", "near",
                 "neo", "ksm", "ftm", "waves", "shib", "dash", "chz", "sushi",
                 "ar", "audio","one","zec","hot","tfuel","celo","mana","enj","iota","zil",
                 "flow","rvn","ren","zrx","ankr","sand","1inch","ocean","bake","win","inj","ogn","alice",
                 "slp","super"]

def build_drivers():

    global driver2,driver1

    driver1 = webdriver.Chrome('C:/Users/Deadvin/Downloads/chromedriver', options=chrome_options)
    driver2 = webdriver.Chrome('C:/Users/Deadvin/Downloads/chromedriver', options=chrome_options)

def fix_time():

    tz = pytz.timezone("Europe/Sofia")
    tim = tz.localize(datetime.datetime.now(), is_dst=None)
    tim = str(tim)
    tim = tim[:-7]
    tim = re.sub(':', '', tim)
    tim = re.sub('-', '', tim)
    tim = re.sub(' ', '', tim)

    return tim

def news():

    driver1.get('https://www.newsnow.co.uk/h/Business+&+Finance/Cryptocurrencies?type=ln')

    element = driver1.find_element(by=By.XPATH, value='/html/body/div[4]/div[4]/main/div[2]/div/div/div[1]/div[2]/div/a')
    text = element.text
    link = element.get_attribute("href")

    source = driver1.find_element(by=By.XPATH, value=
        '/html/body/div[4]/div[4]/main/div[2]/div/div/div[1]/div[2]/div[1]/span/span[1]').text

    news_title = news_db.find_one({'text': text})

    if not news_title:

        driver2.get(link)
        time.sleep(12)
        url = driver2.current_url

        print("===========   NEWS  ==========", flush=True)
        print(text, flush=True)
        print(source, flush=True)
        print(url, flush=True)
        print("   ", flush=True)

        news_db.insert_one({
            "text": text,
            "link": url,
            "source": source,
            "time": fix_time(),
            "seen": 1,
        })
        requests.get(api_url + "ren_news", verify=False)

    # print("NEWS DONE")

def news_top():

    driver1.get('https://www.newsnow.co.uk/h/Business+&+Finance/Cryptocurrencies')

    for x in range(1, 10):

        element = driver1.find_element(by=By.XPATH, value=
            '/html/body/div[4]/div[4]/main/div[2]/div[' + str(x) + ']/div/div[1]/div/div/a')

        text = element.text
        link = element.get_attribute("href")

        source = driver1.find_element(by=By.XPATH, value=
            '/html/body/div[4]/div[4]/main/div[2]/div[' + str(
                x) + ']/div/div[1]/div/div/span[1]/span[1]').text

        news_title = db_news_f.find_one({'text': text})

        if text and source:
            if not news_title:

                driver2.get(link)
                time.sleep(12)
                url = driver2.current_url

                db_news_f.insert_one({
                    "text": text,
                    "link": url,
                    "source": source,
                    "time": fix_time(),
                    "seen": 1,
                })
                requests.get(api_url + "ren_news_f", verify=False)

                print("=========  NEWS  TOP =========", flush=True)
                print(text, flush=True)
                print(source, flush=True)
                print(url, flush=True)
                print("  ", flush=True)

    # print("TOP NEWS DONE")

def events():

    driver2.get(
        'https://coinmarketcal.com/en/?form%5Bdate_range%5D=16%2F09%2F2021+-+01%2F08%2F2024&form%5Bkeyword%5D=&form%5Bsort_by%5D=created_desc&form%5Bsubmit%5D=&form%5Bshow_reset%5D=')

    player = driver2.find_element(by=By.XPATH, value='/html/body/main/section[1]/div[2]/div[3]/article[1]/div/div')

    link = driver2.find_element(by=By.XPATH, value='/html/body/main/section[1]/div[2]/div[3]/article[1]/div/div/a')

    text = player.text

    split = text.splitlines()

    symbol = re.search(r'\((.*?)\)', split[0]).group(1).lower()

    for word in words:
        if word == symbol:

            exsist = event_db.find_one({'text': split[3]})
            if not exsist:
                fcm.sendPush_twitter(symbol, split[1], link.get_attribute("href"), "events")

                event_db.insert_one({
                    "sym": symbol,
                    "date": split[1],
                    "name": split[2],
                    "text": split[3],
                    "link": link.get_attribute("href"),
                    "time": fix_time(),
                    "seen": 1
                })

    #  =====================================  BOX 2

    player = driver2.find_element(by=By.XPATH, value='/html/body/main/section[1]/div[2]/div[3]/article[2]/div/div')

    link = driver2.find_element(by=By.XPATH, value='/html/body/main/section[1]/div[2]/div[3]/article[2]/div/div/a')

    text = player.text

    split = text.splitlines()

    symbol = re.search(r'\((.*?)\)', split[0]).group(1).lower()

    for word in words:
        if word == symbol:

            exsist = event_db.find_one({'text': split[3]})

            if not exsist:
                fcm.sendPush_twitter(symbol, split[1], link.get_attribute("href"), "events")

                event_db.insert_one({
                    "sym": symbol,
                    "date": split[1],
                    "name": split[2],
                    "text": split[3],
                    "link": link.get_attribute("href"),
                    "time": fix_time(),
                    "seen": 1
                })

    #   =====================================  BOX 3

    player = driver2.find_element(by=By.XPATH, value='/html/body/main/section[1]/div[2]/div[3]/article[3]/div/div')

    link = driver2.find_element(by=By.XPATH, value='/html/body/main/section[1]/div[2]/div[3]/article[3]/div/div/a')

    text = player.text

    split = text.splitlines()

    symbol = re.search(r'\((.*?)\)', split[0]).group(1).lower()

    for word in words:
        if word == symbol:

            exsist = event_db.find_one({'text': split[3]})

            if not exsist:
                fcm.sendPush_twitter(symbol, split[1], link.get_attribute("href"), "events")

                event_db.insert_one({
                    "sym": symbol,
                    "date": split[1],
                    "name": split[2],
                    "text": split[3],
                    "link": link.get_attribute("href"),
                    "time": fix_time(),
                    "seen": 1
                })

    # print("EVENTS DONE")

def main():

    global driver2, driver1

    while True:
        try:
            news()
            time.sleep(20)
            news()
            time.sleep(20)
            news_top()
            time.sleep(20)
            news()
            time.sleep(20)
            news()
            time.sleep(20)
            news_top()
            time.sleep(20)
            events()

        except Exception as e:
            print('===================================')
            print(e, flush=True)
            print('===================================')
            driver1.quit()
            driver2.quit()
            time.sleep(random.randint(30, 60))

            with open("logs/log.txt", "a") as myfile:
                myfile.write('\n' + "=========================================")
                myfile.write('\n' + "WEB")
                myfile.write('\n' + str(e))
                myfile.write('\n' + "=========================================")

            build_drivers()
