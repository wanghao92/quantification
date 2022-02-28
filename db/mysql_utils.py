import pymysql
import conf.env as env


def connect(localhost, port, user, pswd, dbName):
    try:
        db = pymysql.connect(host = localhost, port = port, user = user, password = pswd, database = dbName, cursorclass = pymysql.cursors.DictCursor)
        print("connect mysql[host:{}, port:{}] success!".format(localhost, port))
    except Exception:
        raise Exception("connect mysql error")

    return db

def excute_sql(db, sql):
    try:
        cur = db.cursor()
        cur.execute(sql)
        db.commit()
    except Exception:
        db.rollback()
        print("execte sql:'{}' error".format(sql))


if __name__ == '__main__':
    db = connect(env.PC_LOCAL_MYSQL_HOST, env.PC_LOCAL_MYSQL_PORT, env.PC_LOCAL_MYSQL_USER, env.PC_LOCAL_MYSQL_PSWD, env.PC_LOCAL_MYSQL_DB)
    excute_sql(db)
    db.close()