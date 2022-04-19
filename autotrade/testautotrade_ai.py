# IMPORT ---------------------------------------------------------------------------------------------------------------------------------------

import time
import pyupbit
import datetime
import requests
import schedule
from fbprophet import Prophet
import numpy as np

# SET ------------------------------------------------------------------------------------------------------------------------------------------

# access = "your-access"
# secret = "your-secret"
myToken = "xoxb-3121161129187-3123495414420-9fTtHcBUPURqtZt49YReRrWn"

# FUNCTION ------------------------------------------------------------------------------------------------------------------------------------

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
predict_price("KRW-BTC")
schedule.every().hour.do(lambda: predict_price("KRW-BTC"))

def start_price():
    """시작금액 설정"""
    balances = get_balance("KRW-BTC")
    if balances >= 50000:
        return 50000
    else:
        return balances

def find_k():
    """돌파구간 설정 변수 k 구하기"""
    global best_k
    ror_ = 0
    for k in np.arange(0.1, 1.0, 0.1):
        df = pyupbit.get_ohlcv("KRW-BTC", count=7)
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        fee = 0.0005
        df['ror'] = np.where(df['high'] > df['target'],
                            df['close'] / df['target'] - fee,
                            1)

        ror = df['ror'].cumprod()[-2]
        if ror_ < ror:
            ror_ = ror
            result = k
    best_k = result
schedule.every().day.at("08:59").do(find_k)

def profit_and_loss(t):
    """손익계산"""
    if t == 0:
        start_balances = get_balance("KRW-BTC")
    if t == 1:
        end_balances = get_balance("KRW-BTC")
    if t == 2:
        post_message(myToken,"#자동투자", datetime.datetime.now().date() + " 손익 : " + str(start_balances - end_balances))
schedule.every().day.at("09:00").do(profit_and_loss(0))
schedule.every().day.at("08:59:30").do(profit_and_loss(1))
schedule.every().day.at("08:59:50").do(profit_and_loss(2))


# MAIN ----------------------------------------------------------------------------------------------------------------------------------------

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#자동투자ai", "autotrade start")

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(minutes=1):
            target_price = get_target_price("KRW-BTC", best_k)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and current_price < predicted_close_price:
                krw = start_price()
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    post_message(myToken,"#자동투자ai", "BTC buy : " +str(buy_result))
        else:
            btc = get_balance("BTC")
            if btc > 0.0001:
                sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)
                post_message(myToken,"#자동투자ai", "BTC buy : " +str(sell_result))

        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#자동투자ai", e)
        time.sleep(1)