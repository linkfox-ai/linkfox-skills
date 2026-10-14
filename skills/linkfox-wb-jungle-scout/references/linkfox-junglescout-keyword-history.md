# linkfox-junglescout-keyword-history

## 功能与适用范围

查询单个亚马逊关键词在指定日期范围内的历史精确搜索量。每个数据点代表 7 天周期，适用于趋势方向、旺淡季、节假日效应和需求波动分析。

它不做关键词拓展、ASIN 反查、PPC 竞价、当前排名、商品销量或非 Amazon 平台搜索量。

## MCP 调用

- 响应字段来源：`skills/linkfox-junglescout-keyword-history/references/api.md`。仅从该文件核对并恢复下方响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`tool-jungle-scout/keywords/historical-search-volume`
- `arguments`：直接使用本 reference 请求参数对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游 `errcode` / `errorCode` / `code` 与消息字段。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `marketplace` | string | 是 | `us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`；未指定使用 `us` |
| `keyword` | string | 是 | 单个要查询的关键词 |
| `startDate` | string | 是 | `YYYY-MM-DD` |
| `endDate` | string | 是 | `YYYY-MM-DD`；与起始日期间隔最长 366 天 |

日期跨度超过 366 天时拆成多次请求，并在报告中分段标明；不要因空结果自动改词或扩大日期。

## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| historicalSearchVolumeList | array | 历史搜索量周期列表 |

### historicalSearchVolumeList 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 数据周期标识（市场/关键词/日期范围） |
| estimateStartDate | string | 周期开始日期（YYYY-MM-DD，7天统计周期起点） |
| estimateEndDate | string | 周期结束日期（YYYY-MM-DD，7天统计周期终点） |
| estimatedExactSearchVolume | integer | 该周期内精确匹配搜索量（次/周） |
| type | string | 资源类型，固定值 `historical_keyword_search_volume` |

## MCP 参数示例

```json
{
  "toolName": "tool-jungle-scout/keywords/historical-search-volume",
  "arguments": {
    "marketplace": "us",
    "keyword": "yoga mat",
    "startDate": "2026-01-01",
    "endDate": "2026-08-27"
  }
}
```

## 错误与展示

HTTP 200 后检查 `errcode`/`errorCode`；`200` 解析 `historicalSearchVolumeList`，`401`/授权错误和 `402`/余额错误读取 `references/onboarding.md`，其他错误根据 `errmsg` 调整日期、关键词或站点。错误示例：`{"errcode":401,"errmsg":"authorized error"}`。

业务成功需检查 `errcode` / `errorCode` / `code`，不得只依据代理层成功判断。

表格展示周期起止日期和精确搜索量，并同时给出趋势图/峰谷总结；注明数据是周维度精确搜索量、查询窗口和更新时间。空字段、`0` 或 `-1` 按不可用处理，不当作需求为零。

## 反馈 API

使用独立地址 `POST https://skill-api.linkfox.com/api/v1/public/feedback`；JSON 字段：`skillName: linkfox-wb-jungle-scout`、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）和包含用户意图、实际结果与原因的 `content`。




