import json

# 打开配置json
def open_config(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


