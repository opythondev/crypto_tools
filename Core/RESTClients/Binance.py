from enum import Enum
import requests


class Filter(Enum):
    include = 1
    exclude = 2
    none = 3
    quote = 4


class BinannceOrderBookExeption(Exception):
    pass


class BinanceClient:
    __host = "https://api.binance.com"
    __fhost = "https://fapi.binance.com"
    __raw_ticker_list = {}
    __filter_mode = Filter.none
    __filter_list = []

    def __init__(self, filter_type=Filter.none, filter_list=None):
        self.__filter_mode = filter_type
        if filter_list is not None:
            self.__filter_list = filter_list

    def __fetch_spot_tickers(self):
        url = self.__host + "/api/v3/exchangeInfo"
        request = requests.get(url)
        if request.status_code == 200:
            self.__raw_ticker_list = request.json()
        else:
            raise BinannceOrderBookExeption(f"{request.status_code}")

    def __fetch_futures_m_tickers(self):
        url = self.__fhost + "/fapi/v1/exchangeInfo"
        request = requests.get(url)
        if request.status_code == 200:
            self.__raw_ticker_list = request.json()
        else:
            raise BinannceOrderBookExeption(f"{request.status_code}")

    def __filter_fetched_list(self, fetched_list):
        if self.__filter_mode == Filter.none:
            return fetched_list
        elif self.__filter_mode == Filter.exclude:
            return [s for s in fetched_list if s['symbol'] not in self.__filter_list]
        elif self.__filter_mode == Filter.include:
            return [s for s in fetched_list if s['symbol'] in self.__filter_list]
        elif self.__filter_mode == Filter.quote:
            return [s for s in fetched_list if s['quoteAsset'] in self.__filter_list]

    def __count_decimal(self, number):
        try:
            int(number.rstrip('0').rstrip('.'))
            return 1
        except:
            return len(str(float(number)).split('.')[-1])

    def format_futures_m_tickers_data(self):
        self.__fetch_futures_m_tickers()
        raw_ticker_data = self.__raw_ticker_list

        all_symbols = [t for t in raw_ticker_data["symbols"] if t['status'] in 'TRADING']
        fltered_symbols = self.__filter_fetched_list(all_symbols)

        formated_symbols_list = []

        for current_symbol in fltered_symbols:
            price_decimal = None
            volume_decimal = None
            for ticker_filter in current_symbol['filters']:
                if ticker_filter['filterType'] == "PRICE_FILTER":
                    price_decimal = ticker_filter['minPrice']
                elif ticker_filter['filterType'] == "LOT_SIZE":
                    volume_decimal = ticker_filter['minQty']

            price_decimal = self.__count_decimal(price_decimal)
            volume_decimal = self.__count_decimal(volume_decimal)

            formated_symbols_list.append({
                "symbol": current_symbol["symbol"],
                "baseAsset": current_symbol['baseAsset'],
                "quoteAsset": current_symbol['quoteAsset'],
                "price_decimal": price_decimal,
                "volume_decimal": volume_decimal
            })
        return formated_symbols_list

    def format_spot_tickers_data(self):
        self.__fetch_spot_tickers()
        raw_ticker_data = self.__raw_ticker_list

        all_symbols = [t for t in raw_ticker_data["symbols"] if t['status'] in 'TRADING']
        spot_symbols = [s for s in all_symbols if s['isSpotTradingAllowed'] is True]
        fltered_symbols = self.__filter_fetched_list(spot_symbols)

        formated_symbols_list = []

        for current_symbol in fltered_symbols:
            price_decimal = None
            volume_decimal = None
            for ticker_filter in current_symbol['filters']:
                if ticker_filter['filterType'] == "PRICE_FILTER":
                    price_decimal = ticker_filter['minPrice']
                elif ticker_filter['filterType'] == "LOT_SIZE":
                    volume_decimal = ticker_filter['minQty']

            price_decimal = self.__count_decimal(price_decimal)
            volume_decimal = self.__count_decimal(volume_decimal)

            formated_symbols_list.append({
                "symbol": current_symbol["symbol"],
                "baseAsset": current_symbol['baseAsset'],
                "quoteAsset": current_symbol['quoteAsset'],
                "price_decimal": price_decimal,
                "volume_decimal": volume_decimal
            })
        return formated_symbols_list

    def fetch_spot_symbols(self) -> [str]:
        self.__fetch_spot_tickers()
        raw_ticker_data = self.__raw_ticker_list
        all_symbols = [t for t in raw_ticker_data["symbols"] if t['status'] in 'TRADING']
        spot_symbols = [s for s in all_symbols if s['isSpotTradingAllowed'] is True]

        output_symbols = []
        for symbol_dict in spot_symbols:
            output_symbols.append(symbol_dict['symbol'])

        return output_symbols

    def test_connection(self):
        request = requests.get(self.__host + "/api/v3/time")
        return request
