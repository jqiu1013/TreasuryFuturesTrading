# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 14:10:28 2020

@author: Juno Qiu
"""
# coding: UTF-8

import datetime 
import time
import pandas as pd
import numpy as np
from WindPy import *
w.start();
import schedule
from twilio.rest import Client

def MaxDrawdown(return_list):
    i = np.argmax((np.maximum.accumulate(return_list) - return_list))
    if i == 0:
        return 0
    j = np.argmax(return_list[:i])
    return return_list[j] - return_list[i], j, i


def MaxBounceBack(return_list):
    i = np.argmax((return_list - np.minimum.accumulate(return_list)))
    if i == 0:
        return 0
    j = np.argmin(return_list[:i])
    return return_list[i] - return_list[j], j, i


def send_message(messagebody):
    account_sid = "111"
    auth_token = "111"
    client = Client(account_sid,auth_token)
    # Jack
    message = client.messages.create(from_ = "+111",body=messagebody + " Signal Sent out Time:"+ datetime.now().strftime('%Y-%m-%d %H:%M:%S'),to="+111")
    print(message.sid)
    print("发送短信成功")
    # Juno
    message = client.messages.create(from_ = "+111",body=messagebody + " Signal Sent out Time:"+ datetime.now().strftime('%Y-%m-%d %H:%M:%S'),to="+111")
    print(message.sid)
    print("发送短信成功")
    
    

# if 1:
def SignalGenerator():

    maxdd_param = 0.20 #开仓
    maxbb_param = 0.20 #平仓
    lockprofit = 0.10
    stoploss = 0.20
    
    Stance = pd.read_csv('C:/Users/jqiu1013/Desktop/Python/TreasuryFuturesTrading/Stance_DD&BB_T_2ndDay.csv')
    Status = Stance['Status'].iloc[-1]

    Next_Available_Time = pd.to_datetime(Stance['Next_Available_Time'].iloc[-1])
    Current_Trade_Time = pd.to_datetime(Stance['Current_Trade_Time'].iloc[-1])
    Current_Trade_Price = Stance['Current_Trade_Price'].iloc[-1]
    Current_Trade_Time_EST = pd.to_datetime(Stance['Current_Trade_Time_EST'].iloc[-1])
    
    if Status == 0:
        print('---------- Current Status:' , Status,'; Current Time:', datetime.now(), '----------')
        # 5min Bar, 54/day
        winddata = w.wsi("t.cfe", "close", Current_Trade_Time_EST- timedelta(minutes = 1), datetime.today(),BarSize = "1")
        data = pd.DataFrame() 
        data['dt']=winddata.Times
        data['Close']=pd.DataFrame(winddata.Data).T
        data['Close'] = data['Close'].fillna(method='pad')
    
        maxdd, MaxDDIndex1, MaxDDIndex2 = MaxDrawdown(np.array(data['Close']))
        
        print('---------- Current MaxDD:' , np.round(maxdd,2),'; Last Price:', data['Close'].iloc[-1],'; Last Wind Time:', data['dt'].iloc[-1], '----------')
        
        currentday1500 = datetime.strptime(str(data['dt'].iloc[-1].date())+'15:00', '%Y-%m-%d%H:%M')
        currentday0930 = datetime.strptime(str(data['dt'].iloc[-1].date())+'09:30', '%Y-%m-%d%H:%M')
        
        if (maxdd >= maxdd_param) & (datetime.now() > Next_Available_Time) & (data['dt'].iloc[-1] <= currentday1500):
            
            if (data['dt'].iloc[-1] == currentday0930) & (data['dt'].iloc[MaxDDIndex2] < currentday0930):
                # 9：30的开仓信号是基于昨天的开仓信号信号，不开仓，只是Update Current_Trade_Time_EST
                Stance['Current_Trade_Time_EST'].iloc[-1] = currentday0930.strftime('%Y/%m/%d %H:%M')
                Stance.to_csv('Stance_DD&BB_T_2ndDay.csv',index=None)     
            else:
                # 开仓动作
                print('---------- Send out Short Signal; Current Time:', datetime.now(), '----------')
                send_message("-1 (Short), @ " + str(data['Close'].iloc[-1]))
                now = datetime.now()
                tomorrow =  now + timedelta(days=1)
                updated_Next_Available_Time = tomorrow.replace(tomorrow.year,tomorrow.month,tomorrow.day,9,0,0,0)
                NewStance = pd.DataFrame({'Status':[-1],'Type':'Open','Next_Available_Time':updated_Next_Available_Time.strftime('%Y-%m-%d %H:%M:%S'),'Current_Trade_Time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Current_Trade_Price':data['Close'].iloc[-1],'Current_Trade_Time_EST':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                Stance = Stance.append(NewStance)
                Stance.to_csv('Stance_DD&BB_T_2ndDay.csv',index=None)
                
            # --------------------------------------------------------------- #

    if Status == -1:
        print('---------- Current Status:' , Status,'; Current Time:', datetime.now(), '----------')

        winddata = w.wsi("t.cfe", "close", Current_Trade_Time_EST- timedelta(minutes = 1), datetime.today(),BarSize = "1")

        data = pd.DataFrame() 
        data['dt']=winddata.Times
        data['Close']=pd.DataFrame(winddata.Data).T
        data['Close'] = data['Close'].fillna(method='pad')
    
        maxbb, MaxBBIndex1, MaxBBIndex2 = MaxBounceBack(np.array(data['Close']))
        
        print('---------- Current MaxBB:' , np.round(maxbb,2),'; Last Price:', data['Close'].iloc[-1],'; Last Wind Time:', data['dt'].iloc[-1], '----------')
        
        currentday1500 = datetime.strptime(str(data['dt'].iloc[-1].date())+'15:00', '%Y-%m-%d%H:%M')
        currentday0930 = datetime.strptime(str(data['dt'].iloc[-1].date())+'09:30', '%Y-%m-%d%H:%M')
        
        if (maxbb >= maxbb_param) & (datetime.now() > Next_Available_Time):
            
            if (data['dt'].iloc[-1] == currentday0930) & (data['dt'].iloc[MaxBBIndex2] < currentday0930):
                
                if Current_Trade_Price <= data['Close'].iloc[-1]:
                    # 9：30的平仓信号是基于昨天的开仓信号信号，且没赚到钱，不平仓，只是Update Current_Trade_Time_EST
                    Stance['Current_Trade_Time_EST'].iloc[-1] = currentday0930.strftime('%Y/%m/%d %H:%M')
                    Stance.to_csv('Stance_DD&BB_T_2ndDay.csv',index=None)   
                else:
                    # 平仓动作
                    print('---------- Send out Prev+Profit CloseShort Signal; Current Time:', datetime.now(), '----------')
                    send_message("+1 (Close Short), @ "  + str(data['Close'].iloc[-1]))
                    now = datetime.now()
                    tomorrow =  now + timedelta(days=1)
                    updated_Next_Available_Time = tomorrow.replace(tomorrow.year,tomorrow.month,tomorrow.day,9,0,0,0)
                    NewStance = pd.DataFrame({'Status':[0],'Type':'Prev+Profit Close','Next_Available_Time':updated_Next_Available_Time.strftime('%Y-%m-%d %H:%M:%S'),'Current_Trade_Time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Current_Trade_Price':data['Close'].iloc[-1],'Current_Trade_Time_EST':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                    Stance = Stance.append(NewStance)
                    Stance.to_csv('Stance_DD&BB_T_2ndDay.csv',index=None)
                
            elif data['dt'].iloc[-1] <= currentday1500:
                # 平仓动作
                print('---------- Send out Normal CloseShort Signal; Current Time:', datetime.now(), '----------')
                send_message("+1 (Close Short), @ "  + str(data['Close'].iloc[-1])) 
                now = datetime.now()
                tomorrow =  now + timedelta(days=1)
                updated_Next_Available_Time = tomorrow.replace(tomorrow.year,tomorrow.month,tomorrow.day,9,0,0,0)
                NewStance = pd.DataFrame({'Status':[0],'Type':'Normal Close','Next_Available_Time':updated_Next_Available_Time.strftime('%Y-%m-%d %H:%M:%S'),'Current_Trade_Time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Current_Trade_Price':data['Close'].iloc[-1],'Current_Trade_Time_EST':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                Stance = Stance.append(NewStance)
                Stance.to_csv('Stance_DD&BB_T_2ndDay.csv',index=None)
                
                
            # --------------------------------------------------------------- #    
            
            
        elif (maxbb < maxbb_param) & (datetime.now() > Next_Available_Time):
            # 是否止盈
            if (data['dt'].iloc[-1] <= currentday1500) & (Current_Trade_Price - data['Close'].iloc[-1] >= lockprofit):
            # 止盈平仓动作
                print('---------- Send out LockProfit CloseShort Signal; Current Time:', datetime.now(), '----------')
                send_message("+1 (Lock Profit Close Short), @ " + str(data['Close'].iloc[-1]))
                now = datetime.now()
                tomorrow =  now + timedelta(days=1)
                updated_Next_Available_Time = tomorrow.replace(tomorrow.year,tomorrow.month,tomorrow.day,9,0,0,0)
                NewStance = pd.DataFrame({'Status':[0],'Type':'LockProfit Close','Next_Available_Time':updated_Next_Available_Time.strftime('%Y-%m-%d %H:%M:%S'),'Current_Trade_Time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Current_Trade_Price':data['Close'].iloc[-1],'Current_Trade_Time_EST':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                Stance = Stance.append(NewStance)
                Stance.to_csv('Stance_DD&BB_T_2ndDay.csv',index=None)
                
            elif (data['dt'].iloc[-1] <= currentday1500) & (data['Close'].iloc[-1] - Current_Trade_Price >= stoploss):
            # 止损平仓动作
                print('---------- Send out StopLoss CloseShort Signal; Current Time:', datetime.now(), '----------')
                send_message("+1 (Stop Loss Close Short), @ " + str(data['Close'].iloc[-1]))
                now = datetime.now()
                tomorrow =  now + timedelta(days=1)
                updated_Next_Available_Time = tomorrow.replace(tomorrow.year,tomorrow.month,tomorrow.day,9,0,0,0)
                NewStance = pd.DataFrame({'Status':[0],'Type':'StopLoss Close','Next_Available_Time':updated_Next_Available_Time.strftime('%Y-%m-%d %H:%M:%S'),'Current_Trade_Time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Current_Trade_Price':data['Close'].iloc[-1],'Current_Trade_Time_EST':datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                Stance = Stance.append(NewStance)
                Stance.to_csv('Stance_DD&BB_T_2ndDay.csv',index=None)
            

            

schedule.every(0.5).minutes.do(SignalGenerator)   
while True:
    # try:
    schedule.run_pending()
    # except TypeError:
        # print("TypeError")
    
