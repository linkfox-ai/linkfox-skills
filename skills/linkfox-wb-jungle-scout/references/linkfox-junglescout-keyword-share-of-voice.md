# linkfox-junglescout-keyword-share-of-voice

## 功能与适用范围

按一个 Amazon 关键词分析搜索结果前 3 页的品牌声量（Share of Voice）。返回自然、广告和综合品牌数量及基础/加权 SOV、平均位置、平均价格，同时返回过去 30 天精确搜索量、PPC 建议出价中位数和 TOP 3 ASIN 点击/转化数据。

适用于品牌可见度、广告位占比、品牌集中度和关键词竞争格局判断。每次仅查询一个关键词；SOV 是抓取快照，不提供历史 SOV 曲线，也不提供产品销量、评论或 Listing 优化结论。

## MCP 调用

- 响应字段来源：`skills/linkfox-junglescout-keyword-share-of-voice/references/api.md`。仅从该文件核对并恢复下方响应字段。
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- `toolName`：`tool-jungle-scout/keywords/share-of-voice`
- `arguments`：直接使用本 reference 请求参数对象，不包裹 `body`、`params` 或 `data`。
- WorkBuddy 自动注入 Authorization；禁止传入 headers、Key、token、JWT、手机号或其他凭证。
- 先检查 MCP schema 与 `isError`；代理成功后读取 text/structured content，text 为 JSON 字符串时只解析一次，再检查下游 `errcode` / `errorCode` / `code` 与消息字段。
- MCP 缺失或失败时停止，不得 HTTP fallback。收费调用失败、空结果或不理想时不得自动重试；同一任务相同 `toolName + arguments` 只调用一次。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `marketplace` | string | 是 | `us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`；默认 `us` |
| `keyword` | string | 是 | 单个要分析的关键词 |

多关键词比较需分别调用，不能将逗号分隔的多个词当成一次请求。追加调用前说明积分消耗并由用户决定。

## 响应结构

### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| shareOfVoice | object | Share of Voice 数据主体 |

### shareOfVoice 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 资源标识 |
| type | string | 固定值 `share_of_voice` |
| estimated30DaySearchVolume | integer | 过去 30 天精确匹配搜索量 |
| exactSuggestedBidMedian | number | PPC 竞价中位数（美元） |
| productCount | integer | 前 3 页搜索结果中的商品总数 |
| updatedAt | string | 数据更新时间 |
| topAsinsModelStartDate | string | TOP ASIN 点击/转化数据窗口起始日期 |
| topAsinsModelEndDate | string | TOP ASIN 点击/转化数据窗口结束日期 |
| brands | array | 品牌 SOV 明细列表 |
| topAsins | array | TOP 3 ASIN 点击转化列表 |

### brands 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| brand | string | 品牌名称 |
| organicProducts | integer | 自然搜索结果中的商品数量 |
| sponsoredProducts | integer | 广告位中的商品数量 |
| combinedProducts | integer | 综合商品数量 |
| organicBasicSov | number | 自然搜索基础 SOV（0–1） |
| organicWeightedSov | number | 自然搜索加权 SOV（0–1） |
| sponsoredBasicSov | number | 广告搜索基础 SOV（0–1） |
| sponsoredWeightedSov | number | 广告搜索加权 SOV（0–1） |
| combinedBasicSov | number | 综合基础 SOV（0–1） |
| combinedWeightedSov | number | 综合加权 SOV（0–1） |
| organicAveragePosition | number | 自然搜索平均排名位置 |
| sponsoredAveragePosition | number | 广告搜索平均排名位置 |
| combinedAveragePosition | number | 综合平均排名位置 |
| organicAveragePrice | number | 自然搜索商品平均价格 |
| sponsoredAveragePrice | number | 广告搜索商品平均价格 |
| combinedAveragePrice | number | 综合商品平均价格 |

### topAsins 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN 编号 |
| name | string | 商品名称 |
| brand | string | 品牌名称 |
| clicks | integer | 点击量（30 天窗口） |
| conversions | integer | 转化量（30 天窗口） |
| conversionRate | number | 转化率（0–1） |

## MCP 参数示例

```json
{
  "toolName": "tool-jungle-scout/keywords/share-of-voice",
  "arguments": {
    "marketplace": "us",
    "keyword": "portable charger"
  }
}
```

## 错误与展示

HTTP 200 后检查 `errcode`/`errorCode`；`200` 读取 `shareOfVoice`，`401`/授权错误和 `402`/余额错误读取 `references/onboarding.md`，其他错误根据 `errmsg` 修正站点或关键词。错误示例：`{"errcode":401,"errmsg":"authorized error"}`。

业务成功需检查 `errcode` / `errorCode` / `code`，不得只依据代理层成功判断。

品牌表按 `combinedWeightedSov` 降序并突出前 5 个品牌；上下文先展示 30 天搜索量和 PPC 中位价，再单列 TOP 3 ASIN 点击、转化和转化率。注明只覆盖前 3 页、数据更新时间和 30 天窗口；缺失、`0` 或 `-1` 字段按 N/A 处理。

## 反馈 API

使用 `POST https://skill-api.linkfox.com/api/v1/public/feedback`，请求 JSON 包括 `skillName: linkfox-wb-jungle-scout`、`sentiment`（`POSITIVE`/`NEUTRAL`/`NEGATIVE`）、`category`（`BUG`/`COMPLAINT`/`SUGGESTION`/`OTHER`）及描述意图和实际结果的 `content`。反馈地址与工具端点分离。




