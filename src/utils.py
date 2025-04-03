# @Time    : 2025/3/13 17:50
# @FileName: check_service_port.py
# @Software: PyCharm
# @author  : mfuuzy
import requests
from .tools import new_payment_preimage, get_channels_data
from .config import CONFIG
from dotenv import dotenv_values

import time

env_vars = dotenv_values(".env")


class FiberApiTests:
    def __init__(self):
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "PostmanRuntime-ApipostRuntime/1.1.0",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }

    def get_node_info(self, url):
        payload = {
            "id": 42,
            "jsonrpc": "2.0",
            "method": "node_info",
            "params": [{}]
        }
        # print(type(self.headers))
        response = requests.request("POST", f'http://{url}', json=payload, headers=self.headers).json()
        response['peer_id'] = response['result']['addresses'][0].split('/')[-1]

        # print(response)
        return response

    def connect_peer(self, a, b):
        payload = {
            "id": 42,
            "jsonrpc": "2.0",
            "method": "connect_peer",
            "params": [{
                "address": self.get_node_info(b)['result']['addresses'][0]
            }]
        }
        response = requests.request("POST", f'http://{a}', json=payload, headers=self.headers).json()
        # print("节点连接 ",response)
        return response

    def open_channel(self, a, b, symbol='ckb', true='true', network=env_vars.get("NETWORK")):
        if symbol == "ckb":
            symbol_dict = {
                "peer_id": f"{self.get_node_info(b)['peer_id']}",
                "funding_amount": "0x174876e800",
                "public": bool(true)
            }
        else:
            if symbol == "seal":
                funding_amount = "0x9184e72a000"
            elif symbol == "usdi":
                funding_amount = "0x1e84800"
            else:
                funding_amount = "0x3b9aca00"

            symbol_dict = {
                "peer_id": f"{self.get_node_info(b)['peer_id']}",
                "funding_amount": funding_amount,
                "public": bool(true),
                "funding_udt_type_script": CONFIG[network][f'{symbol}_type_script']
            }

        payload = {
            "id": 42,
            "jsonrpc": "2.0",
            "method": "open_channel",
            "params": [
                symbol_dict
            ]
        }
        response = requests.request("POST", f'http://{a}', json=payload, headers=self.headers).json()
        print(f"{symbol}: 开通通道",response)
        return response

    def list_channels(self, url, peer):
        payload = {
            "id": 42,
            "jsonrpc": "2.0",
            "method": "list_channels",
            "params": [
                {
                    "peer_id": f'{peer}'
                }
            ]
        }
        response = requests.request("POST", f'http://{url}', json=payload, headers=self.headers).json()
        # print(response.json())
        return response

    def new_invoice(self, url, symbol='ckb', currency=env_vars.get("CURRENCY")):
        if symbol == "usdi":
            amount = '0xf4240'
        else:
            amount = '0x5f5e100'
        symbol_dict = {
            "amount": f"{amount}",
            "currency": f"{currency}",
            "description": "fiber api tests",
            "expiry": "0x2581",
            "final_cltv": "0x28",
            "payment_preimage": f"{new_payment_preimage()['payment_preimage']}",
            "hash_algorithm": "sha256",
        }

        payload = {
            "id": 42,
            "jsonrpc": "2.0",
            "method": "new_invoice",
            "params": [
                symbol_dict
            ]

        }

        response = requests.request("POST", f'http://{url}', json=payload, headers=self.headers).json()
        # print(response)
        return response

    def check_channels(self, a, b, symbol='ckb'):
        channels_data = self.list_channels(a, self.get_node_info(b)['peer_id'])['result']['channels']
        channel_list = get_channels_data(channels_data, CONFIG[env_vars.get("NETWORK")])['channels_dict'][symbol]
        if len(channel_list) == 0:
            print(f"{symbol}: 没有通道")
            return {
                'msg': "没有通道",
                'code': 404
            }
        else:
            i = 0
            while  i < 10:
                for z in get_channels_data(channels_data, CONFIG[env_vars.get("NETWORK")])['channels_dict'][symbol]: # 每次循环重新获取数据
                    if z['state']['state_name'] == "CHANNEL_READY":
                        print("CHANNEL_READY 通道", z)
                        return {
                            'msg': "通常状态正常",
                            'code': 200,
                            'channel': z
                        }
                    elif z['state']['state_name'] == "AWAITING_CHANNEL_READY":
                        i = i + 1
                        time.sleep(5)
                        print(f"等待通道创建，重试次数：{i}", z)
                        continue
                    else:
                        # print(z)
                        i = i + 1
                        # time.sleep(5)
                        # print(f"{symbol}: 通道状态异常", z)
                        continue
                        # return {
                        #     'msg': "通常状态异常",
                        #     'code': 502
                        # }

                        # return {
                        #     'msg': "通常状态异常",
                        #     'code': 404
                        # }


    def send_payment(self, a, b, symbol='ckb'):
        payload = {
            "id": 42,
            "jsonrpc": "2.0",
            "method": "send_payment",
            "params": [
                {
                    "invoice": f"{self.new_invoice(b, symbol=symbol)['result']['invoice_address']}"
                }
            ]
        }

        if self.check_channels(a, b, symbol=symbol)['code'] == 200:

            response = requests.request("POST", f'http://{a}', json=payload, headers=self.headers).json()
            print("付款",response)
            return response

        else:
            return {
                'msg': "send_payment 失败"
            }

    def shutdown_channel(self, a, b, symbol='ckb', force='true', network=env_vars.get("NETWORK")):
        d = self.check_channels(a, b, symbol=symbol)
        if d['code'] == 200:
            channel_id = d['channel']['channel_id']
        else:
            print(f"{symbol}: 获取通道 ID 异常, 无法执行关闭通道操作")
            return {
                'msg': '获取通道 ID 异常',
                'code': 500
            }

        payload = {
            "id": 42,
            "jsonrpc": "2.0",
            "method": "shutdown_channel",
            "params": [
                {
                    "channel_id": f"{channel_id}",
                    "close_script": CONFIG[network][f'{symbol}_type_script'],
                    "fee_rate": "0x3f1",
                    "force": bool(force)
                }
            ]
        }

        response = requests.request("POST", f'http://{a}', json=payload, headers=self.headers).json()
        print(f"{symbol}: 取消通道",response)
        return response


class CheckServices:
    def __init__(self, url_list):
        self.url_list = url_list

    def get_data(self):
        return {
            'url_list': self.url_list
        }

    def check_services(self):
        normal_url_list = []
        for i in self.get_data()['url_list']:
            try:
                response = requests.get(f'http://{i}', timeout=3)
                # print(response.status_code)
                # print('ok')
                # print(f"节点 {i} 通过端口检测，服务正常")
                # if response.status_code ==  405:
                #     print(f" 节点 {i} 通过端口检测，服务正常")
                #     status_code = status_code + 1
                # else:
                #     print("error")
                print(f"节点 {i} 通过健康检测 ✅ ")
                normal_url_list.append(i)
            except:
                print(f"节点 {i} 未通过健康检测 ❌ ")

        if len(normal_url_list) >= 2:
            return {
                'status_code': 201,
                'msg': f"健康节点数量为: {len(normal_url_list)}，可以进行自动化测试",
                'normal_url_list': normal_url_list
            }
        else:
            print("健康节点数量不满足自动化测试最小数量要求,退出自动化测试")
            return {
                'status_code': 505,
                'msg': "节点健康数量不满足自动化测试最小数量要求"

            }


if __name__ == '__main__':
    # print(CheckServicePort('http://52.45.221.66:8227','http://52.45.221.66:8227').check_services())
    # print(CheckServicePort(
    #     ['52.45.221.66:38227', '52.45.221.66:48127', '52.45.221.66:48127', '52.45.221.66:48227']).data_processing()[
    # 'normal_url_list'])
    # print(CheckServicePort(['52.45.221.66:38227','52.45.221.66:48227']).check_services()['status_code'])

    # node_url = CheckServicePort(['52.45.221.66:38227', '52.45.221.66:48127', '52.45.221.66:48127', '52.45.221.66:48227']).data_processing()['normal_url_list']

    FiberApiTests().new_invoice('52.45.221.66:48227')
