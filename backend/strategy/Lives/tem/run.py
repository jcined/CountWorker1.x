live_id = None
try:
    import os
    import sys
    sys.path.append("/countworker/")
    import func
    from strategy.countworker.func import log

    # 获取实盘id
    lives_data = func.read_json(f'./strategy/Lives.json')
    pid = os.getpid()
    for k,v in lives_data.items():
        if str(v["pid"]) == str(pid):
            live_id = k

    import threading
    import requests
    import function
    import time
    import copy
    from main import Main

except Exception as e:
    print(e)
    log(str(e), type="error")
    requests.get(f"http://127.0.0.1:10010/s/error?id={live_id}")

def read_stdin():
    path = f'./strategy/Lives/{live_id}/data/button.json'
    func.write_json(path, {
        "buttons": []
    })
    while True:
        data = func.read_json(path)["buttons"]
        if len(data):
            func.write_json(path, {
                "buttons": []
            })
            Main().Button.press(data)
        time.sleep(1)

if __name__ == "__main__":
    try:
        log("", type="start")
        # Create a thread to read from stdin
        t = threading.Thread(target=read_stdin)
        t.start()
        # 打开配置文件
        config = function.open_config(f"./strategy/Lives/{live_id}/UserSetConfig.json")
        UserConfig = {}
        for parameter in config["config"]:
            UserConfig[parameter["var"]] = parameter["default"]
        # 配置信息
        Main.Name = config["Name"]
        try:
            Main.refresh = config["refresh"]
        except:
            pass
        Main.config = UserConfig
        # 获取交易对
        workers = config["exchanges"]
        # 打开chart文件
        initState: list = []
        initChart: list = []
        try:
            import chart

            try:
                initState = chart.state
            except:
                pass
            try:
                initChart = chart.chart
                # 存入图表key和pie
                for item in initChart:
                    if item["key"] in Main.file_list or item["key"] in Main.pie_data:
                        error = "图表key不能重复"
                        log(error, type="error")
                        raise ValueError(error)
                    if item["type"] == "pie":
                        Main.pie_data[item["key"]] = item["data"]
                    else:
                        Main.file_list[item["key"]] = item
            except:
                pass
        except:
            pass
        Main.State = copy.deepcopy(initState)
        Main.initState = copy.deepcopy(initState)
        # 创建交易对实例
        for exchange in range(len(workers)):
            info = workers[exchange]
            workers[exchange] = Main()
            workers[exchange].__SetExchanges__(info)

        print("策略已启动")
        Main.init()  # 策略初始化
        for worker in workers:
            worker.before_start()  # 交易对初始化
        while True:
            for worker in workers:
                worker.main()
                time.sleep(1)
            Main.before_end()
            Main.__resetState__()  # 重置State
    except Exception as e:
        print(e)
        log(str(e), type="error")
        Main.onerror()
    finally:
        requests.get(f"http://127.0.0.1:10010/s/error?id={live_id}")
