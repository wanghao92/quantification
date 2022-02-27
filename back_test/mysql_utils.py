import pymysql

def connect(localhost, port, user, pswd, dbName):
    try:
        db = pymysql.connect(host = localhost, port = port,user = user, password = pswd, database = dbName)
        print('connect mysql success!')
    except Exception:
        raise Exception("connect mysql error")

    return db

def insert(db):
    ins = "insert into test (id, stock_name, start_time, end_time, price)" \
          "values ('12323445', '中航集团', '2020-10-20', '2022-1-1', 345)"
    try:
        cur = db.cursor()
        cur.execute(ins)
        db.commit()
    except Exception:
        db.rollback()
        print('insert error')


if __name__ == '__main__':
    db = connect('localhost', 3306, 'root', 'admin123', 'stock')
    insert(db)
    db.close()