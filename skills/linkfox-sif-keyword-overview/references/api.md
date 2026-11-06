# SIF 关键词竞争概览 接口说明

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

## 接口：关键词竞争概览（keywordOverview）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sif/keywordOverview`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 关键词，尽量翻译成对应国家站点的语言。最大长度：1000 字符 |
| country | string | 否 | 国家站点，默认 `US`。可选值（共 13 个）：`US`、`UK`、`DE`、`CA`、`JP`、`FR`、`ES`、`IT`、`MX`、`AU`、`AE`、`BR`、`SA` |
| last7d | boolean | 否 | 是否取最近 7 天数据，默认 `true`。传 `false` 时使用 `startDate`/`endDate` 区间 |
| startDate | string | 否 | 开始日期 `yyyy-MM-dd`（`last7d=false` 时生效） |
| endDate | string | 否 | 结束日期 `yyyy-MM-dd`（与 `startDate` 配套） |


#### 参数约束与使用限制

- 每次请求只查询一个关键词；多关键词或多站点对比分别请求。
- 关键词应使用目标站点的当地语言；用户提供其他语言时，先翻译再查询，例如德国站使用德语、日本站使用日语。
- `country` 支持的 13 个站点分别为：美国（US）、英国（UK）、德国（DE）、加拿大（CA）、日本（JP）、法国（FR）、西班牙（ES）、意大利（IT）、墨西哥（MX）、澳大利亚（AU）、阿联酋（AE）、巴西（BR）、沙特阿拉伯（SA）。用户未指定时使用 `US`；列表外代码会被接口校验拒绝。`IN`、`NL`、`SE`、`PL`、`TR`、`SG` 不支持。
- 默认查询最近 7 天；自定义 ABA 周区间时同时传入 `last7d=false`、`startDate` 和 `endDate`。
- 接口通常每个关键词仅返回一条记录，`total` 通常为 1。关键词在目标站点未找到时会返回空结果。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 网关状态码；基础判断见公共规则，本接口以 `200` 表示网关调用成功 |
| errmsg | string | 网关错误消息，如 `authorized error`；异常时用于解释原因 |
| msg | string | 消息 |
| total | integer | 数据总量。注意：本接口通常只返回单条数据，total 通常为1 |
| code | string | SIF 业务返回码，`"1"` 表示成功 |
| data | array | 返回数据（详见下方数据字段） |
| costTime | integer | 耗时（ms） |
| costToken | integer | 消耗token |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| title | string | 标题 |

#### 数据字段（`data` 数组中的每个对象）

| 字段 | 类型 | 说明 |
|------|------|------|
| keyword | string | 关键词。搜索查询的关键词文本 |
| keywordPopularityRank | integer | 关键词热度排名。该关键词的月搜索量在亚马逊所有关键词中的排名，数值越小表示搜索量越大 |
| estimatedWeeklySearchVolume | integer | 周预估搜索量。该关键词在亚马逊上每周的预估搜索次数，反映该词的搜索热度 |
| supplyDemandRatio | number | 供需比率。供应与需求的比率，计算公式：搜索结果商品数 / 月搜索量，数值越小表示竞争越小、机会越大 |
| totalSearchResultProductCount | integer | 搜索结果商品总数。在该关键词下显示的所有商品总数（包括自然搜索、广告位、推荐位等） |
| naturalSearchProductCount | integer | 自然搜索商品数量。在该关键词的自然搜索结果中展示的商品数量（不包括广告位） |
| sponsoredProductsCount | integer | SP广告商品数量。在该关键词下投放Sponsored Products（赞助商品）广告的商品数量 |
| brandAdProductCount | integer | 品牌广告商品数量。在该关键词下投放品牌广告（Brand Ads）的商品数量 |
| videoAdProductCount | integer | 视频广告商品数量。在该关键词下投放视频广告（Video Ads）的商品数量 |
| paidAdvertisingProductCount | integer | PPC广告商品总数。在该关键词下所有PPC付费广告（包括SP、品牌广告、视频广告等）的商品总数 |
| amazonChoiceProductCount | integer | Amazon's Choice商品数量。在该关键词下获得Amazon's Choice推荐标志的商品数量 |
| topRatedProductCount | integer | Top Rated推荐商品数量。在该关键词下出现在Top Rated（高评分）推荐位的商品数量 |
| searchRecommendationProductCount | integer | 搜索推荐商品数量。在该关键词搜索时亚马逊推荐的商品数量 |
| editorialRecommendationsProductCount | integer | Editorial Recommendations商品数量。在该关键词下出现在编辑推荐位的商品数量 |
| recNonadProductCount | integer | 推荐位非广告商品数量。在该关键词下推荐位中属于非广告（自然）的商品数量 |
| recAdProductCount | integer | 推荐位广告商品数量。在该关键词下推荐位中属于广告的商品数量 |
| trackedAsinTotalCount | integer | SIF 跟踪的有曝光 ASIN 去重总数。该关键词下所有位置（自然/广告/推荐）中，SIF 系统追踪到有曝光得分的 ASIN 去重数量（上游字段：`totalAsinNum`） |
| totalMarketplaceKeywordCount | integer | 站点关键词总量。该站点所有关键词的总数量，用于了解市场整体规模 |
| dataPeriodStartDate | string | 数据周期起始日期。本次返回数据对应的 ABA 周起始日期（`yyyy-MM-dd`） |
| dataPeriodEndDate | string | 数据周期结束日期。本次返回数据对应的 ABA 周结束日期（`yyyy-MM-dd`） |
| keywordDataUpdateTime | string | 关键词数据更新时间 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关基础判断之外，还需检查 SIF 业务字段 `code`：`"1"` 表示业务成功，不应套用其他接口的 `code="200"` 约定；业务失败依据 `msg` 解释。
- 关键词在查询站点未找到会返回空结果；结合 `data` 与 `total` 判断，不将空结果解释为零竞争。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/sif/keywordOverview \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"keyword": "wireless charger", "country": "US"}'
```

## 脚本运行约定

入口为 `scripts/sif_keyword_overview.py`，使用同目录公共调用器处理请求、缓存、落盘和输出，只使用一层缓存。

| 选项或约定 | 类型 | 说明 |
|------------|------|------|
| JSON 参数 | string | 首个位置参数为请求 JSON，字段见上方请求参数表。缺少参数或 JSON 格式非法时退出码为 1。 |
| --inline | CLI flag | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 禁用 24 小时响应缓存，本次不读取也不写入缓存内容。 |
| 本地缓存 | 文件 | 默认保留 24 小时缓存，位置为 `<cwd>/linkfox/.cache/linkfox-sif-keyword-overview/`。键为参数 JSON 按键排序后计算 SHA-256 的前 16 位；参数相同且在有效期内复用，命中时附 `_cache.hit=true`。过期或损坏的缓存不复用。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 优先使用自定义网关，去掉结尾 `/`，未设置时使用公共规则中的地址。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 优先使用前者，兼容后者；两者均为空时退出码为 1，按认证指引处理。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 作为同名请求头转发；未配置时为空字符串。 |
| 输出目录 | 运行要求 | 按 SKILL.md 的输出策略在可写的当前项目目录运行，禁止将结果放入 `/tmp`。业务入口在请求前检查项目输出目录、会话数据目录和缓存目录可写，并在本次运行内将公共调用器的输出根目录固定为 `<cwd>/linkfox`，不受 `ACPX_WORKSPACES` 重定向，也不回退到家目录或临时目录；不可写时退出码为 1。 |
| 输出阈值 | integer | 输出阈值为 `8000` UTF-8 字节：不超过阈值全量输出，否则摘要列出顶层字段、常见计数及最大列表的前 3 条样本。 |

完整响应使用 UTF-8 保存，按日期和会话聚合，并登记会话 `_meta.json` 和 `linkfox/index.jsonl`。缓存位于当前工作目录，命中也会保存本次完整输出。公共调用器保留 HTTP JSON 错误体和非 JSON 错误详情，不自动重试关键词查询。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sif-keyword-overview",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```