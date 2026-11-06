# 出海匠 TikTok 商品市场研究 接口说明

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

## 脚本行为与使用限制

- 请求使用 camelCase，不把上游 snake_case 字段直接用作入参。商品网关请求额外透传 `SESSION_ID`（去首尾空白）、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未配置时为空。
- 10 个商品脚本保留 24 小时成功响应缓存，缓存位于 `<cwd>/linkfox/.cache/linkfox-chuhaijiang-tiktok-product/`，按当前目录、API Key 指纹、网关、端点和完整参数隔离，不保存明文 API Key。成功的空结果也缓存；HTTP/业务失败、显式 `error` 或 `success=false` 不缓存；辅助状态 `code`、`errorCode` 若出现，须符合缓存可接受的成功值 `0`、`200`、`ok`、`success`（按字符串转小写比较）。该额外缓存保护不改变公共 HTTP/errcode 响应判断，读取已有缓存时同样校验。`--inline` 不绕过缓存，`--no-cache` 跳过缓存读写并强制请求，可能再次收费，仅在用户明确同意额外消耗或调试时使用。
- 商品入口 CLI：`python scripts/<入口>.py '<JSON 参数>' [--inline] [--no-cache]`；仅接受一个 JSON 对象。始终在当前目录的会话 `data` 下保存完整响应，不能回退家目录或系统临时目录；不可写时退出报错。缓存命中仍落盘。8 KB 以内全量输出；更大结果输出参数、状态、`data.total_count`、各业务列表长度和首个非空业务列表前 3 条；`--inline` 强制全量。详情的 `data.core.items`、`data.channel.items` 分别统计，不把图片等嵌套数组当作主业务列表。
- 业务封装经 `scripts/_chuhaijiang_transport.py` 调用公共 `call_api.run`，固定带 `--no-cache`；公共层中间输出送至空设备，业务入口负责唯一持久化与缓存。预签名响应只留内存，不使用缓存，也不保存含签名 URL 的原始响应。请使用业务入口，避免直接运行公共调用器绕过这些行为。
- 业务对象可能缺失、为 `null` 或新增字段；保留未知字段，解析嵌套值前检查 JSON 类型。金额通常为 `{ "unit": "US", "value": 31 }`，部分榜单金额（包括同名 `interval_gmv`）可能为 number；保留单位与原值，不自行换算。
- 2026-08-29 的接口验证记录：10 个商品接口返回 `errcode=200`；详情可同时返回基础、核心、渠道列表；上传后的外部 PUT 返回 HTTP 200。

## 接口：商品搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/products/search`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未指定 | `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`，小写国家码 |
| page | integer | 否 | 未指定 | 页码，最小 1 |
| pageSize | integer | 否 | 未指定 | 每页最多 10 条 |
| keyword | string | 否 | 未指定 | 搜索关键词 |
| category | string | 否 | 未指定 | 商品分类 ID |
| sellerType | string | 否 | 未指定 | `1`=海外非品牌、`2`=本地、`3`=品牌、`4`=非品牌 |
| minPrice | number | 否 | 未指定 | 最低价格（美元） |
| maxPrice | number | 否 | 未指定 | 最高价格（美元） |
| minRating | number | 否 | 未指定 | 评分范围，0–5 |
| maxRating | number | 否 | 未指定 | 评分范围，0–5 |
| minSold7d | number | 否 | 未指定 | 7 天销量范围 |
| maxSold7d | number | 否 | 未指定 | 7 天销量范围 |
| minSold30d | number | 否 | 未指定 | 30 天销量范围 |
| maxSold30d | number | 否 | 未指定 | 30 天销量范围 |
| freeShipping | boolean | 否 | 未指定 | 是否包邮 |
| sort | string | 否 | `gmv_7d:desc` | `field:asc` 或 `field:desc`；字段为 `daily_sold`、`gmv_30d`、`gmv_7d`、`price`、`rating`、`sold_30d`、`sold_7d` |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.total_count | integer | 匹配记录总数 |
| data.items | array | 本接口业务记录列表 |

#### data.items[] 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 商品标识，用于详情和关联查询 |
| product_name | string | 商品标题 |
| product_images | array / object | 主图与缩略图，按实际嵌套结构解析 |
| floor_price | object / number | 当前最低价格；对象保留 unit、value |
| ceiling_price | object / number | 当前最高价格；对象保留 unit、value |
| product_rating | number | 商品评分 |
| review_count | integer | 评论数（返回时展示） |
| product_sold_count | number | 累计销量；带周期后缀的 `product_sold_count*` 按其周期解释 |
| product_gmv | object / number | 累计 GMV；周期字段按实际窗口解释 |
| seller_id | string | 卖家标识 |
| shop_name | string | 店铺名称 |

金额字段返回对象时按下表解析；若返回 number，直接读取原值。以业务含义描述的项目不约定具体字段名或嵌套结构，应按实际 JSON 读取，不据此推断字段名。

| 金额对象字段 | 类型 | 说明 |
|---|---|---|
| unit | string | 原始单位，例如 `US`；展示时保留 |
| value | number | 金额数值；不自行换算 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败，非法国家码已有此返回记录；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：18 算力/次，按接口独立计费。
- 仅接受本接口请求表中的字段，使用 camelCase；按本接口分页上限准备参数，不补造上游过滤条件。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/products/search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"country":"us","pageSize":5,"keyword":"beauty","minRating":4,"freeShipping":true}'
```

## 接口：商品详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/products/detail`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未指定 | `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`，小写国家码 |
| id | string | 是 | 未指定 | 商品 ID |
| include | string | 否 | 未指定 | `channel` 或 `core`；多个值用英文逗号分隔 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.items | array | 本接口业务记录列表 |

#### data.items[] 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 商品标识，用于详情和关联查询 |
| product_name | string | 商品标题 |
| product_images | array / object | 主图与缩略图，按实际嵌套结构解析 |
| floor_price | object / number | 当前最低价格；对象保留 unit、value |
| ceiling_price | object / number | 当前最高价格；对象保留 unit、value |
| product_rating | number | 商品评分 |
| review_count | integer | 评论数（返回时展示） |
| product_sold_count | number | 累计销量；带周期后缀的 `product_sold_count*` 按其周期解释 |
| product_gmv | object / number | 累计 GMV；周期字段按实际窗口解释 |
| seller_id | string | 卖家标识 |
| shop_name | string | 店铺名称 |
| product_id | string | 商品标识（返回时保留） |
| SKU、规格、卖家信息 | 以实际 JSON 为准 | 字段名不作固定约定，按实际返回结构展示 |

金额字段返回对象时按下表解析；若返回 number，直接读取原值。以业务含义描述的项目不约定具体字段名或嵌套结构，应按实际 JSON 读取，不据此推断字段名。

| 金额对象字段 | 类型 | 说明 |
|---|---|---|
| unit | string | 原始单位，例如 `US`；展示时保留 |
| value | number | 金额数值；不自行换算 |

#### 可选指标与嵌套结构

| 字段 | 类型 | 说明 |
|---|---|---|
| data.core | object | include 含 core 时的核心指标分区 |
| data.core.items | array | 核心指标列表 |
| data.core.items[].product_gmv | object / number | GMV |
| data.core.items[].product_sold_count | number | 销量 |
| data.core.items[] 的近 30 天、广告、视频指标及关联达人/直播/视频数量 | 以实际 JSON 为准 | 按实际字段读取，保留统计周期 |
| data.channel | object | include 含 channel 时的渠道分区 |
| data.channel.items | array | 渠道指标列表 |
| data.channel.items[] 的视频、直播、商品卡、个人达人、卖家达人渠道指标 | object / number | 近 30 天 GMV 与销量；具体字段名不作固定约定 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败，非法国家码已有此返回记录；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：9 算力/次，按接口独立计费。
- 仅接受本接口请求表中的字段，使用 camelCase；本接口不使用分页参数，不补造上游过滤条件。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/products/detail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"country":"us","id":"1732052189676081387","include":"core,channel"}'
```

## 接口：关联达人

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/products/related-creators`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未指定 | `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`，小写国家码 |
| page | integer | 否 | 未指定 | 页码，最小 1 |
| pageSize | integer | 否 | 未指定 | 每页最多 10 条 |
| id | string | 是 | 未指定 | 商品 ID，复用搜索或榜单返回值 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.total_count | integer | 匹配记录总数 |
| data.items | array | 本接口业务记录列表 |

#### data.items[] 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| user_id | string | 达人标识，按实际返回字段保留 |
| uid | string | 达人标识，按实际返回字段保留 |
| unique_id | string | 达人标识，按实际返回字段保留 |
| 昵称、粉丝数 | 以实际 JSON 为准 | 具体字段名不作固定约定；按返回的达人前缀字段展示 |
| 互动和播放指标、视频/直播 GMV | number / object | 分别展示其指标及周期；保留金额单位 |
| 联系方式 | 以实际 JSON 为准 | 可能缺失，不补造 |

金额字段返回对象时按下表解析；若返回 number，直接读取原值。以业务含义描述的项目不约定具体字段名或嵌套结构，应按实际 JSON 读取，不据此推断字段名。

| 金额对象字段 | 类型 | 说明 |
|---|---|---|
| unit | string | 原始单位，例如 `US`；展示时保留 |
| value | number | 金额数值；不自行换算 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败，非法国家码已有此返回记录；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：18 算力/次，按接口独立计费。
- 仅接受本接口请求表中的字段，使用 camelCase；按本接口分页上限准备参数，不补造上游过滤条件。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/products/related-creators" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"country":"us","pageSize":5,"id":"1732052189676081387","page":1}'
```

## 接口：关联直播

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/products/related-lives`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未指定 | `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`，小写国家码 |
| page | integer | 否 | 未指定 | 页码，最小 1 |
| pageSize | integer | 否 | 未指定 | 每页最多 10 条 |
| id | string | 是 | 未指定 | 商品 ID，复用搜索或榜单返回值 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.total_count | integer | 匹配记录总数 |
| data.items | array | 本接口业务记录列表 |

#### data.items[] 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| room_id | string | 直播间标识 |
| 标题、直播链接、达人 ID | 以实际 JSON 为准 | 字段名不作固定约定，按实际直播前缀字段读取 |
| 开播/结束时间 | 以实际 JSON 为准 | 保留原始时间信息 |
| GMV、销量、观众指标 | number / object | 按实际返回字段及周期展示 |

金额字段返回对象时按下表解析；若返回 number，直接读取原值。以业务含义描述的项目不约定具体字段名或嵌套结构，应按实际 JSON 读取，不据此推断字段名。

| 金额对象字段 | 类型 | 说明 |
|---|---|---|
| unit | string | 原始单位，例如 `US`；展示时保留 |
| value | number | 金额数值；不自行换算 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败，非法国家码已有此返回记录；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：18 算力/次，按接口独立计费。
- 仅接受本接口请求表中的字段，使用 camelCase；按本接口分页上限准备参数，不补造上游过滤条件。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/products/related-lives" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"country":"us","pageSize":5,"id":"1732052189676081387","page":1}'
```

## 接口：商品评论

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/products/reviews`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未指定 | `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`，小写国家码 |
| page | integer | 否 | 未指定 | 页码，最小 1 |
| pageSize | integer | 否 | 未指定 | 每页最多 10 条 |
| id | string | 是 | 未指定 | 商品 ID，复用搜索或榜单返回值 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.total_count | integer | 匹配记录总数 |
| data.items | array | 本接口业务记录列表 |

#### data.items[] 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| review_id | string | 评论标识 |
| 内容、评分、发布时间 | 以实际 JSON 为准 | 字段名不作固定约定；展示实际返回值 |
| 图片/媒体、SKU 信息 | 以实际 JSON 为准 | 展示媒体可用性和 SKU 规格 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败，非法国家码已有此返回记录；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：18 算力/次，按接口独立计费。
- 仅接受本接口请求表中的字段，使用 camelCase；按本接口分页上限准备参数，不补造上游过滤条件。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/products/reviews" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"country":"us","pageSize":5,"id":"1732052189676081387","page":1}'
```

## 接口：关联视频

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/products/related-videos`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未指定 | `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`，小写国家码 |
| page | integer | 否 | 未指定 | 页码，最小 1 |
| pageSize | integer | 否 | 未指定 | 每页最多 10 条 |
| id | string | 是 | 未指定 | 商品 ID，复用搜索或榜单返回值 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.total_count | integer | 匹配记录总数 |
| data.items | array | 本接口业务记录列表 |

#### data.items[] 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| video_id | string | 视频标识 |
| 描述、封面、分享链接、达人 ID | 以实际 JSON 为准 | 字段名不作固定约定，按实际视频前缀字段读取 |
| 播放/点赞/互动指标 | number | 按实际返回字段展示 |
| 近 30 天 GMV/销量 | object / number | 保留周期与金额单位 |

金额字段返回对象时按下表解析；若返回 number，直接读取原值。以业务含义描述的项目不约定具体字段名或嵌套结构，应按实际 JSON 读取，不据此推断字段名。

| 金额对象字段 | 类型 | 说明 |
|---|---|---|
| unit | string | 原始单位，例如 `US`；展示时保留 |
| value | number | 金额数值；不自行换算 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败，非法国家码已有此返回记录；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：18 算力/次，按接口独立计费。
- 仅接受本接口请求表中的字段，使用 camelCase；按本接口分页上限准备参数，不补造上游过滤条件。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/products/related-videos" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"country":"us","pageSize":5,"id":"1732052189676081387","page":1}'
```

## 接口：商品热推榜

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/products/rankings/most-promoted`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未指定 | `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`，小写国家码 |
| page | integer | 否 | 未指定 | 页码，最小 1 |
| pageSize | integer | 否 | 未指定 | 每页 1–20 条 |
| date | string | 是 | 未指定 | `YYYYMMDD` |
| granularity | string | 是 | 未指定 | `daily`、`weekly`、`monthly`、`0`、`1` 或 `2` |
| category | string | 否 | 未指定 | 商品分类 |
| sellerType | string | 否 | 未指定 | `1`=海外非品牌、`2`=本地、`3`=品牌、`4`=非品牌 |
| sort | string | 否 | `related_creator_count:desc` | `interval_gmv`、`interval_sold_count`、`live_count`、`live_user_count`、`related_creator_count`、`video_play_count`；格式为 `field:asc` 或 `field:desc` |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.total_count | integer | 匹配记录总数 |
| data.items | array | 本接口业务记录列表 |

#### data.items[] 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 商品标识，用于详情和关联查询 |
| product_name | string | 商品标题 |
| product_images | array / object | 主图与缩略图，按实际嵌套结构解析 |
| floor_price | object / number | 当前最低价格；对象保留 unit、value |
| ceiling_price | object / number | 当前最高价格；对象保留 unit、value |
| product_rating | number | 商品评分 |
| review_count | integer | 评论数（返回时展示） |
| product_sold_count | number | 累计销量；带周期后缀的 `product_sold_count*` 按其周期解释 |
| product_gmv | object / number | 累计 GMV；周期字段按实际窗口解释 |
| seller_id | string | 卖家标识 |
| shop_name | string | 店铺名称 |
| product_id | string | 商品标识（返回时保留） |
| interval_gmv | object / number | 区间 GMV |
| interval_sold_count | number | 区间销量 |
| live_count | integer | 直播数 |
| live_user_count | integer | 直播达人数量 |
| related_creator_count | integer | 关联达人数 |
| video_play_count | number | 视频播放量 |

金额字段返回对象时按下表解析；若返回 number，直接读取原值。以业务含义描述的项目不约定具体字段名或嵌套结构，应按实际 JSON 读取，不据此推断字段名。

| 金额对象字段 | 类型 | 说明 |
|---|---|---|
| unit | string | 原始单位，例如 `US`；展示时保留 |
| value | number | 金额数值；不自行换算 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败，非法国家码已有此返回记录；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：18 算力/次，按接口独立计费。
- 仅接受本接口请求表中的字段，使用 camelCase；按本接口分页上限准备参数，不补造上游过滤条件。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/products/rankings/most-promoted" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"country":"us","pageSize":5,"date":"20260824","granularity":"daily"}'
```

## 接口：商品新品榜

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/products/rankings/new-arrivals`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未指定 | `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`，小写国家码 |
| page | integer | 否 | 未指定 | 页码，最小 1 |
| pageSize | integer | 否 | 未指定 | 每页 1–20 条 |
| category | string | 否 | 未指定 | 商品分类 |
| sellerType | string | 否 | 未指定 | `1`=海外非品牌、`2`=本地、`3`=品牌、`4`=非品牌 |
| listedFrom | string | 否 | 未指定 | 上架日期范围，`YYYYMMDD` |
| listedTo | string | 否 | 未指定 | 上架日期范围，`YYYYMMDD` |
| productStatus | string | 否 | 未指定 | `1`、`2`、`3` 或 `4` |
| sort | string | 否 | `gmv_3d:desc` | `gmv_3d`、`sold_count_3d`、`total_gmv`、`total_sold_count`；格式为 `field:asc` 或 `field:desc` |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.total_count | integer | 匹配记录总数 |
| data.items | array | 本接口业务记录列表 |

#### data.items[] 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 商品标识，用于详情和关联查询 |
| product_name | string | 商品标题 |
| product_images | array / object | 主图与缩略图，按实际嵌套结构解析 |
| floor_price | object / number | 当前最低价格；对象保留 unit、value |
| ceiling_price | object / number | 当前最高价格；对象保留 unit、value |
| product_rating | number | 商品评分 |
| review_count | integer | 评论数（返回时展示） |
| product_sold_count | number | 累计销量；带周期后缀的 `product_sold_count*` 按其周期解释 |
| product_gmv | object / number | 累计 GMV；周期字段按实际窗口解释 |
| seller_id | string | 卖家标识 |
| shop_name | string | 店铺名称 |
| product_id | string | 商品标识（返回时保留） |
| 累计及近 3/7 天 GMV/销量 | object / number | 保留实际指标周期 |
| gmv_3d | object / number | 近 3 天 GMV |
| sold_count_3d | number | 近 3 天销量 |
| total_gmv | object / number | 累计 GMV |
| total_sold_count | number | 累计销量 |
| 商品状态、销量趋势 | 以实际 JSON 为准 | 嵌套结构不作固定约定，按实际字段读取 |

金额字段返回对象时按下表解析；若返回 number，直接读取原值。以业务含义描述的项目不约定具体字段名或嵌套结构，应按实际 JSON 读取，不据此推断字段名。

| 金额对象字段 | 类型 | 说明 |
|---|---|---|
| unit | string | 原始单位，例如 `US`；展示时保留 |
| value | number | 金额数值；不自行换算 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败，非法国家码已有此返回记录；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：18 算力/次，按接口独立计费。
- 仅接受本接口请求表中的字段，使用 camelCase；按本接口分页上限准备参数，不补造上游过滤条件。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/products/rankings/new-arrivals" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"country":"us","pageSize":5}'
```

## 接口：商品销量榜

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/products/rankings/top-selling`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未指定 | `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`，小写国家码 |
| page | integer | 否 | 未指定 | 页码，最小 1 |
| pageSize | integer | 否 | 未指定 | 每页 1–20 条 |
| date | string | 是 | 未指定 | `YYYYMMDD` |
| granularity | string | 是 | 未指定 | `daily`、`weekly`、`monthly`、`0`、`1` 或 `2` |
| category | string | 否 | 未指定 | 商品分类 |
| sellerType | string | 否 | 未指定 | `1`=海外非品牌、`2`=本地、`3`=品牌、`4`=非品牌 |
| sort | string | 否 | `interval_sold_count:desc` | `gmv_growth_rate`、`interval_gmv`、`interval_sold_count`、`sold_count_growth_rate`、`total_gmv`、`total_sold_count`；格式为 `field:asc` 或 `field:desc` |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.total_count | integer | 匹配记录总数 |
| data.items | array | 本接口业务记录列表 |

#### data.items[] 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 商品标识，用于详情和关联查询 |
| product_name | string | 商品标题 |
| product_images | array / object | 主图与缩略图，按实际嵌套结构解析 |
| floor_price | object / number | 当前最低价格；对象保留 unit、value |
| ceiling_price | object / number | 当前最高价格；对象保留 unit、value |
| product_rating | number | 商品评分 |
| review_count | integer | 评论数（返回时展示） |
| product_sold_count | number | 累计销量；带周期后缀的 `product_sold_count*` 按其周期解释 |
| product_gmv | object / number | 累计 GMV；周期字段按实际窗口解释 |
| seller_id | string | 卖家标识 |
| shop_name | string | 店铺名称 |
| product_id | string | 商品标识（返回时保留） |
| interval_gmv | object / number | 区间 GMV，运行时检查类型 |
| interval_sold_count | number | 区间销量 |
| total_gmv | object / number | 累计 GMV |
| total_sold_count | number | 累计销量 |
| gmv_growth_rate | number | GMV 增长率，保留原值 |
| sold_count_growth_rate | number | 销量增长率，保留原值 |

金额字段返回对象时按下表解析；若返回 number，直接读取原值。以业务含义描述的项目不约定具体字段名或嵌套结构，应按实际 JSON 读取，不据此推断字段名。

| 金额对象字段 | 类型 | 说明 |
|---|---|---|
| unit | string | 原始单位，例如 `US`；展示时保留 |
| value | number | 金额数值；不自行换算 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败，非法国家码已有此返回记录；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：18 算力/次，按接口独立计费。
- 仅接受本接口请求表中的字段，使用 camelCase；按本接口分页上限准备参数，不补造上游过滤条件。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/products/rankings/top-selling" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"country":"us","pageSize":5,"date":"20260824","granularity":"daily"}'
```

## 接口：图片搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/products/image-search`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| osKey | string | 是 | - | 上传返回的 `os_key`，网关参数使用 camelCase |
| country | string | 否 | `US` | 大写两位国家码 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.total_count | integer | 匹配记录总数 |
| data.items | array | 本接口业务记录列表 |

#### data.items[] 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 商品标识，用于详情和关联查询 |
| product_name | string | 商品标题 |
| product_images | array / object | 主图与缩略图，按实际嵌套结构解析 |
| floor_price | object / number | 当前最低价格；对象保留 unit、value |
| ceiling_price | object / number | 当前最高价格；对象保留 unit、value |
| product_rating | number | 商品评分 |
| review_count | integer | 评论数（返回时展示） |
| product_sold_count | number | 累计销量；带周期后缀的 `product_sold_count*` 按其周期解释 |
| product_gmv | object / number | 累计 GMV；周期字段按实际窗口解释 |
| seller_id | string | 卖家标识 |
| shop_name | string | 店铺名称 |
| product_id | string | 商品标识（返回时保留） |
| 类目、地区 | 以实际 JSON 为准 | 按实际字段读取，不补造缺失值 |

金额字段返回对象时按下表解析；若返回 number，直接读取原值。以业务含义描述的项目不约定具体字段名或嵌套结构，应按实际 JSON 读取，不据此推断字段名。

| 金额对象字段 | 类型 | 说明 |
|---|---|---|
| unit | string | 原始单位，例如 `US`；展示时保留 |
| value | number | 金额数值；不自行换算 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败，非法国家码已有此返回记录；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：30 算力/次，按接口独立计费。
- 必须先上传取得有效对象键，本地路径不能直接传给图片搜索；已有有效 osKey 时跳过上传。国家码为大写两位字母，默认 US。本接口独立收费，不附带其他查询。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/products/image-search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"osKey":"returned-key","country":"US"}'
```

## 接口：上传预签名

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/upload/presigned-url`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| fileName | string | 是 | 未指定 | 带扩展名的文件名；辅助脚本支持 JPG/JPEG/PNG |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态码；成功示例值为 200，判断遵循公共规则 |
| errmsg | string | 消息，成功时为 `ok` |
| request_id | string | 请求追踪 ID |
| data | object | 业务数据，按本接口结构解析 |
| data.url | string | 外部 HTTP PUT 上传地址，仅留内存 |
| data.os_key | string | 上传对象键，后续图搜参数使用 osKey；脚本兼容 osKey |
| data.os_bucket | string | 存储桶；脚本兼容 osBucket |
| data.signed_url | string | 临时读取地址，禁止用作上传兜底，禁止输出或持久化 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `501`：参数校验失败；依据 `errmsg` 核对参数，不自动连续重试付费接口。

### 使用限制

- **算力消耗**：0 算力/次 （限时）。
- 该路由映射出海匠加速版 `POST /open/v1/upload/presigned-url`。CLI 为 `python scripts/upload_image.py <local-image.jpg|jpeg|png>`；只接受已存在的 JPG/JPEG/PNG 文件，不修改原始图片。
- 申请预签名后，只向 `data.url` 发一次外部 HTTP PUT：body 为图片字节，Content-Type 为图片 MIME 类型，超时 150s，不携带 LinkFox API Key 或透传头。HTTP 200、201、204 为上传成功；PUT 不计入 LinkFox 接口数，也不使用响应缓存。不得使用 signed_url 作为上传兜底；超时、异常状态或无效上传地址均安全报错，不回显临时 URL。
- 不输出、记录或持久化 `data.url` 和 `data.signed_url`。CLI 只输出安全元数据，字段如下；不采用通用响应落盘策略。

| CLI 输出字段 | 类型 | 说明 |
|---|---|---|
| osKey | string | 对象键 |
| osBucket | string / null | 存储桶 |
| fileName | string | 源文件名 |
| contentType | string | 图片 MIME 类型 |
| fileSize | integer | 文件字节数 |
| uploadStatus | integer | 外部 PUT 状态 |
| requestId | string / null | 预签名请求 ID |
| errcode | integer / string / null | 网关状态 |
| errmsg | string / null | 网关消息 |
| presignDataFields | array | data 的字段名称列表，不含字段值 |

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/upload/presigned-url" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"fileName":"product.jpg"}'
```

预签名 curl 仅说明协议；实际上传使用辅助脚本，避免临时签名 URL 暴露在终端。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-chuhaijiang-tiktok-product",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
