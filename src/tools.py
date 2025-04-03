# @Time    : 2025/3/14 19:46
# @FileName: tools.py
# @Software: PyCharm
# @author  : mfuuzy
import hashlib
import secrets


def new_payment_preimage():
    # 需要哈希的原始数据（可以是字符串、交易信息等）
    random_data = secrets.token_hex(32)
    return {
        'payment_preimage': f'0x{hashlib.sha256(random_data.encode()).hexdigest()}'
    }


def find_key_by_args(type_script, target_args):
    for key, value in type_script.items():
        if value.get("args") == target_args:
            return key
    return None

def get_channels_data(data, type_script):
    channels_dict = {
        "ckb": [],
        "seal": [],
        "rusd": [],
        "usdi": []
    }
    for x in data:
        try:
            if x['funding_udt_type_script'] is None:
                # print("ckb 通道: ",x['channel_id'], int(x['local_balance'], 16) / 10 ** 8, int(x['remote_balance'], 16))
                channels_dict['ckb'].append(x)
                # print(
                #     f"ckb 通道: \nchannel_id:{x['channel_id']} local_balance:{int(x['local_balance'], 16) / 10 ** 8} remote_balance: {int(x['remote_balance'], 16)/10**8}")
            else:
                xudt_name = \
                find_key_by_args(type_script, x["funding_udt_type_script"]["args"]).split("_")[0]
                if xudt_name == 'seal':
                    channels_dict['seal'].append(x)
                    # print(
                    #     f"{xudt_name}通道: \nchannel_id:{x['channel_id']} local_balance:{int(x['local_balance'], 16) / 10 ** 12} remote_balance:{int(x['remote_balance'], 16)/10**12}")
                elif xudt_name == 'rusd':
                    channels_dict['rusd'].append(x)
                    # print(
                    #     f"{xudt_name}通道: \nchannel_id:{x['channel_id']} local_balance:{int(x['local_balance'], 16) / 10 ** 8} remote_balance:{int(x['remote_balance'], 16)/10**8}")
                elif xudt_name == 'usdi':
                    channels_dict['usdi'].append(x)
                    # print(
                    #     f"{xudt_name}通道: \nchannel_id:{x['channel_id']} local_balance:{int(x['local_balance'], 16) / 10 ** 8} remote_balance:{int(x['remote_balance'], 16)/10**8}")
                else:
                    print("未定义的 SYMBOL")

                    return {
                        "msg": "未定义的 SYMBOL"
                    }
                    # print(
                    #     f"{xudt_name}通道:  \nchannel_id:{x['channel_id']} local_balance:{int(x['local_balance'], 16) / 10 ** 8} remote_balance:{int(x['remote_balance'], 16)/10**8}")
        except:
            print("查询通道出现异常")
            break

    return {
        'channels_dict': channels_dict
    }