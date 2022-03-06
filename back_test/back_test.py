import datetime

import db.mysql_utils as mysql
import martin as mrt
import deal.trade_utils as tru
import conf.env as env
import model.account as ac
import utils.date_utils as du
import record.dot as rd

def martin_jq():

    db = mysql.connect(env.PC_LOCAL_MYSQL_HOST, env.PC_LOCAL_MYSQL_PORT, env.PC_LOCAL_MYSQL_USER,
                       env.PC_LOCAL_MYSQL_PSWD,
                       env.PC_LOCAL_MYSQL_DB)

    #配置交易时间
    start_date = datetime.datetime(2018, 1, 1)
    end_date = datetime.datetime(2022, 1, 1)
    time_generator = du.DealTimeGenerator(start_date, end_date)

    #配置交易器
    trade = tru.JoinQuantSimulate(db)

    #配置起始资金
    account = ac.Account(1000000.0, 1000000.0, 1000000.0)

    #配置持仓
    hold_shares = []
    hold_share_512800 = mrt.HoldShare('512800.XSHG', '银行etf', 1.18)
    hold_shares.append(hold_share_512800)

    #配置dot
    back_test_info = rd.BackTestInfo('martin', start_date, end_date, account, '', 0)
    dot = rd.dot_utils(db, back_test_info)

    #配置策略
    martin = mrt.Martin(account, hold_shares, trade, dot)

    #交易loop
    now_time = time_generator.generate()
    while now_time is not None:
        martin.set_time_now(now_time)
        martin.run()
        now_time = time_generator.generate()

if __name__ == '__main__':

    martin_jq()

