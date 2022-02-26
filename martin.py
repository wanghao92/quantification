import numpy as np
import datetime as dt
import time

BASE_PRICE_LADDER = 100     # 阶梯数
SECONDS_PER = (24 * 3600)     #
TRADE_FEE_RATE = 0.0001         #手续费
TRADE_FEE_MIN = 5               #最低手续费
TRADE_PRICE_MIN = 10000         #单次最低交易价格
HOLD = 100                      #一手100股


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
        self.hold_prices = []


    '''
        cal can be dealed
        规避n+1
    '''
    def cal_can_deal(self, now_time, stock_cnt):
        can_deal_cnt = 0
        for i in range(len(self.hold_prices)):
            if (now_time - self.hold_prices[i]["deal_time"]).seconds > SECONDS_PER:
                can_deal_cnt += self.hold_prices[i]["stock_cnt"]
                if can_deal_cnt >= stock_cnt:
                    return stock_cnt

        return can_deal_cnt
    '''
        process hold 
    '''
    def deal_stock(self, now_time, stock_cnt, is_buy = True):
        if is_buy :
            hold_price = dict([("deal_time", now_time), ("stock_cnt", stock_cnt)])
            self.hold_prices.append(hold_price)
            return 0
        else:
            dealed_cnt = 0
            for i in range(len(self.hold_prices)):
                if (now_time - self.hold_prices[i]["deal_time"]).seconds > SECONDS_PER:
                    if dealed_cnt < stock_cnt:
                        diff = stock_cnt - dealed_cnt
                        if self.hold_prices[i]["stock_cnt"] > diff:
                            self.hold_prices[i]["stock_cnt"] -= diff
                            dealed_cnt += diff
                        else:
                            dealed_cnt += self.hold_prices[i]["stock_cnt"]
                            self.hold_prices[i]["stock_cnt"] = 0
                    else:
                        break
            for i in range(len(self.hold_prices) - 1, -1, -1):
                if self.hold_prices[i]["stock_cnt"] == 0:
                    self.hold_prices.pop(i)
            return dealed_cnt


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

    def __init__(self, account, hold_shares, period = 60, profit_rate = 10, is_persistence = False, is_back_test = True):
        """
            period:策略运行周期，单位s
            profit_rate:卖出时收益率，当达到该收益率时卖出，单位0.1%，默认涨1%卖出
            account:本次策略运行的账号信息
            hold_shares:详细持仓数组
            is_persistence：策略运行过程中是否进行持久化，实时运行时必须ture
            is_back_test:是否是回测
            time_now:当前时间，实时：返回当前时刻 回测:返回历史时刻
        """
        self.profit_rate = profit_rate
        self.account = account
        self.hold_shares = hold_shares
        self.period = period
        self.is_persistence = is_persistence
        self.is_back_test = is_back_test
        self.time_now = dt.datetime.now()

    def get_time_now(self):
        if self.is_back_test:
            return self.time_now
        else:
            return dt.datetime.now()

    def set_time_now(self, time_now):
        self.time_now = time_now

    def run(self):
        while(True):
            self.ladder_trade()
            time.sleep(self.period)


    # def cal_base_price(self):
    #     for hold_share in self.hold_shares:
    #         if hold_share
    def cal_buy_cnt(self, now_price):
        return ((int)(TRADE_PRICE_MIN / now_price / HOLD) + 1) * HOLD

    def order(self, hold_share, now_price, stock_cnt = 0, is_buy = True):
        if is_buy:
            if stock_cnt == 0:
                stock_cnt = self.cal_buy_cnt(now_price)
            cost = now_price * stock_cnt
            trade_fee = cost * TRADE_FEE_RATE
            if trade_fee < TRADE_FEE_MIN:
                trade_fee = TRADE_FEE_MIN
            if cost + trade_fee > self.account.remain:
                return Deal(0, 0)
            #下单 todo
            hold_share.deal_stock(self.get_time_now(), stock_cnt)
            return Deal(now_price, stock_cnt)
        else:
            deal_cnt = hold_share.cal_can_deal(self.get_time_now(), stock_cnt)
            #下单 todo
            hold_share.deal_stock(self.get_time_now(), deal_cnt, False)
            return Deal(now_price, stock_cnt, False)

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
                        deal = self.order(hold_share, now_price)
                        ladder.buy_price = deal.price
                        ladder.stock_cnt = deal.stock_cnt
                        ladder.buy_time = self.get_time_now()
                        self.update_hold_share(hold_share, deal)

                elif now_price > ladder.buy_price * (1 + 0.001 * self.profit_rate):
                    hold_share.deal_stock()
                    deal = self.order(hold_share, now_price, ladder.stock_cnt, False)
                    deal.buy_price = ladder.buy_price
                    ladder.buy_price = 0
                    ladder.stock_cnt -= deal.stock_cnt
                    ladder.buy_time = self.get_time_now()
                    self.update_hold_share(hold_share, deal)

    def update_hold_share(self, hold_share, deal):
        cost = deal.price * deal.stock_cnt
        if deal.is_buy :
            hold_share.price = (hold_share.price * hold_share.stock_cnt + cost) \
                               / (hold_share.stock_cnt + deal.stock_cnt)
            hold_share.stock_cnt += deal.stock_cnt
            self.account.remain -= cost
            self.account.cost += cost
        else:
            profit = (deal.price - deal.buy_price) * deal.stock_cnt

            if profit > 0:
                hold_share.suc_cnt += 1
                self.account.suc_cnt += 1
            else:
                hold_share.suc_cnt -= 1
                self.account.suc_cnt -= 1
            hold_share.trade_cnt += 1
            hold_share.price = (hold_share.price * hold_share.stock_cnt - cost) \
                               / (hold_share.stock_cnt - deal.stock_cnt)
            hold_share.profit = hold_share.profit + profit
            hold_share.stock_cnt -= deal.stock_cnt
            self.account.remain += cost
            self.account.cost -= cost
            self.account.trade_cnt += 1
            self.account.profit += profit








if __name__ == '__main__':
    a = 0





















