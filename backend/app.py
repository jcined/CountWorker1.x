import threading
from flask import Flask
from flask import render_template, redirect
from flask import Blueprint, request, Response
from flask_cors import CORS
from flask_socketio import SocketIO
from blueprint.api.index import api
from blueprint.api.active.index import active
import func
import psutil
from func import *
from queue import Queue

app = Flask(__name__)
s = Blueprint('s', __name__)

socketio = SocketIO(app, cors_allowed_origins="*")
socketio.init_app(app, ping_timeout=3600, ping_interval=10)


class WSThread(threading.Thread):
    def __init__(self, namespace):
        super().__init__()
        self.WSDATA = Queue()  # 数据队列
        self.stop_requested = True
        self.__namespace = str(namespace)

    def run(self):
        self.stop_requested = False
        while not self.stop_requested:
            # 从队列中获取数据
            data = self.WSDATA.get()
            # 发送数据到客户端
            socketio.emit(data["h"], {'data': data["data"]}, namespace=self.__namespace)
            # 标记任务完成
            self.WSDATA.task_done()

    def stop(self):
        self.stop_requested = True


wsAPIdata = WSThread('/api')
wsAPIdata.start()  # 启动线程


@app.route('/')
@app.route('/login')
@app.route('/chart')
@app.route('/logs')
@app.route('/setting')
def template():
    ver = func.verToken(request.cookies.get("token"), "./admin/account.json")
    print(ver)
    if request.path != "/login" and not ver:
        return redirect('/login')
    elif request.path == "/login" and ver or request.path == "/":
        return redirect('/chart')
    return render_template('index.html')


# 验证ip
@s.before_request
def verS():
    # if request.remote_addr != ip:
    #     return Response(F("1006", "The IP address is incorrect")), 400
    if wsAPIdata.stop_requested is None:
        return Response(F("0000", True)), 200


@s.route('/error')
def error():
    print("策略意外退出")
    path = "./strategy/code/UserSetConfig.json"
    Config = func.read_json(path)
    Config["state"] = False
    func.write_json(path, Config)
    wsAPIdata.WSDATA.put(wsData("error", None))
    return Response(F("0000", True)), 200


# 收到日志信息
@s.route('/log', methods=["POST"])
def Get_log():
    try:
        if not wsAPIdata.stop_requested:
            data = json.loads(request.get_data())["message"]
            try:
                # 将数据放入队列中
                wsAPIdata.WSDATA.put(wsData("log", {
                    "time": data["time"],
                    "type": data["type"],
                    "info": data["info"],
                }))
            except:
                pass
        return Response(F("0000", True)), 200
    except:
        return Response(F("0", "failed")), 500


# 收到状态更新
@s.route('/state', methods=["POST"])
def Get_state():
    print("接收到状态更新")
    state = json.loads(request.get_data())["message"]["state"]
    path = "./strategy/code/UserSetConfig.json"
    data = func.read_json(path)
    data["stateCus"] = state
    func.write_json(path, data)
    try:
        wsAPIdata.WSDATA.put(wsData("state", {
            "state": state,
        }))
        return Response(F("0000", True)), 200
    except Exception as e:
        print(e)
        return Response(F("0", "failed")), 200


# 收到图表更新
@s.route('/chart', methods=["POST"])
def Get_chart():
    print("接收到图表更新")
    data = json.loads(request.get_data())["message"]
    try:
        wsAPIdata.WSDATA.put(wsData("chart", {
            "index": data["index"],
            "type": data["type"],
            "data": data["newdata"],
        }))
        return Response(F("0000", True)), 200
    except:
        return Response(F("0", True)), 400


# 收到收益更新
@s.route('/profit', methods=["POST"])
def Get_profit():
    print("接收到收益更新")
    data = json.loads(request.get_data())["message"]
    try:
        wsAPIdata.WSDATA.put(wsData("profit", {
            "time": data["time"],
            "value": data["value"],
        }))
        return Response(F("0000", True)), 200
    except Exception as e:
        print(e)
        return Response(F("0", True)), 400


@socketio.on('connect', namespace='/api')
def ws():
    print("ws连接成功")
    wsAPIdata.stop_requested = False
    print("启动线程")


@socketio.on('pong')
def handle_pong():
    print('Received pong')


@socketio.on('disconnect', namespace='/api')
def ws_disconnect():
    print("断开连接")
    wsAPIdata.stop()


def ResetPid():
    def changeState(state: bool):
        path = "./strategy/code/UserSetConfig.json"
        data = func.read_json(path)
        data["state"] = state
        func.write_json(path, data)

    PATH = "./strategy/data/strategyProcess.json"
    try:
        pid = func.read_json(PATH)["pid"]
        current_process = psutil.Process(pid)
        script_name = current_process.cmdline()[-1]
        if script_name == './strategy/code/run.py':
            changeState(True)
            print("重置为true")
        else:
            raise ValueError("error")
    except Exception as e:
        print(e)
        func.write_json(PATH, {"pid": None})
        changeState(False)


if __name__ == "__main__":
    SetSeverConfig()
    ResetPid()
    CORS(app, origins='*', websocket_origins='*')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(active, url_prefix='/api/active')
    app.register_blueprint(s, url_prefix='/s')
    socketio.run(app, port=10010, host="0.0.0.0")
