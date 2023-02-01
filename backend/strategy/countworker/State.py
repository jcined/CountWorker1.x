from .ceiling import *
from .func import *
import copy
import csv
import func

# 获取实盘id
live_id = None
lives_data = func.read_json(f'./strategy/Lives.json')
pid = os.getpid()
for k,v in lives_data.items():
    if str(v["pid"]) == str(pid):
        live_id = k

# 策略状态
class Chart:
    refresh = 10  # 状态刷新时间

    State = []  # 状态

    lastTime = time.time() - refresh - 5

    initState = []

    __lastState = []

    @classmethod
    def __resetState__(cls) -> None:
        if time.time() - cls.lastTime >= cls.refresh:
            if cls.State != cls.__lastState:
                # 发送信息
                cls.__lastState = copy.deepcopy(cls.State)
                send_request("/s/state", {
                    "state": cls.State
                },live_id=live_id)
                cls.lastTime = time.time()
        # 重置对象
        cls.State = copy.deepcopy(cls.initState)

    file_list = {}  # 图表文件

    pie_data = {}  # pie数据

    @classmethod
    def Chart(cls, keyname, data) -> None:
        if keyname not in cls.file_list:
            # 如果是pie数据
            if keyname in cls.pie_data:
                cls.pie_data[keyname] = data
                send_request("/s/chart", {
                    "index": keyname,
                    "type": "pie",
                    "newdata": data,
                },live_id=live_id)
                return
            error = f"图表{keyname}未注册"
            log(error, type="error")
            raise ValueError(error)
        list_data = [int(time.time() * 1000), data]
        with open(f"./strategy/data/chartcus/{keyname}.csv", 'a', newline='') as f:
            writer = csv.writer(f)
            data = list(map(str, list_data))
            writer.writerow(data)
        send_request("/s/chart", {
            "index": keyname,
            "type": "line",
            "newdata": list_data,
        },live_id=live_id)
