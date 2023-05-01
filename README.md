## Crypto tools

Состоит из:
1. Калькулятора прибыльности 3х сторонних коридоров
2. Калькулятора прибыльности спредов
3. Хранилища Redis

*WS клиенты для бирж не содержатся в репозитории.\
**UI не содержится в репозитории.

---

### Подготовка проекта

1. Клонируйте проект

В корневой папке проекта:

2. Создайте  redis.conf с необходимыми настройками, установите requirepass

3. Создайте  .env, укажиет параметр REDIS_PASSWORD = 'your_pass'
4. Реализуйте ws клиента для целевой биржи
5. При необходимости внесите изменение в docker-compose.yml
6. В интерфейсе командной строки выполните следующую команду: docker-compose up

---
Требования для ws клиента:
- Для бинанса запись данных из symbol@bookTicker
- В таблицу редиса -n 0
- В формате: 

r.hset("orderbook", "symbol", data)\
data = "ASK_PRICE, ASK_VOL, BID_PRICE, BID_VOL"

Пример данных:\
hset "orderbook" "BTCUSDT" "28630.94000000,1.01625000,28000.94000000,0.47625000"\
hset "orderbook" "ETHBTC" "0.06557300,33.49370000,0.06557200,32.26810000"\
hset "orderbook" "ETHUSDT" "1645.24000000,3.51250000,1600.23000000,67.88360000"

r.hset("orderbook", "BTCUSDT", "28630.94000000,1.01625000,28000.94000000,0.47625000")\
r.hset("orderbook", "ETHBTC", "0.06557300,33.49370000,0.06557200,32.26810000")\
r.hset("orderbook", "ETHUSDT", "1645.24000000,3.51250000,1600.23000000,67.88360000")

---

## Описание

Данные по доступным рынкам получаются в момент запуска из REST api биржи.\
Доступный рынок на Бинанс имеет статус TRADING и isSpotTradingAllowed

---
### SpreadCalculator.py 
### Калькулятор прибыльности спредов


С учетом комисии и округления считает приыльность лимитной покупки по best bid и лимитной продажи по best ask.\
Значение > 100 == профит в %\
Результат записывается в редис -n 2
Подходит для мониторинга активности и всяких штук =)
---
### 3WayCalculator.py
#### Калькулятор прибыльности 3х этапных цепочек обмена

Делался для анализа возможностей торговли внутри биржи (ман/авто)

Пример цепочки:
1. USDT -> BTC
2. BTC -> ETH
3. ETH -> USDT

Варианты расчета:\
LR: USDT -> BTC; BTC -> ETH; ETH -> USDT

RL: USDT-> ETH; ETH -> BTC; BTC -> USDT

Значение > 100 == профит в %\
Учитывает комиссии и округление объемов\
Результат записывается в редис -n 1


