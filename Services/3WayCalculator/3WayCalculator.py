import logging
import math
import time
import redis
import os
import asyncio
from dotenv import load_dotenv
from Core.RESTClients.Binance import BinanceClient
from Core.Tools.Chains import BinanceChains

load_dotenv()

REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

logging.basicConfig(level=logging.DEBUG)


class Calculator:
    __chains = []
    __roundings = {}
    __assets = []

    # localhost redis
    __redis = redis.Redis(host='redis', port=6379, db=0, password=REDIS_PASSWORD)
    __redis_results = redis.Redis(host='redis', port=6379, db=1, password=REDIS_PASSWORD)

    def __init__(self, chains_list):
        self.__chains = chains_list
        self.__generate_roundings(chains_list)
        self.__compose_assets_list()
        self.__redis_results.flushdb()

    def __generate_roundings(self, some_chains):
        for chain in some_chains:
            data = {chain['lsa']: chain['lsa_vol_decimals']}
            data2 = {chain['csa']: chain['convert_vol_decimals']}
            data3 = {chain['rsa']: chain['rsa_vol_decimals']}

            self.__roundings.update(data)
            self.__roundings.update(data2)
            self.__roundings.update(data3)

    def __compose_assets_list(self):
        self.__assets = [*self.__roundings]

    def __fetch_prices(self):
        # return self.__redis.hmget("binanceOrderbook", assets_list)
        return self.__redis.hgetall("orderbook")

    def __round_down(self, number: float, decimals: int):
        if not isinstance(decimals, int):
            raise TypeError("Decimals places must be integer")
        elif decimals < 0:
            raise TypeError("Decimals must be > 0")
        elif decimals == 0:
            return math.floor(number)

        factor = 10 ** decimals
        return math.floor(number * factor) / factor

    def __calc_left_to_right(self, lsa_ask, lsa_rounding, csa_bid, rsa_rounding, rsa_bid):
        try:
            buy_volume = self.__round_down(100 / lsa_ask * 0.999, lsa_rounding)
            convert_volume = self.__round_down(buy_volume * csa_bid * 0.999, rsa_rounding)
            sell_volume = convert_volume * rsa_bid * 0.999
            return sell_volume
        except Exception:
            return -100

    def __calc_right_to_left(self, rsa_ask, rsa_rounding, csa_ask, lsa_rounding, lsa_bid):
        try:
            buy_volume = self.__round_down(100 / rsa_ask * 0.999, rsa_rounding)
            convert_volume = self.__round_down(buy_volume / csa_ask * 0.999, lsa_rounding)
            sell_volume = convert_volume * lsa_bid * 0.999
            return sell_volume
        except Exception:
            return -100

    def __send_results(self, results):
        try:
            self.__redis_results.hmset('data', results)
            # self.__redis_results.publish('data', results)
        except Exception:
            return False

    def calc_all(self):
        prices = self.__fetch_prices()
        results = {}

        for chain in self.__chains:
            try:
                # price data: ask, ask_volume, bid, bid_volume
                # roundings lsa_vol_decimals, convert_vol_decimals, rsa_vol_decimals
                lsa_b = chain['lsa'].encode()
                lsa_data = prices[lsa_b].decode().split(',')

                csa_b = chain['csa'].encode()
                csa_data = prices[csa_b].decode().split(',')

                rsa_b = chain['rsa'].encode()
                rsa_data = prices[rsa_b].decode().split(',')

                # lsa_ask, lsa_rounding, csa_bid, rsa_rounding, rsa_bid
                lr = self.__calc_left_to_right(
                    float(lsa_data[0]),
                    chain["lsa_vol_decimals"],
                    float(csa_data[2]),
                    chain["rsa_vol_decimals"],
                    float(rsa_data[2])
                )

                # rsa_ask, rsa_rounding, csa_ask, lsa_rounding, lsa_bid
                rl = self.__calc_right_to_left(
                    float(rsa_data[0]),
                    chain["rsa_vol_decimals"],
                    float(csa_data[0]),
                    chain["lsa_vol_decimals"],
                    float(lsa_data[2])
                )
                key_left = "LR::" + chain['key']
                key_right = "RL::" + chain['key']
                results.update({key_left: lr})
                results.update({key_right: rl})

            except Exception as error:
                continue
        self.__send_results(results)


def config() -> Calculator:
    markets = BinanceClient().format_spot_tickers_data()
    chains = BinanceChains(markets)

    # test = Gateio_tickers()
    # tickers = test.format_tickers_data()
    # chains = Binance_chains(tickers)

    chains_list = chains.split_chains_list(chains.chains_list, 10000)
    return Calculator(chains_list[0])


async def main(calc: Calculator):
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


