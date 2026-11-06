# Sorftime 亚马逊产品搜索 接口说明

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

## 接口：亚马逊产品搜索（productQuery）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/amazon/productQuery`

### 请求参数

#### POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 亚马逊站点代码：us、gb、de、fr、in、ca、jp、es、it、mx、ae、au、br、sa |
| queryMode | integer | 否 | 查询方式。`1`：单条件查询（默认）；`2`：多条件组合查询（且关系） |
| queryType | integer | 否 | 查询类型（1-16），仅当 queryMode=1 时生效。详见下方“查询类型与条件格式” |
| queryValue | string | 否 | 查询条件值，格式根据 queryMode 和 queryType 不同而变化。详见下方“查询类型与条件格式”及“多条件组合” |
| page | integer | 否 | 分页页码，默认1。每页最多100个产品 |
| queryMonth | string | 否 | 回看历史月份，格式 `yyyy-MM`。不指定时查实时数据 |

#### 站点与默认约定

| 项目 | 约定 |
|------|------|
| 站点 | `us` 美国、`gb` 英国、`de` 德国、`fr` 法国、`in` 印度、`ca` 加拿大、`jp` 日本、`es` 西班牙、`it` 意大利、`mx` 墨西哥、`ae` 阿联酋、`au` 澳大利亚、`br` 巴西、`sa` 沙特阿拉伯。 |
| 默认站点 | 用户未指定时显式传入 `marketplace="us"`；脚本不自行补参数。 |
| 大小写 | 站点代码使用小写；英国为 `gb`，不是 `uk`。 |

#### 查询类型与条件格式

以下为 `queryMode=1` 时的 `queryType` 与 `queryValue` 约定；组合查询中同样用于 `QueryType` 与 `Content`。

| queryType | 名称 | queryValue 格式 | 示例与说明 |
|-----------|------|-----------------|------------|
| 1 | ASIN 相似商品 | ASIN | `B0CVM8TXHP`；查相似商品，不是该 ASIN 自身详情。 |
| 2 | 类目 | NodeId | `3743561`。 |
| 3 | 品牌 | 品牌名称 | `Anker`。 |
| 4 | 卖家名称 | 店铺名称 | `AnkerDirect`。 |
| 5 | 卖家 ID | SellerId | `A294P4X9EWVXLJ`。 |
| 6 | ABA 关键词 | ABA 关键词 | `Power Bank`；当前仅支持 ABA 关键词，不支持任意搜索词。 |
| 7 | 标题或属性匹配 | 关键词 | `10,000mAh 30W` 或 `wireless charger`。 |
| 8 | 价格范围 | `min,max`，以当地货币最小单位计 | `1,1000` 表示美元 0.01–10；美元 19.99 应传 `1999`。 |
| 9 | 月销量范围 | `min,max` | `100,1000`。 |
| 10 | 季节性商品 | 旺季月份列表 | `1,2,3` 表示一月至三月；第四季度为 `10,11,12`。 |
| 11 | 上架日期范围 | `start,end`，日期为 `yyyy-MM-dd` | `2024-06-01,2024-12-01`。 |
| 12 | 评分范围 | `min,max` | `3,5`。 |
| 13 | 评论数量范围 | `min,max` | `10,500`。 |
| 14 | 排名范围 | `bsr_min,bsr_max;sub_min,sub_max` | `500,5000;1,100`，分号分隔大类与小类排名。 |
| 15 | 配送方式 | `FBA` / `FBM` | `FBA` 或 `FBA,FBM`。 |
| 16 | 变体数范围 | `min,max` | `1,50`。 |

范围可省略一端：`,1000` 表示不高于 1000，`100,` 表示不低于 100。日期范围同样可使用 `2024-06-01,`。查询类型与条件格式必须匹配，格式不匹配会报错。

#### 多条件组合

`queryMode=2` 时为 AND 关系，顶层 `queryType` 无效。所有条件放在 `queryValue` 中；该字段类型仍为 **string**，内容是 JSON 数组的序列化文本，不能直接把数组作为顶层字段值。内层字段的大小写必须保持 `QueryType`、`Content`。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| queryValue 中的数组元素 | object | 是 | 每项描述一个筛选条件。 |
| QueryType | integer | 是 | 查询类型，取值 1–16，对应上表。 |
| Content | string | 是 | 条件值，遵循对应查询类型的格式。 |

组合内容示例：`[{"QueryType":1,"Content":"B0CVM8TXHP"},{"QueryType":8,"Content":"100,500"}]`。完整请求的字符串转义见下方唯一 curl 示例。

#### 分页与历史回看限制

| 项目 | 约定 |
|------|------|
| 分页 | `page` 默认 1，每页最多 100 个产品，最多 200 页；仅在用户明确要求时调整页码。 |
| 历史月份 | `queryMonth` 格式 `yyyy-MM`，从 `2024-01` 至当前月份；不传查实时数据。 |
| 完整历史回看 | `us`、`gb`、`de` 支持完整“不限量”回看；分页仍遵循本接口上限。 |
| 历史 Top 100 | 其余支持回看的站点仅支持 Top 100 商品。 |
| 不支持回看 | `au`、`br`、`in` 不支持历史回看。 |
| 后续数据处理 | 非结构化结果不支持 `_dataQuery_executeDynamicQuery` 二次分析；可以从本地保存的 JSON 按需提取数据。 |
| 不可估算数据 | 非标准类目商品可能返回无法预估的销量或销售额，以响应中的 `-1` 为标记。 |

#### 常见场景参数示例

这些是查询条件片段；请求均需显式传入 `marketplace`，默认使用 `us`。

| 场景 | 条件片段 |
|------|----------|
| 相似商品 | `queryMode=1`、`queryType=1`、`queryValue="B0CVM8TXHP"`。 |
| 类目浏览 | `queryMode=1`、`queryType=2`、`queryValue="3743561"`。 |
| 品牌热销 | `queryMode=1`、`queryType=3`、`queryValue="Anker"`。 |
| ABA 关键词 | `queryMode=1`、`queryType=6`、`queryValue="Power Bank"`。 |
| 第四季度旺季 | `queryMode=1`、`queryType=10`、`queryValue="10,11,12"`。 |
| 历史类目与当前对比 | `queryMonth="2024-11"`、`queryMode=1`、`queryType=2`、`queryValue="3743561"`；在已说明额外消耗的范围内，再查询不带 `queryMonth` 的当前数据。 |
| 新品、高销量与 FBA | `queryMode=2`；`queryValue` 序列化内容为 `[{"QueryType":11,"Content":"2024-06-01,"},{"QueryType":9,"Content":"300,"},{"QueryType":15,"Content":"FBA"}]`。 |
| 低价高销量 | `queryMode=2`；`queryValue` 序列化内容为 `[{"QueryType":8,"Content":",2000"},{"QueryType":9,"Content":"500,"}]`。 |
| 卖家商品组合 | `queryMode=1`、`queryType=4`、`queryValue="AnkerDirect"`。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 第一个位置参数 | JSON 文本 | 是 | 请求原样传入，不改变 `queryValue` 字符串、范围语法或字段大小写。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用业务缓存读写；默认复用 24 小时缓存。业务封装调用公共 `call_api.run` 时始终附加此选项，避免公共调用器再建立第二层响应缓存。 |
| --help / -h | CLI flag | 否 | 本地显示用法，不请求接口。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 优先使用配置的基础地址，去掉末尾 `/`；默认公共规则中的正式网关。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 请求时需要 | 优先使用 `LINKFOX_AGENT_API_KEY`，也支持 `LINKFOXAGENT_API_KEY`；缓存命中时不重新认证。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 原样传递为同名请求头；`SESSION_ID` 同时用于数据归档。 |

缓存保存在 `<cwd>/linkfox/.cache/linkfox-sorftime-amazon-product-query/`，文件名为技能名加参数 JSON（`ensure_ascii=False`、`sort_keys=True`）的 SHA-256 前 16 位。TTL 按文件修改时间计算，过期、无法读取或损坏时视为未命中，包括非 UTF-8 内容和异常 `_cache` 标记；命中时在字典响应中添加 `_cache.hit=true`。缓存包含完整响应及错误响应，不自动重试；需要重新请求时由用户决定后使用 `--no-cache`。缓存写入失败不阻断已有结果输出。

完整响应使用 UTF-8 保存在当前目录的会话数据路径，归档文件使用微秒时间戳，避免同一秒内多次查询覆盖前一份结果。大小阈值按 UTF-8 字节计，为 8000 字节。默认生成的会话 ID 在同一进程内保持稳定，并维护 `_meta.json` 与 `index.jsonl`。业务封装在请求前检查当前目录可写，不回退到 `ACPX_WORKSPACES`、家目录或临时目录。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | Sorftime 业务响应码，200 表示业务成功；与网关 errcode 分开判断 |
| errcode | integer / string / null | 网关错误码，按公共响应码基本规则判断；错误响应可返回此字段 |
| errmsg | string | 网关错误消息，错误响应可返回此字段 |
| msg | string | 响应消息 |
| total | integer | 结果总数 |
| page | integer | 当前页码 |
| pageCount | integer | 总页数（最多200页） |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗Token数量 |
| requestConsumed | integer | 消耗的请求数 |
| type | string | 渲染的样式 |
| columns | array | 渲染的列 |
| products | array | 产品列表（详见下方） |

#### 商品对象字段（products 数组元素）

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| title | string | 商品标题 |
| brand | string | 品牌 |
| asinUrl | string | 商品链接，亚马逊Listing详情页URL |
| imageUrl | string | 主图URL |
| productImageUrls | array | 主图列表（所有商品图片URL） |
| parentAsin | string | 父ASIN，有子体时为父级ASIN，无子体时为null |
| variationNum | integer | 变体数 |
| weight | string | 重量，单位g |
| size | array | 尺寸，外包装[最长边,第二长边,最短边]，单位cm |
| price | number | 当前价格，未扣Coupon，单位为当地货币(如美元) |
| oldPrice | number | 划线价，单位为当地货币(如美元) |
| salesPrice | number | 到手价，扣除Coupon后的实际售价，单位为当地货币(如美元) |
| coupon | integer | Coupon政策。值>=0为抵扣金额(如500=$5)，值<0为折扣百分比(如-10=10%折扣) |
| fbaFees | number | FBA费用，单位为当地货币(如美元) |
| fbaDetail | array | FBA明细。首项为配送费，后续为月份:仓储费，如[475,"1-9:5","10-12:15"] |
| platformFee | number | 平台佣金，单位为当地货币(如美元) |
| profitAmount | number | 利润，到手价-FBA费-佣金，单位为当地货币(如美元) |
| profitRate | number | 利润率，例25.83表示25.83% |
| monthlySalesUnits | integer | 月销量，近30日Listing维度不区分子体，推荐用于评估销量，值为-1表示无法预估 |
| monthlySalesRevenue | number | 月销售额，预估值，单位为当地货币(如美元)，值为-1表示无法预估 |
| listingSalesVolumeOfDaily | integer | 日销量，Listing维度不区分子体，值为-1表示无法预估 |
| listingSalesOfDaily | number | 日销售额，单位为当地货币(如美元)，值为-1表示无法预估 |
| salesRank | integer | BSR排名，大类排名 |
| category | array | 大类，[大类名称, NodeId] |
| bsrCategory | array | 小类排名列表，每项包含 nodeId（节点ID）、name（类目名称）、rank（排名）、date（日期，格式yyyyMMdd） |
| rating | number | 当前评分（0.0-5.0，如4.8） |
| ratings | integer | 评分数量 |
| availableDate | string | 上架时间，格式yyyy-MM-dd |
| onlineDays | integer | 上架天数 |
| buyboxSeller | string | Buybox卖家名称 |
| buyBoxSellerId | string | Buybox卖家ID |
| buyboxSellerAddress | string | 卖家所在地，Buybox卖家国籍(二字码如CN、US)，亚马逊自营时为null |
| isFBA | boolean | 是否FBA，Buybox卖家是否使用FBA物流 |
| sellerNum | integer | 卖家数 |
| aPlus | boolean | 有A+ |
| hasVideo | boolean | 有视频 |
| hasBrandStore | boolean | 有品牌店 |


#### bsrCategory 数组元素

以下嵌套字段的类型以实际响应为准，不补造缺失值。

| 字段 | 类型 | 说明 |
|------|------|------|
| nodeId | 以实际响应为准 | 节点 ID。 |
| name | 以实际响应为准 | 类目名称。 |
| rank | 以实际响应为准 | 排名。 |
| date | 以实际响应为准 | 日期，格式 `yyyyMMdd`。 |

#### 脚本错误与缓存标记

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | HTTP 空或非 JSON 错误体时为 `HTTP <状态>: <原因>`；连接错误时为 `Connection failed: <原因>`。JSON 错误体原样保留。 |
| details | string | HTTP 非 JSON 错误体的原始内容；仅存在该错误情况时返回。 |
| _cache | object | 本地缓存命中标记对象。 |
| _cache.hit | boolean | 命中时为 true，不代表上游请求成功。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- Sorftime 响应体的 `code=200` 表示业务成功；若返回其他 `code`，根据 `msg` 解释查询失败。这是网关公共判断后的业务层规则，不以 `code` 替代 `errcode`。
- 不可估算的日/月销量及销售额以 `-1` 表示，不能作为真实销量或销售额使用；月销量为近 30 日 Listing 维度，不区分子体。
- 脚本保留 HTTP 错误体的 JSON；空或非 JSON 错误体及连接失败通过上表字段输出，不把错误缓存命中解释为业务成功。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/amazon/productQuery" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"marketplace":"us","queryMode":2,"queryValue":"[{\"QueryType\":11,\"Content\":\"2024-06-01,\"},{\"QueryType\":9,\"Content\":\"300,\"},{\"QueryType\":15,\"Content\":\"FBA\"}]"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sorftime-amazon-product-query",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
