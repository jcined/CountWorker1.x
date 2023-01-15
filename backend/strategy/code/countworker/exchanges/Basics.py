import abc
from dataclasses import dataclass
from typing import *

# ticker传入参数规则
ticker_type_rule = Literal['last', 'buy', 'sell', 'high', 'low']

# 下单函数配置规则
"""
mode: 交易模式
    保证金模式:  isolated: 逐仓 cross: 全仓
    非保证金模式: cash
pos: 持仓方向: long | short | None
"""
trade_type_rule = Dict[Literal['mode', 'pos'], str]


# Ticker结构体
@dataclass
class TickerType:
    info: Dict
    high: float
    low: float
    buy: float
    sell: float
    last: float
    volume: float
    time: int


# Depth结构体
@dataclass
class DepthType:
    asks: List
    bids: List
    time: int


# Records结构体
@dataclass
class RecordsType:
    open: float
    close: float
    high: float
    low: float
    time: int


# Order结构体
@dataclass
class OrderType:
    info: Dict | List  # 原始接口
    id: str  # 订单id
    price: float  # 委托价格
    amount: float  # 委托数量
    type: str  # 订单类型
    side: Literal["buy", "sell"]  # 订单方向
    posSide: Literal["long", "short", None]  # 持仓方向
    avg: float  # 成交均价
    state: bool  # 订单状态


# Account结构体
@dataclass
class AccountType:
    info: Dict | List  # 原始接口
    total: float  # 币种总权益
    frozenTotal: float  # 挂单冻结数量
    balance: float  # 币种余额


# Position结构体
@dataclass
class PositionType:
    info: Dict | List  # 原始接口
    posSide: Literal["long", "short"]  # 持仓方向
    marginLevel: float  # 杠杆倍数
    size: float  # 头寸
    avgPrice: float  # 开仓平均价
    margin: float  # 保证金余额
    mmr: float  # 维持保证金
    markPrice: float    # 标记价格
    upl: float  # 未实现收益


class Basics(abc.ABC):

    # 交易所配置
    @abc.abstractmethod
    def setOption(self, option: Dict):
        pass

    # 调用交易所功能接口
    @abc.abstractmethod
    def IO(self, method: Literal["GET", "POST"], path: str, data: str | list | dict = "", sign: bool = True):
        """
        IO 函数是一个调用交易所功能接口的函数，它接受四个参数
        :param method:请求方法，可以是 GET 或 POST
        :param path:请求的接口路径
        :param data:请求的数据体，只有在post请求时才有用，默认为空
        :param sign:是否是私有请求，默认为True
        :return: 如果请求成功，会返回一个包含response内容的字典，如果失败，返回 None
        """
        pass

    # 行情数据
    class Ticker(abc.ABC):

        # 当前数据
        @abc.abstractmethod
        def now(self) -> TickerType:
            pass

        # 上n个数据
        @abc.abstractmethod
        def back(self, col: int = -1) -> TickerType:
            pass

        # 手动获取数据
        @abc.abstractmethod
        def get(self) -> TickerType | None:
            pass

    @abc.abstractmethod
    def getTicker(self) -> Ticker:
        """
        :return: 返回Ticker类实例
        """
        pass

    @abc.abstractmethod
    def getDepth(self, sz: int) -> DepthType:
        """
        获取当前交易对市场的订单薄数据
        sz参数为深度档位数量
        """
        pass

    # K线数据
    class Records(abc.ABC):

        @abc.abstractmethod
        def __init__(self, bar: str = "1H"):
            self.bar = bar

        # 当前k线
        @abc.abstractmethod
        def now(self):
            pass

        # 上n个k线
        @abc.abstractmethod
        def back(self, col: int = -1):
            """
            :param col:上n个k线
            :return:Records数据结构
            """
            pass

        # 数据
        @abc.abstractmethod
        def get(self, limit: int = 100) -> list[RecordsType]:
            """
            :param limit:返回的结果集数量
            :return:
            """
            pass

    @abc.abstractmethod
    def getRecords(self, bar) -> Records:
        """
        :return:返回Records类实例
        """
        pass

    # 账户信息
    @abc.abstractmethod
    def getAccount(self, ccy=None) -> AccountType | None:
        pass

    # 仓位信息
    @abc.abstractmethod
    def getPosition(self) -> PositionType | None:
        pass

    # 设置杠杆大小
    @abc.abstractmethod
    def setMarginLevel(self, level: int, mode: Literal["isolated", "cross"] = "cross") -> bool:
        pass

    # 买入
    @abc.abstractmethod
    def buy(self, price: Union[int, float], amount: Union[int, float, str], config: dict):
        pass

    # 卖出
    @abc.abstractmethod
    def sell(self, price: Union[int, float], amount: Union[int, float, str], config: dict):
        pass

    # 取消订单
    @abc.abstractmethod
    def cancelOrder(self, id: str | int) -> bool:
        pass

    # 获取订单信息
    @abc.abstractmethod
    def getOrder(self, id: str | int):
        pass

    # 获取未成交订单列表
    @abc.abstractmethod
    def getPendingOrders(self):
        pass


class ExchangeFactory:
    """
    交易所工厂，用于注册和管理封装的交易所接口
    """
    __exchanges = {}

    @classmethod
    def register_exchange(cls, name: str, exchange_class) -> None:
        cls.__exchanges[name] = exchange_class

    @classmethod
    def create_exchange(cls, name: str, symbol: str) -> Basics:
        exchange_class = cls.__exchanges.get(name)
        if exchange_class is None:
            raise ValueError(f"{name} is not a valid exchange.")
        return exchange_class(symbol)
