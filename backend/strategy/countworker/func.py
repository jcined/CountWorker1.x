import json
import os
import time
import functools
from . import ceiling
import func

# 获取实盘id
live_id = None
lives_data = func.read_json(f'./strategy/Lives.json')
pid = os.getpid()
for k,v in lives_data.items():
    if str(v["pid"]) == str(pid):
        live_id = k

# 日志输出
def log(*info, sep='', type='info'):
    times = int(time.time() * 1000)
    message = sep.join([json.dumps(i) if isinstance(i, (dict, list, tuple, set)) else str(i) for i in info])
    ceiling.insertLog(time=times, type=type, info=message, live_id=live_id)
    ceiling.send_request("/s/log", {
        "time": times,
        "type": type,
        "info": message,
    },live_id=live_id)


# 清除日志
def clearLog(n=None):
    db = ceiling.SQLiteOperator(live_id)
    if n is None:
        db.delete_data("logs")
    else:
        db.delete_data("logs", "ORDER BY time ASC LIMIT {}".format(n))
    db.close()


# 打印收益
def logProfit(value: float) -> None:
    db = ceiling.SQLiteOperator(live_id)
    columns = "time, value"
    times = int(time.time() * 1000)
    values = f"'{times}', '{value}'"
    db.insert_data("profit", columns, values)
    db.close()
    ceiling.send_request("/s/profit", {
        "time": times,
        "value": value,
    },live_id=live_id)


# 清空收益日志
def logProfitClear(n=0) -> None:
    db = ceiling.SQLiteOperator(live_id)
    if n == 0:
        db.delete_data("profit")
    else:
        db.delete_data("profit", f"WHERE id NOT IN (SELECT id FROM profit ORDER BY id DESC LIMIT {n})")
    db.close()


# 执行器
class actuator:
    """
    执行器actuator类是一个用来修饰函数的修饰器。它允许函数在满足指定条件后才执行，或者在满足指定条件后才再次执行。
    参数:
        times: 表示函数最多可以执行的次数。默认值为1。
        interval: 表示时间间隔。默认值为0。单位为秒。
    """

    def __init__(self, times=1, interval=0) -> None:
        self.times = times
        self.count = 0
        self.interval = interval
        self.last_time = time.time()

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            # 如果时间间隔完毕或第一次执行
            if self.interval == 0 or time.time() - self.last_time >= self.interval or self.count == 0:
                if self.count < self.times:
                    result = func(*args, **kwargs)
                    if result:
                        self.count += 1
                        self.last_time = time.time()
            return result

        return wrapper
