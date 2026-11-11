---
name: linkfox-lazada-store-auth
description: 管理 Lazada 卖家店铺授权和连接，适用于绑定、查询授权进度、选店、重新授权、解除连接，以及查看已连接店铺的资料和经营指标。
---

# Lazada 店铺授权与连接管理

## 适用范围

### 适用

管理当前 LinkFox 用户的 Lazada 卖家店铺连接，查询已授权店铺资料和经营指标。一次授权可能产生多个站点的连接，后续业务操作使用所选站点的连接 ID。

**场景速查**

| 用户表达 | 场景 |
|---|---|
| 绑定我的 Lazada 店铺、给 Lazada 店铺授权 | 生成授权链接，由用户在店铺运营环境中打开。 |
| 我授权完了、看看授权成功了吗 | 用原申请 ID 查询授权结果，成功后获取店铺连接。 |
| 有哪些 Lazada 店铺、授权的是哪个站点 | 列出当前用户的店铺连接。 |
| 这家店授权过期了 | 确认店铺连接后引导用户重新授权。 |
| 解除 Lazada 店铺绑定、取消店铺连接 | 确定具体店铺和站点后解除连接。 |
| 查看店铺资料、店铺经营指标 | 选择已连接店铺后读取资料或指标。 |

### 边界

商品、订单、营销和财务操作分别使用对应 Lazada 店铺 Skill。解除连接影响该店铺在 LinkFox 中的授权状态。

## 接口清单

| 操作 | LinkFox 网关与 Lazada 上游 | 对应脚本 | 接口文档 | 性质 |
| --- | --- | --- | --- | --- |
| 发起授权 `authorizeUrl` | `POST /lazada/authorizeUrl` | `scripts/authorize_url.py` | [接口说明](references/api.md#接口发起授权) | 创建申请 |
| 查询授权结果 `authorizationStatus` | `POST /lazada/authorizationStatus` | `scripts/authorization_status.py` | [接口说明](references/api.md#接口查询授权结果) | 只读 |
| 已连接店铺 `authorizedStores` | `POST /lazada/authorizedStores` | `scripts/authorized_stores.py` | [接口说明](references/api.md#接口已连接店铺) | 只读 |
| 解除连接 `disconnect` | `POST /lazada/disconnect` | `scripts/disconnect.py` | [接口说明](references/api.md#接口解除连接) | 写入 |
| 店铺资料 `getSeller` | `POST /lazada/store` → `GET /seller/get` | `scripts/store_api.py getSeller` | [接口说明](references/api.md#接口店铺资料) | 只读 |
| 店铺指标 `getSellerMetrics` | `POST /lazada/store` → `GET /seller/metrics/get` | `scripts/store_api.py getSellerMetrics` | [接口说明](references/api.md#接口店铺指标) | 只读 |

## 前置条件

配置当前用户的 LinkFox 接口密钥。发起授权前确认用户能登录相应的 Lazada 卖家账号。查询状态使用原申请 ID，解除连接前从当前用户的列表确定目标连接。

## 执行方式

- **直接调用接口**见 [接口参考](references/api.md) 中的端点、参数、响应和错误说明。
- **脚本调用（推荐）**使用 Python 3.9+，运行 `python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **店铺资料与指标**使用 `python scripts/store_api.py <操作> '<JSON 参数>' [--inline] [--no-cache]`。也可用 `--params-file <UTF-8 JSON 文件>` 提供参数。
- **调用约束**。授权业务脚本通过预检后发起一次实时请求。已有申请 ID 时按原 ID 查询状态，避免重复创建或连续轮询。

### 输出策略

- 可保存的结果写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<技能名>-<操作>-<时间>.json`。会话优先取 `SESSION_ID`。输出或会话元数据不可写时，在发请求前报错。
- 成功结果不超过 8000 字节时，保存后打印完整 JSON。更大的结果打印摘要，主要列表最多展示前三项。`--inline` 可打印全部可保存数据，同时仍保存文件。
- HTTP、网关或响应格式错误时，脚本保存可用的脱敏诊断并以非零状态退出。
- 授权链接仅在当次交互单独打印给当前用户。保存文件保留申请 ID 和状态。
- 以 `Saved full response:` 后的实际文件路径为准。需要更多字段时，从保存的 JSON 按需提取。

## 执行规则

### 授权与选店流程

1. 新绑定时运行 `authorize_url.py`。可用 `shopName` 记录用户可识别的店铺名称。把脚本单独输出的 Lazada 临时 HTTPS 链接交给当前用户，由用户在熟悉的店铺运营环境完成授权。
2. 用户完成操作后，用原 `requestId` 查询状态。仍为 `PENDING` 时等待用户确认后再查。`AUTHORIZED` 后列出连接并确认目标店铺。申请失败、拒绝或过期时，说明状态，按用户意愿创建新申请。
3. 只从状态为 `AUTHORIZED` 的记录中选择可用连接。候选唯一时直接使用。遇到同名、多店或跨站点时，展示店铺名、站点和卖家 ID 让用户确定目标。将该条记录的 `connectionId` 原样传给店铺查询或下游业务 Skill。
4. 解除连接前明确店铺和站点，取得用户对该目标的明确授权。超时或结果不明时先查看当前连接列表核实。

### 算力消耗

| 操作 | 算力 |
|---|---|
| 发起授权 | 0 算力/次 |
| 查询授权结果 | 0 算力/次 |
| 已连接店铺 | 0 算力/次 |
| 解除连接 | 0 算力/次 |
| 查询店铺资料 | 0 算力/次 |
| 查询经营指标 | 0 算力/次 |

算力消耗以网关实际计费配置为准。

### 解决认证和算力问题

LinkFox Key 未配置或已确认无效时，按 [认证和算力引导](references/onboarding.md) 检查。授权或连接状态异常时，先按 [接口说明](references/api.md) 核对原申请或店铺连接。遇到 402 时先确认网关账户或计费诊断。

发送短信或使用验证码登录前先取得用户同意。创建算力订单前确认套餐、金额和支付方式。下单结果不明时先核对已有订单。安装了 qrcode 和 Pillow 时可生成二维码图片，也可使用支付链接。

### 约束与建议

- 按店铺名、站点、卖家 ID 和连接状态展示店铺。用户自定义名称可能为空或重复，连接 ID 始终用原始字符串。
- `REAUTHORIZATION_REQUIRED` 表示店铺需要重新授权。按原店铺说明重新授权流程，选取新返回的可用连接。
- 仅向当前用户提供授权链接。用于排查时提供脱敏错误码和请求编号，凭据、链接及订单数据不进入报告或反馈。
- 将 LinkFox Key 故障、Lazada 授权失效和站点权限问题分别处理。店铺授权状态异常时按原店铺恢复。

## 使用示例

### 绑定店铺并确认授权

用户：帮我绑定 Lazada 的东南亚店铺。

```sh
python scripts/authorize_url.py '{"shopName":"Lazada 东南亚店"}'
python scripts/authorization_status.py '{"requestId":"22222222-2222-4222-8222-222222222222"}'
python scripts/authorized_stores.py '{}'
```

等待用户完成浏览器授权后，把本次实际申请 ID 替换到第二行再查询。状态为 `AUTHORIZED` 时执行店铺列表查询，并确认目标站点。

### 解除指定店铺连接

用户：解除我 Lazada 马来西亚站这家店的连接。

先列出当前连接，核对店铺和马来西亚站点。用户已明确授权解除该目标时，将真实 `connectionId` 传给 `scripts/disconnect.py`。

## 使用反馈

技能出现错误、指引不清或结果不符合预期时，可按 [Feedback](references/api.md#feedback) 整理脱敏摘要。用户授权发送后再提交。

---

更多跨境电商技能见 [LinkFox Skill](https://skill.linkfox.com/)。
