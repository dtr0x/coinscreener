import pandas as pd
import numpy as np
import requests, datetime, time, os, argparse
from coingecko_pro_api import CoinGeckoAPI

pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.float_format', lambda x: '%.6f' % x)

cg = CoinGeckoAPI()

def request_wrapper(func, kwargs={}):
    try:
        return func(**kwargs)
    except requests.exceptions.HTTPError:
        print('Request error. Retrying in 90 seconds...')
        time.sleep(90)
        return request_wrapper(func, kwargs)

# get unique list items (preserve order)
def unique_list(my_list):
    return pd.Series(my_list).unique().tolist()

# Get number of days from date
def get_ndays(year, month, day):
    d1 = datetime.date(year, month, day)
    d2 = datetime.date.today()
    d = (d2-d1).days
    return d

# Get number of data points per asset
def _data_len_days(price_series):
    return len(price_series.dropna())
def data_len_days(price_data):
    hours = price_data.agg(_data_len_days)
    return (hours/24).astype(int)

# Compute drawdown from price series
def _drawdown(price_series):
    p = price_series.dropna()
    return (max(p) - p.tolist()[-1])/max(p) * 100
def drawdown(price_data):
    return price_data.agg(_drawdown)

# Get drawup from price series
def _drawup(price_series):
    p = price_series.dropna()
    return (p.tolist()[-1] - min(p))/min(p) * 100
def drawup(price_data):
    return price_data.agg(_drawup)

def _max_drawdown(price_series):
    p = np.array(price_series.dropna())
    peak = min(p)
    dd = np.empty(len(p))
    mdd = 0
    for i in range(1, len(p)):
        if p[i] > peak:
            peak = p[i]
        dd[i] = (peak - p[i])/peak * 100
        if dd[i] > mdd:
            mdd = dd[i]
    return mdd
def max_drawdown(price_data):
    return price_data.agg(_max_drawdown)

def _max_drawup(price_series):
    p = np.array(price_series.dropna())
    trough = max(p)
    du = np.empty(len(p))
    mdu = 0
    for i in range(1, len(p)):
        if p[i] < trough:
            trough = p[i]
        du[i] = (p[i] - trough)/trough * 100
        if du[i] > mdu:
            mdu = du[i]
    return mdu
def max_drawup(price_data):
    return price_data.agg(_max_drawup)

# get 4hr ema
def ema200h4(price_data):
    n = len(price_data)
    idx = np.arange((n-1)%4, n, 4)
    prices4hr = price_data.loc[idx]
    return prices4hr.ewm(span=200, adjust=False).mean().iloc[-1]


# get all unique coin ids on the exchange
def get_exchange_coin_ids(exchange_id):
    coin_ids = []
    i = 1
    while(True):
        data = request_wrapper(cg.get_exchanges_tickers_by_id, {'id': exchange_id, 'page': i})['tickers']
        if len(data) == 0:
            break
        else:
            coin_ids += [x['coin_id'] for x in data]
            targets = [k for k in data if 'target_coin_id' in k.keys()]
            if len(targets) > 0:
                coin_ids += [x['target_coin_id'] for x in targets]
            i += 1
    # drop duplicates if any
    return list(set(coin_ids))


# get data for specific coin id
def get_coin_data(coin_id):
    try:
        coin_data = request_wrapper(cg.get_coin_by_id, {'id': coin_id})
        return coin_data
    except ValueError:
        print('Could not find coin with id {}.'.format(coin_id))


# get coin exchange with max volume
def get_max_vol_exchange(coin_data):
    tickers = [(t['market']['identifier'], t['converted_volume']['usd']) for t in coin_data['tickers']]
    tickers = pd.DataFrame(tickers, columns=['exchange_id', 'volume'])
    max_idx = tickers.volume.idxmax()
    return tuple(tickers.loc[max_idx].values)


# other get functions for coin data
def get_name(coin_data):
    return coin_data['name']

def get_symbol(coin_data):
    return coin_data['symbol'].upper()

def get_price(coin_data, currency='usd'):
    return coin_data['market_data']['current_price'][currency]

def get_marketcap(coin_data):
    return coin_data['market_data']['market_cap']['usd']


# return a DataFrame with price history for all coin ids over the given period
def get_price_history(coin_ids, days, interval='daily', currency='usd'):
    price_data = {}

    for coin in coin_ids:
        print('getting data for {}...'.format(coin))
        x = request_wrapper(cg.get_coin_market_chart_by_id, {'id': coin, 'vs_currency': currency, 'days': days, 'interval': interval})
        prices = [p[1] for p in x['prices']]
        price_data[coin] = prices

    max_price_len = max([len(price_data[k]) for k in price_data.keys()])
    # front pad with nans if not enough data
    for k in price_data.keys():
        if len(price_data[k]) < max_price_len:
                price_data[k] = [np.nan] * (max_price_len - len(price_data[k])) + price_data[k]

    return pd.DataFrame(price_data)
