from countworker.exchange import Exchange
from countworker.func import *

class Main(Exchange):

    def before_start(self):
        if self.exchange == "okx":
            self.setOption({
                "APIKey": self.getConfig("APIKey"),
    	        "SecretKey": self.getConfig("SecretKey"),
    	        "Passphrase": self.getConfig("Passphrase"),
            })

    def main(self):
        ticker = self.getTicker().get()    
        log(ticker.last)


