# 店铺授权脚本指南

## 运行环境

使用 Python 3.10 或更高版本。身份凭据、网关环境变量优先级、脚本选项、限制及错误定义统一见 [接口说明](../references/api.md)。未配置凭据按 [认证引导](../references/onboarding.md) 处理。

## CLI

```bash
python authorize_url.py '{"region":"NA","sellerName":"我的店铺","central":"seller","marketplace":"US"}'
python authorized_stores.py
python refresh_token.py '{"sellerId":"A1234567890","region":"NA"}'
python store_tokens.py '{"sellerId":"A1234567890","region":"NA"}'
python cancel_authorization.py '{"sellerId":"A1234567890","region":"NA"}'
python automatic_authorize_url.py --region NA --seller-name '我的店铺' --central seller --marketplace US
python automatic_verify.py
```

JSON 入口支持 `'<JSON 参数>' [--inline] [--no-cache]`；店铺列表支持无参数调用。自动脚本保持单 JSON stdout，链接仅内存传递，接收方必须安全捕获，不直接回显到聊天或工具日志。自动流程请先读 [自动授权文档](../references/automatic-authorization.md)，不能仅凭脚本可运行就假定宿主满足本机要求。

业务封装通过 `_auth_common.py` 调用 `call_api.run`，在公共输出前完成令牌脱敏、XML 错误及计费头兼容。所有业务调用均关闭响应缓存并无自动重试。参数与业务错误退出 1，完成退出 0；网关业务码按接口定义中的基础响应规则判断，兼容整数 0 和字符串 "0"。
