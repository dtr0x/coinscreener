# coinscreener
An application to retrieve and filter asset performance metrics from CoinGecko.

**Note**: This code is configured to use the CoinGecko pro API (requiring a purchased key) for faster requests. However, the free API can also be used by removing the class override in `coingecko_pro_api.py`. If you have a pro API key, you must add it in the `CG_API_KEY` field in this file. See https://www.coingecko.com/en/api/documentation for more information.

### Requirements
```
- pandas
- numpy
- requests
- pycoingecko (https://github.com/man-c/pycoingecko)
```

### Usage
The main entry point is `get_coins.py`, which is ran from the terminal to get asset performance metrics for a given exchange over a selected period. for example,
```
> python get_coins.py -exchanges=uniswap -days=30 -currency=usd
```
will pull 30 days of price data for assets with their primary exchange being uniswap, and the reported values will be in a USD denominated quote currency. It is possible to pass multiple exchanges by separating their IDs with commas.

A dataframe is then produced and saved as csv with the following fields:
* ```drawdown``` the percentage change from the highest point over the given period.
* ```drawup``` the percentage change from the lowest point over the given period.
* ```mdd```  (max drawdown) the maximum peak-to-trough percentage change over the given period.
* ```mdu``` (max drawup) the maximum trough-to-peak percentage change over the given period.
* ```ema``` the exponential moving average of the last 200 4-hour periods.
* ```ema_delta``` the percentage difference of ```ema``` and current price. Can indicate momentum if this value is positive.
* ```n_days``` the number of days for which the asset has available data.
