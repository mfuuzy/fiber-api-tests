# 描述

实现了 testnet 下的 CKB 和部分 XUDT 的自动化测试。目前实现没有将开通 > 等待开通 > 创建 invoice > 发送 >
取消通道串联起来，在已经存在通道的情况下，不依赖此次创建的通道，后续测试可以继续进行。

# 使用说明

在 .env 的 NODE_PRC 中填入对应的 RPC(可填多个),在 SYMBOL_LIST 中填入 token name (可填多个，仅支持小写)。

## 启动

在 main.py 文件 try 段中，可以修改对应的测试用例。

`python3 main.py`

# 实现

-[x] testnet 开通/发送/创建invoice/取消通道
    - [x] ckb
    - [x] rusd
    - [x] usdi
    - [x] seal
# TODO
- [ ] 校验通道是否创建成功
- [ ] 校验发送/接收金额
- [ ] mainnet 开通/发送/创建invoice/取消通道
    - [ ] ckb
    - [ ] rusd
    - [ ] usdi
    - [ ] seal
# 注意事项:

1. 确保节点使用的 CKB 地址中已经事先充值了 CKB 和 XUDT