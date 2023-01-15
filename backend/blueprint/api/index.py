import signal
import psutil
from flask import Blueprint, request, Response
from func import *
import json
import func
import os
import subprocess

api = Blueprint('api', __name__)


class StrategyThread:
    path = "./strategy/code/UserSetConfig.json"
    p = None

    @classmethod
    def __changeState(cls, to: bool) -> None:
        Config = func.read_json(cls.path)
        Config["state"] = to
        func.write_json(cls.path, Config)

    @classmethod
    def run(cls) -> None:
        cls.p = subprocess.Popen(["python", "./strategy/code/run.py"])
        cls.save_var({
            "pid": cls.p.pid
        })  # 保存到本地
        cls.__changeState(True)

    @classmethod
    def stop(cls) -> None:
        pid = cls.load_var()
        current_process = psutil.Process(pid)
        script_name = current_process.cmdline()[-1]
        if script_name == './strategy/code/run.py':
            os.kill(pid, signal.SIGTERM)
            cls.__changeState(False)
            cls.save_var({
                "pid": None
            })
        else:
            cls.save_var({
                "pid": None
            })
            raise ValueError("不是目标进程")

    @classmethod
    def save_var(cls, var, filename="./strategy/data/strategyProcess.json"):
        with open(filename, "w") as f:
            json.dump(var, f)

    @classmethod
    def load_var(cls, filename="./strategy/data/strategyProcess.json"):
        try:
            with open(filename, "r") as f:
                process_info = json.load(f)
                return process_info["pid"]
        except:
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


# 启动策略
@api.route('/start', methods=["GET"])
def start():
    StrategyThread.run()  # 运行策略
    print("运行策略")
    return Response(F("0000", True)), 200


# 停止策略
@api.route('/stop', methods=["GET"])
def stop():
    try:
        StrategyThread.stop()  # 停止策略
    except Exception as e:
        print(e)
        return Response(F("1007", "Stop failed")), 400
    return Response(F("0000", True)), 200


# 初始化策略信息
@api.route('/init', methods=["GET"])
def init():
    print("初始化策略信息")
    try:
        Config = func.read_json("./strategy/code/UserSetConfig.json")
        result = {
            "Name": Config["Name"],
            "exchanges": Config["exchanges"],
            "config": Config["config"],
            "state": Config["state"],
            "profit": func.get_all_profit_data(),
            "sysData": [],
            "chartCustom": func.reda_chartCustom(),
            "stateCustom": Config["stateCus"],
            "Logs": func.get_logs(page_num=1),
        }
        return Response(F("0000", True, result)), 200
    except:
        return Response(F("1004", "Failed to write configuration information")), 400


# 上传策略文件
@api.route('/upload', methods=["POST"])
def upload():
    data = json.loads(request.get_data())
    # 转为python文件
    try:
        func.UpDate().toPython(
            data=[data["Files"]["main"], data["Files"]["config"]],
            fileName=["main.py", "config.py"]
        )
    except:
        return Response(F("1003", "Failed to read the uploaded files")), 400

    try:
        func.UpDate().toPython(data=[data["Files"]["chart"]], fileName=["chart.py"])
    except:
        pass

    # 其他文件处理
    func.UpDate().otherFiles(data=data["Files"]["other"])
    # exchanges包文件处理
    func.UpDate().otherFiles(data=data["Files"]["exchanges"], path="./strategy/code/countworker/exchanges/")

    # 读取config.py并创建json
    try:
        import strategy.code.config as scc
        config = {
            "Name": scc.name,
            "state": False,
            "stateCus": [],
            "profit": [],
            "sysData": [],
            "chartCustom": [],
        }
        try:
            config["exchanges"] = scc.exchanges
        except:
            config["exchanges"] = []
        try:
            config["config"] = scc.config
        except:
            config["config"] = []
        func.write_json("strategy/code/UserSetConfig.json", config)
        return Response(F("0000", True, config)), 200
    except:
        return Response(F("1004", "Failed to write configuration information")), 400


# 更新策略配置
@api.route('/update', methods=["POST"])
def update():
    data = json.loads(request.get_data())
    try:
        Name = data["Name"]
        exchanges = data["exchanges"]
        config = data["config"]
    except:
        return Response(F("1005", "Interface missing parameter")), 400

    # 书写策略配置
    if not func.UpDate().writeConfig(
            Name=Name,
            exchanges=exchanges,
            config=config,
    ): return Response(F("1004", "Failed to write configuration information")), 400

    return Response(F("0000", True)), 200


# 获取更多日志
@api.route('/get-logs', methods=["GET"])
def get_logs():
    page = request.args.get('page')
    before_time = request.args.get('before_time')
    return Response(F("0000", True, func.get_logs(page_num=int(page), before_time=before_time))), 200
