# Amazon 店铺 FBA 综合管理 接口说明

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

## 接口文档索引

| 模块 | 操作数量 | 接口文档 |
|---|---|---|
| 入仓资格 v1 | 1 | [eligibility.md](apis/eligibility.md) |
| FBA 库存 v1 | 4 | [inventory.md](apis/inventory.md) |
| 入仓 v0 保留查询 | 6 | [inbound_v0.md](apis/inbound_v0.md) |
| 入仓 v2024-03-20 | 45 | [inbound.md](apis/inbound.md) |
| MCF 履约 v2020-07-01 | 14 | [outbound.md](apis/outbound.md) |

完整操作与脚本映射见 [capabilities.md](capabilities.md)，机器可读注册表见 [operations.json](operations.json) 和 `../scripts/_fba_endpoints.py`。

## 运行约定与使用限制

| 项目 | 约定 |
|---|---|
| 统一入口 | `python scripts/fba_api.py '<含 api 或 operation 的 JSON>' [--inline] [--no-cache]`；也可调用接口清单中的单操作脚本。 |
| 兼容别名 | `api` 或 `operation` 传 `getShipments` 时选择 `getShipmentsV0`；这是入仓 v0 列表查询，不是现行入仓的 `getShipment`。输出中的 Amazon operationId 仍为 `getShipments`。 |
| 依赖检测 | `python scripts/check_auth_dependency.py [--json]`；返回 0 表示已安装，返回 42 且 stderr 含 `DEPENDENCY_MISSING:` 表示缺失。兼容名称 `linkfox-amazon-spapi-auth` 及各宿主安装路径，不在本技能内实现授权。 |
| 认证 | API Key 优先 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`。店铺授权用 sellerId + region，由服务端解析令牌。 |
| 网关地址 | `LINKFOX_TOOL_GATEWAY` 优先，其次兼容变量 `STORE_API_BASE_URL`、`SPAPI_BASE_URL`，最终为 `https://tool-gateway.linkfox.com`。 |
| 网关放行 | 需允许 `fba/` 和 `inbound/fba/` 路径前缀；1005 结合 errmsg 判断；提示路径未放行时联系后端确认白名单。 |
| 请求参数映射 | 每个接口独立列出网关字段、路径和查询参数。复杂 requestBody 按对应官方模型透传；嵌套字段须符合该模型，不接受任意字段。 |
| 查询编码 | 脚本构造的 queryString 按 RFC 3986 编码：空格为 `%20`，字面加号为 `%2B`；数组仍生成重复键。非空 queryString 原样覆盖自动构造的查询串，调用方须自行保证编码正确。 |
| 缓存 | 业务封装调用公共 run 始终传 `--no-cache`，读写均不保存或复用响应缓存，不另加第二层缓存。公共调用器仍可能建立空缓存目录，此目录不表示已启用缓存。 |
| 输出 | 完整结果由公共调用器保存到当前工作目录的会话 data 目录；默认阈值 8000 字节，大结果摘要含最大列表前 3 条；--inline 全量打印。输出包含 api、developerProxy、resolvedPath、method、queryString、requestBody、payload 等字段，transportHttpStatus 记录 LinkFox 外层状态。当前目录不可写时在请求前报错。 |
| 状态机 | Inbound 2024 按计划、装箱、放置、运输和货件顺序执行；409/422 常见于状态冲突或参数问题。异步步骤用 getInboundOperationStatus 查询，未经用户同意不高频轮询。 |
| 版本边界 | Outbound 2026-07-04、已弃用的 Small and Light、External Fulfillment 和 MFN 不在本技能范围。 |
| 频率 | 各接口配额不同，Eligibility 参考限速约 1 rps；遇 429 降速并先征得用户同意。不得通过换脚本或并发任务绕过 [店铺保护与重试](spapi-protection.md)。 |

## 官方入口

- [getItemEligibilityPreview](https://developer-docs.amazon.com/sp-api/reference/getitemeligibilitypreview)
- [FBA Inventory v1](https://developer-docs.amazon.com/sp-api/reference/fba-inventory-v1)
- [Fulfillment Inbound v2024-03-20](https://developer-docs.amazon.com/sp-api/reference/fulfillment-inbound-v2024-03-20)
- [Fulfillment Inbound v0](https://developer-docs.amazon.com/sp-api/reference/fulfillment-inbound-v0)
- [Fulfillment Outbound 2020-07-01](https://developer-docs.amazon.com/sp-api/reference/fulfillment-outbound-2020-07-01)

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-store-fba",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
