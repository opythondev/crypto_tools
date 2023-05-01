class BinanceChains:
    __tickers_list = []
    __main_assets_list = ['USDT', 'BUSD', 'AUD', 'BIDR', 'BRL', 'EUR', 'GBP', 'RUB', 'TRY',
                          'TUSD', 'USDC', 'DAI', 'IDRT', 'UAH', 'NGN', 'VAI', 'USDP']

    __main_quote_assets = []
    __alt_quote_assets = []

    chains_list = []
    __list_of_chains_lists = []

    def __init__(self, tickers_list):
        self.__tickers_list = tickers_list
        self.__sort_tickers(self.__tickers_list)
        self.__generate_chains()

    def __sort_tickers(self, all_tickers):
        for ticker in all_tickers:
            if ticker['quoteAsset'] in self.__main_assets_list:
                self.__main_quote_assets.append(ticker)
            else:
                self.__alt_quote_assets.append(ticker)

    def __generate_chains(self):
        for alt_asset in self.__alt_quote_assets:
            lsa = alt_asset['baseAsset']
            rsa = alt_asset['quoteAsset']

            lsa_main_assets = []

            for main_asset in self.__main_quote_assets:
                if main_asset['baseAsset'] == lsa:
                    lsa_main_assets.append(main_asset)

            for main_asset in self.__main_quote_assets:
                if main_asset['baseAsset'] == rsa:
                    for lsa_main_asset in lsa_main_assets:
                        if lsa_main_asset['quoteAsset'] == main_asset['quoteAsset']:
                            left_side_asset = lsa_main_asset['symbol']
                            lsa_vol_decimals = lsa_main_asset['volume_decimal']

                            convert_asset = alt_asset['symbol']
                            convert_vol_decimals = alt_asset['volume_decimal']

                            right_side_asset = main_asset['symbol']
                            rsa_vol_decimals = main_asset['volume_decimal']
                            key = lsa_main_asset['symbol'] + ":" + alt_asset['symbol'] + ":" + right_side_asset

                            self.chains_list.append({
                                "key": key,
                                "lsa": left_side_asset,
                                "csa": convert_asset,
                                "rsa": right_side_asset,
                                "lsa_vol_decimals": lsa_vol_decimals,
                                "convert_vol_decimals": convert_vol_decimals,
                                "rsa_vol_decimals": rsa_vol_decimals
                            })

    def split_chains_list(self, chains_list, split_by_n):
        # How many elements each
        # list should have
        n = split_by_n

        # using list comprehension
        x = [chains_list[i:i + n] for i in range(0, len(chains_list), n)]
        return x
