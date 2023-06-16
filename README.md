# RSI-Indicator

RSI indicator for any cryptocurrency

## Usage

Run `python3 main.py -h` for argument guide. There are 5 arguments that you can tune.

1. `--token-name` : list of token-pairs or a single token-pair from Binance e.g. `--token-name BTCUSDT` or `--token-name "BTCUSDT,ETHUSDT,XRPUSDT"`
2. `--interval` : a single interval of candle sticks to use that is available in free version of Binance e.g. `--interval 3m`. Available intervals are 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d
3. `--rsi-lower` : Lower RSI e.g. `--rsi-lower 15`
4. `--rsi-upper` : Upper RSI e.g. `--rsi-upper 85`
5. `--rsi-period` : Number of candles to use in the calculation of RSI `--rsi-period 6`

These default arguments will send signal if `RSI-6` on `3m` candles goes below 15 (time for shot trade) or above 85 (time for long trade).

```sh
    python3 main.py --token-name "BTCUSDT,ETHUSDT,XRPUSDT,MATICUSDT,SUIUSDT" --interval 5m
```

## Author

MasterHM / [@MasterHM-ml](https://github.com/MasterHM-ml/)
