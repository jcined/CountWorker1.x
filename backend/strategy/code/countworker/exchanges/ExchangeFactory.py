from .Basics import ExchangeFactory
from .okx import okx

ExchangeFactory.register_exchange("okx", okx)