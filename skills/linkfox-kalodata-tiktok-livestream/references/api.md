# Kalodata TikTok 直播榜单与详情 接口说明

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

## 接口：直播榜单

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/kalodata/livestream/rank`

### 请求参数

POST Body（JSON），所有参数均可选：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| region | string | 否 | 地区/市场编码，例如 `US`。最大长度 1000 |
| dateRange | string | 否 | 时间范围，例如 `last7Day`（近7天）、`last30Day`（近30天）。最大长度 1000 |
| pageNumber | integer | 否 | 页码，取值 1–5（超范围返回 `errcode 501`） |
| pageSize | integer | 否 | 每页数量，取值 5–100 |
| language | string | 否 | 返回语言，例如 `zh-CN`、`en-US`。最大长度 1000 |
| currency | string | 否 | 货币单位，例如 `USD`。最大长度 1000 |
| category_id | string | 否 | 类目 ID 筛选 |
| shop_id | string | 否 | 店铺 ID 筛选 |
| creator_id | string | 否 | 达人 ID 筛选 |
| product_id | string | 否 | 商品 ID 筛选 |
| followers_range | string | 否 | 达人粉丝数范围筛选 |
| sortField | object | 否 | 排序条件，结构由网关定义；不排序时传空对象 `{}` 走默认榜单顺序 |

> 该接口用于浏览直播榜单，不支持关键词搜索。`sortField` 在 `inputSchema` 中声明为对象（`properties` 为空）；默认按 `revenue`（GMV）降序排列，传入空对象 `{}` 走默认排序。可用的排序字段以网关实际接受的为准；若传入不被支持的排序字段，网关会返回业务错误，此时应回退为默认排序，不要尝试其它绕过逻辑。

省略可选参数时由网关按默认值处理；具体默认地区、币种和时间窗口未明确约定，不应自行假定。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 作为第一个位置参数传入上述请求对象；字段名和大小写保持原值。 |
| --inline | CLI flag | 否 | 强制完整打印 JSON，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次缓存读取与写入；默认仅使用公共调用器的一层 24 小时缓存。 |

脚本入口为 `scripts/kalodata_livestream_search.py`，接收 JSON 位置参数及上述两项 CLI 选项。
非 2xx HTTP 状态会写入标准错误，完整响应 JSON 保持原文；即使响应体缺少 `errcode`，也应依据实际 HTTP 状态判断失败并处理认证或用量错误。
榜单与详情分别使用 `linkfox-kalodata-tiktok-livestream-rank` 与 `linkfox-kalodata-tiktok-livestream-detail` 标识，隔离缓存与输出文件，防止相同参数串用结果。缓存按参数规范化散列，24 小时内复用；过期、JSON 损坏或缓存对象结构异常时重新请求。读取时核验缓存版本、HTTP 状态和业务状态；不含 HTTP 状态的缓存不予复用。仅缓存 HTTP 200 且业务状态正常的对象，错误不缓存；缓存由公共调用器统一管理，业务入口复用该层缓存。同一入口在一秒内多次运行时，完整响应使用不同的高精度时间戳文件名。
密钥优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；网关地址优先读取 `LINKFOX_TOOL_GATEWAY`，回退公共规则默认地址。请求传递 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 上下文头。
业务入口在请求前检查当前工作目录可写，并将输出固定到当前目录的 `linkfox/`，不回退至 `/tmp`、家目录或其他工作区。会话标识优先取 `SESSION_ID`，未配置时按时间和随机值生成。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 直播榜单列表，元素结构见下表 |
| costToken | integer | 本次调用扣费 token，固定 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

#### data 数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| livestream_start_time | integer | 直播开始时间（epoch 毫秒） |
| livestream_end_time | integer | 直播结束时间（epoch 毫秒） |
| livestream_duration | integer | 直播时长（秒） |
| livestream_title | string | 直播标题 |
| livestream_id | string | 直播唯一 ID（字符串，避免大整数精度丢失）；可用作详情接口的 `livestreamId` |
| creator_id | string | 达人唯一 ID（字符串，避免大整数精度丢失） |
| creator_handle | string | 达人账号 handle |
| revenue | string | 总销售额 / GMV（按请求的 `currency` 货币；**返回为字符串**，如 `"185590.52"`） |
| unit_price | string | 件单价（按请求的 `currency` 货币；**返回为字符串**，如 `"265.89"`） |
| views | integer | 观看数 |
| record_type | string | 记录类型（如 `SHORT`） |

> **货币字段为字符串**：榜单接口的 `revenue` 与 `unit_price` 返回的是字符串（如 `"185590.52"`），不是数字，使用前需转换为数值类型（如 `float()` / `Number()`；PowerShell 中先用 `ConvertFrom-Json` 解析响应，再将对应字段值显式转换为数值类型）。默认按 `revenue`（GMV）降序排列。

响应没有 `total`、总页数等分页元数据，也无显式 `rank` 字段；位置由响应顺序体现。按用户要求翻页时，直到某页返回少于 `pageSize` 条或达到第 5 页停止；满页只说明可能有下一页，不自动遍历。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 数据可能存在 T+1 统计延迟，不视为实时直播状态。
- `errcode=501` 且 `errmsg` 形如 `调用 Kalodata 接口失败: Kalodata API HTTP 554: ` 时，属于瞬时上游异常。先说明额外消耗，允许用相同参数重试 1–2 次，不更换参数；持续失败时停止并联系网关侧确认 Kalodata 上游配置。
- `pageNumber` 越界会返回 `errcode=501`，例如 `page_number 范围为 1-5，当前: 999`；核对并修正参数后再按成本约束继续。
- 不支持的 `sortField` 返回业务错误时，告知用户并回退默认排序，不尝试其他字段或绕过逻辑；后续请求仍遵守成本约束。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}"/kalodata/livestream/rank \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "US",
    "dateRange": "last7Day",
    "pageSize": 5,
    "pageNumber": 1
  }'
```

### 响应示例

`region=US, dateRange=last7Day, pageSize=5, pageNumber=1`（节选前 2 条）：

```json
{
  "errcode": 200,
  "data": [
    {
      "livestream_start_time": 1783810950000,
      "livestream_duration": 87457,
      "revenue": "185590.52",
      "livestream_title": "24 HOUR STREAM",
      "creator_id": "7446971784983921710",
      "livestream_id": "7661409374878878494",
      "creator_handle": "pokepiglt",
      "unit_price": "265.89",
      "livestream_end_time": 1783898407000,
      "views": 205348,
      "record_type": "SHORT"
    },
    {
      "livestream_start_time": 1783213207000,
      "livestream_duration": 4306,
      "revenue": "149304.17",
      "livestream_title": "DEALS FOR YOU - Live Now!",
      "creator_id": "7153432386608251946",
      "livestream_id": "7658842218676947743",
      "creator_handle": "based",
      "unit_price": "25.26",
      "livestream_end_time": 1783217513000,
      "views": 51765,
      "record_type": "SHORT"
    }
  ],
  "costToken": 14000,
  "errmsg": "ok"
}
```

## 接口：直播详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/kalodata/livestream/detail`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| livestreamId | string | 是 | 目标直播的唯一 ID（camelCase），例如 `7661409374878878494`。通常来自直播榜单接口的 `livestream_id`。最大长度 1000 |
| region | string | 否 | 地区/市场编码，例如 `US`。最大长度 1000 |
| dateRange | string | 否 | 时间范围，例如 `last7Day`（近7天）、`last30Day`（近30天）。最大长度 1000 |
| language | string | 否 | 返回语言，例如 `zh-CN`、`en-US`。最大长度 1000 |
| currency | string | 否 | 货币单位，例如 `USD`。最大长度 1000 |

> `livestreamId` 为必填，其余参数可选；不传时网关按默认值处理。本接口为单实体详情接口，不支持按关键词/标题搜索直播，也无 `pageNumber`/`pageSize`/`sortField` 等分页或排序参数；需先用直播榜单接口发现直播并获取 `livestream_id`，再用 `livestreamId` 查询详情。

省略可选参数时由网关按默认值处理；具体默认地区、币种和时间窗口未明确约定，不应自行假定。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | 作为第一个位置参数传入上述请求对象；字段名和大小写保持原值。 |
| --inline | CLI flag | 否 | 强制完整打印 JSON，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次缓存读取与写入；默认仅使用公共调用器的一层 24 小时缓存。 |

脚本入口为 `scripts/kalodata_livestream_detail.py`，接收 JSON 位置参数及上述两项 CLI 选项。
非 2xx HTTP 状态会写入标准错误，完整响应 JSON 保持原文；即使响应体缺少 `errcode`，也应依据实际 HTTP 状态判断失败并处理认证或用量错误。
榜单与详情分别使用 `linkfox-kalodata-tiktok-livestream-rank` 与 `linkfox-kalodata-tiktok-livestream-detail` 标识，隔离缓存与输出文件，防止相同参数串用结果。缓存按参数规范化散列，24 小时内复用；过期、JSON 损坏或缓存对象结构异常时重新请求。读取时核验缓存版本、HTTP 状态和业务状态；不含 HTTP 状态的缓存不予复用。仅缓存 HTTP 200 且业务状态正常的对象，错误不缓存；缓存由公共调用器统一管理，业务入口复用该层缓存。同一入口在一秒内多次运行时，完整响应使用不同的高精度时间戳文件名。
密钥优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；网关地址优先读取 `LINKFOX_TOOL_GATEWAY`，回退公共规则默认地址。请求传递 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 上下文头。
业务入口在请求前检查当前工作目录可写，并将输出固定到当前目录的 `linkfox/`，不回退至 `/tmp`、家目录或其他工作区。会话标识优先取 `SESSION_ID`，未配置时按时间和随机值生成。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功 |
| data | array | 单场直播详情；成功时固定为 1 元素数组，元素结构见下表 |
| costToken | integer | 本次调用扣费 token，固定 14000 |
| errmsg | string | 状态消息，成功时为 `ok` |

#### data 数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| livestream_id | string | 直播唯一 ID（与请求的 `livestreamId` 一致） |
| livestream_title | string | 直播标题（如 `24 HOUR STREAM`） |
| creator_id | string | 达人唯一 ID（字符串，避免大整数精度丢失） |
| creator_handle | string | 达人用户名/handle（如 `pokepiglt`） |
| livestream_start_time | integer | 直播开始时间，epoch 毫秒（如 `1783810950000`） |
| livestream_end_time | integer | 直播结束时间，epoch 毫秒（如 `1783898407000`） |
| livestream_duration | integer | 直播时长，单位**秒**（如 `87457`） |
| record_type | string | 记录类型（如 `SHORT`） |
| viewers | integer | 观看人数（注意：DETAIL 用 `viewers`，RANK 用 `views`） |
| revenue | number | 直播销售额 / GMV，**数字**类型，按请求的 `currency` 货币（如 `185590.52`）——注意：在直播 RANK 接口中 `revenue` 是字符串，此处为数字 |
| gpm | number | GMV per mille（每千次展示 GMV），数字类型——DETAIL 独有，RANK 接口无此字段 |
| product_number | integer | 直播带货商品数 |

> **与 RANK 接口的字段名/类型差异**：直播 DETAIL 接口使用 `viewers`（RANK 接口使用 `views`）；DETAIL 的 `revenue` 是**数字**（RANK 的 `revenue` 是**字符串**）；DETAIL 有 `gpm`（RANK 无），DETAIL 无 `unit_price`（RANK 有）。用 `jq`/`ConvertFrom-Json` 抽取时务必使用上方对应接口的字段名。

成功时 `data` 固定为 1 元素数组，共 12 个详情字段，无分页且不包含 `total`。详情无 `unit_price`，不得从榜单字段推断详情结构。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 数据可能存在 T+1 统计延迟，不视为实时直播状态。
- `errcode=501` 且 `errmsg` 形如 `调用 Kalodata 接口失败: Kalodata API HTTP 554: ` 时，属于瞬时上游异常。先说明额外消耗，允许用相同参数重试 1–2 次，不更换参数；持续失败时停止并联系网关侧确认 Kalodata 上游配置。
- 缺少必填 `livestreamId` 可能返回 `errcode=501`；核对是否取得榜单记录的 `livestream_id`，补全正确标识后再按成本约束继续。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}"/kalodata/livestream/detail \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "livestreamId": "7661409374878878494",
    "region": "US",
    "dateRange": "last7Day"
  }'
```

### 响应示例

`livestreamId=7661409374878878494`：

```json
{
  "errcode": 200,
  "data": [
    {
      "livestream_start_time": 1783810950000,
      "livestream_duration": 87457,
      "viewers": 205348,
      "revenue": 185590.52,
      "livestream_title": "24 HOUR STREAM",
      "gpm": 903.79,
      "creator_id": "7446971784983921710",
      "livestream_id": "7661409374878878494",
      "creator_handle": "pokepiglt",
      "livestream_end_time": 1783898407000,
      "record_type": "SHORT",
      "product_number": 68
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
  "skillName": "linkfox-kalodata-tiktok-livestream",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
