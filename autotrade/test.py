import pyupbit
import schedule
import requests
from datetime import date, timedelta, datetime
import numpy as np
from fbprophet import Prophet

myToken = "xoxb-3121161129187-3123495414420-9fTtHcBUPURqtZt49YReRrWn"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

# df = pyupbit.get_ohlcv("KRW-BTC", count = 1)
# df['range'] = (df['high'] - df['low']) * 0.4
# df['target'] = df['open'] + df['range'].shift(1)

# fee = 0.0005
# df['ror'] = np.where(df['high'] > df['target'],
#                      df['close'] / df['target'] - fee,
#                      1)

# df['hpr'] = df['ror'].cumprod()
# df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
# print("MDD(%): ", df['dd'].max())
# df.to_excel("dd.xlsx")

# def file_reset():
#     f1 = open("종가.txt", 'w')
#     f1.close()
#     f2 = open("예측종가.txt", 'w')
#     f2.close()
# file_reset()

def end_price():
    now_hour = datetime.now().hour
    today = date.today()
    yesterday = date.today() - timedelta(1)
    df = pyupbit.get_ohlcv("KRW-BTC", count = 1)
    f = open("종가.txt", 'a')
    f.write(f"{ df['close'] }\n\n")
    f.close()
    if 0 <= now_hour < 9:
        post_message(myToken,"#종가", f"{ df['close'] }" )
    if 9 <= now_hour < 24:
        post_message(myToken,"#종가", f"{ df['close'] }" )
    print(datetime.now(), "write")
end_price()
schedule.every().day.at("09:01").do(end_price)

predicted_close_price = 0
def predict_price1(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    now_hour = datetime.now().hour
    today = date.today()
    tomorow = date.today() + timedelta(1)
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
    f = open("예측종가(1일).txt", 'a')
    if 0 <= now_hour < 9:
        f.write(f"{ today.strftime('%y-%m-%d') } 예측종가: { predicted_close_price} (at { datetime.now() } )\n\n")
        post_message(myToken,"#종가예측_1일", f"{ today.strftime('%y-%m-%d') } 예측종가: { predicted_close_price} (at { datetime.now() } )" )
        print(datetime.now(), "write 예측(1일)")
    if 9 <= now_hour < 24:
        f.write(f"{ tomorow.strftime('%y-%m-%d') } 예측종가: { predicted_close_price} (at { datetime.now() } )\n\n")
        post_message(myToken,"#종가예측_1일", f"{ tomorow.strftime('%y-%m-%d') } 예측종가: { predicted_close_price} (at { datetime.now() } )" )
        print(datetime.now(), "write 예측(1일)")
    f.close()
predict_price1("KRW-BTC")
schedule.every().hour.do(lambda: predict_price1("KRW-BTC"))


predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    now_hour = datetime.now().hour
    today = date.today()
    tomorow = date.today() + timedelta(1)
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=7)
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
    f = open("예측종가.txt", 'a')
    if 0 <= now_hour < 9:
        f.write(f"{ today.strftime('%y-%m-%d') } 예측종가: { predicted_close_price} (at { datetime.now() } )\n\n")
        post_message(myToken,"#종가예측", f"{ today.strftime('%y-%m-%d') } 예측종가: { predicted_close_price} (at { datetime.now() } )" )
        print(datetime.now(), "write 예측")
    if 9 <= now_hour < 24:
        f.write(f"{ tomorow.strftime('%y-%m-%d') } 예측종가: { predicted_close_price} (at { datetime.now() } )\n\n")
        post_message(myToken,"#종가예측", f"{ tomorow.strftime('%y-%m-%d') } 예측종가: { predicted_close_price} (at { datetime.now() } )" )
        print(datetime.now(), "write 예측")
    f.close()
predict_price("KRW-BTC")
schedule.every().hour.do(lambda: predict_price("KRW-BTC"))


while True:
    schedule.run_pending()