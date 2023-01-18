import signal
import func
import os

path = "./admin/account.json"
data = func.read_json(path)

if data["account"] is None and data["password"] is None:
    data["account"] = func.generate_random_str(10)
    data["password"] = func.generate_random_str(10)
    func.write_json(path, data)
    sever = func.read_json("SeverConfig.json")
    view = f"""
*********************************************
    网址: http://{sever["ip"]}:10010
    账户: {data["account"]}
    密码: {data["password"]}
*********************************************
注意:请在防火墙打开10010端口以访问服务
    """
    print(view)
else:
    view = """
**************CountWorker后台管理**************
*   0:退出                                    *
*   1:查看账户密码                             *
*   2:重置账户密码                             *
*   3:重启服务器                               *
*   4:关闭服务器                               *
**********************************************
"""
    print(view)
    while True:
        r = input()
        if r == "0":
            break
        elif r == "1":
            view = f"""
**********************************************
    账户: {data["account"]}               
    密码: {data["password"]}              
**********************************************
"""
            print(view)
        elif r == "2":
            account = input("请输入重置账户:")
            password = input("请输入重置密码:")
            if input("确定重置密码[y/n]:") == "y":
                data["account"] = account
                data["password"] = password
                func.write_json(path, data)
                print("重置成功")
        elif r == "3":
            try:
                pid = func.read_json("SeverConfig.json")["pid"]
                # 尝试关闭服务器
                try:
                    os.kill(pid, signal.SIGKILL)
                except:
                    pass
                # 启动服务器
                os.system("nohup python3 app.py &")
                print("服务器重启成功")
            except Exception as e:
                print(f"重启服务器失败，错误原因:{e}")
        elif r == "4":
            try:
                pid = func.read_json("SeverConfig.json")["pid"]
                os.kill(pid, signal.SIGKILL)
                print("服务器关闭成功")
            except Exception as e:
                print(f"服务器关闭失败，错误原因:{e}")
        else:
            print("请输入合法指令")