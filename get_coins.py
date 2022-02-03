from util import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-exchanges', type=str, required=True)
    parser.add_argument('-days', type=int, required=True)
    parser.add_argument('-currency', type=str, required=True)
    args = parser.parse_args()

    exchange_ids = args.exchanges.split(',')
    days = args.days
    currency = args.currency

    now = datetime.datetime.now()
    y = now.year
    m = now.month
    d = now.day

    filename = '{}-{}-{}__{}-{}-{}.csv'.format('-'.join(exchange_ids), currency, days, y, m, d)

    coin_ids = []

    for exchg in exchange_ids:
        coin_ids += get_exchange_coin_ids(exchg)

    coin_ids = unique_list(coin_ids)

    coins = []

    for c in coin_ids:
        coin_data = get_coin_data(c)
        if coin_data:
            max_vol_exchange = get_max_vol_exchange(coin_data)
            if max_vol_exchange[0] in exchange_ids:
                name = get_name(coin_data)
                symbol = get_symbol(coin_data)
                price = get_price(coin_data, currency)
                mc = get_marketcap(coin_data)
                vol24hr = max_vol_exchange[1]
                if mc > 0:
                    vol_mc_ratio = vol24hr/mc
                else:
                    vol_mc_ratio = 0

                coins.append((name, symbol, c, price, mc, vol24hr, vol_mc_ratio))


    df = pd.DataFrame(coins, columns=['name', 'symbol', 'id', 'price', 'marketcap', 'vol24hr', 'vol_mc_ratio'])

    coins = df['id']

    price_data = get_price_history(coins, days, 'hourly', currency)

    df['drawdown'] = drawdown(price_data).values
    df['drawup'] = drawup(price_data).values
    df['mdd'] = max_drawdown(price_data).values
    df['mdu'] = max_drawup(price_data).values
    df['ema'] = ema200h4(price_data).values
    df['ema_delta'] = (df['price'] - df['ema'])/df['ema'] * 100
    df['n_days'] = data_len_days(price_data).values

    df.to_csv('data/' + filename, index=False)
