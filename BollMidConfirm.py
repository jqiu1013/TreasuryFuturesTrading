import datetime
import time
import pandas as pd
import numpy as np
import schedule
from twilio.rest import Client

from WindPy import *
w.start()
winddata = w.wsi("T.CFE", "open,high,low,close", datetime.now() - timedelta(days=10), datetime.now(), "BarSize=30;Fill=Previous", usedf=True)
winddata = pd.DataFrame(winddata[1])
Avg_window = 26
Std_window = 26

winddata['Boll_Mid'] = winddata['close'].rolling(Avg_window).mean()
winddata['Boll_Lower'] = winddata['Boll_Mid'] - 2*winddata['close'].rolling(Avg_window).std()
winddata['Boll_Upper'] = winddata['Boll_Mid'] + 2*winddata['close'].rolling(Avg_window).std()

# 强做多信号 [2,2,1]
stronglong_param1 = 2
stronglong_param2 = 2
stronglong_param3 = 1
# 弱做多信号 [3,2,1]
weeklong_param1 = 3
weeklong_param2 = 2
weeklong_param3 = 1
# 强做空信号 [2,2,2]
strongshort_param1 = 2
strongshort_param2 = 2
strongshort_param3 = 2
# 弱做空信号 [5,3,2]
weekshort_param1 = 5
weekshort_param2 = 3
weekshort_param3 = 2


# 强做多信号 [2,2,1]
if sum(winddata['close'][(-stronglong_param1-stronglong_param3):-stronglong_param3] < winddata['Boll_Mid'][(-stronglong_param1-stronglong_param3):-stronglong_param3]) >= stronglong_param2 and sum(winddata['open'][(-stronglong_param1-stronglong_param3):-stronglong_param3] < winddata['Boll_Mid'][(-stronglong_param1-stronglong_param3):-stronglong_param3]) >= stronglong_param2 and sum(winddata['close'][-stronglong_param3:] > winddata['Boll_Mid'][-stronglong_param3:]) == stronglong_param3 and sum(winddata['open'][-stronglong_param3:] > winddata['Boll_Mid'][-stronglong_param3:]) == stronglong_param3 and sum(winddata['open'][-stronglong_param3:] < winddata['close'][-stronglong_param3:]) == stronglong_param3:
    print("强做多信号信号发出")

# 弱做多信号 [3,2,1]
elif sum(winddata['close'][(-weeklong_param1-weeklong_param3):-weeklong_param3] < winddata['Boll_Mid'][(-weeklong_param1-weeklong_param3):-weeklong_param3]) >= weeklong_param2 and sum(winddata['open'][(-weeklong_param1-weeklong_param3):-weeklong_param3] < winddata['Boll_Mid'][(-weeklong_param1-weeklong_param3):-weeklong_param3]) >= weeklong_param2 and sum(winddata['close'][-weeklong_param3:] > winddata['Boll_Mid'][-weeklong_param3:]) == weeklong_param3 and sum(winddata['open'][-weeklong_param3:] > winddata['Boll_Mid'][-weeklong_param3:]) == weeklong_param3 and sum(winddata['open'][-weeklong_param3:] < winddata['close'][-weeklong_param3:]) == weeklong_param3 and winddata['open'][-weeklong_param3-1] < winddata['Boll_Mid'][-weeklong_param3-1] and winddata['close'][-weeklong_param3-1] > winddata['Boll_Mid'][-weeklong_param3-1]:
    print("弱做多信号信号发出")

# 强做空信号 [2,2,2]
elif sum(winddata['close'][(-strongshort_param1-strongshort_param3):-strongshort_param3] > winddata['Boll_Mid'][(-strongshort_param1-strongshort_param3):-strongshort_param3]) >= strongshort_param2 and sum(winddata['open'][(-strongshort_param1-strongshort_param3):-strongshort_param3] > winddata['Boll_Mid'][(-strongshort_param1-strongshort_param3):-strongshort_param3]) >= strongshort_param2 and sum(winddata['close'][-strongshort_param3:] < winddata['Boll_Mid'][-strongshort_param3:]) == strongshort_param3 and sum(winddata['open'][-strongshort_param3:] < winddata['Boll_Mid'][-strongshort_param3:]) == strongshort_param3 and sum(winddata['open'][-strongshort_param3:] > winddata['close'][-strongshort_param3:]) == strongshort_param3:
    print("强做空信号信号发出")

# 弱做空信号 [5,3,2]
elif sum(winddata['close'][(-weekshort_param1-weekshort_param3):-weekshort_param3] > winddata['Boll_Mid'][(-weekshort_param1-weekshort_param3):-weekshort_param3]) >= weekshort_param2 \
        and sum(winddata['open'][(-weekshort_param1-weekshort_param3):-weekshort_param3] > winddata['Boll_Mid'][(-weekshort_param1-weekshort_param3):-weekshort_param3]) >= weekshort_param2 \
        and sum(winddata['close'][-weekshort_param3:] < winddata['Boll_Mid'][-weekshort_param3:]) == weekshort_param3 \
        and sum(winddata['open'][-weekshort_param3:] < winddata['Boll_Mid'][-weekshort_param3:]) == weekshort_param3 \
        and sum(winddata['open'][-weekshort_param3:] > winddata['close'][-weekshort_param3:]) == weekshort_param3 \
        and winddata['open'][-weekshort_param3-1] > winddata['Boll_Mid'][-weekshort_param3-1] \
        and winddata['close'][-weekshort_param3-1] < winddata['Boll_Mid'][-weekshort_param3-1]:
    print("弱做空信号信号发出")
# 无信号
else:
    prev_ = '['
    for i in range(-7,0):
        if winddata['close'][i]>winddata['Boll_Upper'][i] and winddata['open'][i]>winddata['Boll_Upper'][i]:
            prev_ = prev_ + '1）UP上，'
        elif (winddata['close'][i]>winddata['Boll_Upper'][i] and winddata['open'][i]<winddata['Boll_Upper'][i]) \
                or (winddata['close'][i]<winddata['Boll_Upper'][i] and winddata['open'][i]>winddata['Boll_Upper'][i]):
            prev_ = prev_ + '2）UP压，'
        elif (winddata['close'][i]<winddata['Boll_Upper'][i] and winddata['open'][i]<winddata['Boll_Upper'][i]) \
                or (winddata['close'][i]>winddata['Boll_Mid'][i] and winddata['open'][i]>winddata['Boll_Mid'][i]):
            prev_ = prev_ + '3）Mid上，'
        elif (winddata['close'][i]>winddata['Boll_Mid'][i] and winddata['open'][i]<winddata['Boll_Mid'][i]) \
                or (winddata['close'][i]<winddata['Boll_Mid'][i] and winddata['open'][i]>winddata['Boll_Mid'][i]):
            prev_ = prev_ + '4）Mid压，'
        elif (winddata['close'][i]>winddata['Boll_Lower'][i] and winddata['open'][i]>winddata['Boll_Lower'][i]) \
                or (winddata['close'][i]<winddata['Boll_Mid'][i] and winddata['open'][i]<winddata['Boll_Mid'][i]):
            prev_ = prev_ + '5）Mid下，'
        elif (winddata['close'][i] > winddata['Boll_Lower'][i] and winddata['open'][i] < winddata['Boll_Lower'][i]) \
                or (winddata['close'][i] < winddata['Boll_Lower'][i] and winddata['open'][i] > winddata['Boll_Lower'][i]):
            prev_ = prev_ + '2）DN压，'
        elif winddata['close'][i]<winddata['Boll_Lower'][i] and winddata['open'][i]<winddata['Boll_Lower'][i]:
            prev_ = prev_ + '1）DN下，'
    prev_ = prev_ + ']'
    print(prev_)
