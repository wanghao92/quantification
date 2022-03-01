import db.mysql_utils as mysql
import martin as mrt
import deal.trade_utils as tru
import conf.env as env
import model.account as ac


def martin_jq():

    db = mysql.connect(env.PC_LOCAL_MYSQL_HOST, env.PC_LOCAL_MYSQL_PORT, env.PC_LOCAL_MYSQL_USER,
                       env.PC_LOCAL_MYSQL_PSWD,
                       env.PC_LOCAL_MYSQL_DB)

    trade = tru.JoinQuantSimulate(db)

    account = ac.Account(100000000, 100000000, 100000000, 0, 0, 0, 0, 0, 0)

    hold_shares = []

    martin = mrt.Martin(account, hold_shares, trade)

if __name__ == '__main__':

    martin_jq()

