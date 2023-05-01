# coding: utf-8
import requests
from Core.RESTClients.Binance import Filter
from Core.Tools.Chains import BinanceChains


class GateIoOrderBookExeption(Exception):
    pass


class GateioTickers:
    __host = "https://api.gateio.ws/api/v4"
    __raw_ticker_list = {}
    __filter_mode = Filter.none
    __filter_list = []

    def __init__(self, filter_type=Filter.none, filter_list=None):
        self.__filter_mode = filter_type
        if filter_list is not None:
            self.__filter_list = filter_list

    def __fetch_tickers(self):
        url = self.__host + "/spot/currency_pairs"
        request = requests.get(url)
        if request.status_code == 200:
            self.__raw_ticker_list = request.json()
        else:
            raise GateIoOrderBookExeption(f"{request.status_code}")

    def __filter_fetched_list(self, fetched_list):
        if self.__filter_mode == Filter.none:
            return fetched_list
        elif self.__filter_mode == Filter.exclude:
            return [s for s in fetched_list if s['symbol'] not in self.__filter_list]
        if self.__filter_mode == Filter.include:
            return [s for s in fetched_list if s['symbol'] in self.__filter_list]

    def __count_decimal(self, number):
        try:
            int(number.rstrip('0').rstrip('.'))
            return 1
        except:
            return len(str(float(number)).split('.')[-1])

    def format_tickers_data(self):
        self.__fetch_tickers()
        raw_ticker_data = self.__raw_ticker_list

        all_symbols = [t for t in raw_ticker_data if t['trade_status'] in 'tradable']
        fltered_symbols = self.__filter_fetched_list(all_symbols)

        formated_symbols_list = []

        for current_symbol in fltered_symbols:
            # volume_decimal = self.__count_decimal(current_symbol['amount_precision'])

            formated_symbols_list.append({
                "symbol": current_symbol["id"],
                "baseAsset": current_symbol['base'],
                "quoteAsset": current_symbol['quote'],
                "volume_decimal": current_symbol['amount_precision']
            })
        # self.formated_ticker_list.extend(formated_symbols_list)
        return formated_symbols_list

    def test_connection(self):
        request = requests.get(self.__host + "/api/v3/time")
        return request


if __name__ == "__main__":
    test = GateioTickers()
    tickers = test.format_tickers_data()

    chains = BinanceChains(tickers)

    listt = set()
    for chain in chains.chains_list:
        listt.add(f'{chain["lsa"]}')
        listt.add(f'{chain["rsa"]}')
        listt.add(f'{chain["csa"]}')

    chains_lists = chains.split_chains_list(chains.chains_list, 10000)

    print("q")