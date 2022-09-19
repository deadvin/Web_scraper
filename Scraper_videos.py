import time
import random
import pymongo
from selenium.webdriver.common.by import By
import Firebase_manager as fcm
from selenium import webdriver
import requests
import keys.keys as keys
import Utils


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
driver = webdriver.Chrome(keys.chromepath, options=chrome_options)

words = ["btc", "eth", "ada", "bnb",
                 "xrp", "sol", "dot", "doge", "eth", "uni", "luna", "link", "avax", "ltc", "bch",
                 "algo", "icp", "matic", "fil", "ftt","trx",
                 "xlm", "vet", "etc", "atom", "theta",
                 "xtz","aave", "egld", "cake", "eos", "xmr", "hbar", "qnt", "grt", "axs", "near",
                 "neo", "ksm", "ftm", "waves", "shib", "dash", "chz", "sushi",
                 "ar", "audio","one","zec","hot","tfuel","celo","mana","enj","iota","zil",
                 "flow","rvn","ren","zrx","ankr","sand","1inch","ocean","bake","win","inj","ogn","alice",
                 "slp","super"]

urls = ["https://www.youtube.com/c/CoinBureau/videos", "https://www.youtube.com/c/CryptocurrencyNews1/videos",
        "https://www.youtube.com/c/JRNYCrypto/videos", "https://www.youtube.com/c/AltcoinDaily/videos",
        "https://www.youtube.com/c/CryptosRUs/videos", "https://www.youtube.com/c/TheCryptoLark/videos",
        "https://www.youtube.com/channel/UCGDjpwZV-bU-sLSnhInCfKQ/videos",
        "https://www.youtube.com/channel/UCjemQfjaXAzA-95RKoy9n_g/videos",
        "https://www.youtube.com/channel/UCRvqjQPSeaWn-uEx-w0XOIg/videos",
        "https://www.youtube.com/c/FUDTV/videos",
        "https://www.youtube.com/c/ChicoCrypto/videos",
        "https://www.youtube.com/c/TylerSCrypto/videos",
        "https://www.youtube.com/channel/UCN9Nj4tjXbVTLYWN0EKly_Q/videos"
        ]


def youtube():

    for url in urls:

        try:
            time.sleep(2)
            driver.get(url)
            time.sleep(2)
            body = driver.find_element(by=By.XPATH, value='//*[@id="video-title"]').text
            link = driver.find_element(by=By.XPATH, value='//*[@id="video-title"]')
            name = driver.find_element(by=By.CLASS_NAME, value='style-scope ytd-channel-name').text
            exsist = tube_db.find_one({'text': body})

            if not exsist:

                tube_db.insert_one({
                    "name": name,
                    "text": body,
                    "link": link.get_attribute("href"),
                    "time": Utils.fix_time(),
                    "seen": 1
                })
                requests.get(api_url + "ren_vid", verify=False)

                if name == "Coin Bureau":
                    fcm.sendPush_twitter(name, body, link.get_attribute("href"), "vid")

                print('=======  YOUTUBE =========')
                print(body, flush=True)

        except Exception as e:
            print('===================================')
            print(e, flush=True)
            print('===================================')


def main():

    print("ONLINE YOUTUBE")

    try:
        driver.get("https://www.youtube.com/c/CoinBureau/videos")
        time.sleep(random.randint(3, 6))
        driver.execute_script("window.scrollTo(0, 200)")
        time.sleep(random.randint(3, 6))
        el = driver.find_element(by=By.XPATH, value=
            '/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/form[2]/div/div/button/div[1]')

        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_to_element_with_offset(el, 5, 5)
        action.click()
        action.perform()

    except Exception as e:
        print('===================================')
        print(e, flush=True)
        print('===================================')
        driver.quit()
        time.sleep(random.randint(30, 60))

    time.sleep(random.randint(13, 19))

    try:
        while True:
            youtube()
            time.sleep(120)

    except Exception as e:
        print('===================================')
        print(e, flush=True)
        print('===================================')
        time.sleep(random.randint(50, 150))

        with open("logs/log.txt", "a") as myfile:
            myfile.write('\n' + "=========================================")
            myfile.write('\n' + "YOUTUBE")
            myfile.write('\n' + str(e))
            myfile.write('\n' + "=========================================")
