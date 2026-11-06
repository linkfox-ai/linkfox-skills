# Amazon 店铺 FBA 入仓管理 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 范围与脚本契约

覆盖 51 个操作：45 个 v2024-03-20、6 个 v0；上游共 28 GET、16 POST、7 PUT。

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权 Seller ID，最长 64 字符。 |
| region | string | 是 | NA / EU / FE；CLI 自动转换为大写。 |
| skipDepCheck | boolean | 否 | 默认 false；仅本地调试或外部已确认依赖时跳过安装检测，不绕过授权。 |
| confirmWrite | boolean | 提交类必填 | 八个提交操作须在用户明确确认后传 true；其余操作不要求此控制字段。 |
| --inline | CLI flag | 否 | 强制打印完整业务结果，仍保存响应。 |
| --no-cache | CLI flag | 否 | 强制本次读取或生成访问网关；仅在用户要求刷新或确认外部状态变化后使用。写入本来不缓存。 |

### 脚本兼容与运行约定

所有公开操作接收一个 JSON 字符串参数以及 `--inline`、`--no-cache`。不接受、存储或透传原始店铺令牌；不允许调用方覆盖 `body`、`contentType`、`method`、`path`、`queryString`。仅使用 sellerId + region；网关地址按 `LINKFOX_TOOL_GATEWAY` → `STORE_API_BASE_URL` → `SPAPI_BASE_URL` → 正式网关的顺序兼容。支持两个 API key 环境变量，并透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME。

依赖检测 0 表示已找到认证技能，42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。支持认证技能目录别名 `linkfox-amazon-spapi-auth`、OpenClaw、Hermes 与自定义目录探测；不得自行调用授权或令牌接口绕过依赖。

业务封装提供按会话隔离的 24 小时成功读取/生成缓存（键包含操作及参数，不含 skipDepCheck）。写入和提交不缓存；写入或生成成功后清理当前会话的既有缓存，仅保留当次可缓存的生成结果。公共 `call_api.run` 始终加 `--no-cache`，避免第二层响应缓存；其内部可能创建空缓存目录。失败、连接错误与非成功响应不缓存。一次脚本运行最多一次网关请求。

失败或空结果不得自动换参数、翻页或连续试探；需要继续调用时先征得用户同意。请求不确定时优先利用现有任务标识恢复，不直接重建计划。

请求前检查 `<cwd>/linkfox` 可写，不回退家目录或临时目录。完整原始响应另存为 `linkfox-amazon-store-fulfillment-inbound-raw-<timestamp>.json`；业务加工结果保存为 `linkfox-amazon-store-fulfillment-inbound-<timestamp>.json`。两者均在同一会话 data 目录，采用微秒文件名避免同秒覆盖。业务 stdout 保持 8 KB 摘要策略。会话名按安全字符清理，发生变化时附加哈希，避免名称冲突。

## 业务前置条件

- Amazon 应用和卖家授权必须包含 Amazon Fulfillment role；India 流程及创建或检查刊登还需 Product Listing role。
- 创建计划前，MSKU 已在目标 marketplace 建立符合 FBA 入库条件的刊登。涉及电池或危险品时，先在刊登中补齐相应资料。
- 其他市场、商品与工作流限制见 [市场限制](marketplace-constraints.md)。

## 分组索引

| 分组 | 操作数 | 接口文档 |
|---|---|---|
| 入库计划 | 7 | [inbound-plans.md](apis/inbound-plans.md) |
| 装箱 | 7 | [packing.md](apis/packing.md) |
| 分仓 | 3 | [placement.md](apis/placement.md) |
| 货件 | 7 | [shipments.md](apis/shipments.md) |
| 货件内容更新 | 4 | [shipment-content-updates.md](apis/shipment-content-updates.md) |
| 送达窗口与交货单 | 4 | [delivery-windows-and-documents.md](apis/delivery-windows-and-documents.md) |
| 自配送预约 | 4 | [self-ship-appointments.md](apis/self-ship-appointments.md) |
| 运输 | 3 | [transportation.md](apis/transportation.md) |
| 预处理、合规与商品标签 | 5 | [prep-compliance-labels.md](apis/prep-compliance-labels.md) |
| 异步状态 | 1 | [asynchronous-operations.md](apis/asynchronous-operations.md) |
| 保留的 v0 查询与文档 | 6 | [legacy-v0.md](apis/legacy-v0.md) |

## 规范来源

- [Fulfillment Inbound API 概述](https://developer-docs.amazon.com/sp-api/docs/fulfillment-inbound-api)
- [v2024-03-20 接口参考](https://developer-docs.amazon.com/sp-api/reference/fulfillment-inbound-v2024-03-20)
- [v2024-03-20 OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-inbound-api-model/fulfillmentInbound_2024-03-20.json)
- [v0 OpenAPI 模型](https://github.com/amzn/selling-partner-api-models/blob/main/models/fulfillment-inbound-api-model/fulfillmentInboundV0.json)

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-fulfillment-inbound",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
