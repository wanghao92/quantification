import datetime
import db.mysql_utils as mysql
import conf.env as env
import pandas as pd
TRADE_FEE_RATE = 0.0001  # 手续费
TRADE_FEE_MIN = 5  # 最低手续费


class TradeUtils:

    def get_price(self, now_time):
        pass

    def order(self):
        pass


class JoinQuantSimulate(TradeUtils):

    def __init__(self, db):
        self.db = db
        self.cache = None


    '''
        @:return
            价格列表，默认返回10个[(price, count)]
            前5个是买单报价，后5个是卖单报价，价格依次升高
            price:unit(1分)
            count:unit(1股)
    '''

    def get_price(self, stock_code, now_time=None):

        if now_time is None:
            now_time = datetime.datetime.now()

        if self.cache is not None:
            data = self.cache[self.cache['date_time'] == now_time]
            if data.size != 0:
                return self.get_price_ladder(data)

        table_name = 'jq_' + stock_code.replace('.', '_')
        sql = "select * from {} where date_time >= %s order by date_time limit 1000".format(table_name)
        cur = self.db.cursor()
        try:
            cur.execute(sql, now_time)
            data = cur.fetchall()
            if data is None:
                return None
            self.cache = pd.DataFrame(data)

            self.get_price_ladder(self.cache[self.cache['date_time'] == now_time])

        except Exception as e:
            print("execte sql:'{}' error".format(sql))
            print(repr(e))
        finally:
            cur.close()

    def get_price_ladder(self, data):
        if data is None:
            return None
        result = []
        diff_price = (data.iloc[0].high - data.iloc[0].low) / 10
        diff_count = int(data.iloc[0].volume / 10)
        for i in range(10):
            result.append((data.iloc[0].low + i * diff_price, diff_count))
        return result



    '''
        发出交易指令
        @:param
        price:价格(unit:分)
        count:数量（unit:股)
        is_buy: true买， FALSE卖
        now_time: 不传为当前时间
        @:return
        (price, count)：(实际买/卖价格(unit:分)，实际买/卖数量(unit:股)
    '''

    def order(self, stock_code, price, count, is_buy=True, now_time=None):

        t_price = 0
        t_count = 0
        if now_time == None:
            now_time = datetime.datetime.now()

        result = self.get_price(stock_code, now_time)
        if result is None:
            return 0, 0
        if is_buy:
            for i in range(5, 10):
                if price >= result[i][0]:
                    if count - t_count > result[i][1]:
                        t_price += result[i][0] * result[i][1]
                        t_count += result[i][1]
                    else:
                        t_price += result[i][0] * (count - t_count)
                        t_count = count
                        break
                else:
                    break

        else:
            for i in range(4, -1, -1):
                if price <= result[i][0]:
                    if count - t_count > result[i][1]:  #需要买的数量>挂单数量
                        t_price += price * result[i][1]
                        t_count += result[i][1]
                    else:
                        t_price += price * (count - t_count)
                        t_count = count
                        break
                else:
                    break
        if t_count == 0:
            return 0, 0
        else:
            return t_price / t_count, int(t_count / 100) * 100


def stub_jq_simulat_get_price():
    db = mysql.connect(env.PC_LOCAL_MYSQL_HOST, env.PC_LOCAL_MYSQL_PORT, env.PC_LOCAL_MYSQL_USER,
                       env.PC_LOCAL_MYSQL_PSWD,
                       env.PC_LOCAL_MYSQL_DB)
    trade = JoinQuantSimulate(db)
    data = trade.get_price('512800.XSHG', datetime.datetime(2017, 9, 13, 10, 42, 0))
    print(data)
    db.close()


def stub_jq_simulat_order():
    db = mysql.connect(env.PC_LOCAL_MYSQL_HOST, env.PC_LOCAL_MYSQL_PORT, env.PC_LOCAL_MYSQL_USER,
                       env.PC_LOCAL_MYSQL_PSWD,
                       env.PC_LOCAL_MYSQL_DB)
    trade = JoinQuantSimulate(db)
    print('------BUY------')
    data = trade.order('512800.XSHG', 116, 10000, True, datetime.datetime(2022, 2, 25, 14, 42, 0))
    print(data)
    data1 = trade.order('512800.XSHG', 116, 10000 - data[1], True, datetime.datetime(2022, 2, 25, 14, 43, 0))
    print(data1)
    data2 = trade.order('512800.XSHG', 117, 10000 - data[1] - data1[1], True, datetime.datetime(2022, 2, 25, 16, 43, 0))
    print(data2)

    print('------sell-------')
    data = trade.order('512800.XSHG', 116, 10000, False, datetime.datetime(2022, 2, 25, 14, 42, 0))
    print(data)
    data1 = trade.order('512800.XSHG', 119, 10000 - data[1], False, datetime.datetime(2022, 2, 25, 14, 43, 0))
    print(data1)
    data2 = trade.order('512800.XSHG', 117, 10000 - data[1] - data1[1], False,
                        datetime.datetime(2022, 2, 25, 14, 43, 0))
    print(data2)
    db.close()


if __name__ == '__main__':
    stub_jq_simulat_get_price()
    # stub_jq_simulat_order()
