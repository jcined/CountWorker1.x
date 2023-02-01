from flask import Blueprint, Response, request
from lockfile import FileLock
import func
import json

active = Blueprint('active', __name__)


@active.before_request
def verCookie():
    token = request.cookies.get("token")
    if request.path == "/api/login":
        return
    elif not token:
        return Response(func.F("1001", "The request is invalid because the token is missing")), 401
    # 验证
    if not func.verToken(token, "./admin/account.json"):
        return Response(func.F("1002", "token verification fails")), 401


# 交互按钮
@active.route('/button/<key>')
def button(key):
    id = request.args.get('id')
    if func.read_json(f"./strategy/{id}/UserSetConfig.json")["state"]:
        path = f'./strategy/{id}/data/button.json'
        lock = FileLock(path)
        lock.acquire()
        try:
            data = func.read_json(path)["buttons"]
            data.append(key)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({"buttons": data}, f, ensure_ascii=False)
            return Response(func.F("0000", True)), 200
        finally:
            lock.release()
    return Response(func.F("1009", "Button interaction failed")), 500
