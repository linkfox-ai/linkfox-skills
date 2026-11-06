# Jungle Scout 根据 ASIN 反查关键词 接口说明

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

## 接口：根据 ASIN 反查关键词

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/tool-jungle-scout/keywords/by-asin`

### 请求参数

POST Body（JSON）：

#### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`；使用小写代码，用户未指定站点时由调用方选择 `us`，不是服务端可省略的必填字段 |
| asins | array\<string\> | 是 | ASIN 列表，最多 10 个；使用标准 10 位亚马逊 ASIN（以 B0 开头） |

#### 可选参数 — 结果控制

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| needCount | int | 否 | 返回的结果总数（内部自动分页） |
| includeVariants | boolean | 否 | 是否包含变体商品的关键词 |
| sort | string | 否 | 排序字段，默认 `-monthly_search_volume_exact`（精确搜索量降序）。可选值见下方排序字段表 |

#### 可选参数 — 搜索量筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minMonthlySearchVolumeExact | int | 否 | 最小月精确搜索量（1-999999） |
| maxMonthlySearchVolumeExact | int | 否 | 最大月精确搜索量（1-999999） |
| minMonthlySearchVolumeBroad | int | 否 | 最小月广泛搜索量（1-999999） |
| maxMonthlySearchVolumeBroad | int | 否 | 最大月广泛搜索量（1-999999） |

#### 可选参数 — 关键词特征筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minWordCount | int | 否 | 最小单词数（1-99999） |
| maxWordCount | int | 否 | 最大单词数（1-99999） |
| minOrganicProductCount | int | 否 | 最小自然搜索结果数（1-99999） |
| maxOrganicProductCount | int | 否 | 最大自然搜索结果数（1-99999） |

#### 排序字段

| sort 值 | 说明 |
|---------|------|
| name / -name | 关键词名称 升序/降序 |
| dominant_category / -dominant_category | 主类目 升序/降序 |
| monthly_trend / -monthly_trend | 月趋势 升序/降序 |
| quarterly_trend / -quarterly_trend | 季度趋势 升序/降序 |
| monthly_search_volume_exact / -monthly_search_volume_exact | 精确搜索量 升序/降序（默认降序） |
| monthly_search_volume_broad / -monthly_search_volume_broad | 广泛搜索量 升序/降序 |
| recommended_promotions / -recommended_promotions | 推荐促销 升序/降序 |
| sp_brand_ad_bid / -sp_brand_ad_bid | SP品牌广告出价 升序/降序 |
| ppc_bid_broad / -ppc_bid_broad | PPC广泛出价 升序/降序 |
| ppc_bid_exact / -ppc_bid_exact | PPC精确出价 升序/降序 |
| ease_of_ranking_score / -ease_of_ranking_score | 排名难度分 升序/降序 |
| relevancy_score / -relevancy_score | 相关度分 升序/降序 |
| organic_product_count / -organic_product_count | 自然结果数 升序/降序 |

#### 站点映射

| 站点 | marketplace 值 |
|------|---------------|
| 美国 | us |
| 英国 | uk |
| 德国 | de |
| 印度 | in |
| 加拿大 | ca |
| 法国 | fr |
| 意大利 | it |
| 西班牙 | es |
| 墨西哥 | mx |
| 日本 | jp |

#### 查询条件映射与使用限制

- “搜索量大于 1 万”映射为 `minMonthlySearchVolumeExact: 10000`；“搜索量 1000 到 5000”同时设置 `minMonthlySearchVolumeExact: 1000` 和 `maxMonthlySearchVolumeExact: 5000`。
- “按相关度排序”使用 `sort: -relevancy_score`；“前 50 个”使用 `needCount: 50`。未指定数量时可按场景选择 30–100；关注变体流量时使用 `includeVariants: true`。
- `needCount` 由内部自动分页实现，不能当作独立页码；动态计费按实际查询页数计算，公式见 SKILL.md。调整筛选或增加查询范围可能增加消耗。
- 搜索量和排名定期更新，`updatedAt` 标注最后更新时间；排名并非实时数据。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | string | 是 | 首个位置参数为上述请求体的 JSON。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁止本次读取和写入响应缓存；默认开启 24 小时缓存。 |
| --help / -h | CLI flag | 否 | 显示本地帮助，不请求接口。 |

仅使用公共调用器的一层缓存，缓存目录为 `<cwd>/linkfox/.cache/linkfox-junglescout-keyword-by-asin/`，缓存键为参数排序序列化后的 SHA-256 前 16 位，有效期为 24 小时；命中有效缓存时添加 `_cache.hit=true` 并复用结果。`--no-cache` 禁止缓存读写，公共调用器仍会准备缓存目录。

支持 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 两种密钥变量、`LINKFOX_TOOL_GATEWAY` 网关覆盖和 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。使用当前工作目录保存数据，入口在请求前检查会话数据目录可写；工作目录本身位于系统临时目录（包括 `/tmp`）时也在请求前报错，不回退到用户目录或临时目录。会话标识优先取 `SESSION_ID`，未提供时自动生成。完整响应以 UTF-8 保存并登记到会话元数据；摘要阈值为 8000 字节，最大列表取前 3 项。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断。 |
| errmsg | string | 网关消息或错误原因；认证错误示例为 `{"errcode": 401, "errmsg": "authorized error"}`。 |
| errorCode | 未明确 | 可能出现的业务状态字段，成功码为整数 200，认证失败码为整数 401；字段是否返回及类型未明确，出现时还须按下方业务规则检查结果。 |
| costToken | integer | 消耗 token 数 |
| keywordInfoList | array | 关键词信息列表 |

#### keywordInfoList 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 关键词 |
| country | string | 市场代码 |
| monthlySearchVolumeExact | integer | 月精确匹配搜索量 |
| monthlySearchVolumeBroad | integer | 月广泛匹配搜索量 |
| monthlyTrend | float | 月环比趋势（%） |
| quarterlyTrend | float | 季度趋势（%） |
| dominantCategory | string | 主要类目 |
| relevancyScore | integer | 关键词与 ASIN 的相关度（0-100） |
| easeOfRankingScore | integer | 排名容易程度（0-100，越高越容易排名） |
| organicRank | integer | ASIN 的自然搜索排名 |
| sponsoredRank | integer | ASIN 的广告排名 |
| overallRank | integer | 综合排名位置 |
| organicProductCount | integer | 自然搜索结果中的商品总数 |
| sponsoredProductCount | integer | 广告位商品总数 |
| ppcBidExact | float | 精确匹配 PPC 建议出价（USD） |
| ppcBidBroad | float | 广泛匹配 PPC 建议出价（USD） |
| spBrandAdBid | float | SP 品牌广告建议出价（USD） |
| recommendedPromotions | integer | 推荐促销量 |
| primaryAsin | string | 该关键词下排名最高的 ASIN |
| relativeOrganicPosition | float | 查询 ASIN 的自然排名相对位置 |
| relativeSponsoredPosition | float | 查询 ASIN 的广告排名相对位置 |
| organicRankingAsinsCount | integer | 有自然排名的查询 ASIN 数量 |
| sponsoredRankingAsinsCount | integer | 有广告排名的查询 ASIN 数量 |
| avgCompetitorOrganicRank | float | 查询 ASIN 的平均自然排名 |
| avgCompetitorSponsoredRank | float | 查询 ASIN 的平均广告排名 |
| variationLowestOrganicRank | integer | 变体中最佳自然排名 |
| variationLowestSponsoredRank | integer | 变体中最佳广告排名 |
| competitorOrganicRank | array | 各 ASIN 的自然排名，元素为 `{asin, organicRank}` |
| competitorSponsoredRank | array | 各 ASIN 的广告排名，元素为 `{asin, sponsoredRank}` |
| updatedAt | string | 数据最后更新时间 |

#### competitorOrganicRank 数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 查询 ASIN。 |
| organicRank | integer | 该 ASIN 的自然搜索排名。 |

#### competitorSponsoredRank 数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | 查询 ASIN。 |
| sponsoredRank | integer | 该 ASIN 的广告排名。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 实际响应包含 `errorCode` 时，还须检查业务结果：`200` 表示成功，`401` 表示认证失败并按认证指引处理，其他非成功值表示业务异常，依据响应中的错误消息说明原因。HTTP 状态与 `errcode` 满足公共正常响应规则，不代表可忽略 `errorCode` 中的业务错误；未返回该字段时不自行补造。
- `keywordInfoList` 为空时，说明本次 ASIN、站点和筛选条件下未返回关键词，不据此断言 ASIN 没有流量；不自动放宽筛选或追加检索。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/tool-jungle-scout/keywords/by-asin" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"marketplace": "us", "asins": ["B0DXXXXXXX"], "needCount": 50, "sort": "-monthly_search_volume_exact"}'
```

### 响应示例

```json
{
  "costToken": 10,
  "keywordInfoList": [
    {
      "name": "yoga mat",
      "country": "us",
      "monthlySearchVolumeExact": 85420,
      "monthlySearchVolumeBroad": 125000,
      "monthlyTrend": 12.5,
      "quarterlyTrend": 8.3,
      "dominantCategory": "Sports & Outdoors",
      "relevancyScore": 95,
      "easeOfRankingScore": 42,
      "organicRank": 5,
      "sponsoredRank": 3,
      "overallRank": 4,
      "organicProductCount": 2000,
      "sponsoredProductCount": 48,
      "ppcBidExact": 1.25,
      "ppcBidBroad": 0.95,
      "spBrandAdBid": 2.10,
      "recommendedPromotions": 5,
      "primaryAsin": "B0DXXXXXXX",
      "relativeOrganicPosition": 0.12,
      "relativeSponsoredPosition": 0.08,
      "organicRankingAsinsCount": 1,
      "sponsoredRankingAsinsCount": 1,
      "avgCompetitorOrganicRank": 5.0,
      "avgCompetitorSponsoredRank": 3.0,
      "variationLowestOrganicRank": 3,
      "variationLowestSponsoredRank": 2,
      "competitorOrganicRank": [{"asin": "B0DXXXXXXX", "organicRank": 5}],
      "competitorSponsoredRank": [{"asin": "B0DXXXXXXX", "sponsoredRank": 3}],
      "updatedAt": "2026-04-10"
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
  "skillName": "linkfox-junglescout-keyword-by-asin",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```