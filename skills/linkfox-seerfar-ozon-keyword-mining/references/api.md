# Seerfar Ozon 关键词挖掘 接口说明

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

## 接口：关键词挖掘

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/seerfar/ozon/keywordMining`

### 请求参数

POST Body（JSON）。以下字段与接口 `inputSchema` 一致。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 种子关键词，挖掘围绕该词展开（maxLength 1000） |
| page | object | 是 | 分页与排序：`{page, pageSize, orders[]}` |
| page.page | integer | 否 | 页码，从 1 开始，默认 1 |
| page.pageSize | integer | 否 | 每页条数，默认 20 |
| page.orders | array | 否 | 排序规则，元素为 `{field, direction}`，子字段见下表 |
| matchType | integer | 否 | 关键词匹配模式：`0` 精准、`1` 模糊；作用于种子词及 `includeKeywords`，模糊匹配用于扩大拓展，精准匹配用于收窄 |
| includeKeywords | array<string> | 否 | 包含关键词数组（最多 1000），用于在种子词基础上进一步收窄/指定必须出现的词 |
| excludeKeywords | array<string> | 否 | 排除关键词数组（最多 1000），用于剔除不相关词 |
| wordCount | {min,max} | 否 | 关键词字数/字符数范围 |
| searchVolume | {min,max} | 否 | 搜索热度范围 |
| searchChange30 | {min,max} | 否 | 30 天搜索变化范围 |
| productViews | {min,max} | 否 | 商品浏览量范围 |
| products | {min,max} | 否 | 商品数范围 |
| sellers | {min,max} | 否 | 卖家数范围 |
| price | {min,max} | 否 | 价格范围 |
| marketSpace | {min,max} | 否 | 市场空间范围 |
| conversionSharing | {min,max} | 否 | 转化集中度范围 |
| relevancy | {min,max} | 否 | 相关度范围（与种子词的相关程度） |
| uniqQueriesWCa | {min,max} | 否 | 加购数范围 |
| ca | {min,max} | 否 | 加购转化率范围 |
| titleDensity | {min,max} | 否 | 标题密度范围 |
| adRivalCount | {min,max} | 否 | 广告竞品数范围 |
| uId | string | 否 | 用户 ID |
| memberId | string | 否 | 成员 ID（一个成员唯一标识，数据归属于 memberId） |

> **与市场热词搜索的区别**：不支持按 `searchDate` 选月、不支持按 `categories` 类目筛选，也没有 `monthlySales` / `monthlyRevenue` / `volume` / `reviews` / `ratings` / `weight` 等筛选项。若需浏览全市场热词请改用 `marketKeywordSearch`。
> **排序**：建议通过 `page.orders` 按核心指标排序（如 `searchVolume` DESC、`sellers` ASC、`relevancy` DESC），避免在无序大结果集中翻页。

#### 排序对象 `page.orders[*]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| field | string | 未明确 | 排序字段，例如 `searchVolume`、`sellers`、`relevancy` |
| direction | string | 未明确 | `DESC` 倒序、`ASC` 正序；默认值未约定 |

#### 范围筛选对象

上表所有 `{min,max}` 均为对象，适用于各自的指标；两个子字段均可选，可只给单边或同时给上下界。数值类型未细分为整数或小数，不额外收窄数值范围。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| min | 数值 | 否 | 对应指标下界 |
| max | 数值 | 否 | 对应指标上界 |

#### 脚本选项与缓存

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON | 是 | 第一个位置参数，按上述字段原样提交 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应 |
| --no-cache | CLI flag | 否 | 禁用响应缓存的读取和写入，重新请求 |

默认使用 24 小时单层响应缓存，路径为 `<cwd>/linkfox/.cache/linkfox-seerfar-ozon-keyword-mining/`。缓存键使用参数排序 JSON 的 SHA-256 前 16 位；命中时标记 `_cache.hit=true` 并仍保存完整响应。业务脚本通过公共调用器运行，不叠加第二层缓存。错误和空结果也可能被缓存；需要绕过缓存重新查询时使用 `--no-cache`，并遵守 SKILL.md 的成本约束。
会话数据固定保存在当前工作目录，不回退到家目录或临时目录；当前目录不可写时在请求前报错。网关支持 `LINKFOX_TOOL_GATEWAY` 覆盖；认证依次兼容 `LINKFOX_AGENT_API_KEY` 与 `LINKFOXAGENT_API_KEY`，会话请求头保留 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。

缓存中的 `_http_status` 是产生该响应时的历史状态，命中缓存不代表发起了新请求。旧缓存可能没有此字段，此时 HTTP 状态未知，不从 `code` / `errcode` 推断；确需重新确认状态时，按成本约束决定是否使用 `--no-cache`。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 返回码，`"200"` 表示成功（成功时返回） |
| errcode | integer | 错误码，`200` 表示成功；业务错误时仅返回此项（成功时与 `code` 并存） |
| msg | string | 消息；成功为 `ok` |
| errmsg | string | 错误消息；成功为 `ok`，业务错误时为原因描述 |
| total | integer | 总记录数 |
| data | array | 关键词挖掘数据（详见下方） |
| columns | array | 列定义，元素字段见下方 `columns[*]` 表 |
| costTime | integer | 接口耗时（毫秒） |
| costToken | integer | 消耗 Token 数量 |
| type | string | 响应展示类型，如 `tableListWorkbenches` |

#### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer | 业务脚本记录的实际 HTTP 状态码，非网关业务字段；用于结合公共响应码规则判断状态，不覆盖响应体中的 `code` / `errcode` / 错误原因。未获得 HTTP 响应的连接错误不附加此字段 |

#### data[*] 关键词市场对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| query | string | 关键词（俄语原文） |
| queryCn | string | 关键词中文翻译 |
| platform | integer | 平台：`0` Ozon，`1` Wildberries |
| searchVolume | integer | 月搜热度 |
| count30GrowthRate | number | 月搜增长（%，可为负） |
| productCount | integer | 商品数；大部分行返回，与种子词完全一致的行可能缺失 |
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
| relevancy | number | 与种子词的相关程度；种子词本身为 `100`，相关词的值更低；按该字段降序可优先保留贴合主题的词 |
| titleDensity | number | 关键词在商品标题中的密度，数据行中有返回 |
| wordCount | integer | 字数，数据行中有返回 |
| categories | array | 类目 ID 数组 |
| categoryInfos | array | schema 中定义的类目信息；仅见于列定义，数据行不填充，需判空；出现时按下方字段表解析，不套用市场关键词搜索接口的填充行为 |
| products | array | Top 商品数据（详见下方） |
| id | string | 记录 ID |
| dimension | 未限定 | 维度信息，虽在 schema / 列定义中出现，数据行不填充，需判空 |

#### products[*] Top 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| ozonId | integer | Ozon 商品 ID |
| sku | integer | SKU ID |
| title | string | 商品标题（俄语） |
| imageUrl | string | 主图 URL |
| advert | integer | 广告标识（0/1） |

#### categoryInfos[*] 类目信息对象字段

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

#### `columns[*]` 列定义

| 字段 | 类型 | 说明 |
|------|------|------|
| field | 未限定 | 列对应的字段名 |
| title | 未限定 | 列标题 |
| cellType | 未限定 | 单元格展示类型 |
| sortable | 未限定 | 排序能力标记 |
| filterable | 未限定 | 筛选能力标记 |

数据以 Ozon 为主，可包含 Wildberries；无平台过滤入参，需要时按响应中的 `platform` 在本地筛选。返回的 `categories` 可用于本地分组或过滤，不代表支持同名请求参数。`columns` 不透明且可能部分填充，不作为数据行已存在对应字段的证据；缺失的 `dimension` 也需判空。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

业务错误可能在 HTTP 200 时仅返回 `errcode`、`errmsg`，没有 `code`；按公共规则判断状态，勿因缺少 `code` 而丢弃错误原因。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 400 | 参数错误 | 查看 `errmsg`；常见为缺 `keyword` / `page` 或关键词为空，补齐后是否继续调用遵守成本约束 |

缺种子词的错误示例：

```json
{"errcode": 400, "errmsg": "keyword 为必填参数", "keyword": ""}
```

缺分页对象的错误示例：

```json
{"errcode": 400, "errmsg": "page 为必填参数"}
```

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/seerfar/ozon/keywordMining \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "keyword": "платье",
    "page": {"page": 1, "pageSize": 5, "orders": [{"field": "searchVolume", "direction": "DESC"}]}
  }'
```

### 响应示例

以 `keyword:"платье"`、按 `searchVolume` DESC 挖掘的真实响应（截取 2 行，`products` 各保留 1 条）：

```json
{
  "code": "200",
  "msg": "ok",
  "errcode": 200,
  "errmsg": "ok",
  "total": 1000,
  "costTime": 4255,
  "costToken": 16000,
  "type": "tableListWorkbenches",
  "data": [
    {
      "id": "6a4559d2d1fd12d9b57e7d19",
      "query": "платье",
      "queryCn": "裙子",
      "platform": 0,
      "searchVolume": 392783,
      "count30GrowthRate": -4.2,
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
      "relevancy": 100,
      "titleDensity": 1.0,
      "wordCount": 1,
      "categories": ["15621031_200000933_93182"],
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0}
      ]
    },
    {
      "id": "6a4559bcd1fd12d9b57b6866",
      "query": "платье женское",
      "queryCn": "女装",
      "platform": 0,
      "searchVolume": 349725,
      "count30GrowthRate": -29.4,
      "productCount": 711194,
      "competingProducts": 5974,
      "sellers": 1063,
      "avgPrice": 5261.0,
      "itemsViews": 137.3,
      "viewSharing": 15.0,
      "conversionSharing": 18.8,
      "marketSpace": 59,
      "returnCancellationRate": 49.4,
      "uniqQueriesWCa": 41624,
      "ca": 11.9,
      "relevancy": 12,
      "titleDensity": 0.1,
      "wordCount": 2,
      "categories": ["15621031_200000933_93182", "15621031_200000933_93184"],
      "products": [
        {"ozonId": 4380710124, "sku": 4380710124, "title": "Платье T-SOD", "imageUrl": "https://ir.ozone.ru/s3/multimedia-1-7/wc300/10636393147.jpg", "advert": 0}
      ]
    }
  ]
}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-seerfar-ozon-keyword-mining",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```