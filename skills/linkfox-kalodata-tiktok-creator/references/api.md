# Kalodata TikTok 达人榜单与详情 接口说明

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

## 接口：达人榜单

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/kalodata/creator/rank`

### 请求参数

POST Body（JSON），所有参数均可选：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 否 | 地区/市场编码，例如 `US` |
| dateRange | string | 否 | 时间范围，例如 `last7Day`、`last30Day` |
| pageNumber | integer | 否 | 页码，取值 1-5 |
| pageSize | integer | 否 | 每页数量，取值 5-100 |
| language | string | 否 | 返回语言，例如 `zh-CN`、`en-US` |
| currency | string | 否 | 货币单位，例如 `USD` |
| category_ids | array<integer> | 否 | 类目 ID 列表筛选 |
| shop_id | string | 否 | 店铺 ID 筛选 |
| revenue_range | string | 否 | 成交金额 / GMV 范围筛选 |
| creator_type | string | 否 | 达人类型筛选 |
| followers_range | string | 否 | 粉丝数范围筛选 |
| engagement_rate | string | 否 | 互动率筛选 |
| sortField | object | 否 | 排序条件；不排序时传空对象 `{}` 走默认榜单顺序 |

> 默认按 `revenue`（GMV）降序排列。可用排序字段以网关实际接受的为准；若传入不支持的排序字段，回退默认排序，不要尝试其它绕过逻辑。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | JSON object | 是 | 首个位置参数为请求体 JSON；字段见本接口参数表。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用业务脚本的 24 小时缓存，强制重新请求，不读取也不写入该缓存。 |

业务封装提供单层 24 小时本地缓存；调用公共 `call_api.run` 时固定加入 `--no-cache`，避免重复缓存。缓存位于 `<cwd>/linkfox/.cache/linkfox-kalodata-tiktok-creator/`，按接口路径和规范化参数生成键，隔离榜单与详情。缓存文件以版本化封装保存原始 HTTP 状态和响应体；不符合缓存封装版本、缺少 HTTP 状态、过期或损坏的缓存不复用，命中时标记 `_cache.hit`。错误响应也会缓存；需要重试时使用业务 CLI 的 `--no-cache`，避免再次命中已缓存的结果。

响应始终保存到当前工作目录的会话数据路径；禁止回退到 `/tmp`、家目录或其他工作区，请求前检查实际会话数据目录是否可写，不可写时报错。保持 `SESSION_ID` 聚合与会话 `_meta.json`、`index.jsonl` 索引。小响应全量输出、大响应摘要及 `--inline` 行为见 SKILL.md。

#### 使用限制

- 榜单不是关键词搜索，只按市场、时间及支持的条件浏览排行榜。
- 需要分页时，在已明确的任务范围与消耗预期内继续请求，直到返回条数少于 `pageSize` 或达到第 5 页；没有 `total` 或总页数，不能推算完整总量。失败或空结果不得自动翻页或更改筛选连续试探。
- 数据可能存在 T+1 统计延迟，展示和比较时保持请求窗口与币种一致。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 达人榜单数据 |
| costToken | integer | 本次调用扣费 token，通常为 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

#### data 数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| creator_nickname | string | 达人昵称 |
| creator_handle | string | TikTok 主页名，例如 `@based` |
| creator_id | string | 达人唯一 ID，字符串格式以避免大整数精度丢失 |
| creator_followers | string | 粉丝数，以字符串返回 |
| content_views | string | 内容总观看数，以字符串返回 |
| sales_volumn | integer | 销量，字段拼写为 `volumn` |
| revenue | number | 总销售额 / GMV，按请求的 `currency` 返回 |
| video_revenue | number | 短视频带货销售额 |
| live_revenue | number | 直播带货销售额 |
| revenue_growth_rate | number | 销售额增长率（%），可正可负 |

> `outputSchema` 可能声明 `total` 字段，但真实响应不包含 `total`，也没有总页数等分页元数据；分页停止条件见本接口使用限制。

#### 脚本输出补充

| 字段 / 输出 | 类型 | 说明 |
|---|---|---|
| _cache.hit | boolean | 缓存命中时为 true；其余业务字段保持响应值。 |
| _cache.raw | any | 仅当响应自带的 `_cache` 不是对象时保留其原值，避免输出器误用该字段。 |
| error / rawResponse | string / any | 仅当响应 JSON 不是对象时，用 error 说明结构异常，rawResponse 完整保留原值，不补造达人数据。 |
| stderr HTTP 状态码 | integer / 无 | 本次请求或已缓存请求的原始 HTTP 状态；连接失败时为无，不用 errcode 代替 HTTP 状态。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode:501` 可能表示上游调用失败或参数无效；若 `errmsg` 包含 Kalodata HTTP 554，可在说明额外消耗后用相同参数重试 1–2 次，不自动更换参数，也不无限重试。脚本不自动重试；经用户决定重试时须加 `--no-cache`。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/kalodata/creator/rank" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "US",
    "dateRange": "last7Day",
    "pageSize": 10,
    "pageNumber": 1,
    "currency": "USD"
  }'
```

### 响应示例

```json
{
  "errcode": 200,
  "data": [
    {
      "revenue_growth_rate": 1.36,
      "revenue": 389817.79,
      "video_revenue": 238900.7,
      "sales_volumn": 14781,
      "content_views": "79192665",
      "creator_followers": "3700000",
      "creator_id": "7153432386608251946",
      "creator_handle": "@based",
      "creator_nickname": "BASED",
      "live_revenue": 150857.09
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

## 接口：达人详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/kalodata/creator/detail`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| creatorId | string | 是 | 达人唯一 ID，例如 `7153432386608251946`，可从达人榜单响应的 `creator_id` 获取 |
| shop_id | string | 否 | 店铺 ID 筛选 |
| category_ids | array<integer> | 否 | 类目 ID 列表筛选 |
| region | string | 否 | 地区/市场编码，例如 `US` |
| dateRange | string | 否 | 时间范围，例如 `last7Day`、`last30Day` |
| language | string | 否 | 返回语言，例如 `zh-CN`、`en-US` |
| currency | string | 否 | 货币单位，例如 `USD` |

> `creatorId` 为必填。本接口不支持按关键词/昵称搜索达人；需先用达人榜单接口发现达人并获取 `creator_id`，再用 `creatorId` 查询详情。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | JSON object | 是 | 首个位置参数为请求体 JSON；字段见本接口参数表。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用业务脚本的 24 小时缓存，强制重新请求，不读取也不写入该缓存。 |

业务封装提供单层 24 小时本地缓存；调用公共 `call_api.run` 时固定加入 `--no-cache`，避免重复缓存。缓存位于 `<cwd>/linkfox/.cache/linkfox-kalodata-tiktok-creator/`，按接口路径和规范化参数生成键，隔离榜单与详情。缓存文件以版本化封装保存原始 HTTP 状态和响应体；不符合缓存封装版本、缺少 HTTP 状态、过期或损坏的缓存不复用，命中时标记 `_cache.hit`。错误响应也会缓存；需要重试时使用业务 CLI 的 `--no-cache`，避免再次命中已缓存的结果。

响应始终保存到当前工作目录的会话数据路径；禁止回退到 `/tmp`、家目录或其他工作区，请求前检查实际会话数据目录是否可写，不可写时报错。保持 `SESSION_ID` 聚合与会话 `_meta.json`、`index.jsonl` 索引。小响应全量输出、大响应摘要及 `--inline` 行为见 SKILL.md。

#### 使用限制

- 单次查询一个 `creatorId`；不能只用昵称或 handle 定位达人，也不支持关键词搜索。
- 数据可能存在 T+1 统计延迟，展示和比较时保持请求窗口与币种一致。

### 响应结构

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 单个达人的详情数据，固定为 1 元素数组（有效编号通常返回一条） |
| costToken | integer | 本次调用扣费 token，通常为 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

#### data 数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| creator_id | string | 达人唯一 ID |
| creator_nickname | string | 达人昵称 |
| creator_handle | string | 达人 handle |
| creator_region | string | 达人地区 |
| creator_status | string | 达人状态 |
| creator_bio | string | 达人简介 |
| creator_belonged_shop_id | string | 所属店铺 ID |
| creator_followers | string | 粉丝总数，以字符串返回 |
| new_followers | integer | `dateRange` 窗口内新增粉丝 |
| revenue | number | 总销售额 / GMV |
| video_revenue | number | 视频销售额 |
| live_revenue | number | 直播销售额 |
| sales_volumn | integer | 销量，字段拼写为 `volumn` |
| unit_price | number | 件单价 |
| video_number | integer | 窗口内视频数 |
| video_views | integer | 视频总播放量 |
| video_gpm | number | 视频 GPM |
| live_number | integer | 窗口内直播数 |
| live_views | integer | 直播总观看量 |
| live_gpm | number | 直播 GPM |
| product_number | integer | 关联商品数 |
| shop_number | integer | 关联店铺数 |
| creator_contact_email | string | 联系邮箱 |
| creator_contact_ins | string | Instagram 联系方式 |
| creator_contact_whatsapp | string | WhatsApp 联系方式 |
| creator_contact_facebook | string | Facebook 联系方式 |
| creator_contact_tiktok | string | TikTok 联系方式 |
| creator_contact_zalo | string | Zalo 联系方式 |
| creator_contact_line | string | Line 联系方式 |

> `data` 对于有效 `creatorId` 通常为 1 元素数组。详情响应不包含 `total` 字段。

#### 脚本输出补充

| 字段 / 输出 | 类型 | 说明 |
|---|---|---|
| _cache.hit | boolean | 缓存命中时为 true；其余业务字段保持响应值。 |
| _cache.raw | any | 仅当响应自带的 `_cache` 不是对象时保留其原值，避免输出器误用该字段。 |
| error / rawResponse | string / any | 仅当响应 JSON 不是对象时，用 error 说明结构异常，rawResponse 完整保留原值，不补造达人数据。 |
| stderr HTTP 状态码 | integer / 无 | 本次请求或已缓存请求的原始 HTTP 状态；连接失败时为无，不用 errcode 代替 HTTP 状态。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode:501` 可能表示上游调用失败或参数无效；若 `errmsg` 包含 Kalodata HTTP 554，可在说明额外消耗后用相同参数重试 1–2 次，不自动更换参数，也不无限重试。脚本不自动重试；经用户决定重试时须加 `--no-cache`。
- 若错误源于 `creatorId` 缺失或无效，核对编号是否来自榜单响应的 `creator_id`，不要用昵称代替。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/kalodata/creator/detail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "creatorId": "7153432386608251946",
    "region": "US",
    "dateRange": "last7Day",
    "currency": "USD"
  }'
```

### 响应示例

```json
{
  "errcode": 200,
  "data": [
    {
      "creator_contact_line": "",
      "video_revenue": 238900.7,
      "sales_volumn": 14781,
      "video_number": 222,
      "creator_contact_email": "",
      "product_number": 51,
      "creator_bio": "based.com/tt",
      "revenue": 389817.79,
      "live_gpm": 29.32,
      "video_views": 74047861,
      "video_gpm": 3.23,
      "creator_handle": "@based",
      "creator_nickname": "BASED",
      "live_views": 5144804,
      "creator_followers": "3700000",
      "creator_region": "us",
      "unit_price": 26.37,
      "new_followers": 100000,
      "creator_belonged_shop_id": "7495079418085345590",
      "creator_status": "BELONGED_TO_SELLER",
      "creator_contact_tiktok": "based",
      "creator_id": "7153432386608251946",
      "shop_number": 1,
      "live_number": 2,
      "live_revenue": 150857.09
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-kalodata-tiktok-creator",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
