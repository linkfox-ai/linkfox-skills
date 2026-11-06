# SIF ASIN 流量来源分析 接口说明

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

## 接口：ASIN 流量来源汇总（asinSummary）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sif/asinSummary`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchValue | string | 是 | 搜索值，ASIN码，多个用逗号分隔，最多10个ASIN，最大长度1000字符 |
| country | string | 否 | 国家站点，用户未指定时使用默认 `US`。可选值（共 13 个）：`US`、`UK`、`DE`、`CA`、`JP`、`FR`、`ES`、`IT`、`MX`、`AU`、`AE`、`BR`、`SA` |
| last7d | boolean | 否 | 是否取最近 7 天数据，默认 `true`。传 `false` 时使用 `startDate`/`endDate` 区间 |
| startDate | string | 否 | 开始日期 `yyyy-MM-dd`（`last7d=false` 时生效；不填取系统最新 ABA 周） |
| endDate | string | 否 | 结束日期 `yyyy-MM-dd`（与 `startDate` 配套） |
| conditions | string | 否 | 条件筛选，多个以英文逗号隔开；返回至少包含所列任一渠道流量的 ASIN 汇总行。可选值：`nf`（自然流量）、`sp`（SP广告）、`sb`（SB常规）、`sbv`（视频广告）、`ad`（广告流量）、`acAd`（SP推荐）、`totalPeriod.in`（新进全部流量词） |
| sortBy | string | 否 | 排序字段，留空使用系统默认排序。可选值：`totalKeywordNum`（全部流量词）、`naturalKeywordNum`（自然流量词）、`brandKeywordNum`（品牌广告词）、`vedioKeywordNum`（视频广告词）、`acKeywordNum`（AC推荐词）、`erKeywordNum`（ER推荐词）、`trKeywordNum`（TR推荐词）、`sumScore`（所有关键词曝光总得分）、`totalNfScore`（所有自然排名曝光总得分）、`totalSpSocre`（所有SP广告曝光总得分，注意拼写）、`totalBrandScore`（所有品牌广告曝光总得分）、`totalVedioScore`（所有视频广告曝光总得分）、`totalAcScore`（所有AC推荐曝光总得分）、`totalTrScore`（所有TR推荐曝光总得分）、`totalErScore`（所有ER推荐曝光总得分） |
| pageNum | integer | 否 | 页码，默认 `1` |
| pageSize | integer | 否 | 每页数量，最小10，最大 **10000**，默认 `10000` |
| desc | boolean | 否 | 是否降序，默认 `true` |

#### 使用限制

- 站点仅支持参数表中的代码，其他代码会被接口格式校验拒绝；不支持 IN、NL、SE、PL、TR、SG。
- 默认使用最近七天窗口；自定义窗口按参数表设置。仅提供本期与上期对比，不能据此构造任意多周历史趋势。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | CLI positional | 是 | 第一个位置参数为上述请求参数的 JSON 字符串，脚本按原样传递。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用缓存读取和写入；默认复用 24 小时本地缓存。 |

| 环境变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| LINKFOX_TOOL_GATEWAY | string | 否 | 网关基础地址，默认值见公共规则；拼接端点前去除末尾 `/`。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | string | 是，二选一 | 优先读取前者，兼容后者；直接作为 Authorization 请求头值，不添加 Bearer 前缀。已有可用缓存时不发请求，也不要求读取密钥。 |
| SESSION_ID | string | 否 | 原样透传同名请求头；去除首尾空白后用于会话目录。未提供时生成进程内稳定的会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | string | 否 | 原样透传相应请求头；未提供时为空字符串。 |

脚本入口为 `python scripts/sif_asin_summary.py '<JSON 参数>' [--inline] [--no-cache]`。仅使用公共调用器的一层缓存，不额外建立业务缓存；缓存路径为 `<cwd>/linkfox/.cache/linkfox-sif-asin-summary/linkfox-sif-asin-summary-<hash>.json`，hash 为按键排序、保留中文的参数 JSON 的 SHA-256 前 16 位。字段顺序不同的相同参数复用缓存，过期或损坏时重新请求；缓存命中返回对象会添加 `_cache.hit=true`。完整响应（包括错误或空结果）也会缓存，不得因此自动重试。

完整响应始终以 UTF-8 保存在当前工作目录的会话数据目录，命中缓存也保存。业务封装在请求前检查输出根目录和会话 `data` 目录可创建、可写且位于 `<cwd>/linkfox` 内；目录被文件占用或不可写时立即报错，不产生接口消耗。通过本技能脚本调用时，输出根目录固定为 `<cwd>/linkfox`，不采用 `ACPX_WORKSPACES`、家目录或临时目录回退，禁止写入 `/tmp`。具体输出展示策略见 `SKILL.md`。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态码；正常响应判定见公共规则。网关成功值为 200，错误时返回对应错误码。 |
| errmsg | string | 网关消息；网关错误时包含原因。 |
| code | string | SIF 业务返回码，`"1"` 表示成功 |
| msg | string | 消息 |
| total | integer | 本次实际返回的数据数量 |
| data | array | 返回数据，ASIN汇总对象数组（详见下方） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| title | string | 标题 |
| isParentAsin | boolean | 搜索的是否是父ASIN |
| variantsNum | integer | 有关键词的变体商品数量 |
| noKeywordVariantsNum | integer | 无关键词的变体商品数量 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗token |

#### data 数组元素字段

> 字段后缀约定：`*Prev` 为上一周期数值；`*In` / `*Out` 为本周期相对上期新进 / 退出数量，用于跨周对比。

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN 编码。亚马逊商品标准识别码 |
| productTitle | string | 商品标题 |
| productCategory | string | 商品类目 |
| productPrice | number | 商品售价 |
| productImageUrl | string | 商品主图 URL |
| productFeatures | array | 商品特征列表 |
| customerRatingCount | integer | 客户评分总数 |
| productStarRating | number | 商品星级（0–5 星） |
| productRatingScore | number | 商品评分数值（0–5，亚马逊页面显示数值） |
| isVariantProduct | boolean | 是否为变体 |
| recentMonthlySalesBucket | string | 近一月销量桶（仅 keywordSummary 路径有值，形如 `"300+"` 或 `"1,000+"`） |
| isMonitored | boolean | 是否已监控 |
| monitoringStartTime | string | 商品关注时间 |
| dataPeriodStartDate | string | 数据周期起始日期（`yyyy-MM-dd`） |
| totalExposureScore | number | 总曝光分数。该商品在所有关键词下的曝光量综合评分 |
| totalExposureScorePrev | number | 上周期总曝光分数 |
| totalTrafficKeywordCount | integer | 流量关键词总数 |
| totalTrafficKeywordCountIn | integer | 本周期新进流量关键词数量 |
| totalTrafficKeywordCountOut | integer | 本周期退出流量关键词数量 |
| totalTrafficKeywordCountPrev | integer | 上周期流量关键词总数 |
| naturalSearchExposureScore | number | 自然搜索曝光总分 |
| naturalSearchExposureRatio | number | 自然搜索曝光占比 |
| naturalSearchExposureScorePrev | number | 上周期自然搜索曝光分数 |
| naturalSearchKeywordCount | integer | 自然搜索关键词数量 |
| naturalSearchKeywordCountIn | integer | 本周期新进自然搜索关键词数量 |
| naturalSearchKeywordCountOut | integer | 本周期退出自然搜索关键词数量 |
| naturalSearchKeywordCountPrev | integer | 上周期自然搜索关键词数量 |
| sponsoredProductsExposureScore | number | SP 广告曝光总分 |
| sponsoredProductsExposureRatio | number | SP 广告曝光占比 |
| sponsoredProductsExposureScorePrev | number | 上周期 SP 广告曝光分数 |
| sponsoredProductsKeywordCount | integer | SP 广告关键词数量 |
| brandAdExposureScore | number | 品牌广告曝光总分 |
| brandAdExposureRatio | number | 品牌广告曝光占比 |
| brandAdExposureScorePrev | number | 上周期品牌广告曝光分数 |
| brandAdKeywordCount | integer | 品牌广告关键词总数 |
| topBrandAdKeywordCount | integer | 页面顶部品牌广告关键词数量 |
| bottomBrandAdKeywordCount | integer | 页面底部品牌广告关键词数量 |
| videoAdExposureScore | number | 视频广告曝光总分 |
| videoAdExposureRatio | number | 视频广告曝光占比 |
| videoAdExposureScorePrev | number | 上周期视频广告曝光分数 |
| videoAdKeywordCount | integer | 视频广告关键词数量 |
| amazonsChoiceExposureScore | number | Amazon's Choice 曝光总分 |
| amazonsChoiceExposureRatio | number | Amazon's Choice 曝光占比 |
| amazonsChoiceExposureScorePrev | number | 上周期 AC 曝光分数 |
| amazonsChoiceKeywordCount | integer | Amazon's Choice 关键词数量 |
| amazonsChoiceKeywordCountIn | integer | 本周期新进 AC 关键词数量 |
| amazonsChoiceKeywordCountOut | integer | 本周期退出 AC 关键词数量 |
| editorialRecommendationsExposureScore | number | Editorial Recommendations 曝光总分 |
| editorialRecommendationsExposureRatio | number | Editorial Recommendations 曝光占比 |
| editorialRecommendationsKeywordCount | integer | Editorial Recommendations 关键词数量 |
| topRatedExposureScore | number | Top Rated 推荐曝光总分 |
| topRatedExposureRatio | number | Top Rated 推荐曝光占比 |
| topRatedKeywordCount | integer | Top Rated 推荐关键词数量 |
| frequentlyBoughtKeywordCount | integer | 高频购买推荐关键词数量（Top Rated Frequently Bought） |
| recommendPositionExposureScore | number | 推荐位曝光总分 |
| recommendAdExposureScore | number | 推荐位广告曝光分数 |
| recommendNonadExposureScore | number | 推荐位非广告曝光分数 |
| nonAcRecommendExposureScore | number | 非 AC 推荐位曝光分数 |
| recommendKeywordCount | integer | 推荐位关键词总数 |
| recommendAdKeywordCount | integer | 推荐位广告关键词数量 |
| recommendNonadKeywordCount | integer | 推荐位非广告关键词数量 |
| ppcTrafficSources | array | PPC 付费广告流量来源标记。包含：SP 广告、头部品牌广告、底部品牌广告、视频广告 |
| naturalSearchTrafficSources | array | 自然搜索流量来源标记 |
| amazonRecommendationSources | array | 亚马逊推荐流量来源标记。包含：Best Seller、AC、ER、TR、TRFOB 等 |
| promotionalDealSources | array | 促销活动流量来源标记。包含：Coupon、Limited Time Deal、Lowest Price in 30 Days 等 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常网关响应仍需检查 SIF 业务字段：`code = "1"` 表示 SIF 业务成功；其他业务值依据 `msg` 解释，不能把网关正常直接等同于取得业务数据。
- 业务成功但 `total=0` 或 `data=[]` 时说明无返回记录，提示核对 ASIN、站点及所选周期或筛选条件，不凭空补充曝光指标，也不自动更换参数或翻页。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sif/asinSummary" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"searchValue":"B09V3KXJPB,B0BN1K7WJP","country":"US","last7d":false,"startDate":"2026-03-08","endDate":"2026-03-14","conditions":"ad","sortBy":"totalSpSocre","pageNum":1,"pageSize":10000,"desc":true}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sif-asin-summary",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```