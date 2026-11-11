---
name: linkfox-lazada-store-finance
description: 查询已授权 Lazada 卖家店铺的打款状态、交易明细和账户流水，适用于核对平台结算、回款与资金往来。
---

# Lazada 店铺财务查询

## 适用范围

### 适用

读取已授权 Lazada 店铺的打款状态、交易明细和账户流水。

| 用户表达 | 查询场景 |
| --- | --- |
| 查看某个结算周期是否已打款 | 按日期查询打款状态。 |
| 核对账单交易或某笔订单的财务明细 | 在指定日期范围内查询交易明细。 |
| 核对账户入账与资金往来 | 查询账户流水。 |

### 边界

店铺绑定和授权失效由 `linkfox-lazada-store-auth` 处理。核对订单商品与发货状态使用 `linkfox-lazada-store-orders`。本技能提供财务只读查询。

## 接口清单

| 操作 | LinkFox 网关与 Lazada 上游 | 对应脚本 | 接口文档 | 性质 |
| --- | --- | --- | --- | --- |
| 打款状态 `listPayouts` | `POST /lazada/finance` → `GET /finance/payout/status/get` | `scripts/finance_api.py listPayouts` | [接口说明](references/api.md#打款状态) | 只读 |
| 交易明细 `listTransactionDetails` | `POST /lazada/finance` → `GET /finance/transaction/details/get` | `scripts/finance_api.py listTransactionDetails` | [接口说明](references/api.md#交易明细) | 只读 |
| 账户流水 `listAccountTransactions` | `POST /lazada/finance` → `POST /finance/transaction/accountTransactions/query` | `scripts/finance_api.py listAccountTransactions` | [接口说明](references/api.md#账户流水) | 只读 |

## 前置条件

通过授权 Skill 确认目标店铺及站点，使用同一记录的 `connectionId`。目标应用需具备对应财务权限。

## 执行方式

- **脚本调用（推荐）**。使用 Python 3.9+，运行 `python scripts/finance_api.py <操作> '<JSON 参数>' [--inline] [--no-cache]`。也可用 `--params-file <UTF-8 JSON 文件>` 提供参数。
- **接口调用**。在 LinkFox 网关请求中填入 `operation`，直接调用方式见 [接口参考](references/api.md)。
- **调用约束**。业务脚本通过预检后发起一次实时请求。按用户要求选择日期范围与分页，空结果或失败时说明实际情况。

### 输出策略

- 可保存的结果写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<技能名>-<操作>-<时间>.json`。会话优先取 `SESSION_ID`。输出或会话元数据不可写时，在发请求前报错。
- 成功结果不超过 8000 字节时，保存后打印完整 JSON。更大的结果打印摘要，主要列表最多展示前三项。`--inline` 可打印全部可保存数据，同时仍保存文件。
- HTTP、网关或响应格式错误时，脚本保存可用的脱敏诊断并以非零状态退出。
- 以 `Saved full response:` 后的实际文件路径为准。需要更多字段时，从保存的 JSON 按需提取。

## 执行规则

### 查询流程

1. 先确认用户需要核对的是打款、账单交易还是账户流水，再选日期格式和对应操作。
2. 按店铺、站点、日期和币种展示结果。明确本次查询范围和是否还有后续页。
3. 以实际返回的状态和金额字段为准。缺失字段保留为未知，分开说明店铺订单金额和资金结算金额。

### 算力消耗

本 Skill 的三个财务查询操作均为 0 算力/次。算力消耗以网关实际计费配置为准。

### 解决认证和算力问题

LinkFox Key 未配置或确认无效时，按 [认证和算力指引](references/onboarding.md) 检查。店铺授权失效或财务权限缺失时，按 [错误处理](references/api.md#错误处理) 定位。

发送短信或使用验证码登录前先取得用户同意。创建算力订单前确认套餐、金额和支付方式。下单结果不明时先核对已有订单。安装了 qrcode 和 Pillow 时可生成二维码图片，也可使用支付链接。

### 约束与建议

- 账户流水用于核对实际记录。仅汇总同一币种且统计口径一致的金额。
- 反馈和摘要只保留核对所需字段，省略账户、交易和买家标识及原始响应。

## 使用示例

查询指定结算日起的打款状态。替换命令中的实际店铺连接和起始日期。

```sh
python scripts/finance_api.py listPayouts '{"connectionId":"11111111-1111-4111-8111-111111111111","params":{"created_after":"2026-10-01"}}'
```

## 使用反馈

技能出现错误、指引不清或结果不符合预期时，可按 [Feedback](references/api.md#feedback) 整理脱敏摘要。用户授权发送后再提交。

---

更多跨境电商技能见 [LinkFox Skill](https://skill.linkfox.com/)。
