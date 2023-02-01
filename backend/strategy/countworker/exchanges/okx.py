import base64
import hashlib
import hmac
from datetime import datetime
import requests
from ..func import *
from .Basics import *


class okx(Basics):

    def __init__(self, symbol):
        self.symbol = symbol
        self.APIKey = None
        self.SecretKey = None
        self.Passphrase = None
        self.httpUrl = "https://www.okx.com"
        self.wwsUrl = "wss://ws.okx.com:8443/ws/v5/public"

    def setOption(self, option: Dict[Literal['APIKey', 'SecretKey', 'Passphrase'], Union[str, bool]]) -> None:
        self.APIKey = option["APIKey"]
        self.SecretKey = option["SecretKey"]
        self.Passphrase = option["Passphrase"]

    class Ticker(Basics.Ticker):

        def __init__(self, out):
            self.out = out

        def now(self) -> int | float:
            pass

        def back(self, col: int = -1) -> int | float:
            pass

        def get(self) -> TickerType | None:
            data = self.out.IO("GET", f"/api/v5/market/ticker?instId={self.out.symbol}", sign=False)
            if data is not None:
                data_data = data['data'][0]
                ticker = TickerType(
                    info=data,
                    high=float(data_data["high24h"]),
                    low=float(data_data["low24h"]),
                    buy=float(data_data["bidPx"]),
                    sell=float(data_data["askPx"]),
                    last=float(data_data["last"]),
                    volume=float(data_data["vol24h"]),
                    time=int(data_data["ts"]),
                )
                return ticker
            return None

    def getTicker(self) -> Ticker:
        return self.Ticker(self)

    def getDepth(self, sz: Optional[int] = 1) -> DepthType | None:
        if sz > 400:
            sz = 400
        data = self.IO("GET", f"/api/v5/market/books?instId={self.symbol}&sz={sz}", sign=False)
        if data is not None:
            data_data = data["data"][0]
            depth = DepthType(
                asks=data_data['asks'],
                bids=data_data['bids'],
                time=int(data_data['ts']),
            )
            return depth
        return None

    class Records(Basics.Records):

        def __init__(self, out, bar: str = "1H"):
            self.out = out
            self.bar = bar

        def now(self):
            pass

        def back(self, col: int = -1):
            pass

        def get(self, limit: int = 100) -> list[RecordsType]:
            results = []
            after = ''
            first_request = False
            while True:
                params = f"?instId={self.out.symbol}&bar={self.bar}&limit={min(limit, 300)}"
                if first_request:
                    params += f"&after={after}"
                data = self.out.IO("GET", f"/api/v5/market/candles{params}", sign=False)
                if data is not None:
                    first_request = True
                    data_data = data["data"]
                    if len(data_data) > 0:
                        after = data_data[-1][0]
                        data_data.reverse()    # 翻转
                        for i in range(len(data_data)):
                            results.append(RecordsType(
                                time=int(data_data[i][0]),
                                open=float(data_data[i][1]),
                                high=float(data_data[i][2]),
                                low=float(data_data[i][3]),
                                close=float(data_data[i][4]),
                            ))
                        limit -= len(data_data)
                        if limit <= 0:
                            break
                    else:
                        break
                else:
                    break
            return results

    def getRecords(self, bar) -> Records:
        return self.Records(self, bar)

    def getAccount(self, ccy=None) -> AccountType | None:
        if ccy is None:
            ccy = self.symbol.split("-")[0]
        data = self.IO("GET", f"/api/v5/account/balance?ccy={ccy}")
        if data is not None:
            data_data = data["data"][0]["details"]
            return AccountType(
                info=data,
                total=float(data_data["eq"]),
                frozenTotal=float(data_data["ordFrozen"]),
                balance=float(data_data["cashBal"]),
            )
        return None

    def getPosition(self) -> PositionType | None:
        data = self.IO("GET", f"/api/v5/account/positions?instId={self.symbol}")
        if data is not None:
            data_data = data["data"][0]
            return PositionType(
                info=data,
                marginLevel=float(data_data["lever"]),
                size=float(data_data["pos"]),
                avgPrice=float(data_data["avgPx"]),
                posSide=data_data["posSide"],
                margin=float(data_data["margin"]),
                mmr=float(data_data["mmr"]),
                markPrice=float(data_data["markPx"]),
                upl=float(data_data["upl"]),
            )
        return None

    def setMarginLevel(self, level: Union[int], mode: Literal["isolated", "cross"] = "cross") -> bool:
        body = {
            "instId": self.symbol,
            "lever": level,
            "mgnMode": mode,
        }
        data = self.IO("POST", "/api/v5/account/set-leverage", body)
        if data is not None:
            return True
        return False

    def __trade(self, price, amount, config: trade_type_rule,
                side: Literal["buy", "sell"]) -> str | None:
        body = {
            "instId": self.symbol,
            "tdMode": config["mode"],
            "side": side,
        }
        pos_map = {
            "long": "long",
            "short": "short",
        }
        if config["pos"] is not None:
            body["posSide"] = pos_map[config["pos"]]
        if price == -1:
            body["ordType"] = "market"
        else:
            body["ordType"] = "limit"
            body["px"] = price
        body["sz"] = amount
        data = self.IO("POST", "/api/v5/trade/order", body)
        if data is not None:
            log(f"okx::{self.symbol}",f"价格:{price}",f"数量:{amount}", type="buy", sep=' ')
            return data["data"][0]["ordId"]
        return None

    def buy(self, price: Union[int, float], amount: Union[int, float], config: trade_type_rule) -> str | None:
        return self.__trade(price, amount, config, "buy")

    def sell(self, price: float, amount: str | float, config: trade_type_rule) -> str | None:
        return self.__trade(price, amount, config, "sell")

    def cancelOrder(self, id: str | int) -> bool:
        body = {
            "instId": self.symbol,
            "ordId": str(id),
        }
        data = self.IO("POST", "/api/v5/trade/cancel-order", body)
        if data is not None:
            log(f"{self.symbol}", type="cancel")
            return True
        return False

    def getOrder(self, id: str | int) -> OrderType | None:
        data = self.IO("GET", f"/api/v5/trade/order?instId={self.symbol}&ordId={id}")
        if data is not None:
            data_data = data["data"][0]
            return OrderType(
                info=data,
                id=str(data_data["ordId"]),
                price=float(data_data["px"]),
                amount=float(data_data["sz"]),
                type=data_data["ordType"],
                side=data_data["side"],
                posSide=data_data["posSide"],
                avg=float(data_data["avgPx"]),
                state=data_data["state"],
            )
        return None

    def getPendingOrders(self) -> list[OrderType] | None:
        data = self.IO("GET", f"/api/v5/trade/orders-pending?instId={self.symbol}")
        if data is not None:
            result = []
            data_data = data["data"]
            for i in range(len(data_data)):
                result.append(OrderType(
                    info=data,
                    id=str(data_data["ordId"]),
                    price=float(data_data["px"]),
                    amount=float(data_data["sz"]),
                    type=data_data["ordType"],
                    side=data_data["side"],
                    posSide=data_data["posSide"],
                    avg=float(data_data["avgPx"]),
                    state=data_data["state"],
                ))
            return result
        return None

    def IO(self, method: Literal["GET", "POST"], path: str, data: str | list | dict = "", sign: bool = True):
        if sign:
            timestamp = datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%dT%H:%M:%SZ")
            signature = self.__get_signature(method, path, data, timestamp)
            headers = {
                "OK-ACCESS-KEY": self.APIKey,
                "OK-ACCESS-SIGN": signature,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": self.Passphrase,
            }
        else:
            headers = {}
        url = f"{self.httpUrl}{path}"
        if method == 'GET':
            try:
                response = requests.get(url, headers=headers)
            except:
                return None
        else:
            try:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=data)
            except:
                return None
        if response.status_code != 200:
            print(response.text)
            log(response.text, type="error")
            return None
        return response.json()

    # 获取签名
    def __get_signature(self, method: Literal['GET', 'POST'], request_path: str, body: str = "",timestamp=""):
        """
        get_signature 函数用来计算签名，它接受四个参数
        :param method:为请求方法，可以是 GET 或 POST
        :param request_path:为请求的接口路径
        :param body:为请求的数据体，只有在post请求时才有用，默认为空
        :param timestamp:为请求的时间，ISO格式，默认为当前时间
        :return:返回签名
        """
        message = f"{timestamp}{method}{request_path}{body}"
        signature = hmac.new(bytes(self.SecretKey, 'latin1'), msg=bytes(message, 'latin1'),
                             digestmod=hashlib.sha256).digest()
        return base64.b64encode(signature).decode()
