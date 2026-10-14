# `linkfox-google-trend-get-trend-by-keys`

## 功能说明

按一个关键词查询 Google Trends 在指定国家/地区和时间范围内的搜索兴趣，用于历史趋势、区域热度和季节性分析。返回值是选定范围内以峰值归一化的 0–100 相对热度，不是绝对搜索量。

## 能力边界与特殊规则

- 每次请求只接受一个 `keyword`，最多 100 个字符；多关键词比较必须分别调用并比较结果。
- 关键词应使用目标地区语言，例如 US 使用英文、DE 使用德文、JP 使用日文；语言不匹配时先翻译。
- 支持地区：`US`、`GB`、`JP`、`CA`、`MX`、`DE`、`FR`、`IT`、`ES`、`NL`、`AU`、`SG`、`AE`、`BR`、`IN`、`TR`、`PL`、`SE`；默认 `US`。
- `dayRangeStart` 与 `dayRangeEnd` 同时提供时，自定义时间范围优先；数据从 2004 年起，冷门词可能没有充分数据。
- 不提供绝对搜索量、Google Ads bid/CPC、Amazon 关键词、社交媒体热度、SEO 排名或网站流量，也不能将结果送入二次 SQL 查询。
- 失败或空结果不自动换词、改时间、翻页或连续试探；继续调用前先说明额外积分消耗。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`googleTrend/getTrendByKeys`，即原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- **arguments**：直接传下方请求参数对象，不添加 `body`、`params`、`data`、`headers`、Authorization、API key 或 token；WorkBuddy 自动注入授权。
- **返回解析**：先检查 MCP 连接、schema、`isError` 和代理错误；代理成功后读取 text/structured content，text 为 JSON 时只解析一次，再按响应字段检查下游状态。
- **调用纪律**：禁止 HTTP 直连或 MCP 缺失时回退；同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或结果不理想不得自动重试、翻页或改参数探测。
### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `keyword` | string | 是 | 目标地区语言的关键词，最多 100 字符 |
| `region` | string | 否 | 地区代码，默认 `US`，取支持地区列表 |
| `dayRangeStart` | string | 否 | 起始日期，`YYYY-MM-DD`，不早于 2004 年 |
| `dayRangeEnd` | string | 否 | 结束日期，`YYYY-MM-DD`，与起始日期同时传入时启用自定义范围 |

### 响应字段

#### 完整响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| trendInfoForKeys | array | 关键词趋势信息数组 |
| trendInfoForKeys[].keyword | string | 关键词 |
| trendInfoForKeys[].trendValues | array | 趋势值数组 |
| trendInfoForKeys[].trendValues[].timeRange | string | 时间，格式为 yyyy-MM-dd |
| trendInfoForKeys[].trendValues[].value | string | 值（归一化搜索热度，0-100） |
| chartOption | object | 图表渲染元数据 |
| chartOption.type | string | 数据类型 |
| chartOption.fieldX | string | X轴字段 |
| chartOption.fieldY | array | Y轴字段 |
| chartOption.data | array | 数据 |
| costToken | integer | 消耗token |

### 错误与成本

- 先按 MCP/代理层与下游业务层分层处理错误；MCP 授权和下游 401/402/403 见 `onboarding.md`。
- 参数或日期范围错误时只根据实际错误消息修正，不自动换关键词、改时间或重复调用。
- `costToken` 是来源响应定义中的消耗字段。同一任务内相同 `toolName + arguments` 不得重复调用，失败或空结果后继续调用前先提醒可能产生额外积分。

### MCP 示例

```json
{
  "toolName": "googleTrend/getTrendByKeys",
  "arguments": {
    "keyword": "wireless charger",
    "region": "US",
    "dayRangeStart": "2024-01-01",
    "dayRangeEnd": "2025-01-01"
  }
}
```


## 使用与展示

```json
{"keyword":"sunscreen","region":"AU","dayRangeStart":"2023-01-01","dayRangeEnd":"2025-12-31"}
```

展示峰值、低谷、持续变化和季节性，并解释 0–100 归一化尺度；有 `chartOption` 时说明 X/Y 字段和趋势形状。注明关键词、地区、时间范围、调用时间和数据来源，缺失或无效字段标注 N/A，不把相对热度表述成绝对销量。

## 反馈 API

若用户明确表达结果错误、不符合意图、满意、抱怨或改进建议，可异步 POST 到独立地址 `https://skill-api.linkfox.com/api/v1/public/feedback`，不要与工具网关混用：

```json
{
  "skillName":"linkfox-wb-google-tools",
  "sentiment":"NEGATIVE",
  "category":"BUG",
  "content":"说明用户意图、实际结果及问题"
}
```

`sentiment` 取 `POSITIVE`、`NEUTRAL`、`NEGATIVE`；`category` 取 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`。
