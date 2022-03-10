import datetime

import numpy as np
import datetime as dt
import time
import utils.date_utils as du

BASE_PRICE_LADDER = 100  # 阶梯数
TRADE_PRICE_MIN = 10000  # 单次最低交易价格
HOLD = 100  # 一手100股
PRINT_ON = True

# 阶梯数组，单个价格阶梯
class LadderHold:

    def __init__(self, ladder_price, buy_time, buy_price, stock_cnt):
        self.ladder_price = ladder_price
        self.buy_time = buy_time
        self.buy_price = buy_price
        self.stock_cnt = stock_cnt


# 单一股票持仓
class HoldShare:

    def __init__(self, stock_code, stock_name, base_price=0.0, stock_cnt=0, price=0.0, ladder_rate=0.01,
                 profit=0, trade_cnt=0, suc_cnt=0):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.create_time = None  # 建仓时间
        self.temp_price = 0  # 实时价格缓存
        self.stock_cnt = stock_cnt  # 持仓数量(unit:股)
        self.price = price  # 持仓价格
        self.profit = profit  # 持仓利润
        self.trade_cnt = trade_cnt  # 交易次数
        self.suc_cnt = suc_cnt  # 成功次数
        self.end_time = None  # 平仓时间
        self.base_price = base_price  # 基准价格
        self.ladder_rate = ladder_rate  # 阶梯利率(unit:0.01)
        self.ladder_holds = self.cal_ladder_hold()  # 生成价格阶梯数组 @see:LadderHold
        self.hold_prices = []  # (deal_time: ,stock_cnt: )

    def update_ladder(self, ladder_rate):
        self.ladder_rate = ladder_rate
        self.ladder_holds = self.cal_ladder_hold()

    '''
        cal can be dealed
        规避n+1
    '''

    def cal_can_deal(self, now_time, stock_cnt):
        can_deal_cnt = 0
        for i in range(len(self.hold_prices)):
            if du.get_time_diff(now_time, self.hold_prices[i]["deal_time"], 'day') > 1:
                can_deal_cnt += self.hold_prices[i]["stock_cnt"]
                if can_deal_cnt >= stock_cnt:
                    return stock_cnt

        return can_deal_cnt

    '''
        维护hold_prices
    '''

    def deal_stock(self, now_time, stock_cnt, is_buy=True):
        dealed_cnt = 0
        if is_buy:
            hold_price = dict([("deal_time", now_time), ("stock_cnt", stock_cnt)])
            self.hold_prices.append(hold_price)
        else:
            dealed_cnt = 0
            for i in range(len(self.hold_prices)):
                if du.get_time_diff(now_time, self.hold_prices[i]["deal_time"], 'day') > 1:
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
        if PRINT_ON:
            total = 0
            for i in range(len(self.hold_prices)):
                total += self.hold_prices[i]["stock_cnt"]
            print("deal_stock:time:{} total:{}, stockCnt:{}, dealCnt:{}, is_buy:{}".format(now_time, total, stock_cnt, dealed_cnt, is_buy))
        return dealed_cnt

    def cal_ladder_hold(self):
        price_ladder = np.zeros(BASE_PRICE_LADDER * 2)
        price_ladder[BASE_PRICE_LADDER] = self.base_price
        for i in range(1, BASE_PRICE_LADDER):
            price_ladder[BASE_PRICE_LADDER + i] \
                = price_ladder[BASE_PRICE_LADDER + i - 1] * (1 + self.ladder_rate)
            price_ladder[BASE_PRICE_LADDER - i] \
                = price_ladder[BASE_PRICE_LADDER - i + 1] * (1 - self.ladder_rate)
        price_ladder[0] = price_ladder[1] * (1 - self.ladder_rate)
        ladders = [LadderHold(price_ladder[i], None, 0, 0) for i in range(1, BASE_PRICE_LADDER * 2)]

        return ladders


class Deal:
    '''
        price:交易价格
        stock_cnt：交易数量
        is_buy：买入True，卖出False
        buy_price：买入时价格，当is_buy为false时有效
    '''

    def __init__(self, price, stock_cnt, is_buy=True, buy_price=0):
        self.price = price
        self.stock_cnt = stock_cnt
        self.is_buy = is_buy
        self.buy_price = buy_price


class Martin:

    def __init__(self, account, hold_shares, trade_utils, dot_utils, profit_rate=0.01, period=60, is_persistence=False,
                 is_back_test=True):
        """
            period:策略运行周期，单位s
            profit_rate:卖出时收益率，当达到该收益率时卖出，单位0.1%
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
        self.trade_utils = trade_utils
        self.dot_utils = dot_utils


    def __str__(self):
        return self.account.to_string()

    def get_time_now(self):
        if self.is_back_test:
            return self.time_now
        else:
            return dt.datetime.now()

    def set_time_now(self, time_now):
        self.time_now = time_now

    def loop_run(self):
        while (True):
            self.run()
            time.sleep(self.period)

    # def cal_base_price(self):
    #     for hold_share in self.hold_shares:
    #         if hold_share
    def cal_buy_cnt(self, now_price):
        return ((int)(TRADE_PRICE_MIN / now_price / HOLD) + 1) * HOLD

    def order(self, hold_share, now_price, stock_cnt=0, is_buy=True):
        if is_buy:
            if stock_cnt == 0:
                stock_cnt = self.cal_buy_cnt(now_price)
            cost = now_price * stock_cnt
            if cost > self.account.remain:
                return Deal(0, 0)

            result = self.trade_utils.order(hold_share.stock_code,
                                            now_price, stock_cnt, True, self.get_time_now())
            if result[0] != 0 and result[1] != 0:
                hold_share.deal_stock(self.get_time_now(), result[1])
                self.dot_utils.deal_dot(hold_share.stock_code, hold_share.stock_name,
                                        result[1], result[0], self.get_time_now())
            return Deal(result[0], result[1])
        else:
            deal_cnt = hold_share.cal_can_deal(self.get_time_now(), stock_cnt)
            if deal_cnt == 0:
                return Deal(0, 0, False)

            result = self.trade_utils.order(hold_share.stock_code,
                                            now_price, stock_cnt, False, self.get_time_now())
            if result[0] != 0 and result[1] != 0:
                hold_share.deal_stock(self.get_time_now(), result[1], False)
                self.dot_utils.deal_dot(hold_share.stock_code, hold_share.stock_name,
                                        result[1], result[0], self.get_time_now(), False)
            return Deal(result[0], result[1], False)

    def is_price_range(self, price, base_price):
        return (base_price * 1.001) >= price >= base_price

    def run(self):

        for hold_share in self.hold_shares:

            price_list = self.trade_utils.get_price(hold_share.stock_code, self.get_time_now())
            if price_list is None:
                return
            hold_share.temp_price = price_list[5][0]
            for ladder in hold_share.ladder_holds:
                if ladder.stock_cnt == 0:  # buy
                    if self.is_price_range(ladder.ladder_price, price_list[5][0]):
                        deal = self.order(hold_share, price_list[8][0])
                        if deal.price == 0 or deal.stock_cnt == 0:
                            continue
                        ladder.buy_price = deal.price
                        ladder.stock_cnt = deal.stock_cnt
                        ladder.buy_time = self.get_time_now()
                        self.update_hold_share(hold_share, deal)
                elif self.is_price_range(ladder.buy_price * (1 + self.profit_rate), price_list[0][0]):
                    deal = self.order(hold_share, price_list[3][0], ladder.stock_cnt, False)
                    if deal.price == 0 or deal.stock_cnt == 0:
                        continue
                    deal.buy_price = ladder.buy_price
                    ladder.buy_price = 0
                    ladder.stock_cnt -= deal.stock_cnt
                    ladder.buy_time = self.get_time_now()
                    self.update_hold_share(hold_share, deal)
        self.update_account_info()

    def update_account_info(self):
        market_value = 0
        for hold_share in self.hold_shares:
            market_value += hold_share.stock_cnt * hold_share.temp_price
        self.account.market_value = market_value
        self.account.total_money = self.account.remain + market_value
        self.account.total_profit = self.account.total_money - self.account.init_money
        self.account.yield_rate = self.account.total_profit / self.account.init_money

        self.dot_utils.real_count_dot(self.account.total_money, self.account.remain,
                                      self.account.market_value, self.account.total_profit, self.get_time_now())

    def update_hold_share(self, hold_share, deal):
        cost = deal.price * deal.stock_cnt
        if deal.is_buy:
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
                print("profit:{}, buy:{}, sell:{}, cnt:{}".format(profit, deal.buy_price, deal.price, deal.stock_cnt))
            hold_share.trade_cnt += 1
            hold_share.price = (hold_share.price * hold_share.stock_cnt - cost) \
                               / (hold_share.stock_cnt - deal.stock_cnt)
            hold_share.profit += profit
            hold_share.stock_cnt -= deal.stock_cnt
            self.account.remain += cost
            self.account.cost -= cost
            self.account.trade_cnt += 1
            self.account.profit += profit

        if PRINT_ON:
            print("update_hold_share:{},code:{},cnt:{},price:{};deal.price:{},deal.cnt:{};tradeCnt:{},sucCnt:{},remain:{},profit:{}" \
                  .format(hold_share.stock_name, hold_share.stock_code, hold_share.stock_cnt, hold_share.price,
                          deal.price, deal.stock_cnt,
                          self.account.trade_cnt, self.account.suc_cnt, self.account.remain, self.account.profit))




def hold_share_test():
    hold_share_512800 = HoldShare('512800.XSHG', '银行etf', 1.017, 0, 0, 0.005)
    now_time = datetime.datetime(2020, 1, 1)
    total = 0
    for i in range(200):
        deal_cnt = 1000 * (i % 10)
        if i % 3 == 0:  #sell
            result = hold_share_512800.deal_stock(now_time, deal_cnt, False)
            total -= result
            print("time:{}, sell:{}, total:{}".format(now_time, result, total))
        else:
            hold_share_512800.deal_stock(now_time, deal_cnt)
            total += deal_cnt
            print("time:{}, buy:{}, total:{}".format(now_time, deal_cnt, total))
        now_time += datetime.timedelta(hours=7)
    print(hold_share_512800)

if __name__ == '__main__':
    hold_share_test()
