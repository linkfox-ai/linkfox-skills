# 亚马逊前台搜索 接口说明

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

## 接口：亚马逊前台搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/search`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 关键词；请尽量翻译为对应国家的语言，比如美国用英语关键词，德国用德语关键词等等（最大长度1024） |
| amazonDomain | string | 否 | 亚马逊各个国家站点，默认 `amazon.com` |
| node | string | 否 | 亚马逊类目节点（最大长度1000） |
| language | string | 否 | 语言区域代码，如 en_US、de_DE、ja_JP、fr_FR（最大长度1000） |
| sort | string | 否 | 排序方式：`relevanceblender`（精选，默认）、`price-asc-rank`（价格从低到高）、`price-desc-rank`（价格从高到低）、`review-rank`（平均客户评价）、`date-desc-rank`（最新到货）、`exact-aware-popularity-rank`（畅销商品） |
| page | integer | 否 | 页码（从1开始，每页大概20条），默认 `1` |
| deliveryZip | string | 否 | 配送地邮编，用于模拟亚马逊前台地址，建议使用目标国家主要城市的常用邮编，如美国站常用纽约邮编 10001（最大长度1000） |
| device | string | 否 | 设备类型：`desktop`、`mobile`、`tablet`，默认 `desktop`（最大长度1000） |
| includeSellerSpriteData | boolean | 是（Skill 调用） | 高级参数，每次 Skill 调用必须显式传入；`true` 时调用卖家精灵补全销量、销售额、品牌、履约等竞品数据，并按成功批次追加动态算力消耗，不需要补全时传 `false`。服务端为兼容旧调用，缺省时仍按 `false` 处理 |

#### 支持的 amazonDomain 值

| 域名 | 国家 |
|------|------|
| amazon.com | 美国 |
| amazon.co.uk | 英国 |
| amazon.de | 德国 |
| amazon.fr | 法国 |
| amazon.it | 意大利 |
| amazon.es | 西班牙 |
| amazon.co.jp | 日本 |
| amazon.ca | 加拿大 |
| amazon.com.au | 澳大利亚 |
| amazon.com.br | 巴西 |
| amazon.in | 印度 |
| amazon.nl | 荷兰 |
| amazon.se | 瑞典 |
| amazon.pl | 波兰 |
| amazon.sg | 新加坡 |
| amazon.sa | 沙特阿拉伯 |
| amazon.ae | 阿联酋 |
| amazon.com.mx | 墨西哥 |
| amazon.com.tr | 土耳其 |
| amazon.com.be | 比利时 |
| amazon.cn | 中国 |
| amazon.eg | 埃及 |

#### 常用 language 值

| 区域代码 | 说明 |
|----------|------|
| en_US | 美国站 英语 |
| en_GB | 英国站 英语 |
| de_DE | 德国站 德语 |
| fr_FR | 法国站 法语 |
| it_IT | 意大利站 意大利语 |
| es_ES | 西班牙站 西班牙语 |
| ja_JP | 日本站 日语 |
| en_CA | 加拿大站 英语 |
| fr_CA | 加拿大站 法语 |
| en_AU | 澳大利亚站 英语 |
| pt_BR | 巴西站 葡萄牙语 |
| en_IN | 印度站 英语 |
| hi_IN | 印度站 印地语 |
| nl_NL | 荷兰站 荷兰语 |
| sv_SE | 瑞典站 瑞典语 |
| pl_PL | 波兰站 波兰语 |
| en_SG | 新加坡站 英语 |
| ar_AE | 阿联酋/沙特阿拉伯/埃及站 阿拉伯语 |
| en_AE | 阿联酋/沙特阿拉伯/埃及站 英语 |
| tr_TR | 土耳其站 土耳其语 |
| nl_BE | 比利时站 荷兰语 |
| fr_BE | 比利时站 法语 |
| zh_CN | 中国站 中文 |
| pt_MX | 墨西哥站 西班牙语 |

#### 常用 deliveryZip 值

| 国家 | 城市 | 邮编 |
|------|------|------|
| 美国 | 纽约 | 10001 |
| 英国 | 伦敦 | EC1A 1BB |
| 德国 | 柏林 | 10115 |
| 法国 | 巴黎 | 75001 |
| 意大利 | 罗马 | 00100 |
| 西班牙 | 马德里 | 28001 |
| 日本 | 东京 | 100-0001 |
| 加拿大 | 多伦多 | M5A 1A1 |
| 澳大利亚 | 悉尼 | 2000 |
| 巴西 | 圣保罗 | 01000-000 |
| 印度 | 新德里 | 110001 |
| 荷兰 | 阿姆斯特丹 | 1012 |
| 瑞典 | 斯德哥尔摩 | 111 22 |
| 波兰 | 华沙 | 00-001 |
| 新加坡 | 新加坡 | 018989 |
| 沙特阿拉伯 | 利雅得 | 11564 |
| 阿联酋 | 阿布扎比 | 00000 |
| 墨西哥 | 墨西哥城 | 01000 |
| 土耳其 | 伊斯坦布尔 | 34349 |
| 比利时 | 布鲁塞尔 | 1000 |
| 中国 | 北京 | 100000 |
| 埃及 | 开罗 | 11511 |

#### 补全开关与使用限制

- 只有需求包含月销量、月销售额、品牌、卖家数量、履约方式或其他卖家精灵竞品字段，或用户明确要求启用时，才传 `true`；启用前说明额外动态费用。不能仅因“找竞品”自动开启。
- 关键词应使用目标站点语言。接口仅提供实时前台结果，不提供历史搜索量或历史排名；历史聚合分析应使用 ABA 等数据源。
- 每页约 20 个商品；每一页是独立请求并分别计费。每次调用模拟一次真实搜索，避免短时间连续高频请求。
- 同一会话同一参数组合默认只调用一次。失败或空结果不得自动更换关键词、翻页或修改邮编连续试探；继续检索前先向用户说明额外消耗。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 第一个位置参数为请求对象的 JSON 字符串，字段同上；保留原样传递，不自动改写关键词或补全开关。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用响应缓存读取和写入，强制重新请求；默认启用 24 小时缓存。 |

- CLI：`python scripts/amazon_search.py '<JSON 参数>' [--inline] [--no-cache]`。
- 密钥优先读取 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`；可通过 `LINKFOX_TOOL_GATEWAY` 自定义网关（去除末尾 `/`）。请求携带 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 环境头，HTTP 超时为 150 秒。
- 响应缓存由公共调用器统一管理，只有一层。位置为 `<cwd>/linkfox/.cache/linkfox-amazon-search/linkfox-amazon-search-<hash>.json`；hash 为请求 JSON 按键排序、保留中文后计算 SHA-256 的前 16 位，缓存有效期为文件修改时间起 24 小时。缓存命中时添加 `_cache.hit=true`，并提示缓存路径。缓存结果可能不是当前实时结果，需要刷新时显式使用 `--no-cache`。
- 缓存按请求参数区分，不额外按密钥或网关区分；默认也缓存接口返回的错误或空结果，不自动重试。`--no-cache` 不覆盖已有缓存。
- 完整响应及会话元数据保存在当前工作目录的 `linkfox/` 中。业务入口在请求前检查当前目录可写，并固定该输出根目录，禁止临时目录回退；不使用公共调用器的家目录或临时目录兜底。响应不超过 8000 字节时全量打印，超过时输出最大列表长度及前 3 条样本；`--inline` 始终全量打印。输出保存使用 UTF-8。
- 完整响应文件以微秒整数时间戳命名并独占创建；同秒多次查询或多个 CLI 进程遇到重名时递增文件名中的时间戳，不覆盖先前响应。每份文件登记在会话元数据中。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态码，正常响应判断遵循公共规则。 |
| errmsg | string | 业务消息或错误原因。 |
| total | integer | 总行数 |
| keyword | string | 搜索关键词 |
| type | string | 渲染的样式 |
| columns | array | 渲染的列定义 |
| costToken | integer | 消耗token |
| sellerSpriteEnriched | boolean | 本次请求是否启用了卖家精灵竞品数据补全 |
| products | array | 搜索结果列表（详见下方） |

#### products 商品对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| title | string | 标题 |
| brand | string | 品牌 |
| price | number | 价格 |
| extractedPrice | number | 解析后的价格 |
| oldPrice | number | 划线价格 |
| extractedOldPrice | number | 解析后的划线价格 |
| currency | string | 币种 |
| priceUnit | string | 价格单位 |
| extractedPriceUnit | number | 解析后的价格单位 |
| rating | number | 评分 |
| ratings | integer | 评分数 |
| position | integer | 位置 |
| sponsored | boolean | 是否赞助商 |
| imageUrl | string | 缩略图 |
| asinUrl | string | 链接 |
| delivery | string | 配送信息 |
| fulfillment | string | 配送信息（如 FBA） |
| availableDate | string (date) | 上架时间 |
| monthlySalesUnits | integer | 月销量 |
| monthlySalesRevenue | string | 月销售额 |
| sellerNation | string | 卖家国籍 |
| dimension | string | 尺寸 |
| weight | string | 重量 |
| options | string | 选项 |
| offers | string | 优惠信息 |
| badges | string | 亚马逊前台搜索标识 |
| tags | string | 标签 |
| snapEbtEligible | boolean | SNAP/EBT资格 |
| sourceType | string | 来源类型：amazon |
| sourceTool | string | 来源工具 |
| keyword | string | 关键词 |

#### 本地缓存附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 仅脚本复用本地缓存时附加的标记，不是远端业务字段。 |
| _cache.hit | boolean | 为 `true` 时表示本次结果来自本地缓存。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 原始动态消耗：`原始 costToken = 20000 + Σ(每个成功卖家精灵补全批次返回的 costToken)`。关闭补全只产生 Amazon 搜索基础消耗；开启后按搜索结果分批补全，成功批次消耗逐批累加，失败且未返回 `costToken` 的批次不追加。读取响应顶层 `costToken` 了解本次消耗，实际扣费以网关结算为准。
- 结算换算：`结算 costToken = 网关倍率 × 原始 costToken`；算力为 `ceil(结算 costToken / 2000)`，金额按算力 / 100 折算为人民币元。按当前默认倍率 1.5，关闭补全时 20000 原始 costToken 结算为 30000 costToken，即 15 算力（￥0.15）；开启补全后费用增加。最终倍率和扣费以网关实际结算为准，每页分别计费。
- 空结果时保留完整响应并提示核对查询条件，后续请求遵守上方成本限制；不能以商品列表为空替代正常响应判断。
- 脚本保留 JSON 错误响应的字段，并在实际收到非正常 HTTP 状态时附加 `transportHttpStatus` 和 `error`，避免将失败响应中的空列表当作正常空结果；这两个附加项属于脚本诊断信息，不是网关响应字段。非 JSON 的 HTTP 错误保留原始 `details`，连接错误输出 `error`，不主动重试。应依据实际响应消息解释，不另造成功判断。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazon/search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyword":"wireless earbuds","amazonDomain":"amazon.com","page":1,"includeSellerSpriteData":false}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
