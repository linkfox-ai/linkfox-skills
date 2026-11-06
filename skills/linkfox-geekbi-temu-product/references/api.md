# GeekBI Temu 商品搜索与详情 接口说明

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


## 接口：商品搜索（goodsSearch）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/goodsSearch`

### 请求参数

POST Body（JSON）。所有字段均可选；空对象 `{}` 使用 `regionId=211`、`page=1`、`size=20`、`matchMode=2`。

#### 分页、匹配、品类与状态

| 参数 | 类型 | 必填 | 默认值 / 约束 | 说明 |
|---|---|---:|---|---|
| `regionId` | integer | 否 | `211`（美国）；`>=1` | Temu 地区 ID；只取非空有效的 `sites[].regionId`，不得用 `siteId` 替代 |
| `page` | integer | 否 | `1`；`>=1` | 页码 |
| `size` | integer | 否 | `20`；`1..200` | 每页数量；`page * size` 不得超过 10000 |
| `keyword` | string | 否 | 最大 300 字符 | 匹配商品标题的关键词 |
| `matchMode` | integer | 否 | `2`；`1..2` | `1`=严格匹配，`2`=模糊匹配 |
| `catIds` | integer[] | 否 | - | 品类 ID 数组；元素只取品类列表非空有效的 `categories[].catId` |
| `status` | integer[] | 否 | 元素为 `1`、`2`、`3` | `1`=正常，`2`=缺货，`3`=下架 |
| `hostingMode` | integer | 否 | `1..2` | `1`=全托管，`2`=半托管 |
| `sort` | string | 否 | 最大 100 字符 | 排序字段；只使用接口确认支持的字段 |
| `order` | string | 否 | `asc` 或 `desc` | 排序方向，不区分大小写 |

`catIds` 中空值会被服务端过滤，`status` 中空值会被拒绝；调用方只传有效整数。

网关 JSON 中 `catIds` 和 `status` 必须传数组，例如 `{"catIds":[984,982],"status":[1,2]}`。服务端会把数组编码为上游单个英文逗号参数；不要在 JSON 中传逗号字符串，也不要传重复键。

#### 销量、销售额与增长率

| 参数 | 类型 | 必填 | 默认值 | 约束 / 单位 |
|---|---|---|---|---|
| `soldMin` | integer | 否 | 未指定 | 历史累计总销量，`>=0` |
| `soldMax` | integer | 否 | 未指定 | 历史累计总销量，`>=0` |
| `daySoldMin` | integer | 否 | 未指定 | 平均日销量，`>=0` |
| `daySoldMax` | integer | 否 | 未指定 | 平均日销量，`>=0` |
| `weekSoldMin` | integer | 否 | 未指定 | 平均周销量，`>=0` |
| `weekSoldMax` | integer | 否 | 未指定 | 平均周销量，`>=0` |
| `monthSoldMin` | integer | 否 | 未指定 | 平均月销量，`>=0` |
| `monthSoldMax` | integer | 否 | 未指定 | 平均月销量，`>=0` |
| `daySoldRateMin` | number | 否 | 未指定 | 日销量增长率，百分比 |
| `daySoldRateMax` | number | 否 | 未指定 | 日销量增长率，百分比 |
| `weekSoldRateMin` | number | 否 | 未指定 | 周销量增长率，百分比 |
| `weekSoldRateMax` | number | 否 | 未指定 | 周销量增长率，百分比 |
| `monthSoldRateMin` | number | 否 | 未指定 | 月销量增长率，百分比 |
| `monthSoldRateMax` | number | 否 | 未指定 | 月销量增长率，百分比 |
| `salesMin` | number | 否 | 未指定 | 历史累计销售额，当前站点货币，`>=0` |
| `salesMax` | number | 否 | 未指定 | 历史累计销售额，当前站点货币，`>=0` |
| `daySalesMin` | number | 否 | 未指定 | 平均日销售额，当前站点货币，`>=0` |
| `daySalesMax` | number | 否 | 未指定 | 平均日销售额，当前站点货币，`>=0` |
| `weekSalesMin` | number | 否 | 未指定 | 平均周销售额，当前站点货币，`>=0` |
| `weekSalesMax` | number | 否 | 未指定 | 平均周销售额，当前站点货币，`>=0` |
| `monthSalesMin` | number | 否 | 未指定 | 平均月销售额，当前站点货币，`>=0` |
| `monthSalesMax` | number | 否 | 未指定 | 平均月销售额，当前站点货币，`>=0` |
| `daySalesRateMin` | number | 否 | 未指定 | 日销售额增长率，百分比 |
| `daySalesRateMax` | number | 否 | 未指定 | 日销售额增长率，百分比 |
| `weekSalesRateMin` | number | 否 | 未指定 | 周销售额增长率，百分比 |
| `weekSalesRateMax` | number | 否 | 未指定 | 周销售额增长率，百分比 |
| `monthSalesRateMin` | number | 否 | 未指定 | 月销售额增长率，百分比 |
| `monthSalesRateMax` | number | 否 | 未指定 | 月销售额增长率，百分比 |

#### 价格、库存、店铺与评价

| 参数 | 类型 | 必填 | 默认值 | 约束 / 单位 |
|---|---|---|---|---|
| `quantityMin` | integer | 否 | 未指定 | 剩余库存，`>=0` |
| `quantityMax` | integer | 否 | 未指定 | 剩余库存，`>=0` |
| `mallSoldMin` | integer | 否 | 未指定 | 店铺历史累计总销量，`>=0` |
| `mallSoldMax` | integer | 否 | 未指定 | 店铺历史累计总销量，`>=0` |
| `priceMin` | number | 否 | 未指定 | 商品价格，当前站点货币，`>=0` |
| `priceMax` | number | 否 | 未指定 | 商品价格，当前站点货币，`>=0` |
| `supplyPriceMin` | number | 否 | 未指定 | 供货价，人民币，`>=0` |
| `supplyPriceMax` | number | 否 | 未指定 | 供货价，人民币，`>=0` |
| `goodsScoreMin` | number | 否 | 未指定 | 商品评分，`0..5` |
| `goodsScoreMax` | number | 否 | 未指定 | 商品评分，`0..5` |
| `reviewNumMin` | integer | 否 | 未指定 | 历史累计评论数，`>=0` |
| `reviewNumMax` | integer | 否 | 未指定 | 历史累计评论数，`>=0` |

#### 时间范围

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `onSaleTimeMin` | string | 否 | 未指定 | 商品上架时间范围，ISO-8601 date-time，最大 40 字符 |
| `onSaleTimeMax` | string | 否 | 未指定 | 商品上架时间范围，ISO-8601 date-time，最大 40 字符 |
| `mallOpenTimeMin` | string | 否 | 未指定 | 店铺开店时间范围，ISO-8601 date-time，最大 40 字符 |
| `mallOpenTimeMax` | string | 否 | 未指定 | 店铺开店时间范围，ISO-8601 date-time，最大 40 字符 |

所有成对的 `*Min` 都不得大于对应的 `*Max`。时间字段仍应始终使用 ISO-8601 date-time；服务端只在同组 Min/Max 同时提供时解析并比较时间，单独提供一个非法时间字符串时可能由上游拒绝。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 位置参数；不接受数组或其他顶层类型。业务参数见本接口请求表。 |
| --inline | CLI flag | 否 | 强制完整打印，仍落盘，不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过缓存读写并强制刷新；商品搜索/详情可能再次扣算力，站点/品类辅助接口仅强制刷新。 |

业务封装提供一层 24 小时本地成功响应缓存，成功空结果也可缓存；缓存键包含网关地址、接口路径、API Key 指纹及完整参数。缓存目录为 `<cwd>/linkfox/.cache/linkfox-geekbi-temu-product/`，文件名为 `linkfox-geekbi-temu-product-<缓存键哈希>.json`。HTTP/业务错误、连接失败、超时和无效 JSON 均不缓存。有效的成功响应 JSON 缓存可直接读取；公共调用器以 `--no-cache` 运行，避免重复缓存。
API Key 优先取 `LINKFOX_AGENT_API_KEY`，回退到 `LINKFOXAGENT_API_KEY`；网关使用 `LINKFOX_TOOL_GATEWAY`，未设置则使用公共规则中的默认地址。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空字符串。
完整响应及错误保存在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-geekbi-temu-product-<timestamp>.json`；会话优先取 `SESSION_ID`，未设置则自动生成，记录会话元数据。当前目录不可写时在请求前报错，不回退到用户目录或系统临时目录。摘要忽略 `columns`，保留最大业务列表前 3 条，`--inline` 始终全量打印。
这些地址是 LinkFox 工具网关路由；服务端调用 GeekBI 上游 GET API，客户端不得改用上游 `/api/v1/temu/...` 路径。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；已验证的成功值为 200，按公共规则判断 |
| errmsg | string | 网关消息；已验证成功消息为 ok |
| `items` | array | 当前页商品；每个业务字段都可能缺失或为 `null` |
| `columns` | array | 渲染列定义 |
| `total` | integer | 上游报告的匹配总数；服务只限制可访问窗口 `page * size <= 10000`，不会截断 `total`；上游缺失时回退为当前 `items` 长度 |
| `page` | integer | 当前页码 |
| `size` | integer | 每页数量 |
| `regionId` | integer | 本次请求使用的地区 ID |
| `title` | string | `Temu 数据查询` |
| `sourceType` | string | `temu` |
| `sourceTool` | string | `geekbi_temu` |
| `type` | string | `tableListWorkbenches` |

业务字段均可能缺失或为 `null`。下表标注业务字段的常见 JSON 类型，不保证每次返回均为该类型；实际返回类型优先，不强制转换、不把缺失值补为零。金额除供货价外按当前站点货币解释；供货价筛选明确使用人民币，供货价响应按实际返回口径展示，不自行换算。

#### items[] 商品对象

| 字段 | 类型 | 说明 |
|---|---|---|
| goodsId | string | 商品 ID，详情查询标识 |
| mallId | 未限定 | 店铺 ID |
| thumbnail | string | 商品缩略图 |
| goodsName | string | 商品名称 |
| goodsNameCn | string | 中文商品名 |
| goodsNameEn | string | 英文商品名 |
| brand | string | 品牌 |
| sku | 未限定 | 商品 SKU |
| catIds | integer[] | 所属品类 ID 数组 |
| catItems | object[] | 所属品类节点，结构见下表 |
| sold | integer | 历史累计总销量 |
| quantity | integer | 剩余库存 |
| daySold | number | 平均日销量 |
| weekSold | number | 平均周销量 |
| monthSold | number | 平均月销量 |
| mallSold | integer | 店铺累计总销量 |
| sales | number | 历史累计销售额，当前站点货币 |
| minPrice | number | 最低价格，当前站点货币 |
| maxPrice | number | 最高价格，当前站点货币 |
| daySales | number | 平均日销售额，当前站点货币 |
| weekSales | number | 平均周销售额，当前站点货币 |
| monthSales | number | 平均月销售额，当前站点货币 |
| daySoldRate | number | 日销量增长率，百分比 |
| weekSoldRate | number | 周销量增长率，百分比 |
| monthSoldRate | number | 月销量增长率，百分比 |
| daySalesRate | number | 日销售额增长率，百分比 |
| weekSalesRate | number | 周销售额增长率，百分比 |
| monthSalesRate | number | 月销售额增长率，百分比 |
| supplyPrice | number | 供货价 |
| minSupplyPrice | number | 最低供货价 |
| medianSupplyPrice | number | 供货价中位数 |
| maxSupplyPrice | number | 最高供货价 |
| goodsScore | number | 商品评分 |
| reviewNum | integer | 累计评论数 |
| hostingMode | integer | 1=全托管，2=半托管 |
| status | integer | 1=正常，2=缺货，3=下架 |
| isAd | 未限定 | 是否广告商品 |
| isCustom | 未限定 | 是否定制 |
| isPresale | 未限定 | 是否预售 |
| onSaleTime | string | 上架时间 |
| mallOpenTime | string | 店铺开店时间 |
| createTime | string | 创建时间 |
| updateTime | string | 更新时间 |
| similarNum | integer | 相似商品数量 |
| extraFields | 未限定 | 上游扩展字段，保留原结构 |

#### catItems[] 品类对象

| 字段 | 类型 | 说明 |
|---|---|---|
| catId | integer | 品类 ID |
| catName | string | 品类名称 |
| catLevel | integer | 品类层级 |
| parentCatId | integer | 父级品类 ID |
| isLeaf | boolean | 是否叶子节点 |
| extraFields | 未限定 | 上游扩展字段，保留原结构 |

#### columns[] 渲染列定义

每个列定义通常包含以下字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| field | string | 字段名 |
| title | string | 展示标题 |
| cellType | string | 单元格类型：number 或 text |
| sortable | boolean | 是否支持排序 |
| filterable | boolean | 是否支持筛选 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

无商品时保留成功空列表，不自动改变筛选条件。

| HTTP / 业务码 | 含义 | 处理建议 |
|---|---|---|
| HTTP 200 + errcode=30001 | 上游业务拒绝 | 按消息停止或修正参数，不作为成功数据解析。 |
| HTTP 200 + errcode=30005 | 上游授权失败 | 停止调用并联系工具管理员。 |
| 400 | 参数校验失败 | 按消息修正字段，不自动换关键词、翻页或站点连续重试。 |
| 403 | 无权限 | 停止并联系工具管理员，不按充值问题处理。 |
| 429 | 请求过于频繁 | 停止连续调用，后续调用仍遵守成本约束。 |
| 502 / 503 / 504 | 网关或上游异常 | 付费搜索/详情不自动重试；说明可能再次扣费并取得用户确认后，才可按原参数重试一次。 |

脚本原样保存并回显网关 JSON 错误，不以 Python 堆栈替代业务错误。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/geekbi/temu/goodsSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"regionId":211,"keyword":"dress","catIds":[984],"page":1,"size":20,"sort":"sold","order":"desc"}'
```

## 接口：商品详情（goodsDetail）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/goodsDetail`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 / 约束 | 说明 |
|---|---|---:|---|---|
| `goodsId` | string | 是 | 非空；最大 100 字符 | Temu 商品 ID，通常来自搜索 `items[].goodsId`；不能仅凭标题推测 |
| `regionId` | integer | 否 | `211`（美国）；`>=1` | Temu 地区 ID；只取非空有效的 `sites[].regionId`，不得用 `siteId` 替代；与搜索使用同一值 |

搜索后深查只复用非空 `items[].goodsId` 及同一 `regionId`，保持价格与市场口径。空 `goodsId` 或非法 `regionId` 会被拒绝。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 位置参数；不接受数组或其他顶层类型。业务参数见本接口请求表。 |
| --inline | CLI flag | 否 | 强制完整打印，仍落盘，不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过缓存读写并强制刷新；商品搜索/详情可能再次扣算力，站点/品类辅助接口仅强制刷新。 |

业务封装提供一层 24 小时本地成功响应缓存，成功空结果也可缓存；缓存键包含网关地址、接口路径、API Key 指纹及完整参数。缓存目录为 `<cwd>/linkfox/.cache/linkfox-geekbi-temu-product/`，文件名为 `linkfox-geekbi-temu-product-<缓存键哈希>.json`。HTTP/业务错误、连接失败、超时和无效 JSON 均不缓存。有效的成功响应 JSON 缓存可直接读取；公共调用器以 `--no-cache` 运行，避免重复缓存。
API Key 优先取 `LINKFOX_AGENT_API_KEY`，回退到 `LINKFOXAGENT_API_KEY`；网关使用 `LINKFOX_TOOL_GATEWAY`，未设置则使用公共规则中的默认地址。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空字符串。
完整响应及错误保存在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-geekbi-temu-product-<timestamp>.json`；会话优先取 `SESSION_ID`，未设置则自动生成，记录会话元数据。当前目录不可写时在请求前报错，不回退到用户目录或系统临时目录。摘要忽略 `columns`，保留最大业务列表前 3 条，`--inline` 始终全量打印。
这些地址是 LinkFox 工具网关路由；服务端调用 GeekBI 上游 GET API，客户端不得改用上游 `/api/v1/temu/...` 路径。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；已验证的成功值为 200，按公共规则判断 |
| errmsg | string | 网关消息；已验证成功消息为 ok |
| `goods` | object | 商品对象，字段与搜索 `items[]` 相同 |
| `history` | array | 最近 30 天历史记录；业务字段可缺失或为 `null` |
| `regionId` | integer | 本次请求使用的地区 ID |
| `title` | string | `Temu 商品详情` |
| `sourceType` | string | `temu` |
| `sourceTool` | string | `geekbi_temu` |
| `type` | string | `productWorkbenches` |
| `columns` | array | 商品详情渲染列 |

业务字段均可能缺失或为 `null`。下表标注业务字段的常见 JSON 类型，不保证每次返回均为该类型；实际返回类型优先，不强制转换、不把缺失值补为零。金额除供货价外按当前站点货币解释；供货价筛选明确使用人民币，供货价响应按实际返回口径展示，不自行换算。

#### goods 商品对象

| 字段 | 类型 | 说明 |
|---|---|---|
| goodsId | string | 商品 ID，详情查询标识 |
| mallId | 未限定 | 店铺 ID |
| thumbnail | string | 商品缩略图 |
| goodsName | string | 商品名称 |
| goodsNameCn | string | 中文商品名 |
| goodsNameEn | string | 英文商品名 |
| brand | string | 品牌 |
| sku | 未限定 | 商品 SKU |
| catIds | integer[] | 所属品类 ID 数组 |
| catItems | object[] | 所属品类节点，结构见下表 |
| sold | integer | 历史累计总销量 |
| quantity | integer | 剩余库存 |
| daySold | number | 平均日销量 |
| weekSold | number | 平均周销量 |
| monthSold | number | 平均月销量 |
| mallSold | integer | 店铺累计总销量 |
| sales | number | 历史累计销售额，当前站点货币 |
| minPrice | number | 最低价格，当前站点货币 |
| maxPrice | number | 最高价格，当前站点货币 |
| daySales | number | 平均日销售额，当前站点货币 |
| weekSales | number | 平均周销售额，当前站点货币 |
| monthSales | number | 平均月销售额，当前站点货币 |
| daySoldRate | number | 日销量增长率，百分比 |
| weekSoldRate | number | 周销量增长率，百分比 |
| monthSoldRate | number | 月销量增长率，百分比 |
| daySalesRate | number | 日销售额增长率，百分比 |
| weekSalesRate | number | 周销售额增长率，百分比 |
| monthSalesRate | number | 月销售额增长率，百分比 |
| supplyPrice | number | 供货价 |
| minSupplyPrice | number | 最低供货价 |
| medianSupplyPrice | number | 供货价中位数 |
| maxSupplyPrice | number | 最高供货价 |
| goodsScore | number | 商品评分 |
| reviewNum | integer | 累计评论数 |
| hostingMode | integer | 1=全托管，2=半托管 |
| status | integer | 1=正常，2=缺货，3=下架 |
| isAd | 未限定 | 是否广告商品 |
| isCustom | 未限定 | 是否定制 |
| isPresale | 未限定 | 是否预售 |
| onSaleTime | string | 上架时间 |
| mallOpenTime | string | 店铺开店时间 |
| createTime | string | 创建时间 |
| updateTime | string | 更新时间 |
| similarNum | integer | 相似商品数量 |
| extraFields | 未限定 | 上游扩展字段，保留原结构 |

#### catItems[] 品类对象

| 字段 | 类型 | 说明 |
|---|---|---|
| catId | integer | 品类 ID |
| catName | string | 品类名称 |
| catLevel | integer | 品类层级 |
| parentCatId | integer | 父级品类 ID |
| isLeaf | boolean | 是否叶子节点 |
| extraFields | 未限定 | 上游扩展字段，保留原结构 |

#### history[] 历史记录

最近 30 天内的每日记录，字段均可缺失或为 `null`，不保证返回 30 条。`createTime` 用作记录时间。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | 未限定 | 历史记录 ID |
| sold | integer | 历史累计总销量 |
| sales | number | 历史累计销售额，当前站点货币 |
| minPrice | number | 最低价格，当前站点货币 |
| maxPrice | number | 最高价格，当前站点货币 |
| quantity | integer | 剩余库存 |
| goodsScore | number | 商品评分 |
| reviewNum | integer | 累计评论数 |
| daySold | number | 平均日销量 |
| weekSold | number | 平均周销量 |
| monthSold | number | 平均月销量 |
| daySales | number | 平均日销售额，当前站点货币 |
| weekSales | number | 平均周销售额，当前站点货币 |
| monthSales | number | 平均月销售额，当前站点货币 |
| daySoldRate | number | 日销量增长率，百分比 |
| weekSoldRate | number | 周销量增长率，百分比 |
| monthSoldRate | number | 月销量增长率，百分比 |
| daySalesRate | number | 日销售额增长率，百分比 |
| weekSalesRate | number | 周销售额增长率，百分比 |
| monthSalesRate | number | 月销售额增长率，百分比 |
| createTime | string | 创建时间 |
| extraFields | 未限定 | 上游扩展字段，保留原结构 |

#### columns[] 渲染列定义

每个列定义通常包含以下字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| field | string | 字段名 |
| title | string | 展示标题 |
| cellType | string | 单元格类型：number 或 text |
| sortable | boolean | 是否支持排序 |
| filterable | boolean | 是否支持筛选 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

无有效商品编号时停止链式查询并说明原因；不把参数错误或上游拒绝当作空商品资料。

| HTTP / 业务码 | 含义 | 处理建议 |
|---|---|---|
| HTTP 200 + errcode=30001 | 上游业务拒绝 | 按消息停止或修正参数，不作为成功数据解析。 |
| HTTP 200 + errcode=30005 | 上游授权失败 | 停止调用并联系工具管理员。 |
| 400 | 参数校验失败 | 按消息修正字段，不自动换关键词、翻页或站点连续重试。 |
| 403 | 无权限 | 停止并联系工具管理员，不按充值问题处理。 |
| 429 | 请求过于频繁 | 停止连续调用，后续调用仍遵守成本约束。 |
| 502 / 503 / 504 | 网关或上游异常 | 付费搜索/详情不自动重试；说明可能再次扣费并取得用户确认后，才可按原参数重试一次。 |

脚本原样保存并回显网关 JSON 错误，不以 Python 堆栈替代业务错误。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/geekbi/temu/goodsDetail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"goodsId":"601099512345678","regionId":211}'
```

## 接口：站点列表（siteList）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/siteList`

### 请求参数

无业务参数，Body 传 `{}`。只将非空且为正整数的 `sites[].regionId` 用于商品搜索和详情；`sites[].siteId` 是上游内部 ID，不得代替 `regionId`。如果没有有效 `regionId`，应停止链式调用并告知用户。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| 无业务参数 | object | 否 | {} | 传空对象，不添加市场筛选参数 |


#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 位置参数；不接受数组或其他顶层类型。业务参数见本接口请求表。 |
| --inline | CLI flag | 否 | 强制完整打印，仍落盘，不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过缓存读写并强制刷新；商品搜索/详情可能再次扣算力，站点/品类辅助接口仅强制刷新。 |

业务封装提供一层 24 小时本地成功响应缓存，成功空结果也可缓存；缓存键包含网关地址、接口路径、API Key 指纹及完整参数。缓存目录为 `<cwd>/linkfox/.cache/linkfox-geekbi-temu-product/`，文件名为 `linkfox-geekbi-temu-product-<缓存键哈希>.json`。HTTP/业务错误、连接失败、超时和无效 JSON 均不缓存。有效的成功响应 JSON 缓存可直接读取；公共调用器以 `--no-cache` 运行，避免重复缓存。
API Key 优先取 `LINKFOX_AGENT_API_KEY`，回退到 `LINKFOXAGENT_API_KEY`；网关使用 `LINKFOX_TOOL_GATEWAY`，未设置则使用公共规则中的默认地址。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空字符串。
完整响应及错误保存在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-geekbi-temu-product-<timestamp>.json`；会话优先取 `SESSION_ID`，未设置则自动生成，记录会话元数据。当前目录不可写时在请求前报错，不回退到用户目录或系统临时目录。摘要忽略 `columns`，保留最大业务列表前 3 条，`--inline` 始终全量打印。
这些地址是 LinkFox 工具网关路由；服务端调用 GeekBI 上游 GET API，客户端不得改用上游 `/api/v1/temu/...` 路径。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；已验证的成功值为 200，按公共规则判断 |
| errmsg | string | 网关消息；已验证成功消息为 ok |
| `sites` | array | 支持的 Temu 站点 |
| `total` | integer | 站点数量 |
| title | string | Temu 站点列表 |
| sourceType | string | temu |
| sourceTool | string | geekbi_temu |
| type | string | tableListWorkbenches |
| `columns` | array | 渲染列定义 |

业务字段均可能缺失或为 `null`。下表标注业务字段的常见 JSON 类型，不保证每次返回均为该类型；实际返回类型优先，不强制转换、不把缺失值补为零。

#### sites[] 站点对象

| 字段 | 类型 | 说明 |
|---|---|---|
| siteId | integer | 上游内部 ID，不用于市场筛选 |
| regionId | integer | 市场 ID，用于商品搜索和详情 |
| name | string | 站点名称 |
| cnName | string | 中文名称 |
| lang | string | 语言 |
| currency | string | 币种 |
| extraFields | 未限定 | 上游扩展字段，保留原结构 |

#### columns[] 渲染列定义

每个列定义通常包含以下字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| field | string | 字段名 |
| title | string | 展示标题 |
| cellType | string | 单元格类型：number 或 text |
| sortable | boolean | 是否支持排序 |
| filterable | boolean | 是否支持筛选 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

没有有效市场编号时停止链式调用并说明。只请求站点元数据时不调用付费商品接口。

| HTTP / 业务码 | 含义 | 处理建议 |
|---|---|---|
| HTTP 200 + errcode=30001 | 上游业务拒绝 | 按消息停止或修正参数，不作为成功数据解析。 |
| HTTP 200 + errcode=30005 | 上游授权失败 | 停止调用并联系工具管理员。 |
| 400 | 参数校验失败 | 按消息修正字段，不自动换关键词、翻页或站点连续重试。 |
| 403 | 无权限 | 停止并联系工具管理员，不按充值问题处理。 |
| 429 | 请求过于频繁 | 停止连续调用，后续调用仍遵守成本约束。 |
| 502 / 503 / 504 | 网关或上游异常 | 本站点/品类辅助接口可按原参数重试 1–2 次，不自动改参数连续试探。 |

脚本原样保存并回显网关 JSON 错误，不以 Python 堆栈替代业务错误。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/geekbi/temu/siteList" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{}'
```

## 接口：品类列表（categoryList）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/categoryList`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 / 约束 | 说明 |
|---|---|---:|---|---|
| `parentCatId` | integer | 否 | 不传；`>=0` | 不传时返回一级品类；传某个 `categories[].catId` 时查询其下一级 |

品类搜索依赖：先用 `{}` 获取一级节点；需要下钻时只把非空且为非负整数的 `catId` 作为下一次请求的 `parentCatId`；需要筛选商品时只把有效 `catId` 放入商品搜索的 `catIds` 数组。如果没有有效 `catId`，应停止链式调用并告知用户。传 `0` 合法，但不应视为与省略 `parentCatId` 等价；查询一级品类时省略该参数。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 位置参数；不接受数组或其他顶层类型。业务参数见本接口请求表。 |
| --inline | CLI flag | 否 | 强制完整打印，仍落盘，不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过缓存读写并强制刷新；商品搜索/详情可能再次扣算力，站点/品类辅助接口仅强制刷新。 |

业务封装提供一层 24 小时本地成功响应缓存，成功空结果也可缓存；缓存键包含网关地址、接口路径、API Key 指纹及完整参数。缓存目录为 `<cwd>/linkfox/.cache/linkfox-geekbi-temu-product/`，文件名为 `linkfox-geekbi-temu-product-<缓存键哈希>.json`。HTTP/业务错误、连接失败、超时和无效 JSON 均不缓存。有效的成功响应 JSON 缓存可直接读取；公共调用器以 `--no-cache` 运行，避免重复缓存。
API Key 优先取 `LINKFOX_AGENT_API_KEY`，回退到 `LINKFOXAGENT_API_KEY`；网关使用 `LINKFOX_TOOL_GATEWAY`，未设置则使用公共规则中的默认地址。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空字符串。
完整响应及错误保存在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-geekbi-temu-product-<timestamp>.json`；会话优先取 `SESSION_ID`，未设置则自动生成，记录会话元数据。当前目录不可写时在请求前报错，不回退到用户目录或系统临时目录。摘要忽略 `columns`，保留最大业务列表前 3 条，`--inline` 始终全量打印。
这些地址是 LinkFox 工具网关路由；服务端调用 GeekBI 上游 GET API，客户端不得改用上游 `/api/v1/temu/...` 路径。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；已验证的成功值为 200，按公共规则判断 |
| errmsg | string | 网关消息；已验证成功消息为 ok |
| `categories` | array | 指定父级下的品类节点 |
| `total` | integer | 返回节点数量 |
| `parentCatId` | integer / omitted | 本次查询的父级 ID；真实一级查询省略该字段，传父级查询时返回对应 ID |
| title | string | Temu 品类列表 |
| sourceType | string | temu |
| sourceTool | string | geekbi_temu |
| type | string | tableListWorkbenches |
| `columns` | array | 渲染列定义 |

业务字段均可能缺失或为 `null`。下表标注业务字段的常见 JSON 类型，不保证每次返回均为该类型；实际返回类型优先，不强制转换、不把缺失值补为零。

#### categories[] 品类对象

| 字段 | 类型 | 说明 |
|---|---|---|
| catId | integer | 品类 ID |
| catName | string | 品类名称 |
| catLevel | integer | 品类层级 |
| parentCatId | integer | 父级品类 ID |
| isLeaf | boolean | 是否叶子节点 |
| extraFields | 未限定 | 上游扩展字段，保留原结构 |

#### columns[] 渲染列定义

每个列定义通常包含以下字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| field | string | 字段名 |
| title | string | 展示标题 |
| cellType | string | 单元格类型：number 或 text |
| sortable | boolean | 是否支持排序 |
| filterable | boolean | 是否支持筛选 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

没有有效品类编号时停止链式调用并说明；已有有效编号时不自动补查。只请求品类元数据时不调用付费商品接口。

| HTTP / 业务码 | 含义 | 处理建议 |
|---|---|---|
| HTTP 200 + errcode=30001 | 上游业务拒绝 | 按消息停止或修正参数，不作为成功数据解析。 |
| HTTP 200 + errcode=30005 | 上游授权失败 | 停止调用并联系工具管理员。 |
| 400 | 参数校验失败 | 按消息修正字段，不自动换关键词、翻页或站点连续重试。 |
| 403 | 无权限 | 停止并联系工具管理员，不按充值问题处理。 |
| 429 | 请求过于频繁 | 停止连续调用，后续调用仍遵守成本约束。 |
| 502 / 503 / 504 | 网关或上游异常 | 本站点/品类辅助接口可按原参数重试 1–2 次，不自动改参数连续试探。 |

脚本原样保存并回显网关 JSON 错误，不以 Python 堆栈替代业务错误。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/geekbi/temu/categoryList" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"parentCatId":100}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-geekbi-temu-product",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
