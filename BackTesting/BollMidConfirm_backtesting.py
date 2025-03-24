import datetime
import time
import pandas as pd
import numpy as np
import schedule
from twilio.rest import Client

Avg_window = 26
Std_window = 26
hisdata = pd.read_excel('./T_30MinutesData_Bar.xlsx',sheet_name='Sheet1',index_col=0)
hisdata['Boll_Mid'] = hisdata['close'].rolling(Avg_window).mean()
hisdata['Boll_Lower'] = hisdata['Boll_Mid'] - 2*hisdata['close'].rolling(Avg_window).std()
hisdata['Boll_Upper'] = hisdata['Boll_Mid'] + 2*hisdata['close'].rolling(Avg_window).std()
hisdata['next_2_days_high'] = 0
hisdata['next_2_days_low'] = 0
hisdata['next_2_days_close'] = 0
### uniquedates = np.unique(hisdata.index.date)
### pd.date_range(hisdata.index[20],periods=20)
for i in range(0,len(hisdata)-21):
    hisdata.loc[hisdata.index[i],'next_2_days_high'] = hisdata.loc[hisdata.index[i+1:i+21],'high'].max()
    hisdata.loc[hisdata.index[i], 'next_2_days_low'] = hisdata.loc[hisdata.index[i + 1:i + 21], 'low'].min()
    hisdata.loc[hisdata.index[i], 'next_2_days_close'] = hisdata.loc[hisdata.index[i+21], 'close']

static_set = pd.DataFrame()
year_static_set = pd.DataFrame()
test_num=1

########################################################################################################################
#######################################  1. 强做多信号 -- 完全向上突破  ####################################################
########################################################################################################################

# 完全向上/向下突破信号
Before_X_strong = [[2,2], [3,3],[4,4]] #[[2,2]]
After_Y = [1,2] #[1]
lockprofit = [0.10,0.20,0.30] #[0.10]
stoploss = [0.10,0.20,0.30] #[0.10]

for ll in lockprofit:
    for ss in stoploss:
        for xx in Before_X_strong:
            xx_before = xx[0]
            xx_atleast_before = xx[1]
            for yy in After_Y:
                hisdata['position'] = np.nan
                hisdata['pnl'] = np.nan

                print([ll,' ',ss,' ',xx,' ',yy])

                for i in range(7,len(hisdata)-2):

                    # 强做多信号 -- 完全向上突破
                    if sum(hisdata['close'][(i-xx_before-yy):i-yy] < hisdata['Boll_Mid'][(i-xx_before-yy):i-yy]) >= xx_atleast_before \
                            and sum(hisdata['open'][(i-xx_before-yy):i-yy] < hisdata['Boll_Mid'][(i-xx_before-yy):i-yy]) >= xx_atleast_before \
                            and sum(hisdata['close'][i-yy:i] > hisdata['Boll_Mid'][i-yy:i]) == yy \
                            and sum(hisdata['open'][i-yy:i] > hisdata['Boll_Mid'][i-yy:i]) == yy \
                            and sum(hisdata['open'][i-yy:i] < hisdata['close'][i-yy:i]) == yy:

                        hisdata.loc[hisdata.index[i],'position'] = 1
                        if hisdata.loc[hisdata.index[i],'next_2_days_high'] >= hisdata.loc[hisdata.index[i], 'close'] + ll:
                            hisdata.loc[hisdata.index[i], 'pnl'] = ll
                        elif hisdata.loc[hisdata.index[i],'next_2_days_low'] <= hisdata.loc[hisdata.index[i], 'close'] - ss:
                            hisdata.loc[hisdata.index[i], 'pnl'] = -ss
                        else:
                            hisdata.loc[hisdata.index[i], 'pnl'] = hisdata.loc[hisdata.index[i], 'next_2_days_close'] - hisdata.loc[hisdata.index[i], 'close']

                statics = pd.DataFrame({'Type':'Strong_Long','Before_X': xx_before, 'Before_X_Atleast': xx_atleast_before, 'After_Y': yy, \
                                        'lockprofit': ll, 'stoploss': ss, 'totalpnl': hisdata.pnl.sum(), \
                                        'count': len(hisdata) - sum(hisdata.pnl.isna()), 'avgpnl': hisdata.pnl.mean(), \
                                        'winratio': sum(hisdata.pnl > 0) / (len(hisdata) - sum(hisdata.pnl.isna()))}, index=[test_num])
                static_set = static_set.append(statics)
                test_num += 1

########################################################################################################################
#######################################  2. 强做空信号 -- 完全向下突破  ####################################################
########################################################################################################################

for ll in lockprofit:
    for ss in stoploss:
        for xx in Before_X_strong:
            xx_before = xx[0]
            xx_atleast_before = xx[1]
            for yy in After_Y:
                hisdata['position'] = np.nan
                hisdata['pnl'] = np.nan

                print([ll, ' ', ss, ' ', xx, ' ', yy])

                for i in range(7, len(hisdata) - 2):

                    # 强做空信号 -- 完全向下突破
                    if sum(hisdata['close'][(i-xx_before-yy):i-yy] > hisdata['Boll_Mid'][(i-xx_before-yy):i-yy]) >= xx_atleast_before \
                            and sum(hisdata['open'][(i-xx_before-yy):i-yy] > hisdata['Boll_Mid'][(i-xx_before-yy):i-yy]) >= xx_atleast_before \
                            and sum(hisdata['close'][i-yy:i] < hisdata['Boll_Mid'][i-yy:i]) == yy \
                            and sum(hisdata['open'][i-yy:i] < hisdata['Boll_Mid'][i-yy:i]) == yy \
                            and sum(hisdata['open'][i-yy:i] > hisdata['close'][i-yy:i]) == yy:

                        hisdata.loc[hisdata.index[i],'position'] = -1
                        if hisdata.loc[hisdata.index[i],'next_2_days_high'] >= hisdata.loc[hisdata.index[i], 'close'] + ss:
                            hisdata.loc[hisdata.index[i], 'pnl'] = -ss
                        elif hisdata.loc[hisdata.index[i],'next_2_days_low'] <= hisdata.loc[hisdata.index[i], 'close'] - ll:
                            hisdata.loc[hisdata.index[i], 'pnl'] = ll
                        else:
                            hisdata.loc[hisdata.index[i], 'pnl'] = hisdata.loc[hisdata.index[i], 'close'] - hisdata.loc[hisdata.index[i], 'next_2_days_close']

                statics = pd.DataFrame({'Type':'Strong_Short','Before_X': xx_before, 'Before_X_Atleast': xx_atleast_before, 'After_Y': yy, \
                                        'lockprofit': ll, 'stoploss': ss, 'totalpnl': hisdata.pnl.sum(), \
                                        'count': len(hisdata) - sum(hisdata.pnl.isna()), 'avgpnl': hisdata.pnl.mean(), \
                                        'winratio': sum(hisdata.pnl > 0) / (len(hisdata) - sum(hisdata.pnl.isna()))}, index=[test_num])
                static_set = static_set.append(statics)
                test_num += 1

########################################################################################################################
#############################################  3. 压中线向上突破  #########################################################
########################################################################################################################

# 压中线向上/向下突破
Before_X_week = [[2,1],[3,2],[4,3],[5,3],[5,4],[6,4],[8,6],[10,8]] #[[2,1]]
After_Y = [1,2] #[1]
lockprofit = [0.10,0.20,0.30] #[0.1]
stoploss = [0.10,0.20,0.30] #[0.1]

for ll in lockprofit:
    for ss in stoploss:
        for xx in Before_X_week:
            xx_before = xx[0]
            xx_atleast_before = xx[1]
            for yy in After_Y:
                hisdata['position'] = np.nan
                hisdata['pnl'] = np.nan

                print([ll, ' ', ss, ' ', xx, ' ', yy])

                for i in range(7, len(hisdata) - 2):

                    # 弱做多信号 -- 压中线向上突破
                    if sum(hisdata['close'][(i - xx_before - yy):i - yy] < hisdata['Boll_Mid'][(i - xx_before - yy):i - yy]) >= xx_atleast_before \
                            and sum(hisdata['open'][(i - xx_before - yy):i - yy] < hisdata['Boll_Mid'][(i - xx_before - yy):i - yy]) >= xx_atleast_before \
                            and sum(hisdata['close'][i - yy:i] > hisdata['Boll_Mid'][i - yy:i]) == yy \
                            and sum(hisdata['open'][i - yy:i] > hisdata['Boll_Mid'][i - yy:i]) == yy \
                            and sum(hisdata['open'][i - yy:i] < hisdata['close'][i - yy:i]) == yy \
                            and hisdata['open'][i - yy - 1] < hisdata['Boll_Mid'][i - yy - 1] \
                            and hisdata['close'][i - yy - 1] > hisdata['Boll_Mid'][i - yy - 1]:

                        hisdata.loc[hisdata.index[i], 'position'] = 1
                        if hisdata.loc[hisdata.index[i], 'next_2_days_high'] >= hisdata.loc[hisdata.index[i], 'close'] + ll:
                            hisdata.loc[hisdata.index[i], 'pnl'] = ll
                        elif hisdata.loc[hisdata.index[i], 'next_2_days_low'] <= hisdata.loc[hisdata.index[i], 'close'] - ss:
                            hisdata.loc[hisdata.index[i], 'pnl'] = -ss
                        else:
                            hisdata.loc[hisdata.index[i], 'pnl'] = hisdata.loc[hisdata.index[i], 'next_2_days_close'] - \
                                                                   hisdata.loc[hisdata.index[i], 'close']

                statics = pd.DataFrame({'Type':'Week_Long','Before_X': xx_before, 'Before_X_Atleast': xx_atleast_before, 'After_Y': yy, \
                                        'lockprofit': ll, 'stoploss': ss, 'totalpnl': hisdata.pnl.sum(), \
                                        'count': len(hisdata) - sum(hisdata.pnl.isna()), 'avgpnl': hisdata.pnl.mean(), \
                                        'winratio': sum(hisdata.pnl > 0) / (len(hisdata) - sum(hisdata.pnl.isna()))}, index=[test_num])
                static_set = static_set.append(statics)
                test_num += 1

########################################################################################################################
#############################################  4. 压中线向下突破  #########################################################
########################################################################################################################

for ll in lockprofit:
    for ss in stoploss:
        for xx in Before_X_week:
            xx_before = xx[0]
            xx_atleast_before = xx[1]
            for yy in After_Y:
                hisdata['position'] = np.nan
                hisdata['pnl'] = np.nan

                print([ll, ' ', ss, ' ', xx, ' ', yy])

                for i in range(7, len(hisdata) - 2):

                    # 弱做空信号 -- 压中线向下突破
                    if sum(hisdata['close'][(i - xx_before - yy):i - yy] > hisdata['Boll_Mid'][(i - xx_before - yy):i - yy]) >= xx_atleast_before \
                         and sum(hisdata['open'][(i - xx_before - yy):i - yy] > hisdata['Boll_Mid'][(i - xx_before - yy):i - yy]) >= xx_atleast_before \
                         and sum(hisdata['close'][i - yy:i] < hisdata['Boll_Mid'][i - yy:i]) == yy \
                         and sum(hisdata['open'][i - yy:i] < hisdata['Boll_Mid'][i - yy:i]) == yy \
                         and sum(hisdata['open'][i - yy:i] > hisdata['close'][i - yy:i]) == yy \
                         and hisdata['open'][i - yy - 1] > hisdata['Boll_Mid'][i - yy - 1] \
                         and hisdata['close'][i - yy - 1] < hisdata['Boll_Mid'][i - yy - 1]:

                        hisdata.loc[hisdata.index[i],'position'] = -1
                        if hisdata.loc[hisdata.index[i],'next_2_days_high'] >= hisdata.loc[hisdata.index[i], 'close'] + ss:
                            hisdata.loc[hisdata.index[i], 'pnl'] = -ss
                        elif hisdata.loc[hisdata.index[i],'next_2_days_low'] <= hisdata.loc[hisdata.index[i], 'close'] - ll:
                            hisdata.loc[hisdata.index[i], 'pnl'] = ll
                        else:
                            hisdata.loc[hisdata.index[i], 'pnl'] = hisdata.loc[hisdata.index[i], 'close'] - hisdata.loc[hisdata.index[i], 'next_2_days_close']

                statics = pd.DataFrame({'Type':'Week_Short','Before_X': xx_before, 'Before_X_Atleast': xx_atleast_before, 'After_Y': yy, \
                                        'lockprofit': ll, 'stoploss': ss, 'totalpnl': hisdata.pnl.sum(), \
                                        'count': len(hisdata) - sum(hisdata.pnl.isna()), 'avgpnl': hisdata.pnl.mean(), \
                                        'winratio': sum(hisdata.pnl > 0) / (len(hisdata) - sum(hisdata.pnl.isna()))}, index=[test_num])
                static_set = static_set.append(statics)
                test_num += 1

static_set.to_csv('static_set.csv')
















