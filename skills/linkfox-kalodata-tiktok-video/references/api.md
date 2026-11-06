# Kalodata TikTok 视频榜单与详情 接口说明

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

## 接口：视频榜单

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/kalodata/video/rank`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 否 | 地区/市场编码，例如 `US` |
| dateRange | string | 否 | 时间范围，例如 `last7Day`、`last30Day` |
| pageNumber | integer | 否 | 页码，取值 1-5 |
| pageSize | integer | 否 | 每页数量，取值 5-100 |
| language | string | 否 | 返回语言，例如 `zh-CN`、`en-US` |
| currency | string | 否 | 货币单位，例如 `USD` |
| category_id | string | 否 | 类目 ID 筛选 |
| shop_id | string | 否 | 店铺 ID 筛选 |
| creator_id | string | 否 | 达人 ID 筛选 |
| product_id | string | 否 | 商品 ID 筛选 |
| revenue_range | string | 否 | GMV 范围；响应中的 `revenue` 即 GMV，例如 `1-100`、`>1000`、`<100` |
| followers_range | string | 否 | 达人粉丝数范围筛选 |
| ads_roas | number | 否 | 广告 ROAS 筛选 |
| sortField | object | 否 | GMV 排序条件，例如 `{"field":"revenue","type":"DESC"}` |

#### sortField 嵌套字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sortField.field | string | 未明确约定 | GMV 排序字段，示例为 `revenue`；不推断其他支持字段。 |
| sortField.type | string | 未明确约定 | 排序方向，示例为 `DESC`；完整枚举未明确，不推断其他取值。 |

榜单仅浏览带货视频排行，不支持关键词搜索；`revenue_range` 按 GMV 过滤。响应不含 `total` 或总页数，本次结果数为 `data.length`；用户需要继续且已说明成本时，可查看下一页，直到本页条数少于 `pageSize` 或达到第 5 页。失败或空结果不得自动翻页或改条件试探。

#### 脚本选项与运行约定

| 选项 / 约定 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | JSON object | 是 | 第一个位置参数；字段见上表，未约定服务端默认值时不自行补造。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过读取和保存响应缓存；缓存目录仍可被创建。 |
| 24 小时缓存 | 本地行为 | 默认启用 | 仅由公共调用器维护一层缓存；按接口标识与规范化 JSON 参数隔离榜单和详情，成功缓存命中时带 `_cache.hit=true`。 |
| 缓存目录 | path | 自动 | `<cwd>/linkfox/.cache/linkfox-kalodata-tiktok-video-<接口标识>/`；缓存按接口隔离，使用包含 HTTP 状态的格式，不读取缺少 HTTP 状态且无法区分接口的缓存格式。 |
| 会话目录 | path | 自动 | 固定使用当前工作目录的 `linkfox/`，以 `SESSION_ID` 聚合会话；不采用 `ACPX_WORKSPACES`、家目录或临时目录回退，目录不可写时在请求前报错。 |

缓存有效期为 24 小时；公共调用器仅缓存 HTTP 200 且 `errcode` 符合其正常响应缓存条件的对象，错误不缓存。完整输出、8 KB 阈值、摘要、会话元数据及 `--inline` 由公共调用器完成。网关读取 `LINKFOX_TOOL_GATEWAY`，缺省为公共规则的地址；认证优先 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`，并透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。脚本不自动重试。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码；成功示例为 200，判断遵循公共规则 |
| data | array | 视频榜单数据；元素字段见下表 |
| costToken | integer | 本次调用扣费 token，通常为 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

#### data[*] 视频字段

| 字段 | 类型 | 说明 |
|------|------|------|
| video_id | string | 视频 ID，字符串格式以避免大整数精度丢失 |
| video_title | string | 视频标题 / 文案 |
| views | integer | 播放量 |
| digg_count | integer | 点赞数 |
| comment_count | integer | 评论数 |
| share_count | integer | 分享数 |
| revenue | number | 总销售额 / GMV，按请求的 `currency` 返回 |
| revenue_growth_rate | number | 销售额增长率（%），可正可负 |
| ad | integer | 是否广告/带货视频标识（1=是） |
| ad_view_ratio | number | 广告播放占比（%） |
| ad_revenue_ratio | number | 广告带来的销售额占比（%） |
| ads_roas | number | 广告 ROAS |
| belonged_creator_id | string | 所属达人 ID |
| belonged_creator_handle | string | 所属达人用户名 |
| creator_debut | string | 达人入驻日期（`YYYY-MM-DD`） |

榜单返回 `data` 数组，不含总量及总页数元数据。`creator_debut` 按实际响应展示，示例中未返回时不补造。金额按请求 `currency` 返回，数据可能有 T+1 统计延迟。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

脚本遇到非 2xx HTTP 响应时，在标准错误输出实际 HTTP 状态码；保存的 JSON 仍为响应正文，不新增业务字段。目录预检失败与接口调用或响应处理失败分别报告，并保留 `OSError` 的异常类型和原因。

- `errcode=501` 表示上游调用失败或参数无效；若 `errmsg` 含 Kalodata HTTP 554，可用相同参数重试 1–2 次。重试前说明额外消耗，不自动换参数连续试探；脚本不自动重试。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/kalodata/video/rank" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"region":"US","dateRange":"last7Day","revenue_range":"1-100","sortField":{"field":"revenue","type":"DESC"},"pageSize":10,"pageNumber":1,"currency":"USD"}'
```

### 响应示例

```json
{
  "errcode": 200,
  "data": [
    {
      "video_id": "7659161409279806734",
      "video_title": "Ashley always getting me into trouble...",
      "views": 8935253,
      "digg_count": 183512,
      "comment_count": 2668,
      "share_count": 29847,
      "revenue": 180245.0,
      "revenue_growth_rate": 0,
      "ad": 1,
      "ad_view_ratio": 6.494768530896663,
      "ad_revenue_ratio": 0,
      "ads_roas": 4.24,
      "belonged_creator_id": "7565796510165943309",
      "belonged_creator_handle": "kimkrecs"
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

## 接口：视频详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/kalodata/video/detail`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| videoId | string | 是 | TikTok 视频 ID，例如 `7659161409279806734`，可从视频榜单响应的 `video_id` 获取 |
| region | string | 否 | 地区/市场编码，例如 `US` |
| dateRange | string | 否 | 时间范围，例如 `last7Day`、`last30Day` |
| language | string | 否 | 返回语言，例如 `zh-CN`、`en-US` |
| currency | string | 否 | 货币单位，例如 `USD` |

`videoId` 为必填字符串，可来自榜单 `video_id` 或从用户提供的 TikTok 视频 URL 取出编号；脚本不会自动解析 URL。本接口一次查询一个视频，不能仅凭标题或关键词发现视频。

#### 脚本选项与运行约定

| 选项 / 约定 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | JSON object | 是 | 第一个位置参数；字段见上表，未约定服务端默认值时不自行补造。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过读取和保存响应缓存；缓存目录仍可被创建。 |
| 24 小时缓存 | 本地行为 | 默认启用 | 仅由公共调用器维护一层缓存；按接口标识与规范化 JSON 参数隔离榜单和详情，成功缓存命中时带 `_cache.hit=true`。 |
| 缓存目录 | path | 自动 | `<cwd>/linkfox/.cache/linkfox-kalodata-tiktok-video-<接口标识>/`；缓存按接口隔离，使用包含 HTTP 状态的格式，不读取缺少 HTTP 状态且无法区分接口的缓存格式。 |
| 会话目录 | path | 自动 | 固定使用当前工作目录的 `linkfox/`，以 `SESSION_ID` 聚合会话；不采用 `ACPX_WORKSPACES`、家目录或临时目录回退，目录不可写时在请求前报错。 |

缓存有效期为 24 小时；公共调用器仅缓存 HTTP 200 且 `errcode` 符合其正常响应缓存条件的对象，错误不缓存。完整输出、8 KB 阈值、摘要、会话元数据及 `--inline` 由公共调用器完成。网关读取 `LINKFOX_TOOL_GATEWAY`，缺省为公共规则的地址；认证优先 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`，并透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。脚本不自动重试。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码；成功示例为 200，判断遵循公共规则 |
| data | array | 单个视频详情数据；有效编号通常返回 1 个元素，字段见下表 |
| costToken | integer | 本次调用扣费 token，通常为 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

#### data[*] 视频字段

| 字段 | 类型 | 说明 |
|------|------|------|
| video_id | string | 视频 ID，字符串格式以避免大整数精度丢失 |
| video_title | string | 视频标题 / 文案 |
| video_region | string | 视频地区，可能为空字符串 |
| belonged_creator_id | string | 归属达人 ID |
| belonged_creator_handle | string | 归属达人用户名 |
| views | integer | 播放量 |
| digg_count | integer | 点赞数 |
| comment_count | integer | 评论数 |
| share_count | integer | 分享数 |
| revenue | number | 总销售额 / GMV |
| sales_volumn | integer | 销量，字段拼写为 `volumn` |
| video_gpm | number | 视频 GPM（每千次播放 GMV） |
| ad | integer | 是否投放广告（1=有广告，0=无广告） |
| ads_views | integer | 广告播放数 |
| ads_roas | number | 广告 ROAS |
| ad_cpa | number | 广告 CPA |
| ad_view_ratio | number | 广告播放占比（%） |
| ads_period | integer | 广告投放周期（天） |
| duration | number | 视频时长（秒） |
| product_number | integer | 视频关联商品数 |

有效 `videoId` 的 `data` 通常为 1 元素数组，不含 `total`。`video_region` 可能为空字符串；金额按请求 `currency` 返回，数据可能有 T+1 统计延迟。空数组按无数据解释，不补造视频信息。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

脚本遇到非 2xx HTTP 响应时，在标准错误输出实际 HTTP 状态码；保存的 JSON 仍为响应正文，不新增业务字段。目录预检失败与接口调用或响应处理失败分别报告，并保留 `OSError` 的异常类型和原因。

- `errcode=501` 表示上游调用失败或参数无效；若 `errmsg` 含 Kalodata HTTP 554，可用相同参数重试 1–2 次。重试前说明额外消耗，不自动换参数连续试探；脚本不自动重试。
- 若 501 与缺失或无效 `videoId` 有关，核对编号是否来自榜单结果或有效视频链接；不改用标题猜测查询。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/kalodata/video/detail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"videoId":"7659161409279806734","region":"US","dateRange":"last7Day","currency":"USD"}'
```

### 响应示例

```json
{
  "errcode": 200,
  "data": [
    {
      "comment_count": 2668,
      "video_region": "",
      "ads_views": 7901839,
      "ad": 1,
      "sales_volumn": 3835,
      "ad_cpa": 6.518341651222737,
      "ad_view_ratio": 6.494768530896663,
      "product_number": 1,
      "belonged_creator_id": "7565796510165943309",
      "ads_roas": 4.24,
      "share_count": 29847,
      "duration": 105.1,
      "belonged_creator_handle": "kimkrecs",
      "revenue": 180245.0,
      "video_title": "Ashley always getting me into trouble ...",
      "digg_count": 183512,
      "video_gpm": 20.17,
      "ads_period": 3,
      "views": 8935253,
      "video_id": "7659161409279806734"
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-kalodata-tiktok-video",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
