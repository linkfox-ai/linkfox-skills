# 卖家精灵类目市场调研 接口说明

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

## 接口：选市场列表

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sellersprite/market/research`

### 请求参数

参数与工具 `_sellersprite_market_research` 的 `inputSchema` 对齐。

**必填**：仅 `marketplace`；默认值不取消其必填要求。

**说明**：带「毛利率」等且 schema 写明「输入 N 表示 N%」的数值参数，取值范围一般为 **0–100**。**例外**：下列 **GoodsCrn / BrandCrn / SellerCrn / EbcProportion / FbaProportion / FbmProportion / AmazonSelfProportion** 的 `min*` / `max*` 入参须传 **小数**，见 [集中度与结构占比](#集中度与结构占比)。

#### 类目、地域与头部样本

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| marketplace | string | 是 | maxLength 1000，默认 `US` | 站点编码，见 [marketplace](#marketplace-可选值) |
| nodeIdPath | string | 否 | maxLength 1000 | 类目节点 ID 路径，如 `172282:281407` |
| departmentKeyword | string | 否 | maxLength 1000 | 类目关键字路径，如 `Electronics:Accessories & Supplies` |
| sellerLocation | string | 否 | maxLength 1000 | 卖家所属地，多个英文逗号分隔；可选值由卖家精灵表 1.3 定义，此处未列举具体枚举，不猜测取值 |
| newProduct | integer | 否 | 默认 `3` | 新品定义（月） |
| topNum | integer | 否 | 默认 `10` | 头部 Listing 数量 |

#### 时间与分页、排序

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| month | string | 否 | 正则 `^(nearly\|(19\|20)\d{2}(0[1-9]\|1[0-2]))$` | 筛选日期：`nearly` 为最近 30 天；`yyyyMM` 为具体月份，如 `202507`；最多支持当前月往前共 24 个月内的月份，历史范围受第三方限制 |
| page | integer | 否 | 默认 `1` | 页码，从 1 开始 |
| size | integer | 否 | 默认 `50`，最小 `1`，最大 `200` | 每页条数 |
| orderField | string | 否 | maxLength 1000 | 排序字段，见 [orderField](#orderfield-可选值) |
| orderDesc | boolean | 否 | 默认 `true` | `true` 降序，`false` 升序 |

#### 市场规模与主体数量

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minAvgRevenue | number | 否 | 最低月均销售额 |
| maxAvgRevenue | number | 否 | 最高月均销售额 |
| minAvgUnits | integer | 否 | 最低月均销量 |
| maxAvgUnits | integer | 否 | 最高月均销量 |
| minGoodsCount | integer | 否 | 最低商品数量 |
| maxGoodsCount | integer | 否 | 最高商品数量 |
| minSellers | integer | 否 | 最小卖家数量 |
| maxSellers | integer | 否 | 最大卖家数量 |
| minBrands | integer | 否 | 最小品牌数量 |
| maxBrands | integer | 否 | 最大品牌数量 |
| minAvgSellers | number | 否 | 最小平均卖家数量 |
| maxAvgSellers | number | 否 | 最大平均卖家数量 |

#### 集中度与结构占比

以下 **7 组**筛选入参（对应卖家精灵字段 **GoodsCrn、BrandCrn、SellerCrn、EbcProportion、FbaProportion、FbmProportion、AmazonSelfProportion**）须传 **小数**，约定为 **0～1** 之间的比例（例如 **`0.35` 表示 35%**）。**不要**按整数百分数传 **0～100**（例如勿用 `40` 表示 40%，除非已与实网行为核对）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minGoodsCrn | number | 否 | 最小商品集中度（小数 0～1） |
| maxGoodsCrn | number | 否 | 最大商品集中度（小数 0～1） |
| minSellerCrn | number | 否 | 最小卖家集中度（小数 0～1） |
| maxSellerCrn | number | 否 | 最大卖家集中度（小数 0～1） |
| minBrandCrn | number | 否 | 最小品牌集中度（小数 0～1） |
| maxBrandCrn | number | 否 | 最大品牌集中度（小数 0～1） |
| minAmazonSelfProportion | number | 否 | 最小 Amazon 自营占比（小数 0～1） |
| maxAmazonSelfProportion | number | 否 | 最大 Amazon 自营占比（小数 0～1） |
| minFbaProportion | number | 否 | 最小 FBA 占比（小数 0～1） |
| maxFbaProportion | number | 否 | 最大 FBA 占比（小数 0～1） |
| minFbmProportion | number | 否 | 最小 FBM 占比（小数 0～1） |
| maxFbmProportion | number | 否 | 最大 FBM 占比（小数 0～1） |
| minEbcProportion | number | 否 | 最小 A+ 数量占比（小数 0～1） |
| maxEbcProportion | number | 否 | 最大 A+ 数量占比（小数 0～1） |

#### 新品数量占比（入参刻度以 schema 为准）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minNewProportion | number | 否 | 最小新品数量占比（与其它占比字段刻度可能不同，以工具 schema / 实网为准） |
| maxNewProportion | number | 否 | 最大新品数量占比（与其它占比字段刻度可能不同，以工具 schema / 实网为准） |

#### 价格、评分、毛利、BSR（市场平均）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minAvgPrice | number | 否 | 最低平均价格 |
| maxAvgPrice | number | 否 | 最高平均价格 |
| minAvgRating | number | 否 | 最低平均评分值 |
| maxAvgRating | number | 否 | 最高平均评分值 |
| minAvgRatings | integer | 否 | 最低平均评分数 |
| maxAvgRatings | integer | 否 | 最高平均评分数 |
| minAvgProfit | number | 否 | 最低平均毛利率（输入 N 表示 N%，0–100） |
| maxAvgProfit | number | 否 | 最高平均毛利率（输入 N 表示 N%，0–100） |
| minAvgBsr | integer | 否 | 最低平均 BSR 排名 |
| maxAvgBsr | integer | 否 | 最高平均 BSR 排名 |

#### 新品维度

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minNewCount | integer | 否 | 最小新品数量 |
| maxNewCount | integer | 否 | 最大新品数量 |
| minNewAvgPrice | number | 否 | 最小新品平均价格 |
| maxNewAvgPrice | number | 否 | 最大新品平均价格 |
| minNewAvgRating | number | 否 | 最小新品平均星级 |
| maxNewAvgRating | number | 否 | 最大新品平均星级 |
| minNewAvgRatings | integer | 否 | 最小新品平均评分数 |
| maxNewAvgRatings | integer | 否 | 最大新品平均评分数 |
| minNewAvgUnits | number | 否 | 最低新品月均销量 |
| maxNewAvgUnits | number | 否 | 最高新品月均销量 |
| minNewAvgRevenue | number | 否 | 最低新品月均销售额 |
| maxNewAvgRevenue | number | 否 | 最高新品月均销售额 |

#### 头部 Listing 指标

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minTopAvgUnits | integer | 否 | 最低头部月均销量 |
| maxTopAvgUnits | integer | 否 | 最高头部月均销量 |
| minTopAvgRevenue | number | 否 | 最低头部月均销售额 |
| maxTopAvgRevenue | number | 否 | 最高头部月均销售额 |
| minTopAvgBsr | integer | 否 | 最低头部平均 BSR |
| maxTopAvgBsr | integer | 否 | 最高头部平均 BSR |

#### 重量与体积

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minWeight | number | 否 | 最低重量 |
| maxWeight | number | 否 | 最高重量 |
| minVolume | number | 否 | 最低体积 |
| maxVolume | number | 否 | 最高体积 |

#### marketplace 可选值

| 取值 | 含义 |
|------|------|
| US | 美国站 USD($) |
| JP | 日本站 JPY(￥) |
| UK | 英国站 GBP(£) |
| DE | 德国站 EUR(€) |
| FR | 法国站 EUR(€) |
| IT | 意大利站 EUR(€) |
| ES | 西班牙站 EUR(€) |
| CA | 加拿大站 C$($) |
| IN | 印度站 INR(₹) |

#### orderField 可选值

与工具 schema「表 1.6」一致。

| 取值 | 含义 |
|------|------|
| total_units | 月销量 |
| total_amount | 月销售额 |
| bsr_rank | BSR 排名 |
| price | 价格 |
| rating | 评分 |
| reviews | 评分数 |
| profit | 毛利率 |
| reviews_rate | 留评率 |
| available_date | 上架时间 |
| questions | Q&A |
| total_units_growth | 月销量增长率 |
| total_amount_growth | 月销售额增长率 |
| reviews_increasement | 月新增评分数 |
| bsr_rank_cv | 近 7 天 BSR 增长数 |
| bsr_rank_cr | 近 7 天 BSR 增长率 |
| amz_unit | 子体销量 |

#### 脚本选项与运行约定

| 参数 / 约定 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 第一个位置参数，字段按上表原样传递，不自动补充或改写筛选条件。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次缓存读写；默认使用 24 小时本地缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 优先使用此基础地址，未设置时使用公共规则中的默认地址，移除末尾斜线后拼接接口路径。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是，二选一 | 优先使用前者；两者都为空时报错并走账号引导。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 原样作为请求头传递，未设置时为空字符串；SESSION_ID 同时用于会话目录聚合。 |

缓存路径为 `<cwd>/linkfox/.cache/linkfox-sellersprite-market-research/`，文件名由技能标识及参数 JSON 按键排序后 SHA-256 的前 16 位组成。同参数命中有效缓存时直接复用，响应增加 `_cache.hit=true`。缓存对象包括错误或空结果；脚本不会自动重试或刷新。业务脚本仅调用公共调用器的一层缓存。

完整数据保存到 SKILL.md 所述的当前工作目录，保持会话 `_meta.json` 与 `index.jsonl` 登记。当前目录不可写时在请求前报错，不回退到家目录、ACPX_WORKSPACES 或临时目录。读取具体字段时按需提取保存的 JSON。

### 响应结构

接口 `outputSchema` 字段如下；不补造缺失指标。集中度、结构占比等入参与响应里标为 `(%)` 的字段可能使用不同刻度，按各自定义解释；新品占比不能套用七组比例参数的刻度。

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 可选网关状态码；按公共规则判断，不要求成功响应一定出现此字段。 |
| errmsg | string | 可选网关消息；错误时据此解释原因。 |
| total | integer | 总条数 |
| marketplace | string | 站点编码 |
| data | array | 类目市场列表（对应第三方 `data.items`） |
| columns | array | 渲染的列 |
| costToken | integer | 消耗 token |
| type | string | 渲染的样式 |

#### data[] 元素（单条类目市场）

| 字段 | 类型 | 说明 |
|------|------|------|
| nodeId | string | 节点 ID |
| nodeIdPath | string | 节点 ID 路径 |
| nodeLabelName | string | 节点名称 |
| nodeLabelPath | string | 节点名称路径 |
| nodeLabelLocale | string | 节点名称翻译 |
| nodeLabelPathLocale | string | 节点名称路径翻译 |
| marketplace | string | 市场标志 |
| currency | string | 该市场的货币类型 |
| ranking | integer | 排名 |
| totalProducts | integer | 商品总数 |
| topProducts | integer | 样本数量 |
| sellers | integer | 卖家数量 |
| brands | integer | 品牌数量 |
| avgSellers | number | 平均卖家数 |
| avgUnits | integer | 月均销量 |
| totalUnits | integer | 月总销量 |
| avgRevenue | number | 月均销售额 |
| totalRevenue | number | 月总销售额 |
| avgPrice | number | 平均价格 |
| avgRating | number | 平均评分值 |
| avgRatings | integer | 平均评分数 |
| avgBsr | integer | 平均 BSR |
| avgProfit | number | 平均利润率(%) |
| fbaProportion | number | FBA 占比(%) |
| fbmProportion | number | FBM 占比(%) |
| amazonSelfProportion | number | Amazon 自营占比(%) |
| ebcProportion | number | A+ 商品占比(%) |
| returnRatio | number | 退货率(%) |
| avgReturnRatio | number | 退货率类目平均值(%) |
| searchToPurchaseRatio | number | 搜索购买比(千分比) |
| sellerNation | string | 最多卖家归属地 code |
| sellerNationLabel | string | 最多卖家归属地 label |
| sellerProportion | number | 最多卖家归属地占比(%) |
| avgWeight | number | 平均重量(pound) |
| baseAvgWeight | number | 平均重量(g) |
| avgVolume | number | 平均体积(in³) |
| baseAvgVolume | number | 平均体积(cm³) |
| top10Images | array | 前 10 商品图片，元素见下表 |

#### top10Images[] 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| image | string | 图片链接 |
| asin | string | ASIN |

#### 本地错误输出

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | 业务脚本在 HTTP 错误、连接失败、响应无法解析为 JSON 或不是 JSON 对象时返回的错误说明；HTTP 错误不覆盖响应已有的 `error`，不得当作市场结果。 |
| details | string | 响应无法解析为 JSON 或不是 JSON 对象时保留的原始文本。 |
| _http_status | integer / null | 业务脚本保留的实际 HTTP 状态；连接失败时为 `null`。随完整响应保存和缓存，不是网关字段；缓存命中时表示该缓存生成时的状态，不代表当前服务状态。 |
| _cache.hit | boolean | 仅本地缓存命中时由脚本追加，不是接口业务字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 脚本结果按 `_http_status` 与响应 `errcode` 共同判断；HTTP 非 `200`–`299` 时，即使 JSON 内 `errcode=200` 或有空 `data`，也不能当作正常市场结果。`401` / `402` 按账号或算力引导处理，其他 HTTP 错误保留原始原因；大响应摘要未展开状态时，从保存的 JSON 读取。
- 连接失败或本地 `error` 表示调用未完成或响应无法解析，不按无候选解释。旧缓存若缺少 `_http_status`，其历史 HTTP 状态无法推断，不据此宣称调用正常；不要自动清缓存或重发收费请求，需要重新核实时遵守成本约束。
- 正常响应中的空市场列表按当前条件下无候选解释；调整阈值或翻页前遵守成本约束，不自动连续试探。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sellersprite/market/research" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"marketplace":"US","month":"nearly","minAvgRevenue":10000,"maxGoodsCrn":0.4,"orderField":"total_amount","orderDesc":true,"page":1,"size":50}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sellersprite-market-research",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```