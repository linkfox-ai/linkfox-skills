# 友鹰 Shopee 商品选品 接口说明

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

## 接口：商品查询与筛选（getProductInfos）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/youying/shopee/getProductInfos`

### 请求参数

POST Body（JSON）：

#### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| station | string | 是 | **必填**。Shopee站点，可传名称或代码。见下方站点映射表 |

#### 站点映射

| 站点 | station 值 | 代码 |
|------|-----------|------|
| 马来西亚 | malaysia | MY |
| 中国台湾 | taiwan_china | Taiwan_CHN |
| 印度尼西亚 | indonesia | ID |
| 泰国 | thailand | TH |
| 菲律宾 | philippines | PH |
| 新加坡 | singapore | SG |
| 越南 | vietnam | VN |
| 巴西 | brazil | BR |
| 墨西哥 | mexico | MX |
| 智利 | chile | CL |
| 哥伦比亚 | columbia | CO |

#### 关键词筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 商品标题关键词 |
| keywordType | integer | 否 | 匹配模式：1=整句语句(默认)，2=多词AND，3=多词OR |
| notExistKeyword | string | 否 | 排除包含此关键词的商品 |
| notExistKeywordType | integer | 否 | 排除匹配模式：1=整句(默认)，2=多词AND，3=多词OR |

#### 价格筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| priceMin | number | 否 | 商品总价起始值（当地货币） |
| priceMax | number | 否 | 商品总价结束值 |

#### 销量筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| soldMin | integer | 否 | 前30天销售件数起始值 |
| soldMax | integer | 否 | 前30天销售件数结束值 |
| estimateSoldStart | integer | 否 | 估算前30天销售件数起始值 |
| estimateSoldEnd | integer | 否 | 估算前30天销售件数结束值 |
| historicalSoldStart | integer | 否 | 商品总销售件数起始值 |
| historicalSoldEnd | integer | 否 | 商品总销售件数结束值 |
| paymentStart | number | 否 | 前30天销售金额起始值 |
| paymentEnd | number | 否 | 前30天销售金额结束值 |

#### 评价筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ratingMin | number | 否 | 商品评分最小值（0-5） |
| ratingMax | number | 否 | 商品评分最大值 |
| ratingsMin | integer | 否 | 评分数起始值 |
| ratingsMax | integer | 否 | 评分数结束值 |
| favoriteMin | integer | 否 | 收藏数起始值 |
| favoriteMax | integer | 否 | 收藏数结束值 |

#### SKU 筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skuNumberStart | integer | 否 | SKU总数起始值 |
| skuNumberEnd | integer | 否 | SKU总数结束值 |

#### 时间筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| listingDateFrom | string | 否 | 商品上架时间起始值（格式: yyyy-MM-dd） |
| listingDateTo | string | 否 | 商品上架时间结束值（格式: yyyy-MM-dd） |
| statTimeStart | string | 否 | 统计时间起始值（格式: yyyy-MM-dd HH:mm:ss） |
| statTimeEnd | string | 否 | 统计时间结束值（格式: yyyy-MM-dd HH:mm:ss） |
| lastModiTimeStart | string | 否 | 最新抓取时间起始值（格式: yyyy-MM-dd） |
| lastModiTimeEnd | string | 否 | 最新抓取时间结束值（格式: yyyy-MM-dd） |
| approvedDateStart | string | 否 | 店铺开张时间起始值（格式: yyyy-MM-dd） |
| approvedDateEnd | string | 否 | 店铺开张时间结束值（格式: yyyy-MM-dd） |

#### 类目筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pL1Id | string | 否 | 1级类目ID |
| pL2Id | string | 否 | 2级类目ID |
| pL3Id | string | 否 | 3级类目ID |
| cidList | string | 否 | 类目id列表，完整路径，多组用`｜`隔开，如: `AAA,BBB,CCC｜DDD,EEE` |

#### 店铺筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shopIdList | string | 否 | 指定店铺id列表，多个逗号隔开 |
| notExistShopIdList | string | 否 | 排除店铺id列表，多个逗号隔开 |
| merchant | string | 否 | 店铺名称或用户名称 |
| shopLocation | string | 否 | 店铺所在地 |

#### 商品属性筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shippingIconType | integer | 否 | 店铺所在地：0=本地, 1=海外 |
| cbOption | integer | 否 | 发货地点：0=本土, 1=跨境 |
| isShopeeVerified | integer | 否 | 虾皮优选：0=非优选, 1=优选 |
| isOfficialShop | integer | 否 | 官方店铺：0=否, 1=是 |
| isHotSales | integer | 否 | 是否热销：0=非热销, 1=热销 |
| pids | string | 否 | 商品id列表(最多500个)，逗号隔开 |

#### 排序与分页

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| orderBy | string | 否 | - | 排序字段：`rating`(评分), `price`(价格), `historical_sold`(总销量), `sold`(30天销量), `payment`(30天销售额), `favorite`(收藏数), `ratings`(评分数), `gen_time`(上架时间), `estimate_sold`(估算销量) |
| orderByType | string | 否 | DESC | 排序方向：`ASC`(升序), `DESC`(降序) |
| page | integer | 否 | 1 | 页码（从1开始） |
| pageSize | integer | 否 | 1000 | 每页商品数（范围1-1000） |

#### 参数约束与使用限制

- `station` 始终必填，可传上述站点名称或代码；未指定时询问用户。脚本按传入值透传，不擅自转换站点值。
- 标题关键词匹配与排除分别通过 `keywordType` 和 `notExistKeywordType` 设置。数值区间可按需只传一侧或同时传起止值。
- `pids` 最多包含 500 个商品 ID；`page` 从 1 开始，`pageSize` 为 1–1000，默认 1000。
- `price` 和 `payment` 等金额为当地货币，不是美元；站点币种依次为：马来西亚 MYR、中国台湾 TWD、印尼 IDR、泰国 THB、菲律宾 PHP、新加坡 SGD、越南 VND、巴西 BRL、墨西哥 MXN、智利 CLP、哥伦比亚 COP。
- 数据时效取决于友鹰抓取进度，`lastModiTime` 表示最新抓取时间。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 第一个位置参数，完整对象透传为请求体。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过缓存读取与写入；默认使用 24 小时缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 优先使用此网关地址，否则采用公共规则中的默认地址；移除尾部斜杠。 |
| LINKFOX_AGENT_API_KEY | 环境变量 | 认证必需其一 | 优先使用的 API Key。 |
| LINKFOXAGENT_API_KEY | 环境变量 | 认证必需其一 | 备用 API Key；优先变量为空时使用。 |
| SESSION_ID | 环境变量 | 否 | 聚合同一任务的数据，未设置时自动生成；须为单个目录名，不允许路径分隔符、冒号、`.` 或 `..`。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 与 SESSION_ID 一起作为同名请求头透传；未设置时传空字符串。 |

入口为 `scripts/youying_shopee_search.py`，通过 `call_api.run` 统一调用，不另建 HTTP transport 或缓存层。
缓存位于 `<cwd>/linkfox/.cache/linkfox-youying-shopee-get-product-infos/`，缓存键为排序后 JSON 的 SHA-256 前 16 位，TTL 为 24 小时；该路径下符合键算法且未过期的缓存可直接命中，命中时增加 `_cache.hit=true`。完整响应（包括错误、空结果）均会缓存；不自动重试。
业务封装沿用此缓存位置和键；Windows 下使用扩展绝对路径访问，避免缓存文件名超过传统路径长度限制时写入失败而重复请求。
响应及会话元数据仅写入当前工作目录下的 `linkfox/`，忽略公共调用器的其他目录回退；当前目录不可写时在请求前报错，不回退到用户家目录或临时目录，不写入 `/tmp`。公共调用器提供唯一的响应缓存层。
完整响应文件使用 `<slug>-<timestamp>.json` 命名；业务封装以独占创建分配文件名，时间戳重名时递增，避免同秒连续查询或缓存命中覆盖已有响应，并将各文件分别登记到会话元数据。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码；按公共规则判断，认证失败示例值为 401。 |
| errmsg | string | 网关错误消息，认证失败示例值为 authorized error。 |
| errorCode | 未约定 | 兼容状态字段名；具体类型以实际响应为准。响应表格和认证失败示例使用 errcode，响应判断遵循公共规则。 |
| total | integer | 当前返回记录数 |
| totalSize | integer | 总结果数 |
| sourceTool | string | 来源工具标识 |
| sourceType | string | 来源类型：`shopee` |
| columns | array | 渲染列定义 |
| costToken | integer | 消耗 token |
| type | string | 渲染样式 |
| products | array | 商品列表（见下方字段） |

#### products 数组中每个商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| pid | string | 商品唯一ID |
| title | string | 商品标题 |
| description | string | 商品描述 |
| imageUrl | string | 商品主图URL |
| productUrl | string | Shopee商品链接 |
| shopeeUrl | string | Shopee域名下的商品链接 |
| price | number | 商品默认价（当地货币） |
| minPrice | number | SKU最低价 |
| maxPrice | number | SKU最高价 |
| sold | integer | 前30天销售件数 |
| estimateSold | integer | 估算前30天销售件数 |
| historicalSold | integer | 商品总销售件数 |
| payment | number | 前30天销售额（当地货币） |
| rating | number | 商品评分（0-5） |
| ratings | integer | 评分数 |
| favorite | integer | 收藏数 |
| viewCount | integer | 浏览数 |
| stock | integer | 库存数 |
| skuNumber | integer | SKU数量 |
| genTime | string | 上架时间 |
| statTime | string | 统计时间 |
| lastModiTime | string | 最新抓取时间 |
| categoryStructure | string | 类目结构路径 |
| cid | string | 类目ID（逗号分隔） |
| shopId | string | 店铺ID |
| shopName | string | 店铺名称 |
| shopUrl | string | 店铺链接 |
| userName | string | 店主名称 |
| shopLocation | string | 店铺所在地 |
| shopProductsCount | integer | 店铺商品总数 |
| approvedDate | string | 店铺开张时间 |
| isOfficialShop | integer | 是否官方店铺（1=是, 0=否） |
| isShopeeVerified | integer | 虾皮优选（1=是, 0=否） |
| isHotSales | integer | 是否热销（1=是, 0=否） |
| shippingIconType | integer | 店铺所在地类型（0=本地, 1=海外, 3或null=未知） |
| cbOption | integer | 发货地点（0=本土, 1=跨境） |
| estimatedDays | integer | 预计到货天数 |
| status | integer | 商品状态（1=正常, 0=下架, 8=列表中排除） |
| notExist | integer | 是否存在（0=存在, 1=不存在） |

#### 脚本本地附加字段

- `_http_status`：本次实际请求的 HTTP 状态码，由业务脚本记录，不是网关响应字段；用于按公共规则区分 HTTP 成功与失败，并识别 401 / 402。保留响应正文的 `errcode`、`errmsg` 等字段，不以 HTTP 状态覆盖业务状态。摘要未显示该值时，从保存文件按需读取。
- `_cache.hit=true`：命中本地缓存；此时 `_http_status`（若有）是缓存生成时的历史状态，不代表本次发起请求。既有缓存可能缺少 `_http_status`，连接失败也没有实际 HTTP 状态；不得据此推断 HTTP 200，也不自动补发请求。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 本接口没有额外业务状态码判断。`total` 为本次返回记录数，`totalSize` 为总结果数；二者不可混用。字段结构以真实响应为准，不补造未返回的商品数据。

### 响应示例

认证失败示例：

```json
{"errcode":401,"errmsg":"authorized error"}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/youying/shopee/getProductInfos" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"station":"malaysia","keyword":"Storage Box","keywordType":2,"soldMin":100,"orderBy":"sold","orderByType":"DESC","pageSize":50}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-youying-shopee-get-product-infos",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```