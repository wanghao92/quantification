class Account:

    def __init__(self, init_money, total_money, remain, cost=0, profit=0,
                 market_value=0, trade_cnt = 0, suc_cnt = 0, total_profit = 0, name = 'lemon'):
        self.name = name
        self.init_money = init_money
        self.total_money = total_money
        self.remain = remain
        self.cost = cost
        self.profit = profit
        self.market_value = market_value    #市值
        self.trade_cnt = trade_cnt
        self.suc_cnt = suc_cnt
        self.total_profit = total_profit

    def __str__(self):
        return self.to_string()

    def to_string(self):
        return "name:" + self.name + "; initMoney:" + self.init_money \
            + "\n totalMoney:" + self.total_money + "remain:" + self.remain + "; cost:" + self.cost \
            + "\n profit:" + self.profit + "; totalProfit:" + self.total_profit + "; markValue" + self.market_value \
            + "\n tradeCnt:" + self.trade_cnt + "; successCnt:" + self.suc_cnt + "; failCnt:" + (self.trade_cnt - self.suc_cnt)