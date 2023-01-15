from .State import Chart
from .exchanges.Basics import *
from .func import *
import strategy.code.countworker.exchanges.ExchangeFactory as Factory


class Exchange(Basics, Chart):

    # 策略名称
    Name: str = None

    # 配置信息
    config: dict = {}

    def __init__(self):
        self.__exchange: str | None = None  # 交易所
        self.__name: str | None = None  # 交易对
        self.__agent = None  # 代理

    # 设置交易对
    def __SetExchanges__(self, info: list) -> None:
        self.__agent = Factory.ExchangeFactory.create_exchange(info[0], info[1])  # 设置交易所代理
        self.__exchange = info[0]
        self.__symbol = info[1]

    # 设置交易所配置
    def setOption(self, option: Dict) -> None:
        self.__agent.setOption(option)

    # 策略初始化
    @staticmethod
    def init() -> None:
        pass

    # 交易对初始化
    def before_start(self):
        pass

    # 运行函数
    def main(self) -> None:
        log("策略没有声明main函数", type="error")
        exit(0)

    # 类函数
    @classmethod
    def before_end(cls) -> None:
        pass

    # 意外错误
    @staticmethod
    def onerror():
        pass

    # 获取交易所
    @property
    def exchange(self):
        return self.__exchange

    # 获取交易对
    @property
    def symbol(self):
        return self.__name

    # 获取配置
    @classmethod
    def getConfig(cls, name):
        try:
            return cls.config[name]
        except:
            log(f"{name}属性不在配置信息内", type="error")

    # 设置配置
    @classmethod
    def setConfig(cls, name, value):
        if cls.config[name]:
            cls.config[name] = value

    def IO(self, method: Literal["GET", "POST"], path: str, data: str | list | dict = "", sign: bool = True):
        self.__agent.IO(method, path, data, sign)

    def getAccount(self, *args, **kwargs):
        self.__agent.getAccount(*args, **kwargs)

    def getPosition(self, *args, **kwargs):
        self.__agent.getPosition(*args, **kwargs)

    def setMarginLevel(self, level: int, mode: Literal["isolated", "cross"] = "cross"):
        self.__agent.setMarginLevel(level)

    def cancelOrder(self, id: str | int):
        self.__agent.cancelOrder(id)

    def getOrder(self, id: str | int):
        self.__agent.getOrder(id)

    def getPendingOrders(self):
        self.__agent.getPendingOrders()

    # 行情数据
    def getTicker(self, *args, **kwargs) -> Basics.Ticker:
        return self.__agent.getTicker(*args, **kwargs)

    # 深度数据
    def getDepth(self, *args, **kwargs) -> DepthType:
        return self.__agent.getDepth(*args, **kwargs)

    # K线数据
    def getRecords(self, *args, **kwargs) -> Basics.Records:
        return self.__agent.getRecords(*args, **kwargs)

    # 买入函数
    def buy(self, price: Union[int, float], amount: Union[int, float, str], config: trade_type_rule):
        return self.__agent.buy(price, amount)

    # 卖出函数
    def sell(self, price: Union[int, float], amount: Union[int, float, str], config: trade_type_rule):
        return self.__agent.sell(price, amount)

    # 按钮
    class Button:
        functions = {}

        def __init__(self, key):
            self.key = key
            self.functions[key] = None

        def __call__(self, func):
            self.functions[self.key] = func
            return func

        @classmethod
        def press(cls, button_keys: list):
            for key in button_keys:
                cls.functions[key]()
