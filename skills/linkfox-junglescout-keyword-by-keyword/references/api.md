# Jungle Scout 根据关键词扩展关键词信息 接口说明

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

## 接口：根据种子关键词扩展关键词信息

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/tool-jungle-scout/keywords/by-keyword`

### 请求参数

POST Body（JSON）：

#### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| marketplace | string | 是 | 目标市场代码。可选值：`us`、`uk`、`de`、`in`、`ca`、`fr`、`it`、`es`、`mx`、`jp`。默认 `us` |
| searchTerms | string | 是 | 种子关键词（单个关键词字符串） |

#### 可选参数 — 结果控制

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| needCount | int | 否 | 返回结果总数 |
| sort | string | 否 | 排序字段，默认 `-monthly_search_volume_exact`（精确搜索量降序） |

#### 可选参数 — 搜索量筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minMonthlySearchVolumeExact | int | 否 | 精确搜索量下限 |
| maxMonthlySearchVolumeExact | int | 否 | 精确搜索量上限 |
| minMonthlySearchVolumeBroad | int | 否 | 广泛搜索量下限 |
| maxMonthlySearchVolumeBroad | int | 否 | 广泛搜索量上限 |

#### 可选参数 — 其他筛选

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| minWordCount | int | 否 | 关键词最少词数（用于筛选长尾词） |
| maxWordCount | int | 否 | 关键词最多词数 |
| minOrganicProductCount | int | 否 | 自然排名商品数下限 |
| maxOrganicProductCount | int | 否 | 自然排名商品数上限 |

#### sort 可选值

| 值 | 说明 |
|----|------|
| name / -name | 关键词名称 升序/降序 |
| dominant_category / -dominant_category | 主类目 升序/降序 |
| monthly_trend / -monthly_trend | 月度趋势 升序/降序 |
| quarterly_trend / -quarterly_trend | 季度趋势 升序/降序 |
| monthly_search_volume_exact / -monthly_search_volume_exact | 精确搜索量 升序/降序（默认降序） |
| monthly_search_volume_broad / -monthly_search_volume_broad | 广泛搜索量 升序/降序 |
| recommended_promotions / -recommended_promotions | 推荐促销 升序/降序 |
| sp_brand_ad_bid / -sp_brand_ad_bid | 品牌广告出价 升序/降序 |
| ppc_bid_broad / -ppc_bid_broad | PPC广泛出价 升序/降序 |
| ppc_bid_exact / -ppc_bid_exact | PPC精确出价 升序/降序 |
| ease_of_ranking_score / -ease_of_ranking_score | 排名难度 升序/降序 |
| relevancy_score / -relevancy_score | 相关性评分 升序/降序 |
| organic_product_count / -organic_product_count | 自然商品数 升序/降序 |

#### 站点映射

| 站点 | marketplace 值 | 说明 |
|------|---------------|------|
| 美国 | us | Amazon.com |
| 英国 | uk | Amazon.co.uk |
| 德国 | de | Amazon.de |
| 印度 | in | Amazon.in |
| 加拿大 | ca | Amazon.ca |
| 法国 | fr | Amazon.fr |
| 意大利 | it | Amazon.it |
| 西班牙 | es | Amazon.es |
| 墨西哥 | mx | Amazon.com.mx |
| 日本 | jp | Amazon.co.jp |

#### 参数约束与使用限制

- `searchTerms` 仅接受一个种子关键词字符串，可以是包含空格的短语；原样传入用户提供的词，英文小写为佳。多种子词需要拆分多次调用。
- 未指定站点时使用 `us`。仅支持上表 10 个站点，不包括澳大利亚、荷兰等市场。
- 默认结果数量有限，需要更多结果时设置 `needCount`；数量默认值和上限未明确，实际返回数量以响应中的 `keywordInfoList` 为准。
- 默认按精确搜索量降序排列。排序只能使用上表预定义值，不支持自定义组合排序。
- 充分使用 `min/max` 筛选缩小范围；长尾词通常可设置 `minWordCount` 为 3 或以上。
- 同一会话同一参数组合默认只调用一次。失败或空结果时不得自动换关键词、翻页或改邮编连续试探；继续检索前先向用户说明额外消耗。
- 搜索量为月均估算值，并非实时数据；`monthlyTrend`、`quarterlyTrend` 分别为环比月度和季度搜索量变化百分比。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 首个位置参数，按上述请求参数原样提交。 |
| --inline | CLI flag | 否 | 强制全量输出，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过本地响应缓存的读取和写入；未传时使用 24 小时缓存。 |

缓存位于 `<cwd>/linkfox/.cache/linkfox-junglescout-keyword-by-keyword/`，键为参数 JSON 排序后 SHA-256 的前 16 位，文件有效期 24 小时；命中时增加 `_cache.hit` 标记。业务封装负责缓存读写，调用公共 `call_api.run` 时始终附加 `--no-cache`，公共调用器不读写第二层响应缓存。缓存也可能保存空结果或错误，命中时仍须按响应规则判断，不能视为查询成功。

完整数据必须保存在当前工作目录的会话目录内，不可写时在请求前报错，不回退家目录或临时目录；`SESSION_ID` 优先，未设置时在进程内生成稳定标识。保存、摘要及 `--inline` 输出由公共调用器处理。支持 `LINKFOX_TOOL_GATEWAY` 网关覆盖、两种 API Key 变量以及 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头透传。

业务脚本在公共调用器返回后读取并解析已保存的完整 JSON；文件缺失、不可读或 JSON 不完整时，向 stderr 报错并返回退出码 1，不因保存失败自动再次请求接口。退出码 0 仅表示本地执行及保存完成，业务是否成功仍按下方响应码规则判断。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| costToken | integer | 消耗 token 数 |
| keywordInfoList | array | 关键词信息列表 |

#### keywordInfoList 数组中每个对象

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 关键词名称 |
| country | string | 市场代码 |
| monthlySearchVolumeExact | integer | 月均精确匹配搜索量 |
| monthlySearchVolumeBroad | integer | 月均广泛匹配搜索量 |
| monthlyTrend | number | 月度搜索量变化百分比 |
| quarterlyTrend | number | 季度搜索量变化百分比 |
| dominantCategory | string | 搜索结果中占比最高的品类 |
| relevancyScore | integer | 与种子词的相关性评分 |
| easeOfRankingScore | integer | 排名容易度评分（越高越容易排名） |
| organicProductCount | integer | 自然排名商品数量 |
| sponsoredProductCount | integer | 广告商品数量 |
| ppcBidExact | number | 精确匹配 PPC 建议出价（美元） |
| ppcBidBroad | number | 广泛匹配 PPC 建议出价（美元） |
| spBrandAdBid | number | Sponsored Brand 广告建议出价（美元） |
| recommendedPromotions | integer | 推荐促销赠品数量 |

#### 状态与脚本附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 如返回，按公共响应码基本规则判断；认证错误示例为 401。 |
| errmsg | string | 如返回，保存并用于解释实际错误原因。 |
| errorCode | integer / string | 业务状态字段；如返回，200 表示业务成功，其他值表示业务错误，同时仍须按公共规则判断 `errcode`。 |
| _cache | object | 脚本命中本地缓存时增加的元信息，不是业务接口请求参数。 |
| _cache.hit | boolean | true 表示复用本地响应。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应含 `errorCode` 时，`200` 表示业务成功，其他值表示业务错误；业务成功还须满足公共响应码基本规则。`errorCode=401` 或 `402` 时按 `onboarding.md` 处理，其他错误依据 `errmsg` 解释；不能仅因 HTTP 成功或存在关键词列表就忽略业务错误。
- 正常返回时解析 `keywordInfoList`；列表为空只表示本次查询未取得关键词，不自动改条件追加请求。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/tool-jungle-scout/keywords/by-keyword" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"marketplace": "us", "searchTerms": "yoga mat", "needCount": 20}'
```

### 响应示例

```json
{
  "costToken": 1,
  "keywordInfoList": [
    {
      "name": "yoga mat thick",
      "country": "us",
      "monthlySearchVolumeExact": 45000,
      "monthlySearchVolumeBroad": 120000,
      "monthlyTrend": 15.3,
      "quarterlyTrend": -5.2,
      "dominantCategory": "Sports & Outdoors",
      "relevancyScore": 856,
      "easeOfRankingScore": 3,
      "organicProductCount": 342,
      "sponsoredProductCount": 28,
      "ppcBidExact": 1.25,
      "ppcBidBroad": 0.89,
      "spBrandAdBid": 2.50,
      "recommendedPromotions": 150
    },
    {
      "name": "yoga mat non slip",
      "country": "us",
      "monthlySearchVolumeExact": 38000,
      "monthlySearchVolumeBroad": 95000,
      "monthlyTrend": 8.1,
      "quarterlyTrend": 12.4,
      "dominantCategory": "Sports & Outdoors",
      "relevancyScore": 920,
      "easeOfRankingScore": 2,
      "organicProductCount": 510,
      "sponsoredProductCount": 35,
      "ppcBidExact": 1.58,
      "ppcBidBroad": 1.12,
      "spBrandAdBid": 3.10,
      "recommendedPromotions": 200
    }
  ]
}
```

#### 认证错误示例

```json
{"errcode": 401, "errmsg": "authorized error"}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-junglescout-keyword-by-keyword",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```