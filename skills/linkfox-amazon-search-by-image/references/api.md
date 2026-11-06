# Amazon 以图搜图 接口说明

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

## 接口：亚马逊以图搜图

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazon/searchByImage`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| imageUrl | string | 是 | 图片URL地址，请确保图片URL地址有效。最大长度：1000 |
| amazonDomain | string | 是 | 亚马逊站点，仅支持以下站点：美国(`amazon.com`)、英国(`amazon.co.uk`)、德国(`amazon.de`)、法国(`amazon.fr`)、意大利(`amazon.it`)、西班牙(`amazon.es`)、日本(`amazon.co.jp`)、印度(`amazon.in`)。默认 `amazon.com` |
| sort | string | 否 | 排序，支持价格、评分、评论数排序。可选值：`default`（默认，按相关性排序）、`price-asc-rank`（价格从低到高）、`price-desc-rank`（价格从高到低）、`rating-asc-rank`（评分从低到高）、`rating-desc-rank`（评分从高到低）、`ratings-asc-rank`（评论数从低到高）、`ratings-desc-rank`（评论数从高到低） |
| deliveryZip | string | 否 | 站内收货地址邮编或城市，如果用户未指定，则取站点（国家）的默认邮编。最大长度：1000。各站点默认邮编：美国=10001、英国=EC1A 1BB、德国=10115、法国=75001、意大利=00100、西班牙=28001、日本=100-0001、印度=110034 |
| countryOrAreaCode | string | 否 | 站外收货的国家代码（如 CN、JP、KR、TW、HK、MO、SG、TH、VN、PH、MY）。站内邮编地址和站外国家地区代码不能同时指定。注意：印度站不支持设置站外国家或地区收货。最大长度：1000 |

> `aggregateByKeepaData` 已废弃，新调用不得传入。需要 Keepa 数据时，先从图搜结果获取 ASIN，再调用对应 Keepa skill。


#### 使用限制与脚本约定

- 图片必须是有效且公开可访问的 URL；本地文件路径不能直接作为 `imageUrl`，先使用上传脚本。
- 用户要求的排序不在请求表枚举内时，应告知支持的选项，不得调用其他工具或使用替代方法补偿不支持的排序。
- `deliveryZip` 与 `countryOrAreaCode` 互斥，印度站不支持站外收货。脚本不自行改变用户的收货条件或连续试探。
- 请求不得传 `aggregateByKeepaData`；CLI 输入该字段时会删除并发出警告，之后才生成缓存键与调用接口。

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | `python scripts/amazon_search_by_image.py '<JSON 参数>'`，字段见本接口请求表。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用业务脚本的 24 小时缓存读写。底层 `call_api.run` 始终使用 `--no-cache`，不叠加第二层缓存。 |

缓存位于 `<cwd>/linkfox/.cache/linkfox-amazon-search-by-image/`，按排序后的参数 JSON 的 SHA-256 前 16 位命名；缓存格式为 JSON，TTL 为 24 小时，命中标记为 `_cache.hit=true`。缓存可能含错误或空结果；缓存命中不代表业务成功，仍按响应码规则判断。上传预签名不使用此缓存。

完整响应按 `SESSION_ID` 聚合到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-search-by-image-<timestamp>.json`；缺省会话标识在进程内稳定生成。会话信息登记在 `_meta.json` 和 `index.jsonl` 中。当前目录不可写应在请求前报错，不回退到家目录或临时目录。响应不超过 8000 UTF-8 字节时全量输出，否则输出顶层字段、常见计数及最长列表前 3 条样本；`--inline` 强制全量输出。

网关地址支持 `LINKFOX_TOOL_GATEWAY` 覆盖，并去除末尾 `/`；密钥优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。公共调用器附带 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 业务状态，按公共规则判断；错误字段表与示例使用此字段。 |
| errmsg | string | 业务或错误消息。 |
| total | integer | 总行数 |
| totalCount | integer | 总数量 |
| perPage | integer | 每页数量 |
| currentPage | integer | 当前页码 |
| type | string | 渲染的样式 |
| sourceType | string | 来源类型 |
| columns | array | 渲染的列 |
| costToken | integer | 消耗token |
| keepaDataEnriched | boolean | 是否已聚合 Keepa 增强数据；新图搜调用默认为 `false` |
| message | string | 数据边界或降级提示；应展示给用户 |
| products | array | 商品列表（详见下方商品字段） |

#### 商品字段

每个商品返回的核心字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| title | string | 商品标题 |
| imageUrl | string | 图片URL（请求地址） |
| asinUrl | string | 亚马逊ASIN的详情网址 |
| price | number | 当前价格（单位：元，如美元/欧元等） |
| oldPrice | number | 划线价格 |
| currency | string | 币种 |
| rating | number | 当前评分（0.0-5.0，如4.5星） |
| ratings | integer | 评分数量 |
| brand | string | 品牌 |
| sourceTool | string | 来源工具 |
| sourceType | string | 来源类型 |

#### 已废弃的 Keepa 聚合字段

以下字段仅保留用于兼容旧调用，新流程不应依赖。请使用 `linkfox-keepa-product-request` 查询当前商品详情，或使用 `linkfox-keepa-product-series` 查询历史趋势。

| 字段 | 类型 | 说明 |
|------|------|------|
| salesRank | integer | 销售排名(keepa) |
| salesRank30 | integer | 近30天平均销售排名(keepa) |
| salesRank90 | integer | 近90天平均销售排名(keepa) |
| salesRank180 | integer | 近180天平均销售排名(keepa) |
| monthlySalesUnits | integer | 月销量(keepa) |
| monthlySalesRevenue | number | 月销售额(keepa) |
| monthlySalesUnits1MonthAgo ~ monthlySalesUnits12MonthsAgo | integer | 1~12月前月销量(keepa) |
| reviewCount | integer | 评论数量(keepa) |
| fbaFees | number | FBA配送费(keepa)（单位：元） |
| profit | number | 利润率(keepa)（利润率百分比，如25.5表示25.5%） |
| referralFeePercentage | number | 推荐费百分比(keepa) |
| fulfillment | string | 配送方式(AMZ, FBA, FBM)(keepa) |
| primePrice | number | Prime价格(keepa) |
| buyBoxSellerId | string | 购买按钮卖家ID(keepa) |
| sellerNum | integer | 卖家数(keepa) |
| variationNum | integer | 变体数量(keepa) |
| parentAsin | string | 父ASIN(keepa) |
| availableDate | string | 上架时间(keepa)（yyyy-MM-dd HH:mm:ss） |
| lastUpdate | string | 最后更新时间(keepa)（yyyy-MM-dd HH:mm:ss） |
| manufacturer | string | 制造商(keepa) |
| model | string | 型号(keepa) |
| color | string | 颜色(keepa) |
| material | string | 产品的材质(keepa)，指其构造中使用的主要材料 |
| weight | string | 重量（克）(keepa) |
| dimension | string | 尺寸(keepa) |
| itemLength | integer | 商品长度(keepa)，单位为毫米，不可用时为0或-1 |
| itemWidth | integer | 商品宽度(keepa)，单位为毫米，不可用时为0或-1 |
| itemHeight | integer | 商品高度(keepa)，单位为毫米，不可用时为0或-1 |
| packageLength | integer | 包装长度（毫米）(keepa) |
| packageWidth | integer | 包装宽度（毫米）(keepa) |
| packageHeight | integer | 包装高度（毫米）(keepa) |
| packageWeight | string | 包装重量（克）(keepa) |
| packageDimensions | string | 包装尺寸(keepa) |
| packageQuantity | integer | 包装中商品的数量(keepa)，不可用时为0或-1 |
| dimensionsType | string | 尺寸类型(keepa) |
| categoryTree | string | 类目树(keepa) |
| categoryTreeId | string | 类目树ID(keepa) |
| rootCategory | integer | 根类目ID(keepa) |
| isAdultProduct | boolean | 是否为成人产品(keepa) |
| isHazmat | boolean | 是否为危险品(keepa) |
| urlSlug | string | URL Slug(keepa) |
| productImageUrls | array | 商品图片列表(keepa) |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `keepaDataEnriched` 新调用默认为 `false`，不因缺少 Keepa 聚合字段而判图搜失败。
- 错误信息可能使用 `errorCode` 名称，错误字段表与示例使用 `errcode`。基础成功判断统一按公共规则，不为 `errorCode` 单独定义成功条件。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazon/searchByImage" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"imageUrl":"https://m.media-amazon.com/images/I/61pAlIX8SZL._AC_SY575_.jpg","amazonDomain":"amazon.com","sort":"default"}'
```

## 接口：获取图片上传预签名地址

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| contentType | string | 是 | 上传图片的 MIME 类型，与文件扩展名对应，见下表。 |
| fileExtension | string | 是 | 不带点的小写扩展名；脚本从本地文件名提取。 |

#### 上传脚本与支持格式

| 参数 / 格式 | 类型 | 必填 | 说明 |
|---|---|---|---|
| local_image_path | CLI string | 是 | `python scripts/upload_image.py <local_image_path>`；必须是存在的本地文件，支持含空格路径。 |
| jpg / jpeg | 扩展名 | 否 | `image/jpeg` |
| png | 扩展名 | 否 | `image/png` |
| gif | 扩展名 | 否 | `image/gif` |
| webp | 扩展名 | 否 | `image/webp` |
| heic | 扩展名 | 否 | `image/heic` |

预签名地址不缓存，每次本地上传重新获取。文件不存在或扩展名不支持时，在请求前报错；文件大小是否可接受以服务实际校验结果为准。认证与网关环境变量、透传请求头遵循本接口调用规范。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 业务状态，按公共规则判断；典型成功值为 200。 |
| errmsg | string | 错误或业务消息。 |
| url | string | OSS 预签名 PUT 地址，含签名查询参数；成功时必须存在且非空，作为上传目标，不用网关地址拼接。 |

#### 后续 OSS 文件上传（非 LinkFox 网关请求）

获取地址后，脚本读取本地文件的二进制内容，向返回的完整 `url` 发起 HTTP PUT；保留签名查询串，超时 120 秒。不向 OSS 请求携带 LinkFox 的 Authorization 密钥。

| 字段 | 位置 / 类型 | 说明 |
|---|---|---|
| Content-Type | Header string | 与预签名请求的 `contentType` 相同。 |
| x-oss-object-acl | Header string | 固定 `public-read`。 |
| 文件内容 | Body bytes | 本地图片完整二进制内容。 |
| HTTP 状态码 | integer | 上传脚本仅接受 200 / 201；其他状态均报上传失败。 |

#### 上传脚本最终输出

| 字段 | 类型 | 说明 |
|---|---|---|
| url | string | 仅上传成功后输出；移除预签名 URL 的 `?` 及其查询串所得的公开图片链接，有效期 24 小时。 |

预签名原始响应通过公共调用器保存在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-search-by-image-upload-<timestamp>.json`；上传 CLI 标准输出仍只输出最终 `{ "url": "..." }` JSON，诊断信息写到 stderr，失败退出码为 1。预签名返回非对象 JSON 或缺少有效 `url` 时，保存原始响应并按失败处理，不执行 OSS PUT。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常响应且返回非空 `url` 后才能执行 OSS PUT；缺少地址时停止，不输出成功链接。
- OSS 上传只接受 HTTP 200 / 201，连接失败或其他状态应报告错误并停止图搜流程。
- 公开链接通过移除签名查询串取得；在 PUT 成功前不将其视为已上传图片。公开链接有效 24 小时。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/file/presignedPut" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"contentType":"image/png","fileExtension":"png"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-search-by-image",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
