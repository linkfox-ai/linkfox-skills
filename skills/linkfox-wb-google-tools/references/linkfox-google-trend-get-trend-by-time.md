# `linkfox-google-trend-get-trend-by-time`

## 功能说明

查询指定国家/地区最近若干天的 Google 热门搜索和上升话题，用于实时热点发现、短期需求扫描和爆发趋势识别。每条热门查询包含相对搜索量、涨幅和观察时间窗。

## 能力边界与特殊规则

- `days` 面向近期窗口，常用值为 `1`（最近 24 小时）、`2`、`7`，默认 `7`；不用于月度或年度历史曲线。
- 支持地区：`US`、`GB`、`JP`、`CA`、`MX`、`DE`、`FR`、`IT`、`ES`、`NL`、`AU`、`SG`、`AE`、`BR`、`IN`、`TR`、`PL`、`SE`；默认 `US`。
- `searchVolume` 和 `increasePercentage` 是相对指标；涨幅范围为 −100 至 100（百分比），不可解释为绝对人数。
- 不提供社会媒体、Amazon、广告、SEO 或竞品网站流量趋势；不自动换地区、改天数或重试空结果。

## MCP 调用

- **MCP server**：`LinkFox`
- **唯一工具**：`proxy_call`
- **toolName**：`googleTrend/getTrendByTime`，即原 endpoint 去掉前导 `/` 后的精确值，区分大小写。
- **arguments**：直接传下方请求参数对象，不添加 `body`、`params`、`data`、`headers`、Authorization、API key 或 token；WorkBuddy 自动注入授权。
- **返回解析**：先检查 MCP 连接、schema、`isError` 和代理错误；代理成功后读取 text/structured content，text 为 JSON 时只解析一次，再按响应字段检查下游状态。
- **调用纪律**：禁止 HTTP 直连或 MCP 缺失时回退；同一任务内相同 `toolName + arguments` 只调用一次。失败、空结果或结果不理想不得自动重试、翻页或改参数探测。
### 请求参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `days` | integer | 否 | `7` | 最近多少天，常用 `1`、`2`、`7` |
| `region` | string | 否 | `US` | 支持地区代码 |

### 响应字段

#### 顶层响应

| 字段路径 | 类型 | 说明 |
|---|---|---|
| costToken | integer | 消耗token |
| chartOption | object | 图表配置对象，包含可视化数据 |
| chartOption.data | array | 数据，图表数据点对象数组 |
| chartOption.fieldX | string | X轴字段 |
| chartOption.fieldY | array | Y轴字段 |
| chartOption.type | string | 数据类型 |
| chartOption.title | string | 标题 |
| trendValues | array | 趋势值，热门查询对象数组（见下方） |

#### `trendValues[]`

| 字段路径 | 类型 | 说明 |
|---|---|---|
| trendValues[].query | string | 关键词 |
| trendValues[].searchVolume | integer | 搜索量值 |
| trendValues[].increasePercentage | integer | 涨幅百分比：整数，取值范围 −100～100，单位为％ |
| trendValues[].startTime | string | 开始时间戳 |
| trendValues[].endTime | string | 结束时间戳 |

### 错误与成本

- 先按 MCP/代理层与下游业务层分层处理错误；MCP 授权和下游 401/402/403 见 `onboarding.md`。
- 地区代码或时间窗口错误时只根据实际错误消息修正，不自动换地区、改窗口或重复调用。
- `costToken` 是来源响应定义中的消耗字段。同一任务内相同 `toolName + arguments` 不得重复调用，失败或空结果后继续调用前先提醒可能产生额外积分。

### MCP 示例

```json
{
  "toolName": "googleTrend/getTrendByTime",
  "arguments": {
    "days": 7,
    "region": "US"
  }
}
```


## 使用与展示

```json
{"days":1,"region":"JP"}
```

表格至少展示 `query`、`searchVolume`、`increasePercentage`；高涨幅（例如超过 50%）可标为爆发话题。摘要必须写明地区和具体时间窗；有 `chartOption` 时说明标题、坐标和数据点。错误时依据 `errmsg` 建议修改地区代码或窗口，不把相对指标写成绝对搜索量。

## 反馈 API

用户表达结果错误、与意图不符、满意、抱怨或建议时，可异步 POST 到 `https://skill-api.linkfox.com/api/v1/public/feedback`，该地址独立于工具网关：

```json
{"skillName":"linkfox-wb-google-tools","sentiment":"NEUTRAL","category":"SUGGESTION","content":"说明用户意图、实际结果及建议"}
```

允许的 `sentiment` 为 `POSITIVE`、`NEUTRAL`、`NEGATIVE`；`category` 为 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`。
