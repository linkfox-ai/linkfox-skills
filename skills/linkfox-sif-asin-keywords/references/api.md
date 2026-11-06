# SIF ASIN 流量关键词 接口说明

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

## 接口：ASIN 流量关键词反查

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sif/asinKeywords`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | ASIN码，最大长度1000字符。一次只能查询一个ASIN；多 ASIN 对比需分别请求 |
| country | string | 否 | 国家站点，默认 `US`。可选值（共 13 个）：美国 `US`、英国 `UK`、德国 `DE`、加拿大 `CA`、日本 `JP`、法国 `FR`、西班牙 `ES`、意大利 `IT`、墨西哥 `MX`、澳大利亚 `AU`、阿联酋 `AE`、巴西 `BR`、沙特阿拉伯 `SA`。不支持 `IN`、`NL`、`SE`、`PL`、`TR`、`SG`，范围外代码会被 API 校验拒绝 |
| keyword | string | 否 | 关键词，最大长度1000。筛选包含该文本的关键词，尽量翻译成对应国家站点的语言 |
| timePieceType | string | 否 | 时间片段类型，默认 `latelyDay`。可选值：`latelyDay`（最近N天）、`month`（某月）、`week`（某周） |
| timePieceValue | string | 否 | 时间片段值，默认 `7`，最大长度1000。`latelyDay` 时仅支持 `7` 或 `30`，不支持任意 N 天；`month` 时为 `YYYY-MM`（如 `2026-04`）；`week` 时为周开始日期 `YYYY-MM-DD`（如 `2026-04-13`），周期结束日期可依据 `periodEndDate` 核对 |
| conditions | string | 否 | 条件筛选，多个以英文逗号隔开。可选值：<br>**标志类**：`nfPosition`（自然流量词）、`isSpAd`（SP广告词）、`isBrandAd`（品牌广告词）、`isVedioAd`（视频广告词）、`isAC`（AC推荐词）、`isAccurateKw`（精准流量词）、`isAccurateTailKw`（精准长尾词）、`isPurchaseKw`（出单词）、`isQualityKw`（转化优质词）、`isStableKw`（转化平稳词）、`isLossKw`（转化流失词）、`isInvalidKw`（无效曝光词）、`isMultiVariantKw`（多变体自然位词）、`isSearchVolUpKw`（搜索量同比增长词）、`isSearchVolDownKw`（搜索量同比下降词）<br>**周期计数类（`.total` 全量 / `.in` 新进）**：`totalPeriod.in`、`nfKeywordCnt.total`、`nfKeywordCnt.in`、`adKeywordCnt.total`、`adKeywordCnt.in`、`allSpKeywordCnt.total`、`allSpKeywordCnt.in`、`spKeywordCnt.total`、`spKeywordCnt.in`、`recSpKeywordCnt.total`、`recSpKeywordCnt.in`、`allSbKeywordCnt.total`、`allSbKeywordCnt.in`、`sbKeywordCnt.total`、`sbKeywordCnt.in`、`sbvKeywordCnt.total`、`sbvKeywordCnt.in` |
| sortBy | string | 否 | 排序字段。可选值：`lastRank`（自然排名）、`adLastRank`（广告排名）、`updateTime`（关键词抓取时间）、`searchesRank`（搜索排名）、`estSearchesNum`（月搜索量）。空字符串为默认系统排序 |
| desc | boolean | 否 | 是否降序，默认 `true`；升序使用 `false`。最佳自然排名使用 `sortBy=lastRank` 升序，最佳广告排名使用 `adLastRank` 升序，高搜索量使用 `estSearchesNum` 降序 |
| pageNum | integer | 否 | 页码，默认 `1` |
| pageSize | integer | 否 | 每页数量，最小10，最大100，默认 `100` |

#### 周期计数筛选的含义

| 条件 | 说明 |
|------|------|
| totalPeriod.in | 本周期新进入的流量词。 |
| nfKeywordCnt.total / nfKeywordCnt.in | 本周期有自然曝光的全部词 / 新进词。 |
| adKeywordCnt.total / adKeywordCnt.in | 本周期有广告曝光的全部词 / 新进词。 |
| allSpKeywordCnt.total / allSpKeywordCnt.in | SP 全部广告词 / 新进词，包含常规与推荐位。 |
| spKeywordCnt.total / spKeywordCnt.in | SP 常规广告词 / 新进词。 |
| recSpKeywordCnt.total / recSpKeywordCnt.in | SP 推荐位广告词 / 新进词。 |
| allSbKeywordCnt.total / allSbKeywordCnt.in | SB 全部广告词 / 新进词。 |
| sbKeywordCnt.total / sbKeywordCnt.in | SB 常规广告词 / 新进词。 |
| sbvKeywordCnt.total / sbvKeywordCnt.in | SBV 视频广告词 / 新进词。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON object | 是 | 作为首个位置参数传入，字段保持原样。 |
| --inline | CLI flag | 否 | 强制完整打印；仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过缓存读取与写入；默认使用 24 小时缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 覆盖网关地址，去掉尾部 `/`；默认地址见公共规则。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是 | 依次读取主变量与兼容变量，均未配置时退出并按认证引导处理。 |
| SESSION_ID | 环境变量 | 否 | 已设置时用于聚合本地会话数据，并将环境变量原值透传到请求头；未设置时仅为本地落盘生成会话标识，请求头值为空。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 透传到对应请求头。 |

响应缓存使用 `scripts/call_api.py` 实现。缓存位置为 `<cwd>/linkfox/.cache/linkfox-sif-asin-keywords/`，键为请求参数经 `json.dumps(ensure_ascii=False, sort_keys=True)` 序列化后 SHA-256 的前 16 位，缓存有效期按文件修改时间计算为 24 小时；命中时带有 `_cache.hit=true` 标记。过期或损坏缓存会重新请求。失败或空响应也会缓存；需要新结果时显式使用 `--no-cache`。

业务入口在请求前检查当前工作目录可写，并将完整响应限定在该目录的 `linkfox/` 下，禁止使用 `/tmp` 作为数据目录，不回退到家目录或临时目录。完整响应以 UTF-8 保存，同时维护会话 `_meta.json` 与 `index.jsonl`；输出策略见 SKILL.md。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态码，按公共响应码基本规则判断；认证失败时可返回 401。 |
| errmsg | string | 网关消息或错误原因。 |
| code | string | SIF 业务返回码，`"1"` 表示成功 |
| msg | string | 消息 |
| total | integer | 本次实际返回的数据数量 |
| data | array | 返回数据数组（详见下方） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| title | string | 标题 |
| isParentAsin | boolean | 是否是父体（pasin） |
| hasVaiants | boolean | 是否有变体 |
| abaCreateDateWeek | string | 最新周 ABA 数据对应的周时间 |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗token |

#### data 数组元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| keyword | string | 关键词 |
| translateKeyword | string | 关键词翻译，站点本地化译文 |
| asin | string | 商品ASIN |
| productNaturalRank | integer | 商品自然搜索排名。该商品在此关键词下的自然搜索结果中的位置排名，如1表示排在搜索结果第1位（首位） |
| naturalRankDisplay | string | 自然排名显示文本。自然搜索排名的字符串表示形式 |
| productAdRank | integer | 商品SP广告排名。该商品在此关键词下的Sponsored Products广告位中的排名位置，如3表示排在广告位第3位 |
| adRankDisplay | string | 广告排名显示文本。SP广告排名的字符串表示形式 |
| weeklySearchVolume | integer | 周搜索量。该关键词在亚马逊平台每周的预估搜索次数 |
| keywordPopularityRank | integer | 关键词搜索热度排名。该关键词的月搜索量在亚马逊所有关键词中的排名，数值越小表示搜索量越大 |
| totalSearchResultProductCount | integer | 该关键词下搜索结果商品总数（在售产品数） |
| trafficShare | number | 流量占比。该关键词为商品带来的流量占所有关键词总流量的比例，其中1表示100% |
| naturalTrafficShare | number | 自然流量得分占比。自然搜索流量得分 / 总得分 |
| paidTrafficShare | number | 付费广告流量得分占比。广告流量得分 / 总得分，按接口返回值展示；SB 得分已定义为包含视频，不将 `brandAdScore` 与 `videoAdScore` 重复相加来重算占比 |
| naturalTrafficScore | number | 自然流量得分。该关键词为该 ASIN 带来的自然搜索曝光得分，0 = 无自然流量曝光 |
| sponsoredProductsScore | number | SP 广告常规得分。Sponsored Products 常规位的流量得分（不含 SP 推荐位） |
| brandAdScore | number | SB 品牌广告得分。Sponsored Brands 品牌广告的流量得分（常规 + 视频，总和） |
| videoAdScore | number | SBV 视频广告得分。Sponsored Brands Video 视频广告的流量得分 |
| sponsoredRecommendationScore | number | SP 推荐位得分。Trending now / Seen on social media / Customers frequently viewed / 4 stars and above 等合计得分 |
| sponsoredRecommendationBreakdown | array | SP 推荐位得分明细。每项 `{title, score, scoreRatio}` |
| clickConcentrationShare | number | ABA TOP3 点击集中度。衡量点击是否集中在头部 ASIN；注意**不是转化率** |
| clickToPurchaseConversionRate | number | 点击到购买的转化率（purchaseQty / clickQty） |
| displayPositionTypes | array | 商品展示位置类型数组。可能包含以下值：natural=自然搜索结果位；ac=Amazon's Choice推荐位；sp=Sponsored Products赞助商品广告位；top=页面顶部品牌广告位；bottom=页面底部品牌广告位；er=Editorial Recommendations编辑推荐位；vedio=视频广告位；tr=Top Rated高评分推荐位；trfob=Top Rated Frequently Bought高频购买推荐位 |
| trafficCharacteristicMarkers | array | 关键词流量特征标记数组。可能包含以下值：isMainKw=主要流量词；isAccurateKw=精准流量词；isAccurateAboveKw=精准大词；isAccurateTailKw=精准长尾词 |
| conversionPerformanceMarkers | array | 转化效果标记数组。可能包含以下值：isPurchaseKw=出单词；isQualityKw=转化优质词；isStableKw=转化平稳词；isLossKw=转化流失词；isInvalidKw=无效曝光词 |
| lastNaturalRankTime | string | 最近有效自然排名的时间 |
| lastAdRankTime | string | 最近有效SP广告排名的时间 |
| periodEndDate | string | 本周期（周粒度）结束日期 = 开始周 + 7 天（站点时间） |
| updateTime | string | 关键词数据更新时间 |

#### sponsoredRecommendationBreakdown 数组元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| title | string | SP 推荐位名称，例如 Trending now、Seen on social media、Customers frequently viewed、4 stars and above。 |
| score | number | 该推荐位曝光得分。 |
| scoreRatio | number | 该推荐位得分占比；例如 0.57 表示 57%。 |

搜索结果商品总数包含自然、广告和推荐位商品；展示位置 `vedio`、变体标记 `hasVaiants` 等保持 API 字段拼写。未返回的字段不补造数值。

现有字段说明未给出广告明细的去重方式与总得分的完整计算公式；得分明细分项展示，付费占比使用 `paidTrafficShare`，不从明细自行推算。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 公共响应正常后，SIF 业务 `code="1"` 表示成功；其他明确返回的业务码按 `msg` 解释失败原因，不能把网关成功等同于业务成功。
- `total` 为本次实际返回的数据数量；空 `data` 表示没有匹配记录，不凭此判断服务异常或推断全量记录数。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sif/asinKeywords" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"asin":"B0XXXXXXXX","country":"US","keyword":"charger","conditions":"nfPosition,isPurchaseKw","sortBy":"lastRank","desc":false,"pageNum":1,"pageSize":50}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sif-asin-keywords",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```