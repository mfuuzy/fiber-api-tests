# @Time    : 2025/3/13 17:35
# @FileName: main.py
# @Software: PyCharm
# @author  : mfuuzy

import json,time
from dotenv import dotenv_values
from src import utils
from tqdm import tqdm

env_vars = dotenv_values(".env")
def countdown_sleep(seconds):
    for _ in tqdm(range(seconds), desc="等待中", unit="s"):
        time.sleep(1)

url_list = utils.CheckServices(json.loads(env_vars.get("NODE_PRC", "[]"))).check_services()

if url_list['status_code'] == 201:
    FiberApiTests = utils.FiberApiTests()
    for a, b in zip(url_list['normal_url_list'], url_list['normal_url_list'][1:]):
        FiberApiTests.connect_peer(a, b)  # 建立节点间的连接
        for symbol in json.loads(env_vars.get("SYMBOL_LIST", "[]")):
            try:
                FiberApiTests.open_channel(a, b, symbol=symbol)
                # time.sleep(50) # 等待通道创建完成
                countdown_sleep(5)
                # FiberApiTests.send_payment(a, b, symbol=symbol) # 会在 B 节点自动创建 invoice，A 节点发送

                # FiberApiTests.shutdown_channel(a, b, symbol=symbol)
            except:
                print(f"测试 {symbol} 时，出现异常")
else:
    print("端口检测失败")
