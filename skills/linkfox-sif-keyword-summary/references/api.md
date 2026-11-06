# SIF 关键词流量来源 接口说明

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

## 接口：关键词流量来源汇总

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sif/keywordSummary`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchKeyword | string | 是 | 搜索关键词，尽量翻译成对应国家站点的语言。最大长度 1000 字符 |
| country | string | 否 | 国家站点，默认 `US`。可选值（共 13 个）：`US`（美国）、`UK`（英国）、`DE`（德国）、`CA`（加拿大）、`JP`（日本）、`FR`（法国）、`ES`（西班牙）、`IT`（意大利）、`MX`（墨西哥）、`AU`（澳大利亚）、`AE`（阿联酋）、`BR`（巴西）、`SA`（沙特阿拉伯） |
| asins | string | 否 | ASIN 过滤列表，多个用英文逗号分隔；不传则返回该关键词下所有 ASIN。最大长度 1000 字符 |
| condition | string | 否 | 条件筛选，每次只能传一个，完整枚举与含义见下方 condition 枚举表 |
| last7d | boolean | 否 | 是否取最近 7 天数据，默认 `true`。传 `false` 时使用 `startDate`/`endDate` 区间 |
| startDate | string | 否 | 开始日期 `yyyy-MM-dd`（`last7d=false` 时生效；不填取系统最新整周） |
| endDate | string | 否 | 结束日期 `yyyy-MM-dd`（与 `startDate` 配套） |
| sortBy | string | 否 | 排序字段。可选值：`totalKeywordNum`（全部流量词）、`naturalKeywordNum`（自然流量词）、`brandKeywordNum`（品牌广告词）、`vedioKeywordNum`（视频广告词）、`acKeywordNum`（AC推荐词）、`erKeywordNum`（ER推荐词）、`trKeywordNum`（TR推荐词）、`sumScore`（所有关键词曝光总得分）、`totalNfScore`、`totalSpSocre`（注意拼写）、`totalBrandScore`、`totalVedioScore`、`totalAcScore`、`totalTrScore`、`totalErScore` |
| pageNum | integer | 否 | 页码，默认 `1` |
| pageSize | integer | 否 | 每页数量，最小 10，最大 100，默认 `100` |
| desc | boolean | 否 | 是否降序，默认 `true` |

#### condition 枚举

| 枚举值 | 说明 |
|------|------|
| nfPosition | 自然搜索流量词。 |
| isSpAd | SP 广告流量词。 |
| isVedioAd | 视频广告流量词，保留原始拼写。 |
| isBrandAd | 品牌广告流量词。 |
| isPPCAd | PPC 广告流量词，包含全部付费广告类型。 |
| isSearchRecommend | 搜索推荐流量词。 |
| acAd | SP 推荐，包括 Trending now、Seen on social media、Customers frequently viewed、4 stars and above 等。 |
| totalPeriod.in | 本期新进全部流量词。 |
| nfKeywordCnt.total / nfKeywordCnt.in | 全部 / 新进自然曝光流量词。 |
| adKeywordCnt.total / adKeywordCnt.in | 全部 / 新进广告曝光流量词。 |
| allSpKeywordCnt.total / allSpKeywordCnt.in | 全部 / 新进 SP 广告词，包含常规位与推荐位。 |
| spKeywordCnt.total / spKeywordCnt.in | 全部 / 新进 SP 常规位流量词。 |
| recSpKeywordCnt.total / recSpKeywordCnt.in | 全部 / 新进 SP 推荐位流量词。 |
| allSbKeywordCnt.total / allSbKeywordCnt.in | 全部 / 新进 SB 广告词。 |
| sbKeywordCnt.total / sbKeywordCnt.in | 全部 / 新进 SB 常规位流量词。 |
| sbvKeywordCnt.total / sbvKeywordCnt.in | 全部 / 新进 SBV 流量词。 |

周期计数枚举中的 `.total` 表示全量，`.in` 表示新进；多个来源筛选需分别请求，并遵守成本约束。

#### 参数约束与使用限制

- 仅支持参数表中的 13 个站点，其他代码会被站点校验拒绝；`IN`、`NL`、`SE`、`PL`、`TR`、`SG` 不在支持范围。
- `sortBy` 留空时使用系统默认排序；保留 `isVedioAd`、`vedioKeywordNum`、`totalVedioScore`、`totalSpSocre` 等原始拼写。
- 本接口以关键词下的 ASIN 流量为中心，仅含下述有限商品资料，不提供整品元数据、跨渠道关键词计数和变体聚合；缺失字段见响应说明。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 作为命令行首个非选项参数，内容为上方请求参数；不在脚本中补写服务端默认值。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 本次跳过缓存读取和写入；默认复用 24 小时缓存。 |

脚本入口为 `scripts/sif_keyword_traffic.py`，通过公共 `scripts/call_api.py` 的 `run` 完成请求、单层缓存、保存和输出。缓存路径为 `<cwd>/linkfox/.cache/linkfox-sif-keyword-summary/linkfox-sif-keyword-summary-<hash>.json`，`hash` 为参数对象按键排序、`ensure_ascii=False` 序列化后的 SHA-256 前 16 位；有效期按文件修改时间计算为 24 小时，命中时标注 `_cache.hit=true`。默认缓存请求返回的结果，包括失败或空结果；缓存命中不表示本次已实时请求或业务成功，不额外叠加缓存。

网关地址优先使用 `LINKFOX_TOOL_GATEWAY`，缺省使用公共规则中的正式地址；主密钥 `LINKFOX_AGENT_API_KEY` 优先于兼容变量 `LINKFOXAGENT_API_KEY`。请求头包含 `Accept: application/json` 及会话追踪头 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。

会话数据只能落在当前工作目录的 `linkfox` 下；请求前检查可写性，失败即报错，不回退到家目录或 `/tmp`，不受外部 `ACPX_WORKSPACES` 改写。每次输出使用微秒时间戳避免同秒调用覆盖文件；按 `SESSION_ID` 聚合，未设置时使用公共调用器的进程内稳定会话标识，并维护 `_meta.json` 和 `index.jsonl`。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态，含义按公共规则；业务字段 `code` 独立判断 |
| errmsg | string | 网关消息 |
| code | string | SIF 业务返回码，`"1"` 表示成功 |
| msg | string | 消息 |
| total | integer | 本次实际返回的数据数量 |
| data | array | 返回数据，商品关键词流量数据对象数组 |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| title | string | 标题 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗token |

#### 脚本本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _http_status | integer | 业务脚本记录的实际 HTTP 状态，写入保存结果及缓存，大响应摘要也展示；不是网关响应字段，不替代 `errcode` 或 SIF `code`。连接失败且未收到 HTTP 响应时不添加。 |

缓存命中时，`_http_status` 是生成该缓存时的历史状态，不代表本次发起了请求；缺少该字段的旧缓存无法还原 HTTP 状态，不据此推断 HTTP 成功，也不自动重新请求。

> 本接口不返回 `isParentAsin`、`variantsNum`、`noKeywordVariantsNum`；如需这些字段请使用 `sif/asinSummary` 接口。

#### 数据项字段（`data` 数组中的每个对象）

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN 编码 |
| productTitle | string | 商品标题 |
| productImageUrl | string | 商品主图 URL |
| productPrice | number | 商品售价 |
| customerRatingCount | integer | 客户评分总数 |
| productStarRating | number | 商品星级（0–5 星） |
| productRatingScore | number | 商品评分数值 |
| productUpdateTime | string | 产品更新时间（`yyyy-MM-dd HH:mm:ss`） |
| dataPeriodStartDate | string | 数据周期起始日期（`yyyy-MM-dd`） |
| totalExposureScore | number | 总曝光分数 |
| totalExposureRatio | number | 总流量份额 |
| naturalSearchExposureScore | number | 自然搜索曝光总分 |
| naturalSearchExposureRatio | number | 自然搜索曝光占比 |
| sponsoredProductsExposureScore | number | SP 广告曝光总分 |
| sponsoredProductsExposureRatio | number | SP 广告曝光占比 |
| brandAdExposureScore | number | 品牌广告曝光总分 |
| brandAdExposureRatio | number | 品牌广告曝光占比 |
| videoAdExposureScore | number | 视频广告曝光总分 |
| videoAdExposureRatio | number | 视频广告曝光占比 |
| amazonsChoiceExposureScore | number | AC 曝光总分 |
| amazonsChoiceExposureRatio | number | AC 曝光占比 |
| editorialRecommendationsExposureScore | number | ER 曝光总分 |
| editorialRecommendationsExposureRatio | number | ER 曝光占比 |
| topRatedExposureScore | number | TR 曝光总分 |
| topRatedExposureRatio | number | TR 曝光占比 |
| recommendPositionExposureScore | number | 推荐位曝光总分 |
| recommendAdExposureScore | number | 推荐位广告曝光分数 |
| recommendAdExposureRatio | number | 推荐位广告流量份额 |
| recommendNonadExposureScore | number | 推荐位非广告曝光分数 |
| recommendNonadExposureRatio | number | 推荐位非广告流量份额 |
| comprehensiveNaturalExposureScore | number | 综合自然流量得分（自然搜索 + 推荐位非广告） |
| comprehensiveNaturalExposureRatio | number | 综合自然流量份额 |
| keywordTotalExposureScore | number | 关键词总得分 |
| keywordNaturalExposureScore | number | 关键词自然得分 |
| keywordSponsoredProductsExposureScore | number | 关键词 SP 广告得分 |
| keywordBrandAdExposureScore | number | 关键词品牌广告得分 |
| keywordVideoAdExposureScore | number | 关键词视频广告得分 |
| keywordAmazonsChoiceExposureScore | number | 关键词 AC 得分 |
| keywordRecommendExposureScore | number | 关键词推荐位得分 |
| keywordRecommendAdExposureScore | number | 关键词推荐位广告得分 |
| keywordRecommendNonadExposureScore | number | 关键词推荐位非广告得分 |
| keywordComprehensiveNaturalExposureScore | number | 关键词综合自然得分（自然 + 推荐位非广告） |
| ppcTrafficSources | array | PPC 付费广告流量来源标记。包含：SP 广告、头部品牌广告、底部品牌广告、视频广告 |
| naturalSearchTrafficSources | array | 自然搜索流量来源标记 |
| amazonRecommendationSources | array | 亚马逊推荐流量来源标记。包含：Best Seller、AC、ER、TR、TRFOB 等 |
| promotionalDealSources | array | 促销活动流量来源标记。包含：Coupon、Limited Time Deal、Lowest Price in 30 Days 等 |

> 本接口不返回以下字段：`productCategory`、`productFeatures`、`isVariantProduct`、`isMonitored`、`monitoringStartTime`，以及各 ASIN 的 `totalTrafficKeywordCount`、`naturalSearchKeywordCount`、`sponsoredProductsKeywordCount`、`brandAdKeywordCount`、`topBrandAdKeywordCount`、`bottomBrandAdKeywordCount`、`videoAdKeywordCount`、`amazonsChoiceKeywordCount`、`editorialRecommendationsKeywordCount`、`topRatedKeywordCount`、`frequentlyBoughtKeywordCount`。如需这些字段，请使用 `sif/asinSummary` 接口。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 脚本结果中的 `_http_status` 用于核对 HTTP 状态：`401` / `402` 按认证和算力引导处理；其他非 `200`–`299` 状态也不能因响应体含 `code="1"` 或 `errcode=200` 而判为成功。连接失败时保留的 `error` 说明原因，不视为业务成功。
- 网关正常响应后，SIF 业务字段 `code="1"` 表示业务成功；其他值或缺失时结合 `msg` 说明具体情况，不把网关成功当作 SIF 业务成功。
- 成功且 `data=[]` 或 `total=0` 表示当前条件未返回记录；说明本次筛选和时间范围，不自动换词、翻页或改变条件试探。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sif/keywordSummary \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"searchKeyword": "wireless charger", "country": "US"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sif-keyword-summary",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```