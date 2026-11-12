---
name: linkfox-lazada-store-finance
description: 查询已授权 Lazada 卖家店铺的打款状态、交易明细和账户流水，适用于核对平台结算、回款与资金往来。
---

# Lazada 店铺财务查询

## 适用范围

### 适用

读取已授权 Lazada 店铺的打款状态、交易明细和账户流水。

**场景速查**

| 用户表达 | 查询场景 |
| --- | --- |
| 查看某个结算周期是否已打款 | 按日期查询打款状态。 |
| 核对账单交易或某笔订单的财务明细 | 在指定日期范围内查询交易明细。 |
| 核对账户入账与资金往来 | 查询账户流水。 |

### 边界

店铺绑定和授权失效由 `linkfox-lazada-store-auth` 处理。核对订单商品与发货状态使用 `linkfox-lazada-store-orders`。本技能提供财务只读查询。

## 接口清单

| 操作 | LinkFox 网关与 Lazada 上游 | 接口文档 | 对应脚本 | 性质 |
| --- | --- | --- | --- | --- |
| 打款状态 `listPayouts` | `POST /lazada/finance` → `GET /finance/payout/status/get` | [接口说明](references/api.md#接口打款状态listpayouts) | `scripts/finance_api.py listPayouts` | 只读 |
| 交易明细 `listTransactionDetails` | `POST /lazada/finance` → `GET /finance/transaction/details/get` | [接口说明](references/api.md#接口交易明细listtransactiondetails) | `scripts/finance_api.py listTransactionDetails` | 只读 |
| 账户流水 `listAccountTransactions` | `POST /lazada/finance` → `POST /finance/transaction/accountTransactions/query` | [接口说明](references/api.md#接口账户流水listaccounttransactions) | `scripts/finance_api.py listAccountTransactions` | 只读 |

## 前置条件

通过授权 Skill 确认目标店铺及站点，使用同一记录的 `connectionId`。目标应用需具备对应财务权限。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md` 及接口清单中的对应文档。
- **脚本调用（推荐）**：使用 Python 3.9+，`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **业务操作入口**：`python scripts/finance_api.py <操作> '<JSON 参数>' [--inline] [--no-cache]`，也可用 `--params-file <UTF-8 JSON 文件>` 提供参数。
- **成本约束**：本技能不消耗算力，业务调用通过输出预检后实时请求一次，不启用 24 小时响应缓存。按用户任务范围分页或查询原申请／写记录，不因失败或空结果自动扩大范围或重放写入。

本地输入、默认值、构参映射及保存结果见 [脚本使用说明](references/script-usage.md)。

### 输出策略

- 始终保存可保存的完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<技能名>-<操作>-<时间>.json`。会话优先取 `SESSION_ID`。输出或会话元数据不可写时，在发请求前报错。
- 响应体不超过 8000 字节：保存后，将完整脱敏 JSON 打印到标准输出。
- 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、可用诊断、最大列表字段的长度和最多前三项样本。
- 添加 `--inline` 可强制全量打印可保存数据，同时仍保存文件。
- HTTP、网关或响应格式错误时，脚本保存可用的脱敏诊断并以非零状态退出。

先通过摘要判断数据是否足够。以 `Saved full response:` 后的实际文件路径为准；需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 查询流程

1. 先确认用户需要核对的是打款、账单交易还是账户流水，再选日期格式和对应操作。
2. 按店铺、站点、日期和币种展示结果。明确本次查询范围和是否还有后续页。
3. 以实际返回的状态和金额字段为准。缺失字段保留为未知，分开说明店铺订单金额和资金结算金额。

### 算力消耗

本 Skill 的三个财务查询操作均为 0 算力/次。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`；先结合接口诊断确认是 LinkFox 用户认证或计费问题。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

Lazada 店铺授权失效、卖家未验证、应用权限或代理限制按接口参考处理。短信、登录和算力订单按用户已授权范围执行；订单结果不明先核对原订单。可选二维码依赖为 qrcode 和 Pillow，未安装时使用支付链接，不静默安装。

### 约束与建议

- 账户流水用于核对实际记录。仅汇总同一币种且统计口径一致的金额。
- 反馈和摘要只保留核对所需字段，省略账户、交易和买家标识及原始响应。

## 使用示例

查询指定结算日起的打款状态。替换命令中的实际店铺连接和起始日期。

```sh
python scripts/finance_api.py listPayouts '{"connectionId":"11111111-1111-4111-8111-111111111111","params":{"created_after":"2026-10-01"}}'
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引整理脱敏反馈，不要打断用户当前流程。仅在用户授权发送后提交。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
