import numpy as np
import datetime as dt

BASE_PRICE_LADDER = 100     # 阶梯数
SECONDS_PER = (24 * 3600)     #


class Account:

    def __init__(self, totalMoney, remain, cost, profit,
                 markValue, tradeCnt, sucCnt, totalProfit):
        self.totalMoney = totalMoney
        self.remain = remain
        self.cost = cost
        self.profit = profit
        self.marketValue = markValue
        self.tradeCnt = tradeCnt
        self.sucCnt = sucCnt
        self.totalProfit = totalProfit


#阶梯数组，单个价格阶梯
class LadderHold:

    def __init__(self, ladder_price, buy_time, deal_time, buy_price, stock_cnt):
        self.ladder_price = ladder_price
        self.buy_time = buy_time
        self.deal_time = deal_time
        self.buy_price = buy_price
        self.stock_cnt = stock_cnt



#单一股票持仓
class HoldShare:

    def __init__(self, stock_code, stock_name, create_time = None, stock_cnt = 0, price = 0,
                 profit = 0, trade_cnt = 0, suc_cnt = 0, end_time = None, base_price = 0, ladder_rate = 1):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.create_time = create_time  #建仓时间
        self.stock_cnt = stock_cnt      #持仓数量
        self.price = price              #持仓价格
        self.profit = profit            #持仓利润
        self.trade_cnt = trade_cnt      #交易次数
        self.suc_cnt = suc_cnt          #成功次数
        self.end_time = end_time        #平仓时间
        self.base_price = base_price    #基准价格
        self.ladder_rate = ladder_rate  #阶梯利率
        self.ladder_holds = self.cal_ladder_hold()       #生成价格阶梯数组

    def cal_ladder_hold(self):
        price_ladder = np.zeros(BASE_PRICE_LADDER * 2)
        price_ladder[BASE_PRICE_LADDER] = self.base_price
        for i in range(1, BASE_PRICE_LADDER):
            price_ladder[BASE_PRICE_LADDER + i] \
                = price_ladder[BASE_PRICE_LADDER + i - 1] * (1 + self.ladder_rate * 0.001)
            price_ladder[BASE_PRICE_LADDER - i] \
                = price_ladder[BASE_PRICE_LADDER - i + 1] * (1 - self.ladder_rate * 0.001)

        return price_ladder

class Deal:
    '''
        price:交易价格
        stock_cnt：交易数量
        is_buy：买入True，卖出False
        buy_price：买入时价格，当is_buy为false时有效
    '''
    def __init__(self, price, stock_cnt, is_buy = True, buy_price = 0):
        self.price = price
        self.stock_cnt = stock_cnt
        self.is_buy = is_buy
        self.buy_price = buy_price


class Martin:

    def __init__(self, account, hold_shares, period = 60, profit_rate = 10, is_persistence = False):
        """
            period:策略运行周期，单位s
            profit_rate:卖出时收益率，当达到该收益率时卖出，单位0.1%，默认涨1%卖出
            account:本次策略运行的账号信息
            hold_shares:详细持仓数组
            is_persistence：策略运行过程中是否进行持久化，实时运行时必须ture
        """
        self.profit_rate = profit_rate
        self.account = account
        self.hold_shares = hold_shares
        self.period = period
        self.is_persistence = is_persistence

    def run(self):
        a = self.account

    def ladder_trade(self):
        for hold_share in self.hold_shares:
            if (hold_share.stock_cnt == 0) or (hold_share.create_time is None):
                continue
            #获取当前价格 todo
            now_price = 0
            #判断是否卖出和买入
            for ladder in hold_share.ladder_holds:
                if ladder.stock_cnt == 0:
                    if ladder.ladder_price > now_price:
                        #买入 todo
                        ladder.buy_price = 0
                        ladder.stock_cnt = 0
                        ladder.deal_time = dt.datetime.now()
                        ladder.buy_time = dt.datetime.now()
                        #更新账户信息 todo
                elif now_price < ladder.buy_price * (1 + 0.001 * self.profit_rate):
                    continue
                if (dt.datetime.now() - ladder.deal_time).seconds < SECONDS_PER:
                    #规避n+1
                    for temp in hold_share.ladder_holds:
                        if temp.stock_cnt == ladder.stock_cnt and (dt.datetime.now() - temp.deal_time).seconds > SECONDS_PER:
                            temp.deal_time = ladder.deal_time
                    #卖出 todo
                    ladder.buy_price = 0
                    ladder.stock_cnt = 0
                    ladder.deal_time = dt.datetime.now()
                    ladder.buy_time = dt.datetime.now()
                    #更新账户信息 todo

    def update_hold_share(self, hold_share, deal):
        if deal.is_buy :
            hold_share.stock_cnt += deal.stock_cnt
            hold_share.price = (hold_share.price * hold_share.stock_cnt + deal.price * deal.stock_cnt) / hold_share.stock_cnt
        else:
            hold_share.profit = hold_share.profit







if __name__ == '__main__':
    a = 0





















