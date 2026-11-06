# 店雷达 1688 商品搜索 接口说明

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

## 接口：1688 商品搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/dld/productSearch`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| keyWord | string | 否 | - | 搜索关键词（必须为中文，最多50字符） |
| goodsUrl | string | 否 | - | 商品链接地址（与keyWord二选一） |
| productIds | string | 否 | - | 商品ID，多个逗号隔开，最多20个 |
| cycle | string | 否 | - | 统计周期：`7`（近7天）或 `30`（近30天） |
| searchType | integer | 否 | 1 | 搜索类型：1-模糊匹配，3-精准匹配 |
| sortField | string | 否 | orderCount30d | 排序字段：orderCount7d, saleCount7d, saleVolume7d, orderCount30d, saleCount30d, saleVolume30d, offerCreateTime, price, consignPrice |
| sortType | string | 否 | desc | 排序类型：desc（降序）、asc（升序） |
| pageIndex | integer | 否 | 1 | 页码（从1开始） |
| pageSize | integer | 否 | 20 | 每页数量（10-100） |
| beginPrice | number | 否 | - | 批发价（起始） |
| endPrice | number | 否 | - | 批发价（结束） |
| beginConsignPrice | number | 否 | - | 代发价（起始） |
| endConsignPrice | number | 否 | - | 代发价（结束） |
| beginOrderCount | integer | 否 | - | 销售笔数（起始） |
| endOrderCount | integer | 否 | - | 销售笔数（结束） |
| beginSaleCount | integer | 否 | - | 销售件数（起始） |
| endSaleCount | integer | 否 | - | 销售件数（结束） |
| beginSaleVolume | number | 否 | - | 销售额（起始） |
| endSaleVolume | number | 否 | - | 销售额（结束） |
| beginStartQuantity | integer | 否 | - | 起购数量（起始） |
| endStartQuantity | integer | 否 | - | 起购数量（结束） |
| beginTpYear | integer | 否 | - | 诚信通年限（起始） |
| endTpYear | integer | 否 | - | 诚信通年限（结束） |
| beginOfferCreateTime | string | 否 | - | 上架时间起始（格式：YYYY-MM-DD） |
| endOfferCreateTime | string | 否 | - | 上架时间结束（格式：YYYY-MM-DD） |
| companyType | integer | 否 | 0 | 公司类型：0-不限，1-店铺，2-工厂 |
| offerType | integer | 否 | 0 | 商品标识：0-不限，2-新品，3-1688严选，4-跨境，5-支持定制，6-镇店之宝 |
| shiLiType | string | 否 | - | 卖家类型（多选逗号隔开）：superFactory（超级工厂）、Power（实力商家）、TrustPass（诚信通） |
| sendTime | string | 否 | - | 发货时间（多选逗号隔开）：24、48、72 |
| faceToFaceSupport | string | 否 | - | 面单支持（多选逗号隔开）：441218（淘宝）、386434（抖音）、422914（拼多多）、422978（小红书）、386370（快手） |
| proxyRights | string | 否 | - | 代发权益（多选逗号隔开）：4360897（一件代发包邮）、449154（先采后付） |
| shopService | string | 否 | - | 卖家服务（多选逗号隔开）：4057409（安心购）、888777（深度认证报告） |
| buyerProtections | string | 否 | - | 权益保障（多选逗号隔开）：商品包邮、7天包退货、支持运费险 |

#### 参数组合与口径

- 关键词必须为中文；英文商品词先翻译，再传入 `keyWord`，最多 50 个字符。`goodsUrl` 与 `keyWord` 二选一；也支持 `productIds` 按编号查询，不额外推定其未说明的互斥关系。
- `cycle` 选择近 7 天或近 30 天；排序中的 `orderCount*` 表示订单数，`saleCount*` 表示销售件数，`saleVolume*` 表示预估销售额。按周期选择对应的 7 天或 30 天排序字段。
- 批发价、代发价和销售额范围均以人民币（CNY）计价；发货时间值表示小时。多选字符串遵循各参数表中的逗号分隔约定及大小写。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| JSON 参数 | JSON | 是 | - | 首个位置参数，按上表原样传入接口；不自动改写筛选、翻页或填充周期。 |
| --inline | CLI flag | 否 | 关闭 | 保存完整响应后强制全量打印。 |
| --no-cache | CLI flag | 否 | 关闭 | 关闭本次响应缓存的读取和写入；不会删除既有缓存。 |

- 脚本默认开启 24 小时缓存，由公共调用器统一维护，不叠加业务缓存。缓存目录为 `<cwd>/linkfox/.cache/linkfox-dld-product-search/`，文件名为 `linkfox-dld-product-search-<key>.json`；`key` 是参数按键排序、保留中文的 JSON 经 SHA-256 计算后取前 16 位。已有缓存符合该命名规则且有效时可直接命中。
- 缓存以参数识别，不按密钥或网关分区；切换账号或网关后需要实时结果时使用 `--no-cache`。错误和空结果也会缓存；需要再次查询时须遵守技能的成本约束。
- 缓存命中时添加 `_cache.hit=true` 并仍保存完整响应。过期、无效或不可读取的缓存按未命中处理。
- 支持 `LINKFOX_TOOL_GATEWAY` 自定义网关及两种密钥变量，优先 `LINKFOX_AGENT_API_KEY`，其次 `LINKFOXAGENT_API_KEY`；传递 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- 业务脚本在请求前检查当前工作目录及会话数据目录可写，将本次响应固定保存在 `<cwd>/linkfox/`，记录会话元数据和索引；当前目录不可写或位于 `/tmp` 下时直接报错，不发请求。不使用 `ACPX_WORKSPACES`、家目录或临时目录回退。

#### 常用检索组合

| 场景 | JSON 参数示例 |
|------|------|
| 瑜伽垫近 30 天销量排序 | `{"keyWord":"瑜伽垫","cycle":"30","sortField":"saleCount30d","sortType":"desc","pageSize":20}` |
| 蓝牙耳机工厂，批发价 10–50 元 | `{"keyWord":"蓝牙耳机","companyType":2,"beginPrice":10,"endPrice":50,"cycle":"30","sortField":"orderCount30d"}` |
| 手机壳跨境商品，代发包邮，近 7 天销售额排序 | `{"keyWord":"手机壳","offerType":4,"proxyRights":"4360897","cycle":"7","sortField":"saleVolume7d"}` |
| 夏季连衣裙新品，按上架时间倒序 | `{"keyWord":"夏季连衣裙","offerType":2,"sortField":"offerCreateTime","sortType":"desc","pageSize":50}` |
| 数据线超级工厂，近 30 天销量至少 1000 件 | `{"keyWord":"数据线","shiLiType":"superFactory","beginSaleCount":1000,"cycle":"30","sortField":"saleCount30d"}` |
| 按商品链接查看近 30 天数据 | `{"goodsUrl":"https://detail.1688.com/offer/805578065498.html","cycle":"30"}` |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总记录数 |
| type | string | 渲染样式 |
| columns | array | 渲染列定义 |
| products | array | 商品列表（详见下方字段） |

#### products 数组元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| offerId | string | 商品ID |
| asin | string | 商品编号 |
| title | string | 商品标题 |
| asinUrl | string | 商品链接地址 |
| imageUrl | string | 商品图片地址 |
| price | number | 批发价 |
| consignPrice | number | 代发价 |
| quantityPrices | string | 价格区间 |
| quantityBegin | integer | 起批量 |
| unit | string | 单位 |
| currency | string | 币种 |
| salesOrderCount | integer | 销售笔数（按统计周期） |
| salesQuantity | integer | 销售件数（按统计周期） |
| estimatedSalesAmount | integer | 预估销售额（按统计周期） |
| deliveryTime | string | 发货时间 |
| availableDate | string | 商品上架时间 |
| levelName | string | 类目层级名称 |
| company | string | 店铺名称 |
| shopId | string | 店铺ID |
| shopUrl | string | 店铺链接地址 |
| dataType | string | 数据类型：weeklyData（周数据）、monthlyData（月数据） |
| sourceType | string | 来源平台（1688） |
| sourceTool | string | 来源工具 |

#### 状态及脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态，按公共规则判断；认证失败示例为 401。 |
| errmsg | string | 业务消息，如 `authorized error`；其他错误依据实际内容解释。 |
| errorCode | 以实际返回为准 | 业务状态字段，200 表示成功，其他值表示业务异常，401 表示未授权；错误响应也可能使用 `errcode`。按下方业务规则检查实际返回的状态字段。 |
| _cache | object | 仅脚本使用本地缓存时附加的缓存标记。 |
| _cache.hit | boolean | 为 true 表示本次读取了有效缓存。 |
| error | string | 公共调用器在连接失败或非 JSON HTTP 错误时生成的错误说明，不是商品业务字段。 |
| details | string | 非 JSON HTTP 错误响应的原始正文（有正文时保留）。 |

`quantityPrices` 为 string 类型，不自行改成数组。批发价对应起批数量下的单位价格，代发价对应单件代发价格；`currency` 为 CNY。`columns` 的内部字段以实际响应为准，不补造结构。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode` 按公共响应码基本规则判断。当实际响应提供 `errorCode` 时，还需检查该字段：200 表示成功，其他值表示业务异常；不得仅因 `errcode` 缺失而忽略 `errorCode` 报错。认证或算力异常按 `references/onboarding.md` 处理，不推定额外专用错误码。业务异常保留实际 `errmsg`，并据消息建议核对关键词或筛选条件；不得自动改参连续试探。
- `total` 表示总记录数，不是本页记录数。空列表不等于认证失败，也不能在没有数据时补造商品或销量。

### 响应示例

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/dld/productSearch \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyWord": "瑜伽垫", "cycle": "30", "sortField": "saleCount30d", "sortType": "desc", "pageSize": 20}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-dld-product-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
