import os
import datetime
import logging
import requests
import numpy as np
import pandas as pd
import argparse
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm


class RSI_Screener:
    def __init__(self,):
        
        self.log_directory=os.path.join('logs', f'{datetime.datetime.now().date()}')
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
        if len(os.listdir(self.log_directory))==0:
            self.log_file_title_index = 1
        else:
            _files=os.listdir(self.log_directory)
            _files.sort(key=lambda x: int(x.split('.')[0]))
            self.log_file_title_index = int(_files[-1].split('.')[0])+1
        logging.root.handlers=[]
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s.%(msecs)03d [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[
                                 logging.FileHandler(os.path.join(self.log_directory, f'{self.log_file_title_index}.txt'), 'w'),
                                 logging.StreamHandler()
                            ])
        self.log = logging.getLogger('TradeSignals')


        self.limit = 100
        self.raw_columns = ["Timestamp", "Open", "High", "Low", "Close", "Volume",  "Close time",	"Quote asset volume",	"Number of trades",	"Taker buy base asset volume",	"Taker buy quote asset volume",	"Ignore"]
        self.col_to_remove = ["Timestamp", "Volume",  "Close time",	"Quote asset volume",	"Number of trades",	"Taker buy base asset volume",	"Taker buy quote asset volume",	"Ignore"]

    #calculation of relative strength index
    def RSI(self, data, period):
        delta = data.diff().dropna()
        u = delta * 0
        d = u.copy()
        u[delta > 0] = delta[delta > 0]
        d[delta < 0] = -delta[delta < 0]
        u[u.index[period-1]] = np.mean( u[:period] ) #first value is sum of avg gains
        u = u.drop(u.index[:(period-1)])
        d[d.index[period-1]] = np.mean( d[:period] ) #first value is sum of avg losses
        d = d.drop(d.index[:(period-1)])
        rs = u.ewm(com=period-1, adjust=False).mean() / d.ewm(com=period-1, adjust=False).mean()
        return 100 - 100 / (1 + rs)


    def get_inference_data(self, token_name, interval):
        url = f"https://api.binance.com/api/v3/klines?symbol={token_name}&interval={interval}&limit={self.limit}"
        self.log.debug("getting data from %s" % url)
        response = requests.get(url=url)
        if response.status_code == 200:
            short_data = response.json()
            short_data = pd.DataFrame(short_data, columns=self.raw_columns)
            short_data.index = pd.to_datetime(short_data["Timestamp"], unit="ms", utc=True)
            short_data.drop(columns=self.col_to_remove, inplace=True)
            short_data = short_data.apply(pd.to_numeric)
            self.log.debug("Returning data frame with %s shape" % str(short_data.shape))
            return short_data



if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--token-name", type=str, default="BTCUSDT,",
                        help="A list of token name from Binance market e.g. 'BTCUSDT,ETHUSDT,BNBUSDT' or 'BTCUSDT'")
    parser.add_argument("--interval", type=str, default="3m", help="candle stick interval from "
                        " 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d,")
    parser.add_argument("--rsi-lower", type=int, default=15, help="Lower RSI indication, 15 by default")
    parser.add_argument("--rsi-upper", type=int, default=85, help="High RSI indication, 85 by default")
    parser.add_argument("--rsi-period", type=int, default=6, help="calculation on last this much candles, 6 by default")
    args = parser.parse_args()
    
    rsi_screener = RSI_Screener()
    with logging_redirect_tqdm():
        for token_name in tqdm(args.token_name.split(","), desc="Downloading data and scanning RSI in %d tokens" % len(args.token_name.split(",")), ncols=120):
            data = rsi_screener.get_inference_data(token_name, args.interval)
            data[f"rsi_{args.rsi_period}"] = rsi_screener.RSI(data.Close, args.rsi_period)
            extreme_rsi = data[f"rsi_{args.rsi_period}"].iloc[-1].item()
            if (extreme_rsi <= args.rsi_lower) or (extreme_rsi >= args.rsi_upper):
                transfer_data = {"TokenName": token_name,
                                "CandleStartTimeInUTC-00:00": data.iloc[-1].name,
                                "RSI": extreme_rsi}
                rsi_screener.log.info(transfer_data)


