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
