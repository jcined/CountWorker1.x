import csv
import json
import os
import random
import base64
import socket
import sqlite3


# 响应
def F(code: str, massage: str | bool, data: list | dict | str | int | Exception | None = None) -> json:
    if massage == True: massage = "success"
    return json.dumps({
        "code": code,
        "massage": massage,
        "data": data,
    })


# token验证
def verToken(token, ACCOUNT_PATH):
    # 读取account.json
    accountData = read_json(ACCOUNT_PATH)
    # 验证
    if str(accountData["cookie"]) == str(token):
        return True
    return False


# 随机字符
def generate_random_str(randomlength):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length = len(base_str) - 1
    for i in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


# 读json
def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


# 写json
def write_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


class UpDate:
    # 转为python文件
    def toPython(self, data: list, fileName: list, path: str = "./strategy/code/") -> None:
        for i in range(len(data)):
            result = base64.b64decode(data[i].split(',')[1]).decode()
            with open(path + str(fileName[i]), 'w', encoding='utf-8') as f:
                f.write(result)

    # 处理其他文件
    def otherFiles(self, data, path: str = "./strategy/code/") -> None:
        try:
            otherData, otherName = [], []
            for i in range(len(data)):
                otherName.append(data[i]["fileName"])
                otherData.append(data[i]["data"])
            self.toPython(data=otherData, fileName=otherName, path=path)
        except:
            pass

    # 书写策略配置
    def writeConfig(self, Name: str, exchanges: list, config: list) -> bool:
        try:
            path = "./strategy/code/UserSetConfig.json"
            data = read_json(path)

            data["Name"] = str(Name)
            data["state"] = False
            data["exchanges"] = exchanges
            data["config"] = config

            write_json(path, data)
            return True
        except:
            return False


# 获取IP地址
def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


# 封装ws数据
def wsData(h: str, data: dict | None) -> dict:
    return {
        "h": h,
        "data": data,
    }


# 获取日志（页码，每页数量，开始时间）
def get_logs(page_num: int, page_size: int = 30, before_time: int = None) -> list:
    try:
        conn = sqlite3.connect("./strategy/data/strategy.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        offset = (page_num - 1) * page_size
        if before_time:
            where = f"WHERE time < '{before_time}'"
        else:
            where = ""
        cursor.execute(f"SELECT * FROM logs {where} ORDER BY time DESC LIMIT {page_size} OFFSET {offset}")
        logs = [dict(log) for log in cursor]
        conn.close()
        return logs
    except Exception as e:
        print(e)
        return []


# 读取csv文件
def read_csv(file_path, chunk_size=1024 * 1024):
    rows = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        while True:
            chunk = list(reader)
            if not chunk:
                break
            for row in chunk:
                row[0] = int(row[0])
                row[1] = float(row[1])
                rows.append(row)
            if len(rows) >= chunk_size:
                yield rows
                rows = []
    if rows:
        yield rows


# 读取图表配置信息
def reda_chartCustom() -> list:
    try:
        import strategy.code.chart as scc
        charts = scc.chart
        # 尝试读取csv文件
        for chart in charts:
            if chart["type"] == "pie":
                continue
            try:
                chart["data"] = []
                for chunk in read_csv(f"./strategy/data/chartcus/{chart['key']}.csv"):
                    chart["data"] = chart["data"] + chunk
                # 判断第一行是否为空
                if chart["data"][0] == []:
                    del chart["data"][0]
                print(chart["data"])
            except:
                chart["data"] = []
        return charts
    except Exception as e:
        print(e)
        return []


# 读取收益日志
def get_all_profit_data(db_name="./strategy/data/strategy.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profit")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


# 读取ip和uid
def SetSeverConfig():
    ip = get_local_ip()
    pid = os.getpid()
    write_json("./SeverConfig.json", {
        "ip": ip,
        "pid": pid,
    })

