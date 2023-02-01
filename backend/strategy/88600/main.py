import sys
sys.path.append("/countworker/")
from strategy.countworker.exchange import Exchange
from strategy.countworker.func import *
import json
import time
from typing import *

class Main(Exchange):

    def __init__(self):
        super().__init__()
        self.initBalance = float(self.getConfig("balance"))
        self.interval = float(self.getConfig("interval"))
        self.tradenum = float(self.getConfig("tradenum"))
        self.upper_bound = None
        self.lower_bound = None
        self._Gpath = "okx_grid.json"
        # Set Balance
        balance = self._G("balance")
        if balance is None:
            self.balance = self.initBalance
        else:
            self.balance = balance
            log("balance属性读取成功")
        # Set Size
        size = self._G("size")
        if size is None:
            self.size = 0
        else:
            self.size = size
            log("size属性读取成功")

    def _G(self, K, V=None):
        # load
        if V is None:
            try:
                with open(self._Gpath, 'r') as f:
                    variable = json.load(f)
                return variable[K]
            except:
                return None
        # save
        try:
            with open(self._Gpath, 'r') as f:
                variable = json.load(f)
        except:
            variable = {}
        variable[K] = V
        with open(self._Gpath, 'w') as f:
            json.dump(variable, f)

    def _GetTicker(self):
        ticker = self.getTicker().get()
        if ticker is None:
            self._GetTicker()
        else:
            return ticker

    class updateProfit:
        fresh_time_s = 300
        last_time = time.time()

        @classmethod
        def add(cls, initBalance: float, total: float) -> None:
            if time.time() - cls.last_time >= cls.fresh_time_s:
                profit = round(total - initBalance, 3)
                logProfit(profit)
                cls.last_time = time.time()

    # Reset bound
    def generate_grid_points(self, price: float) -> None:
        self.upper_bound = price * (1 + self.interval)
        self.lower_bound = price * (1 - self.interval)

    @Exchange.Button("clearProfit")
    def clearProfit():
        log("接收到清空收益请求")
        logProfitClear()

    @Exchange.Button("clearLog")
    def clearLog():
        log("接收到清空日志请求")
        clearLog()

    def before_start(self):
        if self.exchange == "okx":
            self.setOption({
                "APIKey": "123",
                "SecretKey": "123",
                "Passphrase": "123",
            })
        ticker = self._GetTicker()
        self.generate_grid_points(ticker.last)
        amount = round((self.tradenum / ticker.last), 3)
        if self.buy(amount):
            log(f"{self.symbol} price:{ticker.last},amount:{amount}", type='buy')

    def trade(self, amount: float, dirction: Literal["buy", "sell"]) -> bool:
        ticker = self._GetTicker()
        total = round(amount * ticker.last, 3)
        if dirction == "buy":
            if self.balance > total:
                self.balance -= total
                self.size += amount
            else:
                log("买入失败,保证金不足", type='error')
                return False
        else:
            if self.size > amount:
                self.balance += total
                self.size -= amount
            elif self.size > 0:
                self.balance += round(self.size * ticker.last, 3)
                self.size = 0
                log("卖出数量超过持仓数量,已全部卖出")
            else:
                log("卖出失败,当前无持仓", type='error')
                return False
        self._G("size", self.size)
        self._G("balance", self.balance)
        return True

    def buy(self, amount) -> float:
        return self.trade(amount, "buy")

    def sell(self, amount) -> float:
        return self.trade(amount, "sell")

    # main logic
    def logic(self):
        ticker = self._GetTicker()
        # buy or sell 100u
        amount = round(self.tradenum / ticker.last, 3)
        if ticker.last >= self.upper_bound:
            if self.sell(amount):
                log(f"{self.symbol} price:{ticker.last},amount:{amount}", type='sell')
            self.generate_grid_points(ticker.last)

        elif ticker.last <= self.lower_bound:
            if self.buy(amount):
                log(f"{self.symbol} price:{ticker.last},amount:{amount}", type='buy')
            self.generate_grid_points(ticker.last)

        total = round(self.balance + ticker.last * self.size, 3)
        # update profit
        self.updateProfit.add(
            self.initBalance, 
            total
        )
        # update state
        self.State[0][0]["tables"]["rows"].append([
            f"{self.initBalance}$",
            f"{total}$",
            f"{round(total-self.initBalance,3)}$",
            round(self.size, 3),
            ticker.last,
            round(self.lower_bound, 3),
            round(self.upper_bound, 3),
        ])

    def main(self):
        try:
            self.logic()
        except Exception as e:
            log(str(e), type='error')
