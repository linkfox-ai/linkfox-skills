# 店雷达1688商品热销榜单 接口说明

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

## 接口：1688商品热销榜单

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/dld/productBillboard`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyWord | string | 否 | 商品搜索关键字（搜索关键词必须是中文，如果不是请先翻译），最大长度50 |
| date | string | 否 | 查询时间，格式 `YYYY-MM-DD`。周榜：传入该周的周日日期，如 `2025-06-15`（最长近90天）；月榜：传入该月第一天，如 `2025-06-01`（最长近一年，即12个月） |
| pageType | integer | 否 | 榜单类型：`2` = 周榜，`3` = 月榜。默认 `3` |
| pageIndex | integer | 否 | 页码（从1开始），默认 `1` |
| pageSize | integer | 否 | 每页返回数量（10-100），默认 `20` |
| sortField | string | 否 | 排序字段，默认 `orderCount`。可选值：`orderCount`（销售笔数）、`saleCount`（销售件数）、`saleVolume`（预估销售额）、`offerCreateTime`（上架时间）、`price`（批发价）、`consignPrice`（代发价） |
| sortType | string | 否 | 排序类型：`desc`（降序）、`asc`（升序），默认 `desc` |
| searchType | integer | 否 | 商品关键词搜索类型：`1` = 模糊匹配，`3` = 精准匹配。默认 `1` |
| offerType | integer | 否 | 商品标识：`0` = 不限制，`2` = 新品，`3` = 1688严选，`4` = 跨境，`5` = 支持定制，`6` = 镇店之宝。默认 `0` |
| companyType | integer | 否 | 公司类型：`0` = 不限，`1` = 店铺，`2` = 工厂 |
| shiLiType | string | 否 | 卖家会员类型（多选），多个使用","号隔开。可选值：`superFactory`（超级工厂）、`Power`（实力商家）、`TrustPass`（仅诚信通会员） |
| beginTpYear | integer | 否 | 开始诚信通年限 |
| endTpYear | integer | 否 | 结束诚信通年限 |
| beginPrice | number | 否 | 批发价（起始） |
| endPrice | number | 否 | 批发价（结束） |
| beginConsignPrice | number | 否 | 代发价（起始） |
| endConsignPrice | number | 否 | 代发价（结束） |
| beginOrderCount | integer | 否 | 销售笔数（起始） |
| endOrderCount | integer | 否 | 销售笔数（结束） |
| beginSaleCount | integer | 否 | 销售件数（起始） |
| endSaleCount | integer | 否 | 销售件数（结束） |
| beginSaleVolume | number | 否 | 销售额（起始） |
| endSaleVolume | number | 否 | 销售额（结束） |
| beginStartQuantity | integer | 否 | 起始起批量 |
| endStartQuantity | integer | 否 | 结束起批量 |
| beginOfferCreateTime | string | 否 | 上架时间（起始），格式：`YYYY-MM-DD` |
| endOfferCreateTime | string | 否 | 上架时间（结束），格式：`YYYY-MM-DD` |
| sendTime | string | 否 | 发货时间（多选），多个使用","号隔开。可选值：`24`（24小时）、`48`（48小时）、`72`（72小时） |
| proxyRights | string | 否 | 代发权益（多选），多个使用","号隔开。可选值：`4360897`（一件代发包邮）、`449154`（先采后付） |
| shopService | string | 否 | 卖家服务（多选），多个使用","号隔开。可选值：`4057409`（安心购）、`888777`（深度认证报告） |
| buyerProtections | string | 否 | 权益保障（多选），多个用","隔开。可选值：`商品包邮`、`7天包退货`、`支持运费险` |
| faceToFaceSupport | string | 否 | 面单支持（多选），多个使用","号隔开。可选值：`441218`（淘宝）、`386434`（抖音）、`422914`（拼多多）、`422978`（小红书）、`386370`（快手） |
| productIds | string | 否 | 商品ID，以顿号 `、` 隔开搜索多个，最多20个；不能与服务筛选使用的英文逗号混淆 |
| goodsUrl | string | 否 | 商品链接地址 |

#### 脚本选项与缓存

| 选项或约定 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 命令行首个位置参数，内容为上表所列POST请求体。 |
| --inline | CLI flag | 否 | 强制打印完整响应，同时仍保存文件。 |
| --no-cache | CLI flag | 否 | 绕过本地缓存的读取和写入，重新请求并保存本次响应。 |
| 响应缓存 | 本地文件 | 否 | 默认启用24小时缓存，目录为 `<cwd>/linkfox/.cache/linkfox-dld-product-billboard/`；键为参数排序JSON的SHA-256前16位，同参数缓存可继续复用。缓存由公共调用器统一管理。 |
| 完整响应 | 本地文件 | 是 | 按SKILL.md输出策略保存；固定当前工作目录，不回退到家目录或临时目录。请求前检查实际会话元数据与 data 目录，路径被文件占用或不可写时直接报错；不要在 `/tmp` 执行。 |

`LINKFOX_TOOL_GATEWAY` 可覆盖网关地址，缺省回退正式地址，移除末尾斜杠。密钥优先取 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头，并记录会话元数据和索引文件。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 业务状态码，按公共响应码基本规则判断；认证失败示例值为401。 |
| errmsg | string | 响应消息或错误原因；认证失败示例值为 `authorized error`。 |
| errorCode | integer | 业务状态字段，200表示成功，其他值表示业务异常；返回该字段时结合下方业务规则解释。错误响应也可使用 `errcode`。 |
| total | integer | 记录数 |
| type | string | 渲染的样式 |
| columns | array | 渲染的列 |
| products | array | 商品列表（见下方商品对象） |

#### products[*] 商品对象

| 字段 | 类型 | 说明 |
|------|------|------|
| offerId | string | 商品id |
| asin | string | 商品编号 |
| title | string | 商品标题 |
| price | number | 批发价 |
| consignPrice | number | 代发价 |
| currency | string | 币种 |
| unit | string | 单位 |
| quantityBegin | integer | 起批量 |
| quantityPrices | string | 价格区间 |
| salesOrderCount | integer | 销售笔数（按统计周期返回对应的值） |
| salesQuantity | integer | 销售件数（按统计周期返回对应的值） |
| estimatedSalesAmount | integer | 预估销售额（按统计周期返回对应的值） |
| dataType | string | 数据类型：`weeklyData` = 周数据，`monthlyData` = 月数据 |
| availableDate | string | 商品上架时间，格式为 `yyyy-MM-dd HH:mm:ss` |
| deliveryTime | string | 发货时间 |
| levelName | string | 类目层级名称 |
| company | string | 店铺名称 |
| shopId | string | 店铺id |
| shopUrl | string | 店铺链接地址 |
| asinUrl | string | 商品链接地址 |
| imageUrl | string | 图片地址 |
| sourceType | string | 来源平台（1688） |
| sourceTool | string | 来源工具 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先按公共基础规则判断 HTTP 状态与 `errcode`；错误响应可使用 `errcode`，如 `{"errcode":401,"errmsg":"authorized error"}`。
- 若返回 `errorCode`，`200` 表示该业务字段成功，其他值表示业务异常，结合 `errmsg` 说明原因；不能因 `errcode` 缺失便忽略明确的 `errorCode` 失败，也不能用 `errorCode=200` 覆盖 HTTP 或 `errcode` 已指示的失败。保留实际返回字段供核对。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/dld/productBillboard" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "Content-Type: application/json" \
  -d '{
    "keyWord": "手机壳",
    "pageType": 3,
    "date": "2026-03-01",
    "sortField": "orderCount",
    "sortType": "desc",
    "pageSize": 20,
    "pageIndex": 1
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-dld-product-billboard",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```