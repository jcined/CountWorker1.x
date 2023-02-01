import threading
from flask import Flask
from flask import render_template, redirect
from flask import Blueprint, request, Response
from flask_cors import CORS
from flask_socketio import SocketIO
from blueprint.api import api
from blueprint.active import active
import func
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


@app.route('/login')
def login():
    return render_template('index.html')


@app.route('/s/code/<id>')
@app.route('/code')
@app.route('/live')
@app.route('/')
def template(id=None):
    ver = func.verToken(request.cookies.get("token"), "./admin/account.json")
    if not ver:
        return redirect('/login')
    elif request.path == "/login" and ver:
        return redirect('/')
    return render_template('index.html')


@app.route('/live/chart/<id>')
@app.route('/live/logs/<id>')
@app.route('/live/setting/<id>')
def live(id):
    ver = func.verToken(request.cookies.get("token"), "./admin/account.json")
    if request.path != "/login" and not ver:
        return redirect('/login')
    return render_template('live.html')


# 验证ip
@s.before_request
def verS():
    if wsAPIdata.stop_requested is None:
        return Response(F("0000", True)), 200


@s.route('/error')
def error():
    print("策略意外退出")
    id = request.args.get('id')
    path = f"strategy/Lives/{id}/UserSetConfig.json"
    Config = func.read_json(path)
    Config["state"] = False
    func.write_json(path, Config)
    live_data = func.read_json("./strategy/Lives.json")
    live_data[id]["pid"] = None
    func.write_json("./strategy/Lives.json", data=live_data)
    wsAPIdata.WSDATA.put(wsData("error", None))
    return Response(F("0000", True)), 200


# 收到日志信息
@s.route('/log', methods=["POST"])
def Get_log():
    id = request.args.get('id')
    try:
        if not wsAPIdata.stop_requested:
            data = json.loads(request.get_data())["message"]
            try:
                # 将数据放入队列中
                wsAPIdata.WSDATA.put(wsData("log", {
                    "time": data["time"],
                    "type": data["type"],
                    "info": data["info"],
                    "live_id": id,
                }))
            except:
                pass
        return Response(F("0000", True)), 200
    except:
        return Response(F("0", "failed")), 500


# 收到状态更新
@s.route('/state', methods=["POST"])
def Get_state():
    id = request.args.get('id')
    print("接收到状态更新")
    state = json.loads(request.get_data())["message"]["state"]
    path = f"./strategy/Lives/{id}/UserSetConfig.json"
    data = func.read_json(path)
    data["stateCus"] = state
    func.write_json(path, data)
    try:
        wsAPIdata.WSDATA.put(wsData("state", {
            "state": state,
            "live_id": id,
        }))
        return Response(F("0000", True)), 200
    except Exception as e:
        print(e)
        return Response(F("0", "failed")), 200


# 收到图表更新
@s.route('/chart', methods=["POST"])
def Get_chart():
    id = request.args.get('id')
    print("接收到图表更新")
    data = json.loads(request.get_data())["message"]
    try:
        wsAPIdata.WSDATA.put(wsData("chart", {
            "index": data["index"],
            "type": data["type"],
            "data": data["newdata"],
            "live_id": id,
        }))
        return Response(F("0000", True)), 200
    except:
        return Response(F("0", True)), 400


# 收到收益更新
@s.route('/profit', methods=["POST"])
def Get_profit():
    id = request.args.get('id')
    print("接收到收益更新")
    data = json.loads(request.get_data())["message"]
    try:
        wsAPIdata.WSDATA.put(wsData("profit", {
            "time": data["time"],
            "value": data["value"],
            "live_id": id,
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


if __name__ == "__main__":
    SetSeverConfig()
    CORS(app, origins='*', websocket_origins='*')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(active, url_prefix='/api/active')
    app.register_blueprint(s, url_prefix='/s')
    socketio.run(app, port=10010, host="0.0.0.0", allow_unsafe_werkzeug=True)
