import datetime
import time

#获取时间戳秒
def get_sec_stamp(now_time = None):
    if now_time == None:
        return time.time()
    else:
        return time.mktime(now_time.timetuple())
