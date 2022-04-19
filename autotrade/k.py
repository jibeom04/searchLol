import pyupbit
import numpy as np


def get_ror(k):
    df = pyupbit.get_ohlcv("KRW-BTC", count=30)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0005
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror


for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    print("%.1f %f" % (k, ror))

# --------------------------------

# def get_ror(k):
#     df = pyupbit.get_ohlcv("KRW-BTC", count=30)
#     df['range'] = (df['high'] - df['low']) * k
#     df['target'] = df['open'] + df['range'].shift(1)

#     fee = 0.0005
#     df['ror'] = np.where(df['high'] > df['target'],
#                          df['close'] / df['target'] - fee,
#                          1)

#     ror = df['ror'].cumprod()[-2]
#     return ror

# def find_best_k():
#     ror_ = 0
#     for k in np.arange(0.1, 1.0, 0.1):
#         ror = get_ror(k)
#         if ror_ < ror:
#             ror_ = ror
#             result = k
#     print(result)

# find_best_k()

# ------------------------------------

# def find_best_k():
#     global best_k
#     ror_ = 0
#     for k in np.arange(0.1, 1.0, 0.1):
#         df = pyupbit.get_ohlcv("KRW-BTC", count=180)
#         df['range'] = (df['high'] - df['low']) * k
#         df['target'] = df['open'] + df['range'].shift(1)

#         fee = 0.0005
#         df['ror'] = np.where(df['high'] > df['target'],
#                             df['close'] / df['target'] - fee,
#                             1)

#         ror = df['ror'].cumprod()[-2]
#         if ror_ < ror:
#             ror_ = ror
#             result = k
#     best_k = result

# find_best_k()
# print(best_k)