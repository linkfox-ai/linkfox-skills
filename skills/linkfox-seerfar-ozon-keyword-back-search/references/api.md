# Seerfar Ozon 关键词反查 接口说明

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

## 接口：关键词反查

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/keywordBackSearch`

### 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。`skuIds`、`hasVariant`、`page` 为必填项，其余均可选；所有范围筛选项均为 `{min, max}` 对象，可单边或双边传值。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skuIds | array<integer> | 是 | 反查 SKU 列表，最多 20 个 |
| hasVariant | integer | 是 | 是否剔除变体：`0` 不剔除变体、`1` 剔除变体 |
| page | object | 是 | 分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20 |
| page.orders | array<object> | 否 | 排序规则，元素 `{field, direction}`；`direction` 取 `DESC`（倒序）/ `ASC`（正序） |
| page.orders[].field | string | 未单独声明 | 排序字段，如 `searchVolume`、`sellers`、`count30GrowthRate` |
| page.orders[].direction | string | 未单独声明 | `DESC` 倒序、`ASC` 正序 |
| matchType | integer | 否 | `includeKeywords` / `excludeKeywords` 的匹配模式：`0` 精准、`1` 模糊 |
| type | array<string> | 否 | 搜索词类型筛选，固定可选值：`0` 自然搜索词、`1` 广告搜索词；不传不筛选 |
| historyDate | string | 否 | 历史月份 `yyyy-MM`（如 `2026-02`）；按文档可留空查当期 |
| includeKeywords | array<string> | 否 | 包含关键词数组（最多 1000），仅返回包含指定词的搜索词 |
| excludeKeywords | array<string> | 否 | 排除关键词数组（最多 1000），剔除不相关词 |
| searchVolume | {min,max} | 否 | 月搜热度范围 |
| searchChange30 | {min,max} | 否 | 30 天搜索变化范围 |
| wordCount | {min,max} | 否 | 关键词字数范围 |
| productViews | {min,max} | 否 | 商品浏览量范围 |
| products | {min,max} | 否 | 商品数范围 |
| sellers | {min,max} | 否 | 卖家数范围 |
| marketSpace | {min,max} | 否 | 市场空间范围 |
| conversionSharing | {min,max} | 否 | 转化集中度范围 |
| uniqQueriesWCa | {min,max} | 否 | 加购数范围 |
| ca | {min,max} | 否 | 加购转化率范围 |
| conversion | {min,max} | 否 | 转化率范围 |
| titleDensity | {min,max} | 否 | 标题密度范围 |
| adRivalCount | {min,max} | 否 | 广告竞品数范围 |
| adRank | {min,max} | 否 | 广告排名范围 |
| naturalRank | {min,max} | 否 | 自然排名范围 |
| exposure | {min,max} | 否 | 曝光范围 |
| uId | string | 否 | 用户 ID |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，数据归属于 memberId） |

#### 范围筛选子字段

以下结构适用于上表全部 `{min,max}` 字段。各指标边界未区分整数或浮点类型，按数值传入，不额外收紧。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| min | number | 否 | 下界；可只传此项。 |
| max | number | 否 | 上界；可只传此项，也可与 min 同传。 |

#### 参数与使用限制

- `skuIds`、`hasVariant`、`page` 缺任意一项请求会被拒绝；SKU 为空数组触发校验失败，超出 20 个可能被拒绝或截断。
- 本接口不接收 `keyword` 种子词、`searchDate`、`categories` 或 `price` 等其他接口的独有筛选项；历史月份仅用 `historyDate`。
- 无平台筛选入参；需要限定平台时在返回结果中本地筛选。
- 推荐在 `page.orders` 中显式指定排序，减少无序翻页。`type`、自然或广告排名、曝光、转化筛选作用于每词的反查指标；不得将请求范围对象与响应同名字段的类型混淆。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 第一个位置参数，内容为上表请求体。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存响应。 |
| --no-cache | CLI flag | 否 | 禁用缓存读取与写入；默认启用 24 小时本地缓存。 |

脚本在业务传输层保留 HTTP 状态，通过 `call_api.run` 完成缓存和落盘，只有一层缓存。缓存位于 `<cwd>/linkfox/.cache/linkfox-seerfar-ozon-keyword-back-search/`，键为排序后 JSON 的 SHA-256 前 16 位，有效期为 24 小时；该目录内相同键且未过期的缓存文件可直接读取，命中标记为 `_cache.hit`。空结果或错误响应也会写入缓存，出现问题时应先解释，后续调用仍遵守成本约束。
`LINKFOX_TOOL_GATEWAY` 覆盖网关地址；两种密钥变量兼容，优先 `LINKFOX_AGENT_API_KEY`。请求头包含 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。公共调用器按会话组织目录、登记元数据，并在目录不可写时选择后续可写位置；正常使用应选择可写项目目录并设置 `SESSION_ID`，目录优先级见 SKILL.md 的输出策略。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | 总记录数 |
| data | array | 关键词反查数据（详见下方） |
| columns | array | 列定义，元素含 `{field, title, cellType, sortable, filterable}` |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应展示类型，如 `tableListWorkbenches` |

#### 脚本本地附加字段

以下字段由脚本添加，不是网关响应契约：

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer | 本次实际 HTTP 状态，成功及 HTTP 错误均保留；连接失败时无此字段。缓存命中时为缓存生成时的历史状态，不代表新请求。 |
| _cache.hit | boolean | 为 `true` 时表示读取了本地缓存，未再次请求接口。 |
| error / details | 未固定 | 连接错误，或响应为空、非 JSON、非对象时的本地诊断；`details` 保留响应内容，不能据此当作关键词结果。 |

按公共响应规则结合 `_http_status` 与 `errcode` 判断；HTTP 错误即使响应体没有 `errcode` 或写成成功码，也不能视为成功。摘要未列出 `_http_status` 时从完整文件读取。旧缓存可能没有该字段，不能据此推定 HTTP 成功；保留已有业务错误原因，需要重新核实状态时说明额外消耗后再用 `--no-cache`，不得自动重试。

#### data[*] 关键词反查对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| query | string | 关键词（俄语原文） |
| queryCn | string | 关键词中文翻译 |
| platform | integer | 平台：`0` Ozon，`1` Wildberries |
| searchVolume | integer | 月搜热度 |
| count30GrowthRate | number | 月搜增长（%，可为负） |
| productCount | integer | 商品数（部分行可能缺失） |
| competingProducts | integer | 竞品数 |
| sellers | integer | 卖家数 |
| avgPrice | number | 平均价格 |
| itemsViews | number | 商品可见度 |
| viewSharing | number | 浏览集中度（%） |
| conversionSharing | number | 转化集中度（%） |
| marketSpace | number | 市场空间 |
| returnCancellationRate | number | 退货取消率（%） |
| uniqQueriesWCa | integer | 加购数 |
| ca | number | 加购转化率（%） |
| titleDensity | number | 标题密度 |
| wordCount | integer | 字数 |
| categories | array | 类目 ID 数组 |
| dimension | object | 维度对象，承载反查专属指标（详见下方） |
| products | array | Top 商品数据（详见下方） |
| id | string | 记录 ID |
| relevancy | 未声明 | 相关度；仅在 outputSchema / columns 中定义，响应示例的 data 行不返回。 |
| categoryInfos | array<object> | 类目信息；仅在 schema / columns 中定义，响应示例的 data 行不返回，子字段见下方。 |

> **字段填充（以实际响应为准）**：响应示例中，`dimension`（维度对象）**每行均返回**，承载反查专属指标（`type` / `naturalRank` / `exposure` / `conversion` / `x`，详见下方）。`titleDensity`（标题密度）、`wordCount`（字数）每行均返回。`productCount`（商品数）大部分行返回，个别行可能为 `null`。`relevancy`（相关度）虽在 outputSchema / `columns` 中定义，但响应示例的 `data[*]` **不返回**；`categoryInfos`（类目信息）同样**不返回**（同族 `keywordMining` 亦不返回，`marketKeywordSearch` 返回——勿假设一致）。

#### dimension 维度对象字段

每行 `data[*]` 均返回 `dimension`，承载该搜索词相对反查 SKU 的专属指标；输入侧的 `type` / `naturalRank` / `adRank` / `exposure` / `conversion` 筛选项即作用于这些值。

| 字段 | 类型 | 说明 |
|------|------|------|
| type | integer | 搜索词渠道：`0` 自然搜索词、`1` 广告搜索词 |
| naturalRank | integer | 自然排名（反查 SKU 在该词下的自然位次） |
| exposure | number | 曝光（0–1） |
| conversion | number | 转化率（0–1） |
| adRank | 未声明 | 广告排名；广告词行可能额外携带，响应示例未包含，使用前判空。 |
| x | array | 位置/分页指示，语义不透明 |

> 广告词（`type:1`）行可能额外携带 `adRank`；示例 SKU 仅有自然词（`type:0`，按 `type:["1"]` 查询可返回 `total:0`），响应示例未包含 `adRank`，使用前需判空。

#### products[*] Top 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| ozonId | integer | Ozon 商品 ID |
| sku | integer | SKU ID |
| title | string | 商品标题（俄语） |
| imageUrl | string | 主图 URL |
| advert | integer | 广告标识（0/1） |

#### categoryInfos[*] 类目信息对象字段

> 响应示例的 `data[*]` 行中**不返回** `categoryInfos`（仅在 `columns` 列定义中出现）；下方字段为 outputSchema 定义，仅供出现时参考。

| 字段 | 类型 | 说明 |
|------|------|------|
| titleCn | string | 类目中文名 |
| titleEn | string | 类目英文名 |
| titleRu | string | 类目俄语名 |
| cnTitlePath | string | 中文类目路径 |
| enTitlePath | string | 英文类目路径 |
| titlePath | string | 俄语类目路径 |
| id | string | 类目 ID |
| crossBorderSellable | boolean | 是否可跨境销售 |

#### columns[*] 列定义

| 字段 | 类型 | 说明 |
|------|------|------|
| field | 未声明 | 字段标识。 |
| title | 未声明 | 列标题。 |
| cellType | 未声明 | 单元格类型。 |
| sortable | 未声明 | 是否可排序。 |
| filterable | 未声明 | 是否可筛选。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 业务含义 | 处理建议 |
|---------|----------|----------|
| 400 | 参数错误 | 查看 `errmsg`，常见为缺少 `skuIds`、`hasVariant` 或 `page`。 |
| 1002 | 参数校验失败 | 查看 `errmsg`，如 `skuIds` 为空数组；核对请求后再决定是否继续。 |

业务错误可能在 HTTP 200 下仅返回 `errcode` 与 `errmsg`，不含 `code`；成功响应示例同时携带 `code:"200"`、`errcode:200`、`msg:"ok"`、`errmsg:"ok"`。这些样本形态不替代公共响应判断规则。广告词查询可正常返回 `total:0`，空结果不等同接口故障。

错误示例：缺少 SKU 返回 `{"errcode":400,"errmsg":"skuIds 为必填参数"}`；SKU 空数组返回 `{"errcode":1002,"errmsg":"参数校验失败，请检查输入。参数 skuIds 不能为空，请至少传入一个值。"}`。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/seerfar/ozon/keywordBackSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "skuIds": [4380710124],
    "hasVariant": 0,
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "searchVolume", "direction": "DESC"}]}
  }'
```

### 响应示例（简略）

以 `skuIds:[4380710124]`、`hasVariant:0`、按 `searchVolume` DESC 反查的响应示例（截取 2 行，`products` 各保留 2 条）：

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 388,
  "costTime": 1376,
  "costToken": 16000,
  "type": "tableListWorkbenches",
  "data": [
    {
      "id": "6a4559b8d1fd12d9b57aacea",
      "query": "платье женское летнее",
      "queryCn": "夏季女装",
      "platform": 0,
      "searchVolume": 1167418,
      "count30GrowthRate": -4.7,
      "productCount": 519605,
      "competingProducts": 6221,
      "sellers": 974,
      "avgPrice": 2635.0,
      "itemsViews": 131.3,
      "viewSharing": 16.9,
      "conversionSharing": 17.9,
      "marketSpace": 188,
      "returnCancellationRate": 51.7,
      "uniqQueriesWCa": 153707,
      "ca": 13.1,
      "titleDensity": 0.0,
      "wordCount": 3,
      "categories": ["15621031_200000933_93182"],
      "dimension": {"exposure": 0.3495, "x": [1], "naturalRank": 1, "type": 0, "conversion": 0.353},
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0},
        {"ozonId": 3042328733, "sku": 3042328733, "title": "Платье BELLA ROSA", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-3/wc300/9689632131.jpg", "advert": 0}
      ]
    },
    {
      "id": "6a4559d2d1fd12d9b57e7d19",
      "query": "платье",
      "queryCn": "裙子",
      "platform": 0,
      "searchVolume": 392783,
      "count30GrowthRate": -4.2,
      "productCount": null,
      "competingProducts": 5763,
      "sellers": 974,
      "avgPrice": 5791.0,
      "itemsViews": 99.8,
      "viewSharing": 16.2,
      "conversionSharing": 18.3,
      "marketSpace": 68,
      "returnCancellationRate": 55.4,
      "uniqQueriesWCa": 43543,
      "ca": 11.1,
      "titleDensity": 1.0,
      "wordCount": 1,
      "categories": ["15621031_200000933_93182"],
      "dimension": {"exposure": 0.1176, "x": [1], "naturalRank": 1, "type": 0, "conversion": 0.1004},
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0},
        {"ozonId": 3563361777, "sku": 3563361777, "title": "Платье SIMBAL Коллекция лето 2026", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-0/wc300/9173740572.jpg", "advert": 0}
      ]
    }
  ]
}
```

> 两行均为自然词（`dimension.type:0`）；第 2 行 `productCount` 为 `null`（部分行缺失）。`relevancy` / `categoryInfos` 在响应示例的 `data[*]` 中不返回。


## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-keyword-back-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```