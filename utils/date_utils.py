import datetime
import time
import numpy as np
import utils.trade_date as trd


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

def next_deal_date(now_time):
    now_time += datetime.timedelta(days=1)

    while trd.DEAL_DATE[now_time.year - 2005][now_time.month - 1][now_time.day - 1] == 0:
        now_time += datetime.timedelta(days=1)

    return now_time


class DealTimeGenerator:
    '''
        交易时间产生器
        period：产生周期，单位秒
    '''

    def __init__(self, start_date, end_date, period=60):
        self.start_date = start_date
        self.end_date = end_date
        self.period = period
        self.now_date = start_date

    def generate(self, period=None):
        if period is None:
            self.now_date += datetime.timedelta(seconds=self.period)
        else:
            self.now_date += datetime.timedelta(seconds=period)

        up_start = datetime.datetime(self.now_date.year, self.now_date.month, self.now_date.day, 9, 30, 0)
        up_end = datetime.datetime(self.now_date.year, self.now_date.month, self.now_date.day, 11, 30, 0)
        down_start = datetime.datetime(self.now_date.year, self.now_date.month, self.now_date.day, 13, 0, 0)

        if self.now_date < up_start:
            self.now_date = up_start
        elif up_end <= self.now_date < down_start:
            self.now_date = down_start
        elif self.now_date.hour >= 15:
            self.now_date = up_start
            self.now_date += datetime.timedelta(days=1)

        if is_deal_date(self.now_date) is False:
            self.now_date = next_deal_date(self.now_date)

        if self.now_date > self.end_date:
            return None

        return self.now_date


def deal_time_generator_test():
    generator = DealTimeGenerator(datetime.datetime(2021, 1, 1),
                                  datetime.datetime(2021, 1, 5), 60)
    day = generator.generate()
    while day is not None:
        print(day)
        day = generator.generate()

'''
    produce deal_date数据[年][月][日]
'''


def produce_deal_date():
    data = np.zeros((20, 12, 31)).astype(int)
    np.set_printoptions(threshold=1000000)

    start = datetime.datetime(2005, 1, 1)
    end = datetime.datetime(2025, 1, 1)
    deals = trd.DEAL_DATA_STR.split(",")
    for day in deals:
        d = day.split('-')
        data[int(d[0]) - 2005][int(d[1]) - 1][int(d[2]) - 1] = 1
    print(data)


if __name__ == "__main__":
    # produce_deal_date()
    deal_time_generator_test()