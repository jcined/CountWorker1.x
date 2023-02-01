name = "做多网格(模拟)"

config = [
    {
        "var": "balance",
        "name": "初始金额",
        "type": "number",
        "default": 10000,
    },
    {
        "var": "interval",
        "name": "网格间隔",
        "type": "number",
        "remarks": "0.01 == 1%",
        "default": 0.01,
    },
    {
        "var": "tradenum",
        "name": "下单金额",
        "type": "number",
        "remarks": "100 == 100u",
        "default": 300,
    },
]
