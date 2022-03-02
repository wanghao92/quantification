import datetime

import db.mysql_utils as mysql
import martin as mrt
import deal.trade_utils as tru
import conf.env as env
import model.account as ac
import utils.date_utils as du


def martin_jq():

    db = mysql.connect(env.PC_LOCAL_MYSQL_HOST, env.PC_LOCAL_MYSQL_PORT, env.PC_LOCAL_MYSQL_USER,
                       env.PC_LOCAL_MYSQL_PSWD,
                       env.PC_LOCAL_MYSQL_DB)

    trade = tru.JoinQuantSimulate(db)

    account = ac.Account(100000000, 100000000, 100000000)

    hold_shares = []
    hold_share_512800 = mrt.HoldShare('512800.XSHG', '银行etf', 118)

    hold_shares.append(hold_share_512800)
    martin = mrt.Martin(account, hold_shares, trade)

    start_date = datetime.datetime(2016, 1, 1)
    end_date = datetime.datetime(2022, 1, 1)

    time_generator = du.DealTimeGenerator(start_date, end_date)

    now_time = time_generator.generate()
    while now_time is not None:
        martin.set_time_now(now_time)
        martin.run()
        now_time = time_generator.generate()

if __name__ == '__main__':

    martin_jq()

