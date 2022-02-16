from numpy import np

BASE_PRICE_LADDER = 100     #阶梯数

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


class Deal:

    def __init__(self, stock_code, stock_name, buy_time,
                 sell_time, buy_price, sell_price, profit):

        self.stock_code = stock_code
        self.stock_name = stock_name
        self.buy_time = buy_time
        self.sell_time = sell_time
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.profit = profit


class RealCount:

    def __init__(self, money_rate, retreat_rate, yield_rate, total_profit, deal):
        self.money_rate = money_rate
        self.retreat_rate = retreat_rate
        self.yield_rate = yield_rate
        self.total_profit = total_profit
        self.deal = deal


 class HoldBasicInfo:

    def __init__(self, stock_code, stock_name, create_time,
                 stock_cnt, price, profit, trade_cnt, suc_cnt, end_time):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.create_time = create_time
        self.stock_cnt = stock_cnt
        self.price = price
        self.profit = profit
        self.trade_cnt = trade_cnt
        self.suc_cnt = suc_cnt
        self.end_time = end_time

class LadderHold:

    def __init__(self, ladder_price, buy_time, deal_time, buy_price):
        self.ladder_price = ladder_price
        self.buy_time = buy_time
        self.deal_time = deal_time
        self.buy_price = buy_price

class HoldShare:

    def __init__(self, base_price, ladder_rate, hold_basic_info):
        self.base_price = base_price
        self.ladder_rate = ladder_rate
        self.hold_basic_info = hold_basic_info
        self.ladder_hold = self.cal_ladder_hold()

    def cal_ladder_hold(self):
        price_ladder = np.zeros(BASE_PRICE_LADDER * 2)
        price_ladder[BASE_PRICE_LADDER] = self.base_price
        for i in range(1, BASE_PRICE_LADDER):
            price_ladder[BASE_PRICE_LADDER + i] \
                = price_ladder[BASE_PRICE_LADDER + i - 1] * (1 + self.ladder_rate * 0.001)
            price_ladder[BASE_PRICE_LADDER - i] \
                = price_ladder[BASE_PRICE_LADDER - i + 1] * (1 - self.ladder_rate * 0.001)

        return price_ladder



























