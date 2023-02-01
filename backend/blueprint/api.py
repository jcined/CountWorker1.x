import datetime
import signal
import psutil
from flask import Blueprint, request, Response, send_file
from func import *
import json
import func
import os
import subprocess
import importlib

api = Blueprint('api', __name__)


class StrategyThread:
    p = None

    @classmethod
    def __changeState(cls, id, to: bool) -> None:
        path = f"./strategy/Lives/{id}/UserSetConfig.json"
        Config = func.read_json(path)
        Config["state"] = to
        func.write_json(path, Config)

    @classmethod
    def run(cls, id) -> None:
        cls.p = subprocess.Popen(["python", f"./strategy/Lives/{id}/run.py"])
        cls.save_var(id, cls.p.pid)  # 保存到本地
        cls.__changeState(id, True)

    @classmethod
    def stop(cls, id) -> None:
        pid = cls.load_var(id)
        current_process = psutil.Process(pid)
        script_name = current_process.cmdline()[-1]
        if script_name == f'./strategy/Lives/{id}/run.py':
            os.kill(pid, signal.SIGTERM)
            cls.__changeState(id, False)
            cls.save_var(id, None)
        else:
            cls.save_var(id, None)
            raise ValueError("不是目标进程")

    @classmethod
    def save_var(cls, id, var, filename=f"./strategy/Lives.json"):
        data = func.read_json(filename)
        data[id]["pid"] = var
        func.write_json(filename, data)

    @classmethod
    def load_var(cls, id, filename=f"./strategy/Lives.json"):
        try:
            return func.read_json(filename)[id]["pid"]
        except Exception as e:
            print(e)
            return None


@api.before_request
def verCookie():
    token = request.cookies.get("token")
    if request.path == "/api/login":
        return
    elif not token:
        return Response(F("1001", "The request is invalid because the token is missing")), 401
    # 验证
    if not func.verToken(token, "./admin/account.json"):
        return Response(F("1002", "token verification fails")), 401


# 登录
@api.route('/login', methods=["POST"])
def login():
    data = json.loads(request.get_data())
    account = str(data["account"]["_value"])
    password = str(data["password"]["_value"])
    print(account, password)
    # 读取account.json
    accountData = func.read_json("./admin/account.json")
    # 验证
    if str(accountData["account"]) == account and str(accountData["password"]) == password:
        # 设置cookie
        cookie = func.generate_random_str(15)
        resp = Response(F("0000", True))  # 响应体
        resp.set_cookie("token", cookie, max_age=60 * 60 * 24 * 30)
        # 写入account.json
        accountData["cookie"] = cookie
        func.write_json("./admin/account.json", accountData)
        # success
        return resp, 200
    # failed
    return Response(F("1000", "Login failed")), 403


# 初始化信息
@api.route('/data', methods=["GET"])
def data():
    projects_data = func.read_json("./strategy/Projects.json")
    projects_names = []
    for key, value in projects_data.items():
        projects_names.append([value["name"], value["time"], key])
    ignore_files = ['__init__.py', 'function.py', 'run.py', 'UserSetConfig.json']
    projects = []
    for i in projects_names:
        id = i[2]
        files = []
        result = func.get_all_files(f'./strategy/{id}', ignore_files)
        for j in result:
            files.append({
                "name": j,
                "path": f"{id}/{j}"
            })
        projects.append({
            "name": i[0],
            "time": i[1],
            "id": id,
            "files": files,
        })
    lives_data = func.read_json("./strategy/Lives.json")
    lives = []
    for key, value in lives_data.items():
        lives.append({
            "name": value["name"],
            "time": value["time"],
            "id": key,
            "projectId": {
                "name": projects_data[value["id"]]["name"],
                "id": value["id"],
            },
            "state": value["pid"] is not None
        })
    data = {
        "projects": projects,
        "lives": lives,
    }
    return Response(F("0000", True, data)), 200


# 获取代码
@api.route('/code', methods=["GET"])
def code():
    path = request.args.get('path')
    print(path)
    with open(f"./strategy/{path}", "r", encoding='utf-8') as file:
        content = file.read()
    return Response(F("0000", True, content)), 200


# 新建实盘
@api.route('/newlive', methods=["GET"])
def newLive():
    id = request.args.get('id')
    name = request.args.get('name')

    live_id = func.random_Id("./strategy/Lives")
    live_content_path = f"./strategy/Lives/{live_id}"
    func.copy_folder_contents("./strategy/Lives/tem", live_content_path)
    func.copy2_folder_all(f"./strategy/{id}", live_content_path)
    lives_data = func.read_json("./strategy/Lives.json")
    lives_data[live_id] = {
        "pid": None,
        "name": name,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "id": id,
    }
    func.write_json(filename="./strategy/Lives.json", data=lives_data)
    try:
        scc = importlib.import_module(f"strategy.Lives.{live_id}.config")
        importlib.reload(scc)
        config = {
            "Name": name,
            "state": False,
            "stateCus": [],
            "profit": [],
            "sysData": [],
            "chartCustom": [],
            "id": live_id,
        }
        try:
            config["exchanges"] = scc.exchanges
        except Exception as e:
            print(f"184:{e}")
            config["exchanges"] = []
        try:
            config["config"] = scc.config
            print(scc.config)
        except Exception as e:
            print(f"190:{e}")
            config["config"] = []
        print(config)
        func.write_json(f"./strategy/Lives/{live_id}/UserSetConfig.json", config)
    except Exception as e:
        print(e)
        return Response(F("1004", "Failed to write configuration information")), 400
    return Response(F("0000", True)), 200


# 删除实盘
@api.route('/delive', methods=["GET"])
def delive():
    id = request.args.get('id')
    lives_data = func.read_json(f"./strategy/Lives.json")
    if lives_data[id]["pid"] is None:
        shutil.rmtree(f"./strategy/Lives/{id}")
        del lives_data[id]
        func.write_json(f"./strategy/Lives.json", data=lives_data)
        return Response(F("0000", True)), 200
    return Response(F("10015", "Failed to delete live")), 200


# 启动策略
@api.route('/start', methods=["GET"])
def start():
    id = request.args.get('id')
    StrategyThread.run(id)  # 运行策略
    print("运行策略")
    return Response(F("0000", True)), 200


# 停止策略
@api.route('/stop', methods=["GET"])
def stop():
    id = request.args.get('id')
    try:
        StrategyThread.stop(id)  # 停止策略
    except Exception as e:
        print(e)
        return Response(F("1007", "Stop failed")), 400
    return Response(F("0000", True)), 200


# 初始化策略信息
@api.route('/init', methods=["GET"])
def init():
    id = request.args.get('id')
    print(f"初始化策略信息 id:{id}")
    try:
        Config = func.read_json(f"./strategy/Lives/{id}/UserSetConfig.json")
        result = {
            "Name": Config["Name"],
            "exchanges": Config["exchanges"],
            "config": Config["config"],
            "state": Config["state"],
            "profit": func.get_all_profit_data(id),
            "sysData": [],
            "chartCustom": func.reda_chartCustom(id),
            "stateCustom": Config["stateCus"],
            "Logs": func.get_logs(id, page_num=1),
        }
        return Response(F("0000", True, result)), 200
    except Exception as e:
        print(e)
        return Response(F("1004", "Failed to write configuration information")), 400


# 新建项目
@api.route('/newproject', methods=["GET"])
def newproject():
    name = request.args.get('name')
    id = random_Id("./strategy")
    src_folder = "./strategy/tem"
    dest_folder = f"./strategy/{id}"
    func.copy_folder_contents(src_folder, dest_folder)
    data = func.read_json(filename="./strategy/Projects.json")
    data[str(id)] = {
        "name": name,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    func.write_json(filename="./strategy/Projects.json", data=data)
    return Response(F("0000", True)), 200


# 新建文件
@api.route('/newfile', methods=["GET"])
def newfile():
    id = request.args.get('id')
    name = request.args.get('name')
    filename = f"./strategy/{id}/{name}"
    if os.path.exists(filename):
        return Response(F("10014", "New file failed")), 400
    try:
        with open(filename, "w") as file:
            file.write("")
    except Exception as e:
        print("newfile", e)
        return Response(F("10014", "New file failed")), 400
    return Response(F("0000", True)), 200


# 上传
@api.route('/uploadfile', methods=["POST"])
def uploadFile():
    id = request.args.get('id')
    data = request.get_data().decode()
    result = func.process_form_data(data)[0]
    print(result)
    filename = result[0].strip('"')
    with open(f"./strategy/{id}/{filename}", 'w', encoding='utf-8') as f:
        f.write(result[1])
    return Response(F("0000", True)), 200


# 下载
@api.route('/download', methods=["GET"])
def download():
    id = request.args.get('id')
    file = request.args.get('file')
    # 下载文件
    return send_file(f"./strategy/{id}/{file}", as_attachment=True)


# 删除
@api.route('/delete', methods=["GET"])
def delete():
    id = request.args.get('id')
    file = request.args.get('file')
    data = func.read_json(filename="./strategy/Projects.json")
    exist_live = False
    lives_data = func.read_json("./strategy/Lives.json")
    for k, v in lives_data.items():
        if str(v["id"]) == id:
            exist_live = True
            break
    if not exist_live:
        if file == "null":
            ids = [str(id)] if "," not in id else [str(i) for i in id.split(",")]
            for id in ids:
                try:
                    shutil.rmtree(f"./strategy/{id}")
                    del data[id]
                    func.write_json(filename="./strategy/Projects.json", data=data)
                except Exception as e:
                    print("delete", e)
                    return Response(F("10012", "Failed to delete policy")), 400
        else:
            files = [str(file)] if "," not in id else [str(i) for i in file.split(",")]
            for file in files:
                try:
                    os.remove(f"./strategy/{id}/{file}")
                except Exception as e:
                    print("delete", e)
                    return Response(F("10013", "Failed to delete file")), 400
        return Response(F("0000", True)), 200
    return Response(F("10016", "Failed to delete project because of live")), 200


# 重命名
@api.route('/rename', methods=["GET"])
def rename():
    id = request.args.get('id')
    file = request.args.get('file')
    change = request.args.get('change')
    data = func.read_json(filename="./strategy/Projects.json")
    if file == "null":
        try:
            data[id]["name"] = change
            func.write_json(filename="./strategy/Projects.json", data=data)
            return Response(F("0000", True)), 200
        except Exception as e:
            print("rename", e)
            return Response(F("10010", "Rename policy failed")), 400
    else:
        try:
            os.rename(f"./strategy/{id}/{file}", f"./strategy/{id}/{change}")
            return Response(F("0000", True)), 200
        except Exception as e:
            print("rename", e)
            return Response(F("10010", "Rename file failed")), 400


# 上传策略文件
@api.route('/upload', methods=["POST"])
def upload():
    id = request.args.get('id')
    data = json.loads(request.get_data())
    # 其他文件处理
    func.UpDate().otherFiles(id=id, data=data["Files"]["other"])
    # 读取config.py并创建json
    is_reConfig = False
    for i in data["Files"]["other"]:
        if i["fileName"] == "config.py":
            is_reConfig = True
    if is_reConfig:
        try:
            scc = importlib.import_module(f"strategy.{id}.config")
            importlib.reload(scc)
            config = func.read_json(f"strategy/{id}/UserSetConfig.json")
            config["Name"] = scc.name
            try:
                config["config"] = scc.config
                print(scc.config)
            except Exception as e:
                print(f"190:{e}")
                config["config"] = []
            print(config)
            func.write_json(f"strategy/{id}/UserSetConfig.json", config)
        except Exception as e:
            print(f"196:{e}")
            return Response(F("1004", "Failed to write configuration information")), 400
    return Response(F("0000", True)), 200


# 更新策略配置
@api.route('/update', methods=["POST"])
def update():
    id = request.args.get('id')
    data = json.loads(request.get_data())

    try:
        Name = data["Name"]
        exchanges = data["exchanges"]
        config = data["config"]
        # 提取config type
        config_types = []
        for v in config:
            config_types.append(v["type"])
        # 提取项目 UserSetConfig
        UserSetConfig_types = []
        Project_id = func.read_json("./strategy/Lives.json")[id]["id"]
        Project_config = func.read_json(f"./strategy/{Project_id}/UserSetConfig.json")["config"]
        for v in Project_config:
            UserSetConfig_types.append(v["type"])
    except:
        return Response(F("1005", "Interface missing parameter")), 400

    # 书写策略配置
    if not func.UpDate().writeConfig(
            id=id,
            Name=Name,
            exchanges=exchanges,
            config=config,
    ): return Response(F("1004", "Failed to write configuration information")), 400

    # 更新策略
    if config_types != UserSetConfig_types:
        shutil.copy(f"./strategy/{Project_id}/UserSetConfig.json", f"./strategy/Lives/{id}")
    func.copy3_folder_all(f"./strategy/{Project_id}", f"./strategy/Lives/{id}")

    return Response(F("0000", True)), 200


# 获取更多日志
@api.route('/get-logs', methods=["GET"])
def get_logs():
    id = request.args.get('id')
    page = request.args.get('page')
    before_time = request.args.get('before_time')
    return Response(F("0000", True, func.get_logs(id=id, page_num=int(page), before_time=before_time))), 200
