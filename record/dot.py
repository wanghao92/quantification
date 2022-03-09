import datetime
import db.mysql_utils as mysql
import model.account as ac
import conf.env as env
import uuid

CREATE_BASIC_TEST_INFO_SQL = "create table IF NOT EXISTS `back_test_info`(" \
                             "`id` varchar(64)," \
                             "`strategy` varchar(64)," \
                             "`name`  datetime comment 'account name'," \
                             "`test_time` datetime comment '实际的测试时间'," \
                             " `start_time` datetime comment '回测范围起始时间'," \
                             " `end_time` datetime comment '回测范围截止时间'," \
                             "`init_money` float," \
                             "`total_money` float," \
                             "`remain` float," \
                             "`profit` float," \
                             "`market_value` float," \
                             "`trade_cnt` int," \
                             "`suc_cnt` int," \
                             "`total_profit` int," \
                             "`table_index` int," \
                             "`description` longtext," \
                             "primary key (`id`)," \
                             "index index_strategy (`strategy`)," \
                             "index index_test_time (`test_time`)," \
                             "index index_name (`name`)" \
                             ")ENGINE=InnoDB DEFAULT CHARSET=utf8;"


class BackTestInfo:
    def __init__(self, strategy, start_time, end_time, account, description=None, table_index=0):
        self.id = uuid.uuid4()
        self.strategy = strategy
        self.description = description
        self.test_time = datetime.datetime.now()
        self.start_time = start_time
        self.end_time = end_time
        self.name = account.name
        self.init_money = account.init_money
        self.total_money = account.total_money
        self.remain = account.remain
        self.profit = account.profit
        self.market_value = account.market_value
        self.trade_cnt = account.trade_cnt
        self.suc_cnt = account.suc_cnt
        self.total_profit = account.total_profit
        self.table_index = table_index


class DealDot:

    def __init__(self, back_test_info_id, stock_code, stock_name, deal_time, price, is_buy=True):
        self.id = uuid.uuid4()
        self.back_test_info_id = back_test_info_id
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.deal_time = deal_time
        self.price = price
        self.is_buy = is_buy


class RealCountDot:

    def __init__(self, back_test_info_id, date_time, total_money, remain, market_value, money_rate, yield_rate, profit):
        self.id = uuid.uuid4()
        self.back_test_info_id = back_test_info_id
        self.date_time = date_time
        self.total_money = total_money  # total = remain + marketValue
        self.remain = remain
        self.market_value = market_value
        self.money_rate = money_rate  # 资金利用率 (1 - remain/total_maoney)
        self.yield_rate = yield_rate  # 收益( (total-init) / init)
        self.profit = profit  # profit = total - init


class dot_utils:

    '''
        :param
            sample:记录模式
                0:当变化是记录
                >0:每调用sample次记录一次
    '''
    def __init__(self, db, back_test_info, sample=1):
        self.db = db
        self.back_test_info = back_test_info
        self.sample = sample
        self.dot_count = 0
        self.print_no = True
        ins = "insert into back_test_info (`id`, `strategy`, `name`, `test_time`, `start_time`, " \
              "`end_time`, `init_money`, `total_money`, `remain`, `profit`, `market_value`, " \
              "`trade_cnt`, `suc_cnt`, `total_profit`, `table_index`, `description`) " \
              "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur = self.db.cursor()

        try:
            cur.execute(ins, (back_test_info.id, back_test_info.strategy, back_test_info.name, back_test_info.test_time,
                              back_test_info.start_time, back_test_info.end_time, back_test_info.init_money,
                              back_test_info.total_money, back_test_info.remain, back_test_info.profit,
                              back_test_info.market_value, back_test_info.trade_cnt, back_test_info.suc_cnt,
                              back_test_info.total_profit, back_test_info.table_index, back_test_info.description))
            db.commit()
        except Exception as e:
            db.rollback()
            print("execte sql:'{}' error".format(ins))
            print(repr(e))
        finally:
            cur.close()

    def deal_dot(self, stock_code, stock_name, stock_cnt, price, now_time, is_buy=True):

        if self.print_no:
            print("deal_dot:{},code:{},cnt:{},price:{},time:{},is_buy{}".format(stock_name, stock_code, stock_cnt, price, now_time, is_buy))

        ins = "insert into deal_dot_{} (`id`, `back_test_info_id`, `stock_code`, `stock_name`, `stock_cnt`, `deal_time`,`price`, `is_buy`)" \
              "values (%s, %s, %s, %s, %s, %s, %s, %s)".format(self.back_test_info.table_index)
        cur = self.db.cursor()
        try:
            cur.execute(ins, (uuid.uuid4(), self.back_test_info.id, stock_code, stock_name, stock_cnt, now_time, price, is_buy))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print("execte sql:'{}' error".format(ins))
            print(repr(e))
        finally:
            cur.close()

    def real_count_dot(self, total_money, remain, market_value, profit, now_time):

        # if self.sample == 0:
        #     if self.pre_count is not None and self.pre_count.total_money == total_money \
        #         and self.pre_count.remain == remain

        self.dot_count += 1
        if self.dot_count % self.sample != 0:
            return

        ins = "insert into real_count_dot_{} (`id`, `back_test_info_id`, `date_time`, `total_money`, `remain`, `market_value`, `money_rate`, `yield_rate`, `profit`)" \
              "values (%s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.back_test_info.table_index)
        cur = self.db.cursor()
        try:
            cur.execute(ins, (uuid.uuid4(), self.back_test_info.id, now_time, total_money, remain, market_value,
                              (1-remain/total_money), (total_money-self.back_test_info.init_money)/self.back_test_info.init_money, profit))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print("execte sql:'{}' error".format(ins))
            print(repr(e))
        finally:
            cur.close()

def dot_test():
    db = mysql.connect(env.PC_LOCAL_MYSQL_HOST, env.PC_LOCAL_MYSQL_PORT, env.PC_LOCAL_MYSQL_USER,
                       env.PC_LOCAL_MYSQL_PSWD,
                       env.PC_LOCAL_MYSQL_DB)

    start_date = datetime.datetime(2016, 1, 1)
    end_date = datetime.datetime(2022, 1, 1)

    #配置起始资金
    account = ac.Account(1000000.0, 1000000.0, 1000000.0)


    #配置dot
    back_test_info = BackTestInfo('martin', start_date, end_date, account, '')
    dot = dot_utils(db, back_test_info)
    dot.deal_dot('0001234.XETE', 'test compain', 200, 100.1)
    dot.real_count_dot(2000000, 122.0, 123523, 2356.0)

if __name__ == '__main__':
    dot_test()
