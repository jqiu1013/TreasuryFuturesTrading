# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 14:10:28 2020

@author: Juno Qiu
"""
# coding: UTF-8
# 说明：
# last 30 分钟级趋势交易
import datetime
import time
import pandas as pd
import numpy as np
from WindPy import *

w.start()
import schedule
from twilio.rest import Client


def MaxDrawdown(return_list):
    i = np.argmax((np.maximum.accumulate(return_list) - return_list))
    if i == 0:
        return 0
    j = np.argmax(return_list[:i])
    return return_list[j] - return_list[i]


def MaxBounceBack(return_list):
    i = np.argmax((return_list - np.minimum.accumulate(return_list)))
    if i == 0:
        return 0
    j = np.argmin(return_list[:i])
    return return_list[i] - return_list[j]


def send_message(messagebody):
    account_sid = "AC365fdae5090e1e035b8f038b144176f5"
    auth_token = "6022cc537b66a6a2548aaea197ce2a26"
    client = Client(account_sid, auth_token)
    # Jack
    message = client.messages.create(from_="+12566676073",
                                     body=messagebody + " Signal Sent out Time:" + datetime.now().strftime(
                                         '%Y-%m-%d %H:%M:%S'), to="+8613581804397")
    print(message.sid)
    print("发送短信成功")
    # Juno
    message = client.messages.create(from_="+12566676073",
                                     body=messagebody + " Signal Sent out Time:" + datetime.now().strftime(
                                         '%Y-%m-%d %H:%M:%S'), to="+8615650791570")
    print(message.sid)
    print("发送短信成功")


# if 1:
def SignalGenerator():
    maxdd_param = 0.25  # 开仓
    maxbb_param = 0.15  # 平仓

    lookback_param = 5  # lookback days

    Stance = pd.read_csv('Stance_DD&BB_T.csv')

    Status = Stance['Status'].iloc[-1]
    Next_Available_Time = pd.to_datetime(Stance['Next_Available_Time'].iloc[-1])
    Current_Trade_Time = pd.to_datetime(Stance['Current_Trade_Time'].iloc[-1])

    if Status == 0:
        print('---------- Current Status:', Status, '; Current Time:', datetime.now(), '----------')
        # 5min Bar, 54/day

        winddata = w.wsi("t.cfe", "close", Current_Trade_Time - timedelta(minutes=10), datetime.today(), BarSize="1")
        data = pd.DataFrame()
        data['dt'] = winddata.Times
        data['Close'] = pd.DataFrame(winddata.Data).T
        data['Close'] = data['Close'].fillna(method='pad')

        maxdd = MaxDrawdown(np.array(data['Close']))

        print('---------- Current MaxDD:', np.round(maxdd, 2), '; Last Price:', data['Close'].iloc[-1],
              '; Last Wind Time:', data['dt'].iloc[-1], '----------')

        if (maxdd >= maxdd_param) & (datetime.now() > Next_Available_Time):
            # 开仓动作
            print('---------- Send out Short Signal; Current Time:', datetime.now(), '----------')
            send_message("-1 (Short), ")
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            updated_Next_Available_Time = tomorrow.replace(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0, 0)
            NewStance = pd.DataFrame(
                {'Status': [-1], 'Next_Available_Time': updated_Next_Available_Time.strftime('%Y-%m-%d %H:%M:%S'),
                 'Current_Trade_Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            Stance = Stance.append(NewStance)
            Stance.to_csv('Stance_DD&BB_T.csv', index=None)

    if Status == -1:
        print('---------- Current Status:', Status, '; Current Time:', datetime.now(), '----------')

        winddata = w.wsi("t.cfe", "close", Current_Trade_Time - timedelta(0.02), datetime.today(), BarSize="1")

        data = pd.DataFrame()
        data['dt'] = winddata.Times
        data['Close'] = pd.DataFrame(winddata.Data).T
        data['Close'] = data['Close'].fillna(method='pad')

        maxbb = MaxBounceBack(np.array(data['Close']))
        print('---------- Current MaxBB:', np.round(maxbb, 2), '; Last Price:', data['Close'].iloc[-1],
              '; Last Wind Time:', data['dt'].iloc[-1], '----------')

        if (maxbb >= maxbb_param) & (datetime.now() > Next_Available_Time):
            # 平仓动作
            print('---------- Send out CloseShort Signal; Current Time:', datetime.now(), '----------')
            send_message("+1 (Close Short), ")
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            updated_Next_Available_Time = tomorrow.replace(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0, 0)
            NewStance = pd.DataFrame(
                {'Status': [0], 'Next_Available_Time': updated_Next_Available_Time.strftime('%Y-%m-%d %H:%M:%S'),
                 'Current_Trade_Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            Stance = Stance.append(NewStance)
            Stance.to_csv('Stance_DD&BB_T.csv', index=None)


schedule.every(0.1).minutes.do(SignalGenerator)
while True:
    try:
        schedule.run_pending()
    except TypeError:
        print("TypeError")
