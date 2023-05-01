import logging
import math
import time
import redis
import json
import os
import asyncio
from dotenv import load_dotenv
from Core.RESTClients.Binance import BinanceClient, Filter

load_dotenv()

REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

logging.basicConfig(level=logging.DEBUG)


class SpreadCalculator:
    __tickers = []
    __roundings = {}
    __assets = []

    # redis localhost
    __redis = redis.Redis(host='redis', port=6379, db=0, password=REDIS_PASSWORD)
    __redis_results = redis.Redis(host='redis', port=6379, db=2, password=REDIS_PASSWORD)

    def __init__(self, ticker_list):
        self.__tickers = ticker_list
        self.__generate_roundings(ticker_list)
        self.__compose_assets_list()
        self.__redis_results.flushdb()

    def __generate_roundings(self, tickers):
        for ticker in tickers:
            data = {ticker['symbol']: ticker['volume_decimal']}

            self.__roundings.update(data)

    def __compose_assets_list(self):
        self.__assets = [*self.__roundings]

    def __fetch_prices(self):
        try:
            return self.__redis.hgetall("orderbook")
        except redis.exceptions as error:
            logging.warning(error)

    def __round_down(self, number: float, decimals: int):
        if not isinstance(decimals, int):
            raise TypeError("Decimals places must be integer")
        elif decimals < 0:
            raise TypeError("Decimals must be > 0")
        elif decimals == 0:
            return math.floor(number)

        factor = 10 ** decimals
        return math.floor(number * factor) / factor

    def __update_redis(self, results):
        try:
            self.__redis_results.hmset('data', results)
            # json_data = json.dumps(results)
            # self.__redis_results.publish('data', json_data)
        except Exception as error:
            logging.warning(error)
            return False

    def calc_all(self):
        prices = self.__fetch_prices()
        results = {}
        for ticker in self.__tickers:
            try:
                # price data: ask, ask_volume, bid, bid_volume
                ticker_name = ticker['symbol'].encode()
                price_data = prices[ticker_name].decode().split(',')
                bid_buy_vol = self.__round_down(100 / float(price_data[2]), ticker['volume_decimal']) * 0.999
                ask_sell_vol = self.__round_down(bid_buy_vol, ticker['volume_decimal']) * float(price_data[0]) * 0.999
                hundred = self.__round_down(100000 / float(price_data[0]), ticker['volume_decimal'])
                ticks = self.__round_down(float(price_data[0]) - float(price_data[2]), ticker['price_decimal'])

                # msg_data = str(ask_sell_vol) + ',' + str(hundred) + ',' + str(ticks)
                msg_data = json.dumps({"r": ask_sell_vol, "h": hundred, "t": ticks})
                # msg_data = {"r": ask_sell_vol, "h": hundred, "t": ticks}

                key = ticker['symbol']
                results.update({key: msg_data})
            except Exception:
                continue
        self.__update_redis(results)


def config() -> SpreadCalculator:
    filter_list = ["USDT"]
    markets = BinanceClient(filter_type=Filter.quote, filter_list=filter_list).format_spot_tickers_data()
    return SpreadCalculator(markets)


async def main(calc: SpreadCalculator):
    while True:
        ts1 = time.time()
        calc.calc_all()
        ts2 = time.time() - ts1
        logging.debug(ts2)


if __name__ == "__main__":
    calc_object = config()
    loop = asyncio.new_event_loop()
    try:
        loop.create_task(main(calc_object))
        loop.run_forever()
    finally:
        loop.close()


