import datetime
import time
import numpy as np
import trade_date as trd
# 获取时间戳秒
def get_sec_stamp(now_time=None):
    if now_time == None:
        return time.time()
    else:
        return time.mktime(now_time.timetuple())


def is_deal_time(now_time):
    up_start = datetime.datetime(now_time.year, now_time.month, now_time.day, 9, 30, 0)
    up_end = datetime.datetime(now_time.year, now_time.month, now_time.day, 11, 30, 0)
    down_start = datetime.datetime(now_time.year, now_time.month, now_time.day, 13, 0, 0)
    down_end = datetime.datetime(now_time.year, now_time.month, now_time.day, 15, 0, 0)
    if up_start < now_time < up_end:
        return True
    elif down_start < now_time < down_end:
        return True
    else:
        return False

def is_deal_date(now_time):
    return trd.DEAL_DATE[now_time.year - 2005][now_time.month - 1][now_time.day - 1] == 1

def produce_deal_date():
    data = np.zeros((20, 12, 31)).astype(int)
    np.set_printoptions(threshold = 1000000)

    start = datetime.datetime(2005, 1, 1)
    end = datetime.datetime(2025, 1, 1)
    deals = trd.DEAL_DATA_STR.split(",")
    for day in deals:
        d = day.split('-')
        data[int(d[0]) - 2005][int(d[1]) - 1][int(d[2]) - 1] = 1
    print(data)


if __name__ == "__main__":
    produce_deal_date()

