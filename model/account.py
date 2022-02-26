class Account:

    def __init__(self, init_money, total_money, remain, cost, profit,
                 market_value, trade_cnt, suc_cnt, total_profit):
        self.init_money = init_money
        self.total_money = total_money
        self.remain = remain
        self.cost = cost
        self.profit = profit
        self.market_value = market_value    #市值
        self.trade_cnt = trade_cnt
        self.suc_cnt = suc_cnt
        self.total_profit = total_profit