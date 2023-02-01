import csv
import importlib
import json
import os
import random
import base64
import shutil
import sqlite3
import requests


# 响应
def F(code: str, massage: str | bool, data=None) -> json:
    if massage == True:
        massage = "success"
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


# 随机Id
def random_Id(folder_path):
    while True:
        num = random.randint(10000, 99999)
        if not os.path.exists(os.path.join(folder_path, str(num))):
            return num


# 获取文件夹内容
def get_all_files(folder_path, ignore_list):
    files = []
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)) and file not in ignore_list:
            files.append(file)
    return files


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
    def toPython(self, id, data: list, fileName: list, path=None) -> None:
        if path is None:
            path = f"./strategy/{id}/"
        for i in range(len(data)):
            if data[i] is not None:
                try:
                    result = data[i]
                except Exception as e:
                    print("UpDate_result", e)
                    result = data[i]
                with open(path + str(fileName[i]), 'w', encoding='utf-8') as f:
                    f.write(result)

    # 处理其他文件
    def otherFiles(self, id, data, path=None) -> None:
        if path is None:
            path = f"./strategy/{id}/"
        try:
            otherData, otherName = [], []
            for i in range(len(data)):
                otherName.append(data[i]["fileName"])
                otherData.append(data[i]["data"])
            self.toPython(id=id, data=otherData, fileName=otherName, path=path)
        except Exception as e:
            print(f"处理其他文件{e}")

    # 书写策略配置
    def writeConfig(self, id, Name: str, exchanges: list, config: list) -> bool:
        try:
            path = f"strategy/Lives/{id}/UserSetConfig.json"
            data = read_json(path)

            data["Name"] = str(Name)
            data["state"] = False
            data["exchanges"] = exchanges
            data["config"] = config

            write_json(path, data)
            return True
        except Exception as e:
            print(e)
            return False


# 获取IP地址
def get_local_ip() -> str:
    return requests.get('https://checkip.amazonaws.com').text.strip()


# 封装ws数据
def wsData(h: str, data: dict | None) -> dict:
    return {
        "h": h,
        "data": data,
    }


# 获取日志（页码，每页数量，开始时间）
def get_logs(id, page_num: int, page_size: int = 30, before_time: int = None) -> list:
    try:
        conn = sqlite3.connect(f"strategy/Lives/{id}/data/strategy.db")
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
def reda_chartCustom(id) -> list:
    try:
        # import strategy.code.chart as scc
        scc = importlib.import_module(f"strategy.Lives.{id}.chart")
        importlib.reload(scc)
        charts = scc.chart
        # 尝试读取csv文件
        for chart in charts:
            if chart["type"] == "pie":
                continue
            try:
                chart["data"] = []
                for chunk in read_csv(f"strategy/Lives/{id}/data/chartcus/{chart['key']}.csv"):
                    chart["data"] = chart["data"] + chunk
                # 判断第一行是否为空
                if not chart["data"][0]:
                    del chart["data"][0]
                print(chart["data"])
            except Exception as e:
                print(e)
                chart["data"] = []
        return charts
    except Exception as e:
        print(e)
        return []


# 读取收益日志
def get_all_profit_data(id, db_name=None):
    if db_name is None:
        db_name = f"./strategy/Lives/{id}/data/strategy.db"
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


# 解析上传文件
def parse_multipart_form_data(data):
    # 通过 content-type 获取分隔符
    content_type = 'multipart/form-data; boundary=----WebKitFormBoundarycdDjXRHDBneu2R7f'
    boundary = content_type.split('=')[-1]

    # 通过分隔符解析数据
    parts = data.split(boundary)
    parts = [p.strip() for p in parts if p.strip()]

    # 提取文件名和文件内容
    result = []
    for part in parts:
        headers, content = part.split('\r\n\r\n', 1)
        headers = headers.split('\r\n')
        filename = [header.split('=')[-1].strip() for header in headers if 'filename' in header][0]
        content = content.strip()
        result.append([filename, content])
    return result


def process_form_data(form_data):
    result = []
    lines = form_data.split("\r\n")
    start = None
    filename = None
    for i, line in enumerate(lines):
        if "filename" in line:
            if start is not None:
                end = i
                content = "".join(lines[start:end])
                result.append(content)
            filename = line.split('=')[-1].strip('"')
            start = i + 4
    end = len(lines) - 2
    content = "\n".join(lines[start:end])
    result.append([filename, content])
    return result


# 拷贝文件夹
def copy_folder_contents(src_folder, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    for item in os.listdir(src_folder):
        s = os.path.join(src_folder, item)
        d = os.path.join(dest_folder, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, False, None)
        else:
            shutil.copy2(s, d)


# 拷贝文件夹文件
def copy2_folder_all(src_folder, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    for item in os.listdir(src_folder):
        s = os.path.join(src_folder, item)
        d = os.path.join(dest_folder, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)


# 拷贝文件夹文件存在覆盖
def copy3_folder_all(src_folder, dst_folder):
    exclude_files = ["UserSetConfig.json"]
    for root, dirs, files in os.walk(src_folder):
        for file in files:
            if file not in exclude_files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst_folder, file)
                shutil.copy2(src_file, dst_file)
