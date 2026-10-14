# linkfox-junglescout-sales-estimates

## 功能与适用范围

查询单个 Amazon ASIN 在指定历史日期范围内的每日预估销量和最近已知价格，适用于竞品销量监控、季节性观察、新品爬坡和选品需求验证。

每次只能查询一个 ASIN；不能查询今天或未来销量，不能替代实时订单、类目规模、BSR 历史或多 ASIN 同步面板。价格为 USD，销量和收入均为估算。

## MCP 调用

- 响应字段来源：`skills/linkfox-junglescout-sales-estimates/references/api.md`。仅从该文件核对并恢复下方响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`tool-jungle-scout/sales-estimates/query`
- `arguments`：直接使用本 reference 请求参数对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游 `errcode` / `errorCode` / `code` 与消息字段。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `marketplace` | string | 是 | `us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`；默认 `us` |
| `asin` | string | 是 | 标准亚马逊 ASIN，通常 10 位 |
| `startDate` | string | 是 | 开始日期，`YYYY-MM-DD` |
| `endDate` | string | 是 | 结束日期，`YYYY-MM-DD`，必须早于当前日期 |

过去 30 天应将 `endDate` 设为昨天；季度或同比比较必须分段调用。对比多个 ASIN 时分别调用，追加调用前说明积分风险。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| salesEstimateList | array | 销售估算结果列表 |

### salesEstimateList 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 查询的 ASIN |
| id | string | 数据点标识 |
| type | string | 资源类型，固定值 `sales_estimate_result` |
| parentAsin | string | 父体 ASIN（变体场景下返回） |
| isParent | boolean | 是否为父体商品 |
| isVariant | boolean | 是否为变体商品 |
| isStandalone | boolean | 是否为独立商品（非变体） |
| variants | array | 该父体下的变体 ASIN 数组 |
| dailyEstimates | array | 每日估算数据数组 |

### dailyEstimates 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 数据日期（YYYY-MM-DD） |
| estimatedUnitsSold | integer | 当日预估售出件数 |
| lastKnownPrice | number | 最近已知价格（USD） |

## MCP 参数示例

```json
{
  "toolName": "tool-jungle-scout/sales-estimates/query",
  "arguments": {
    "marketplace": "us",
    "asin": "B0D1234567",
    "startDate": "2026-08-01",
    "endDate": "2026-08-27"
  }
}
```

## 错误与展示

HTTP 200 后检查 `errcode`/`errorCode`；`200` 解析 `salesEstimateList`，`401`/授权错误和 `402`/余额错误读取 `references/onboarding.md`，其他错误根据 `errmsg` 修正 ASIN、站点、日期格式和 `endDate`。错误示例：`{"errcode":401,"errmsg":"authorized error"}`。

业务成功需检查 `errcode` / `errorCode` / `code`，不得只依据代理层成功判断。

表格至少列日期、预估销量和最近已知价格；标注数据不含今天、日期窗口和价格币种。缺失、`0` 或 `-1` 按不可用处理，不能误称为无销量。多次调用比较时并列注明每个 ASIN 与日期窗口。

## 反馈 API

使用独立地址 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，JSON 字段为 `skillName: linkfox-wb-jungle-scout`、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）和记录意图与实际结果的 `content`。




