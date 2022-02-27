import datetime

import jqdatasdk as jq
import pandas as pd
import db.mysql_utils as mysql
import conf.env as env

CREATE_BAR_SQL = "create table IF NOT EXISTS `{}`(" \
                 "`date_time` datetime comment '日期'," \
                 "`open` int comment '开盘'," \
                 "`close` int comment '收盘'," \
                 "`low` int comment '最低价'," \
                 "`high` int  comment '最高价'," \
                 "`volume` int comment '成交数'," \
                 "`money` int comment '成交金额'," \
                 "key index_date_time (`date_time`)" \
                 ")ENGINE=InnoDB DEFAULT CHARSET=utf8;"

'''
    更新所有股票基本信息
    type: stock(股票)，index(指数)，etf(ETF基金)，
    fja（分级A），fjb（分级B），fjm（分级母基金），mmf（场内交易的货币基金）,
    open_fund（开放式基金）, bond_fund（债券基金）, stock_fund（股票型基金）, 
    QDII_fund（QDII 基金）, money_market_fund（场外交易的货币基金）, 
    mixture_fund（混合型基金）, options(期权)
'''
def security_info_update(db, types=None):
    if types is None:
        types = ['stock', 'etf']
    for type in types:
        df = jq.get_all_securities([type])
        cur = db.cursor()
        ins = "replace into security_info (`stock_code`, `display_name`, `simple_name`, `stock_type`, `start_date`, `end_date`)" \
              " values (%s, %s, %s, %s, %s, %s)"
        # security_infos = []
        # for index, row in df.iterrows():
        #     security_infos.append((index, row['display_name'], row['name'], row['type'], row['start_date'], row['end_date']))
        security_infos = ((index, row['display_name'], row['name'], row['type'], row['start_date'], row['end_date']) for
                          index, row in df.iterrows())
        try:
            cur.executemany(ins, security_infos)
            db.commit()
        except Exception as e:
            db.rollback()
            print("execte sql:'{}' error".format(ins))
            print(repr(e))
        finally:
            cur.close()


'''
获取历史价格数据
get_bar()
security: 标的代码，支持单个及多个标的
count: 大于0的整数，表示获取bar的个数。如果行情数据的bar不足count个，返回的长度则小于count个数。
unit: bar的时间单位
当unit为'1m', '5m', '15m', '30m', '60m', '120m', '1d', '1w'(一周), '1M'（一月）标准bar时，bar的分割方式与主流股票软件类似，期货的bar各平台也许稍微有差异，我们与文华接近；
当unit为非上述标准bar时('xm', 例如'3m')，只支持分钟级别的, x需要小于240，以每天的开盘为起始点，每x分钟为一条bar；
fields: 获取数据的字段， 支持如下值：'date', 'open', 'close', 'high', 'low', 'volume', 'money', 'open_interest'（期货持仓量），factor(复权因子)。
include_now: 取值True 或者False。 表示是否包含当前bar, 比如策略时间是9:33，unit参数为5m， 如果 include_now=True,则返回9:30-9:33这个分钟 bar。
end_dt：查询的截止时间，支持的类型为datetime.datetime或None，默认为datetime.now()。
fq_ref_date：复权基准日期，为None时为不复权数据。
如果用户输入 fq_ref_date = None, 则获取到的是不复权的数据
如果用户想获取后复权的数据，可以将fq_ref_date 指定为一个很早的日期，比如 datetime.date(2000, 1, 1)
定点复权，以某一天价格点位为参照物，进行的前复权或后复权。设置为当前时间（例如 datetime.datetime.now()）即返回前复权数据 ; 设置为指定时间（非上述日期）
df：默认为True，指定返回数据为dataframe结构；当df=False的时候，传入单个标的时，返回一个np.ndarray，多个标的返回一个字典，key是code，value是np.array
'''
BAR_COUNT_PER_DAY = 4 * 60  #分钟级行情数量，每天交易4个小时
'''
    force_update:True:强制更新，将会删除原表，重新创建新表，
                False:增量更新，计算表中数据日期的范围，和需要更新的范围，只更新不包含的日期范围
'''
def price_bar_update(db, stock_code, start, end, unit = '1m', force_update = False):
    units = {
        '1m'   : 60,
        '5m'   : 60*5,
        '15m'  : 60*15,
        '30m'  : 60*30,
        '60'   : 60*60,
        '12m'  : 60*60*2,
        '1d'   : 60*60*4,
    }
    count = (int)((end - start).seconds / units.get(unit)) + 1

    table_name = stock_code.replace('.', '_')
    cur = db.cursor()
    cur.execute(CREATE_BAR_SQL.format(table_name))

    df = jq.get_bars(stock_code, count, '1m', ['date', 'open', 'close', 'low', 'high', 'volume', 'money'], False, end)
    bars_infos = ((row['date'] * 100, row['open'] * 100, row['close'] * 100, row['low'] * 100, row['high'] * 100, row['volume'], row['money']) for row in df.iterrows())
    ins = "replace into {} (`date_time`, `open`, `close` `low`, `high`, `volume`, `money`)" \
          " values (%s, %s, %s, %s, %s, %s, %s)"
    try:
        cur.executemany(ins, tuple(map(int, bars_infos)))
        db.commit()
    except Exception as e:
        db.rollback()
        print("execte sql:'{}' error".format(ins))
        print(repr(e))
    finally:
        cur.close()


# 查询当天剩余可查询次数
def stub_query_reamin_count():
    jq.auth(env.JOIN_QUANT_USER, env.JOIN_QUANT_PSWD)
    count = jq.get_query_count()
    print(count)


# 更新所有股票信息
def stub_update_all_security_info():
    jq.auth(env.JOIN_QUANT_USER, env.JOIN_QUANT_PSWD)

    db = mysql.connect(env.PC_LOCAL_MYSQL_HOST, env.PC_LOCAL_MYSQL_PORT, env.PC_LOCAL_MYSQL_USER,
                       env.PC_LOCAL_MYSQL_PSWD,
                       env.PC_LOCAL_MYSQL_DB)

    security_info_update(db)
    db.close()

# 更新行情信息
def stub_update_bar():
    jq.auth(env.JOIN_QUANT_USER, env.JOIN_QUANT_PSWD)

    db = mysql.connect(env.PC_LOCAL_MYSQL_HOST, env.PC_LOCAL_MYSQL_PORT, env.PC_LOCAL_MYSQL_USER,
                       env.PC_LOCAL_MYSQL_PSWD,
                       env.PC_LOCAL_MYSQL_DB)
    price_bar_update(db, '000001.XSHE', datetime.datetime(2022, 2, 24, 9, 30, 0), datetime.datetime(2022, 2, 24, 16, 30, 0))


if __name__ == '__main__':

    # stub_update_all_security_info()

    stub_update_bar()