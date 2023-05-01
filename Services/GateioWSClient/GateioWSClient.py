import asyncio
from gate_ws import Configuration, Connection, WebSocketResponse
from gate_ws.spot import SpotBookTickerChannel
import redis

from Core.Tools.Chains import BinanceChains
from Core.RESTClients.Gateio import GateioTickers

r = redis.Redis(host='redis', port=6379, db=0)


# define your callback function on message received
def print_message(conn: Connection, response: WebSocketResponse):
    if response.error:
        print('error returned: ', response.error)
        conn.close()
        return
    print(response.result)


def redis_compose(conn: Connection, response: WebSocketResponse):
    if response.error:
        print('error returned: ', response.error)
        conn.close()
        return
    data = response.result
    if "a" in data:
        data_msg = data['a'] + "," + data['A'] + "," + data['b'] + "," + data['B']
        r.hset("orderbook", f"{data['s']}", str(data_msg))


async def main(tickers_list):
    # initialize default connection, which connects to spot WebSocket V4
    # it is recommended to use one conn to initialize multiple channels
    conn = Connection(Configuration())

    # subscribe to any channel you are interested into, with the callback function
    # channel = SpotPublicTradeChannel(conn, print_message)
    channel = SpotBookTickerChannel(conn, redis_compose)

    channel.subscribe(tickers_list)

    # start the client
    await conn.run()


if __name__ == '__main__':
    r.flushall()
    test = GateioTickers()
    tickers = test.format_tickers_data()

    chains = BinanceChains(tickers)

    list_t = set()
    for chain in chains.chains_list:
        list_t.add(f'{chain["lsa"]}')
        list_t.add(f'{chain["rsa"]}')
        list_t.add(f'{chain["csa"]}')

    list_from_set = list(list_t)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(list_from_set))
    # loop.close()
