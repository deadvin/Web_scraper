import traceback
import pymongo
from binance import Client
import keys.keys as keys
import time
import pandas as pd
import requests
import urllib3
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
api_key = keys.api_key
api_secret = keys.api_secret
client = Client(api_key, api_secret, {"verify": True, "timeout": 60})
api_url = keys.api_url

clientmongo = pymongo.MongoClient(keys.mongo_url, ssl=True)
db_price = clientmongo.prices

db = clientmongo.SentencesDatabase
db_div = db["div"]
counter = 0
one_min = Client.KLINE_INTERVAL_1MINUTE
fifteen_min = Client.KLINE_INTERVAL_15MINUTE
one_hour = Client.KLINE_INTERVAL_1HOUR
one_day = Client.KLINE_INTERVAL_1DAY

# region alt list
alts_list =[]
alts_list.append({'name': 'WAVES', "full":"Waves"})
alts_list.append({'name': 'TFUEL', "full":"Theta Fuel"})
alts_list.append({'name': 'ZEC', "full":"Zcash"})
alts_list.append({'name': 'NEO', "full":"Neo"})
alts_list.append({'name': 'HBAR', "full":"Hedera"})
alts_list.append({'name': 'LINK', "full":"Chainlink"})
alts_list.append({'name': 'HOT', "full":"Holo"})
alts_list.append({'name': 'AGLD', "full":"Adventure Gold"})
# alts_list.append({'name': 'APE', "full":"ApeCoin"})
alts_list.append({'name': 'FLOW', "full":"Flow"})
alts_list.append({'name': 'FTT', "full":"FTX Token"})
alts_list.append({'name': 'BAT', "full":"Basic Attention Token"})
alts_list.append({'name': 'AUDIO', "full":"Audius"})
alts_list.append({'name': 'ADA', "full":"Cardano"})
alts_list.append({'name': 'SOL', "full":"Solana"})
alts_list.append({'name': 'DOGE', "full": "Dogecoin"})
alts_list.append({'name': 'MATIC', "full": "Polygon"})
alts_list.append({'name': 'LUNA', "full": "Terra"})
alts_list.append({'name': 'DOT', "full":"Polkadot"})
alts_list.append({'name': 'INJ', "full": "Injective Protocol"})
alts_list.append({'name': 'AVAX', "full": "Avalanche"})
alts_list.append({'name': 'EOS', "full": "Eosio"})
alts_list.append({'name': 'THETA', "full":"Theta"})
alts_list.append({'name': 'IOTA', "full": "Miota"})
alts_list.append({'name': 'CHZ', "full":"Chiliz"})
alts_list.append({'name': 'ONE', "full": "Harmony"})
alts_list.append({'name': 'KSM', "full": "Kusama"})
alts_list.append({'name': 'NEAR', "full": "Near Protocol"})
alts_list.append({'name': 'XTZ', "full": "Tezos"})
alts_list.append({'name': 'ALGO', "full": "Algorand"})
alts_list.append({'name': 'EGLD', "full": "Elrond"})
alts_list.append({'name': 'AR', "full":"Arweave"})
alts_list.append({'name': 'AXS', "full": "Axieinfinity"})
alts_list.append({'name': 'XRP', "full":"Ripple"})
alts_list.append({'name': 'FIL', "full":"Filecoin",})
alts_list.append({'name': 'VET', "full":"Vechain",})
alts_list.append({'name': 'UNI', "full":"Uniswap", })
alts_list.append({'name': 'CAKE', "full":"PancakeSwap"})
alts_list.append({'name': 'ICP', "full": "Internet Computer"})
alts_list.append({'name': 'ETC', "full": "Ethereum Classic"})
alts_list.append({'name': 'ZIL', "full": "Zilliqa"})
alts_list.append({'name': 'XLM', "full": "Stellar"})
alts_list.append({'name': 'XMR', "full": "Monero"})
alts_list.append({'name': 'SAND', "full": "Sandbox"})
alts_list.append({'name': 'RVN', "full": "Ravencoin"})
alts_list.append({'name': 'MANA', "full":"Decentraland"})
alts_list.append({'name': 'LTC', "full": "Litecoin"})
alts_list.append({'name': 'GALA', "full": "Galagames"})
alts_list.append({'name': 'BNB', "full": "Binance Coin"})
alts_list.append({'name': 'AAVE', "full":"Aave"})
alts_list.append({'name': 'ANKR', "full":"Ankr"})
alts_list.append({'name': '1INCH', "full": "One Inch"})
alts_list.append({'name': 'COTI', "full":"Coti"})
alts_list.append({'name': 'ENJ', "full":"Enjin"})
alts_list.append({'name': 'ATOM', "full": "Cosmos"})
alts_list.append({'name': 'ETH', "full": "Etherium"})
alts_list.append({'name': 'FTM', "full": "Fantom"})
# endregion

def run():

    global counter

    print("BINANCE ONLINE")

    while True:

        try:
            # start_time = time.time()
            time.sleep(1)
            counter += 1

            if counter%10 == 0:
                time_frame = fifteen_min
                db_div_new = db_price["div_15m"]
                db_candles = db_price["candles_15m"]
                endpoint = "_15m"
                petiod = "3750 minutes ago UTC"
            elif counter%24 == 0:
                time_frame = one_hour
                db_div_new = db_price["div_1h"]
                db_candles = db_price["candles_1h"]
                endpoint = "_1h"
                petiod = "250 hours ago UTC"
            elif counter%64 == 0:
                time_frame = one_day
                db_div_new = db_price["div_1d"]
                db_candles = db_price["candles_1d"]
                endpoint = "_1d"
                petiod = "250 days ago UTC"
                counter = 0
            else:
                time_frame = one_min
                db_div_new = db_price["div_1m"]
                db_candles = db_price["candles_1m"]
                endpoint = "_1m"
                petiod = "250 minutes ago UTC"

            klines = client.get_historical_klines("BTCUSDT", time_frame, petiod)
            df_btc = pd.DataFrame(klines)
            df_btc.columns = ['open_time',
                              'o', 'h', 'l', 'c', 'v',
                              'close_time', 'qav', 'num_trades',
                              'taker_base_vol', 'taker_quote_vol', 'ignore']
            df_btc = df_btc.drop('open_time', 1)
            df_btc = df_btc.drop('v', 1)
            df_btc = df_btc.drop('qav', 1)
            df_btc = df_btc.drop('num_trades', 1)
            df_btc = df_btc.drop('taker_base_vol', 1)
            df_btc = df_btc.drop('taker_quote_vol', 1)
            df_btc = df_btc.drop('ignore', 1)
            df_btc = df_btc.drop('close_time', 1)

            df_btc["c"] = df_btc["c"].astype(str).astype(float)

            df_btc["sma"] = (df_btc.c / (df_btc.c.rolling(window=100).mean()))
            df_btc = df_btc.fillna(0)

            db_candles.update_one({"name": "btc"},
                                  {"$set": {"o": df_btc.o.tolist(), "h": df_btc.h.tolist(), "c": df_btc.c.tolist(),
                                            "l": df_btc.l.tolist()}},
                                  upsert=True)

            def f(float):
                return float - 1

            df_btc["sma"] = df_btc.sma.apply(f)

            for alt in alts_list:
                klines = client.get_historical_klines(alt.get('name') + "USDT", time_frame, petiod)
                df = pd.DataFrame(klines)

                df.columns = ['open_time',
                              'o', 'h', 'l', 'c', 'v',
                              'close_time', 'qav', 'num_trades',
                              'taker_base_vol', 'taker_quote_vol', 'ignore']
                df = df.drop('open_time', 1)
                df = df.drop('v', 1)
                df = df.drop('qav', 1)
                df = df.drop('num_trades', 1)
                df = df.drop('taker_base_vol', 1)
                df = df.drop('taker_quote_vol', 1)
                df = df.drop('ignore', 1)
                df = df.drop('close_time', 1)
                df["c"] = df["c"].astype(str).astype(float)

                df['sma_btc'] = df_btc["sma"]
                df["sma"] = (df.c / (df.c.rolling(window=100).mean())) - df['sma_btc']
                df = df.fillna(0)

                def f(float):
                    return (float - 1) * 100

                df["sma"] = df.sma.apply(f)
                df['sma'] = df['sma'].apply(lambda x: round(x, 3))

                db_div_new.update_one({"name": alt.get('name')},
                                  {"$set": {"price": df.sma.iloc[-150:].tolist(), "full_name": alt.get('full')}},upsert=True)

                db_candles.update_one({"name": alt.get('name')},
                                      {"$set": {"o": df.o.tolist(),"h": df.h.tolist(),"c": df.c.tolist(),"l": df.l.tolist()}},
                                      upsert=True)

                if time_frame == Client.KLINE_INTERVAL_1MINUTE:
                    db_div.update_one({"name": alt.get('name')},
                                      {"$set": {"price": df.sma.iloc[-150:].tolist(), "full_name": alt.get('full')}}, upsert=True)

            requests.get(api_url + "ren_div", verify=False)
            requests.get(api_url + "ren_div" + endpoint, verify=False)

            # print("--- %s seconds ---" % (time.time() - start_time))

        except Exception as e:

            print("=========================================")
            print('exception', e)
            print("=========================================")
            with open("logs/binance.txt", "a") as myfile:
                myfile.write('\n' + "=========================================")
                myfile.write('\n' + "BINANCE - EXEPTION:")
                myfile.write('\n' + str(e))
                myfile.write('\n' + str(traceback.format_exc()))
                myfile.write('\n' + "=========================================")

