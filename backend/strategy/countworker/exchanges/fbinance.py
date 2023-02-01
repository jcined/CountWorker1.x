import hashlib
import hmac
from urllib.parse import urlsplit, parse_qs
from ..func import *
import requests
from .Basics import *


class fbinance(Basics):

    def __init__(self, symbol):
        self.symbol = symbol
        self.APIKey = None
        self.SecretKey = None
        self.httpUrl = "https://fapi.binance.com"

    def setOption(self, option: Dict[Literal['APIKey', 'SecretKey'], str]):
        self.APIKey = option["APIKey"]
        self.SecretKey = option["SecretKey"]

    class Ticker(Basics.Ticker):

        def __init__(self, out):
            self.out = out

        def now(self) -> TickerType:
            pass

        def back(self, col: int = -1) -> TickerType:
            pass

        def get(self) -> TickerType | None:
            data = self.out.IO("GET", f"/fapi/v1/trades?symbol={self.out.symbol}", sign=False)
            if data is not None:
                data_data = data[0]
                ticker = TickerType(
                    info=data,
                    buy=float(data_data["price"]),
                    sell=float(data_data["price"]),
                    high=float(data_data["price"]),
                    low=float(data_data["price"]),
                    last=float(data_data["price"]),
                    volume=float(data_data["quoteQty"]),
                    time=int(data_data["time"]),
                )
                return ticker
            return None

    def getTicker(self) -> Ticker:
        pass

    def getDepth(self, sz: int) -> DepthType:
        pass

    class Records(Basics.Records):

        def __init__(self, out, bar: str = "1H"):
            self.out = out
            self.bar = bar

        def now(self):
            pass

        def back(self, col: int = -1):
            pass

        def get(self, limit: int = 100) -> list[RecordsType]:
            pass

    def getRecords(self, bar) -> Records:
        pass

    def getAccount(self, ccy=None) -> AccountType | None:
        pass

    def getPosition(self) -> PositionType | None:
        pass

    def setMarginLevel(self, level: int, mode: Literal["isolated", "cross"] = "cross") -> bool:
        pass

    def buy(self, price: Union[int, float], amount: Union[int, float, str], config: dict):
        pass

    def sell(self, price: Union[int, float], amount: Union[int, float, str], config: dict):
        pass

    def cancelOrder(self, id: str | int) -> bool:
        pass

    def getOrder(self, id: str | int):
        pass

    def getPendingOrders(self):
        pass

    def IO(self, method: Literal["GET", "POST"], path: str, data: str | list | dict = "", sign: bool = True):
        if sign:
            header = {
                'X-MBX-APIKEY': self.APIKey,
            }
            signature = self.__get_signature(path, data)
            if data != "":
                data['timestamp'] = int(time.time() * 1000)
            else:
                path += f"&signature={signature}"
        else:
            header = {}
        if method == 'GET':
            url = f'{self.httpUrl}{path}'
            response = requests.get(url=url, headers=header)
        else:
            response = requests.post(url=f'{self.httpUrl}{path}', headers=header, data=data)
        if response.status_code != 200:
            print(response.text)
            log(response.text, type="error")
            return None
        return response.json()

    # 获取签名
    def __get_signature(self, path, body=None):
        """
        get_signature 函数用来计算签名，它接受四个参数
        :param path: 为请求的接口路径
        :param body: 为请求的数据体，只有在post请求时才有用，默认为None
        :return: 返回签名
        """
        if body is None:
            body = {}
        query = urlsplit(path).query
        query_string = parse_qs(query)
        body_string = json.dumps(sorted(body.items()))
        message = path + query_string + body_string
        signature = hmac.new(self.SecretKey, message, hashlib.sha256).hexdigest().upper()
        return signature
