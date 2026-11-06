# 卖家精灵流量词反查 接口说明

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

## 接口：流量词反查

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sellersprite/traffic/keyword`

### 请求参数

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| marketplace | string | 是 | 见下表 | 市场站点，默认 `US` |
| asin | string | 是 | maxLength 1000 | 要反查的商品 ASIN |
| month | string | 否 | 正则 `^(19\|20)\d{2}(0[1-9]\|1[0-2])$` | 历史月份，格式 `yyyyMM`；不传默认最近 30 天 |
| page | integer | 否 | 默认 1 | 当前页 |
| size | integer | 否 | 默认 50，最小 1，最大 100；最多查 2000 条 | 每页条数 |
| keyword | string | 否 | maxLength 1000 | 关键词筛选 |
| badges | string | 否 | maxLength 1000，多值英文逗号分隔 | 流量词类型（曝光位置），见 [badges 枚举](#badges-枚举) |
| trafficKeywordTypes | string | 否 | maxLength 1000，多值英文逗号分隔 | 流量占比类型，见 [trafficKeywordTypes 枚举](#traffickeywordtypes-枚举) |
| conversionKeywordTypes | string | 否 | maxLength 1000，多值英文逗号分隔 | 流量转化类型，见 [conversionKeywordTypes 枚举](#conversionkeywordtypes-枚举) |
| orderField | string | 否 | maxLength 1000，默认 `rankPosition` | 排序字段，见 [orderField 可选值](#orderfield-可选值) |
| orderDesc | boolean | 否 | 默认 `false` | 排序是否倒序 |

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

#### badges 枚举

| 取值 | 含义 |
|------|------|
| naturalSearching | 自然搜索词 |
| amazonChoice | AC 推荐词 |
| editorialRecommendations | ER 推荐词 |
| fourStar | 四星推荐词 |
| highlyRated | HR 推荐词 |
| sponsorBrand | 品牌推荐词 |
| sponsorVideo | 视频推荐词 |
| ads | SP 广告词 |

#### trafficKeywordTypes 枚举

| 取值 | 含义 |
|------|------|
| primary | 主要流量词 |
| precise | 精准流量词 |
| preciseLongTail | 转化流失词 |

#### conversionKeywordTypes 枚举

| 取值 | 含义 |
|------|------|
| excellent | 转化优质词 |
| stable | 转化平稳词 |
| lost | 转化流失词 |
| invalid | 无效曝光词 |

#### orderField 可选值

| 取值 | 含义 |
|------|------|
| rankPosition | 自然排名（默认） |
| adPosition | 广告排名 |
| createdTime | 创建时间 |
| searchesRank | 搜索量周排名 |
| searches | 月搜索量 |
| purchases | 月购买量 |
| purchaseRate | 购买率 |
| products | 商品数 |
| supplyDemandRatio | 供需比 |
| latest1daysAds | 广告竞品数 |
| bid | PPC 竞价 |
| trafficPercentage | 流量占比 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 作为脚本第一个位置参数传入，字段与上方接口请求参数一致。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本次不读取或写入响应缓存；不改变已有缓存。默认启用 24 小时缓存。 |

脚本在 `<cwd>/linkfox/.cache/linkfox-sellersprite-traffic-keyword/` 下缓存响应，文件名为 `linkfox-sellersprite-traffic-keyword-<hash>.json`；`<hash>` 是参数 JSON（按键排序、保留中文）的 SHA-256 前 16 位，按文件修改时间判定 24 小时有效期。仅使用公共调用器这一层缓存；参数键顺序不同仍可命中同一缓存，命中的对象响应添加 `_cache.hit=true`，每次仍尝试保存完整响应。错误或空结果也会被缓存，不自动重试。

认证兼容 `LINKFOX_AGENT_API_KEY` 优先、`LINKFOXAGENT_API_KEY` 回退；网关支持 `LINKFOX_TOOL_GATEWAY`，未配置使用公共规则中的默认地址。请求透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 环境变量作为同名请求头。

运行前确认任务工作目录可写，不使用 `/tmp`；设置 `ACPX_WORKSPACES` 时也需确认其第一个目录可写且为任务输出目录。公共调用器依次尝试 `ACPX_WORKSPACES` 的第一个目录、当前目录、家目录和系统临时目录下的 `linkfox/`，使用首个可写位置，选定结果在进程内固定。任务应通过可写目录配置避免回退到系统临时目录。会话优先使用 `SESSION_ID`，未配置时自动生成，进程内稳定；维护会话 `_meta.json` 与 `linkfox/` 根目录的 `index.jsonl`。响应文件成功写入时，标准输出报告实际保存路径，以该路径读取数据；响应文件写入失败时，标准错误输出失败信息，随后仍打印响应或摘要，此时不能视为已成功落盘。输出分流按格式化 JSON 的 UTF-8 字节数判断，阈值为 8000 字节；`--inline` 强制全量打印。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总条数 |
| marketplace | string | 市场编码 |
| asin | string | 查询的 ASIN |
| data | array | 流量词列表（对应第三方 `data.items`） |
| summaryList | array | 高频词总结列表 |
| columns | array | 列定义 |
| costToken | integer | 消耗 token |
| type | string | 渲染的样式 |

#### summaryList 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总次数 |
| keywords | string | 词 |

#### data[] 元素（单条流量词）

| 字段 | 类型 | 说明 |
|------|------|------|
| keyword | string | 关键词 |
| keywordCn | string | 关键词中文翻译 |
| trafficKeywordType | string | 流量占比类型 |
| conversionKeywordType | string | 流量转化类型 |
| badges | array | 曝光位置（流量词类型） |
| rankPosition | object | 自然排名位次信息，结构见 [排名对象](#排名对象-rankposition--adposition) |
| adPosition | object | 广告排名位次信息，结构同 [排名对象](#排名对象-rankposition--adposition) |
| searches | integer | 月搜索量 |
| searchesRank | integer | 周搜索量排名 |
| searchesRankTimeFrom | integer | 周搜索量排名时间范围起 |
| searchesRankTimeTo | integer | 周搜索量排名时间范围止 |
| purchases | integer | 月购买量 |
| purchaseRate | number | 购买率 |
| products | integer | 商品数 |
| supplyDemandRatio | number | 供需比 |
| trafficPercentage | number | 流量占比 |
| naturalRatio | number | 流量分布-自然占比 |
| adRatio | number | 流量分布-广告占比 |
| calculatedWeeklySearches | number | 预估周曝光量 |
| impressions | integer | 展示量 |
| clicks | integer | 点击量 |
| bid | number | PPC 竞价 |
| bidMin | number | PPC 竞价下限 |
| bidMax | number | PPC 竞价上限 |
| latest1daysAds | integer | 最近 1 天广告竞品数 |
| latest7daysAds | integer | 最近 7 天广告竞品数 |
| latest30daysAds | integer | 最近 30 天广告竞品数 |
| spr | integer | SPR（SellerSprite Product Rank），关键词维持首页所需的 8 天预估销量 |
| sprt | number | 兼容历史字段；卖家精灵当前官方 v1 文档未定义，勿与 `spr` 混用 |
| monopolyClickRate | number | 垄断点击率 |
| top3ClickingRate | number | Top3 点击率 |
| top3ConversionRate | number | Top3 转化率 |
| titleDensity | number | 标题密度 |
| stats | array | 高频词，元素见下表 |
| updatedTime | integer | 更新时间 |

#### stats[] 元素（高频词子项）

| 字段 | 类型 | 说明 |
|------|------|------|
| keywords | string | 词 |
| total | integer | 总条数 |
| rankPosition | object | 自然排名位次，结构见下 |
| adPosition | object | 广告排名位次，结构见下 |

#### 排名对象 rankPosition / adPosition

| 字段 | 类型 | 说明 |
|------|------|------|
| updatedTime | integer | 排名时间 |
| pageSize | integer | 每页多少条数据 |
| index | integer | 当前页排第几 |
| page | integer | 第几页 |
| position | integer | 总结果中排第几 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 脚本本地诊断字段

- `_http_status` 是业务脚本记录的实际 HTTP 状态码，不是网关业务字段；响应体中的 `errcode`、`errmsg` 和其他字段保持原值。结合此状态码与公共规则判断结果，HTTP `401` / `402` 按认证和算力指引处理，HTTP `403` 不归入这两类。
- 非 JSON 响应以 `error`、`details` 保留原因与响应文本；JSON 非对象响应保存在 `_response_body`。连接失败只有 `error`，没有可用的 HTTP 状态码，不能当作成功响应。
- `_http_status` 随响应缓存和落盘，命中缓存时表示生成该缓存时的状态，不代表本次发起了请求。已有缓存若没有该字段，不能据此推断 HTTP 成功，也不为补充状态自动重试；继续查询仍遵守成本约束。大响应摘要也显示已记录的 HTTP 状态码。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sellersprite/traffic/keyword" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "Content-Type: application/json" \
  -d '{
    "marketplace": "US",
    "asin": "B0XXXXXXXXX",
    "page": 1,
    "size": 50
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sellersprite-traffic-keyword",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```