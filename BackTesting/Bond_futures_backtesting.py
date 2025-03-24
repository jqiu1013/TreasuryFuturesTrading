import datetime
import time
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

class Tech_utliz_tools():

    def __init__(self):
        super(Tech_utliz_tools,self).__init__()

    def MaxDrawdown(self,return_list):
        #先找到对应前最高点的最大回撤的标记点，该标记点代表局部低点
        i = np.argmax((np.maximum.accumulate(return_list) - return_list))
        if i == 0:
            return 0,0,0
        # 局部低点前的高点位置
        j = np.argmax(return_list[:i-return_list.index.start+1])
        return return_list[j] - return_list[i], j-return_list.index.start+1, i-return_list.index.start+1


    def MaxBounceBack(self,return_list):
        i = np.argmax((return_list - np.minimum.accumulate(return_list)))
        if i == 0:
            return 0,0,0
        j = np.argmin(return_list[:i-return_list.index.start+1])
        return return_list[i] - return_list[j], j-return_list.index.start+1, i-return_list.index.start+1

class Strategy_main_body(Tech_utliz_tools):

    def __init__(self,params,params2,lockprofitline,stoplossline):
        super(Strategy_main_body,self).__init__()
        self.params=params
        self.params2 = params2
        self.lockprofit = lockprofitline
        self.stoploss = stoplossline

        self.dat= pd.read_excel('./T_5MinutesData.xlsx',sheet_name='Sheet2',index_col=0)
        self.dat.rename(columns={'Unnamed: 1':'close'},inplace=True)
        data= pd.DataFrame(self.dat['close'])
        data['Datetime']=data.index
        data['dates_without_time'] = [date.strftime('%Y-%m-%d')  for date in data.index]
        data.reset_index(drop=True, inplace=True)
        self.data= data

        self.static_set= pd.DataFrame()
        self.year_static_set= pd.DataFrame()

    def loop(self):
        self.test_num=1
        for ll in self.lockprofit:
            for ss in self.stoploss:
                for DD in self.params:
                    for BB in self.params2:
                        self.position = np.zeros(len(self.data))
                        self.ddbb = np.zeros(len(self.data))
                        self.pnl = np.zeros(len(self.data))
                        self.holdinglength = np.zeros(len(self.data))
                        # self.accumulate_pnls = np.zeros(len(self.data))
                        self.action_lable = pd.Series(np.zeros(len(self.data)))

                        self.laststart = 1
                        self.lastend = 1
                        self.laststart_calc = 1
                        self.lastend_calc = 1
                        self.i = 21

                        statics,year_summary = self.backtesting_func(DD,BB,ll,ss)
                        self.static_set = self.static_set.append(statics)
                        self.year_static_set = pd.concat([self.year_static_set,year_summary],axis=0)
                        self.test_num +=1

        self.static_set.to_csv('static_set.csv')
        self.year_static_set.to_csv('year_static_set.csv')
        print(self.static_set)

    def backtesting_func(self,DD,BB,ll,ss):

        while self.i <len(self.data):

            self.sameday_locs =self.data[self.data['dates_without_time']==self.data.dates_without_time.iloc[self.i]].index
# 平仓
            if (self.position[self.i-1] ==-1) and (self.i != self.lastend+1):
                self.MaxBB, self.MaxBBIndex, self.MaxBBIndex1 = self.MaxBounceBack(self.data.close.iloc[self.laststart_calc:self.i+1])

                # if self.data.dates_without_time.iloc[self.i] == '2015-04-02':
                #     print(1)

                if self.MaxBB >= BB:
                    if (self.MaxBBIndex1 < self.i-self.laststart_calc +1) and (self.i == min(self.sameday_locs)):
                        self.ddbb[self.laststart_calc + self.MaxBBIndex1 - 1] = self.MaxBB
                        if self.data.close.iloc[min(self.sameday_locs)] >= self.data.close.iloc[self.laststart]:
                            self.position[self.i] = -1
                            self.i = self.i + 1
                            self.laststart_calc = min(self.sameday_locs)
                        else:
                            self.ddbb[self.i] = self.MaxBB
                            self.action_lable[self.i]='Prev+Profit Close'
                            self.lastend = self.i
                            self.lastend_calc = self.i
                            self.position[self.i] = -1
                            self.position[self.i + 1: max(self.sameday_locs)+1] = 0
                            self.pnl[self.i] = - (self.data.close.iloc[self.lastend] / self.data.close.iloc[self.laststart] - 1)
                            self.holdinglength[self.i]= (self.lastend - self.laststart + 1) / 54
                            self.i = max(self.sameday_locs) + 1
                    elif self.i <= max(self.sameday_locs)-3:
                        self.ddbb[self.i] = self.MaxBB
                        self.action_lable[self.i] ='Normal Close'
                        self.lastend = self.i
                        self.lastend_calc = self.i
                        self.position[self.i] = -1
                        self.position[self.i + 1: max(self.sameday_locs)+1] = 0
                        self.pnl[self.i] = - (self.data.close.iloc[self.lastend] / self.data.close.iloc[self.laststart] - 1)
                        self.holdinglength[self.i] = (self.lastend - self.laststart + 1) / 54
                        self.i = max(self.sameday_locs) + 1
                    else:
                        self.position[self.i] = -1
                        self.i = self.i + 1

                elif self.MaxBB < BB:
                    if (self.i == max(self.sameday_locs)) - 3 and (self.data.close.iloc[self.laststart] - self.data.close.iloc[self.i] > ll):
                        self.action_lable[self.i] ='LockProfit Close'
                        self.lastend = self.i
                        self.lastend_calc = self.i
                        self.position[self.i] = -1
                        self.position[self.i + 1: max(self.sameday_locs)+1] = 0
                        self.pnl[self.i] = - (self.data.close.iloc[self.lastend] / self.data.close.iloc[self.laststart] - 1)
                        self.holdinglength[self.i] = (self.lastend - self.laststart + 1) / 54
                        self.i = max(self.sameday_locs) + 1
                    elif (self.i <= max(self.sameday_locs)-3) and (self.data.close.iloc[self.i] - self.data.close.iloc[self.laststart] >= ss):
                        self.action_lable[self.i] = 'StopLoss Close'
                        self.lastend = self.i
                        self.lastend_calc = self.i
                        self.position[self.i] = -1
                        self.position[self.i + 1: max(self.sameday_locs)+1] = 0
                        self.pnl[self.i] = - (self.data.close.iloc[self.lastend] / self.data.close.iloc[self.laststart] - 1)
                        self.holdinglength[self.i] = (self.lastend - self.laststart + 1) / 54
                        self.i = max(self.sameday_locs) + 1
                    else:
                        self.position[self.i] = -1
                        self.i += 1

# 开仓
            elif self.i>self.lastend:
                self.MaxDD, self.MaxDDIndex,self.MaxDDIndex1 = self.MaxDrawdown(self.data.close.iloc[self.lastend_calc:self.i+1])

                # if self.data.dates_without_time.iloc[self.i] == '2015-04-13':
                #     print(1)

                if (self.MaxDD>=DD)&(self.i <= max(self.sameday_locs)-3):
                    if  (self.i == min(self.sameday_locs)) and (self.MaxDDIndex1 < self.i-self.lastend_calc +1) and (self.data.close.iloc[min(self.sameday_locs)]>=self.data.close.iloc[self.lastend_calc+self.MaxDDIndex-1]):
                        self.ddbb[self.lastend_calc+self.MaxDDIndex1-1]= self.MaxDD
                        self.i += 1
                        self.laststart_calc = min(self.sameday_locs)
                    else:
                        self.ddbb[self.i]= -self.MaxDD
                        self.action_lable[self.i] = 'Normal Open'
                        self.laststart =self.i
                        self.laststart_calc=self.i
                        self.position[self.i + 1: max(self.sameday_locs)+1] = -1
                        self.i = max(self.sameday_locs) + 1

                else:

                    self.i += 1

        summary_data= self.data

        summary_data['position']= self.position
        summary_data['ddbb']= self.ddbb
        summary_data['pnl']= self.pnl
        summary_data['holdinglength']= self.holdinglength
        # summary_data['accumulate_pnls']= self.accumulate_pnls
        summary_data['action_lable']=self.action_lable

        summary_data.to_csv('siganl_summary%f_%f_%f_%f.csv'%(round(DD,2),round(BB,2),round(ll,2),round(ss,2)))
#总统计
        total_pnl= summary_data.pnl.apply(lambda x : x+1).cumprod().values[-1] -1
        count = len(summary_data[summary_data['pnl']!=0])
        avg_holding_length=  summary_data[summary_data['pnl']!=0]['holdinglength'].mean()
        avgpnl= total_pnl/count
        win_ratio=  len(summary_data[summary_data['pnl']>0])/len(summary_data[summary_data['pnl']!=0])
        statics =pd.DataFrame({'DD':DD,'BB':BB,'止盈线':ll,'止损线':ss,'totalpnl':total_pnl, 'count':count, 'averageholdinglength':avg_holding_length, 'avgpnl':avgpnl, 'winratio':win_ratio},index=[self.test_num])

        summary_data['year'] = summary_data.dates_without_time.apply(lambda x: x[:4])
#分年统计
        year_summary = pd.DataFrame(summary_data.groupby(['year']).apply(lambda x: x.pnl.apply(lambda x: x + 1).cumprod().values[-1] - 1).values, columns=['total_pnl'],index=[summary_data.year.unique()])
        year_summary['DD'] = DD
        year_summary['BB'] = BB
        year_summary['止盈线'] = ll
        year_summary['止损线'] = ss
        year_summary['count'] =summary_data.groupby(['year']).apply(lambda x: len(x[x['pnl'] != 0])).values
        year_summary['avg_holding_length'] =summary_data.groupby(['year']).apply(lambda x: x[x['pnl'] != 0]['holdinglength'].mean()).values
        year_summary['avgpnl'] =summary_data.groupby(['year']).apply(lambda x: (x.pnl.apply(lambda x: x + 1).cumprod().values[-1] - 1) / len(x[x['pnl'] != 0])).values
        year_summary['win_ratio'] =summary_data.groupby(['year']).apply(lambda x: len(x[x['pnl'] > 0]) / len(x[x['pnl'] != 0])).values

        return  statics,year_summary

if __name__ == '__main__':

    # params = [0.10,0.15,0.25]
    # params2 = [0.10,0.15,0.25]
    # lockprofitline = [0.10,0.20,0.30]
    # stoplossline = [0.10,0.20,0.30]

    params = [0.20]
    params2 = [0.20]
    lockprofitline = [0.10]
    stoplossline = [0.20]


    loops =Strategy_main_body(params,params2,lockprofitline,stoplossline)
    loops.loop()


