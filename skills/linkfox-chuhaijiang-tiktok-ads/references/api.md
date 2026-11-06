# 出海匠 TikTok 广告与创意情报 接口说明

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

## 接口：广告搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/ad-creative/ads/search`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `country` | string | 是 | - | 支持小写国家码 `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn` |
| `page` | integer | 否 | 1 | 页码，最小 1 |
| `pageSize` | integer | 否 | 上游默认 | 每页数量，最大 10 |
| `keyword` | string | 否 | - | 搜索关键词 |
| `category` | string | 否 | - | 商品分类 |
| `adType` | string | 否 | - | 上游广告类型分类值 |
| `excludeSparkAds` | boolean | 否 | - | 是否排除 Spark Ads |
| `minViews` | number | 否 | - | 最低播放量 |
| `maxViews` | number | 否 | - | 最高播放量 |
| `minGmv` | number | 否 | - | 最低 GMV |
| `maxGmv` | number | 否 | - | 最高 GMV |
| `minDays` | number | 否 | - | 最少投放天数 |
| `maxDays` | number | 否 | - | 最多投放天数 |
| `sort` | string | 否 | `gmv:desc` | `field:asc` 或 `field:desc` |

网关字段使用 Java/MCP camelCase，再由服务端映射上游 snake_case；不得直接发送 `page_size`、`ad_type`、`has_product` 等上游字段。

`sort` 为 `field:asc` 或 `field:desc`，默认 `gmv:desc`；Java 层没有排序字段枚举，不臆造字段，未知时省略。`category` 为上游分类，不编造标签。

`adType` 使用上游广告类型分类，未提供已知值时不要编造枚举。

脚本选项、缓存、认证兼容与落盘行为见 [脚本运行约定](#脚本运行约定)。

### 响应结构

成功响应示例为 HTTP 200、`errcode=200`、`errmsg=ok`；成功判定遵循公共规则，不限于此示例。除明确列出类型外，业务字段按实际响应解析，允许 null 或缺失，不补造嵌套属性。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer / string / null | 网关状态，按下方基础规则判断；成功响应示例为 200。 |
| `errmsg` | string | 网关消息；成功响应示例为 ok。 |
| `request_id` | string | 请求追踪编号。 |
| `data` | object | 本接口业务数据。 |
| `data.total_count` | integer | 总匹配记录数；并非本页 data.items 长度，缺失时不推算。 |
| `data.items` | array<object> | 主业务记录列表。 |

#### `data.items[]` 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.items[].id` | 未固定；按运行时类型解析 | 广告查询编号；对应广告详情与关联商品必须用此 id，不用 video_id、product_id 或 advertiser_id。 |
| `data.items[].video_id` | 未固定；按运行时类型解析 | 视频编号，不替代搜索结果 id。 |
| `data.items[].product_id` | 未固定；按运行时类型解析 | 关联商品编号，不替代搜索结果 id。 |
| `data.items[].advertiser_id` | 未固定；按运行时类型解析 | 广告主编号。 |
| `data.items[].ad_url` | 未固定；按运行时类型解析 | 广告公开链接。 |
| `data.items[].web_url` | 未固定；按运行时类型解析 | 落地页公开链接。 |
| `data.items[].advertiser_url` | 未固定；按运行时类型解析 | 广告主公开链接。 |
| `data.items[].ad_title` | 未固定；按运行时类型解析 | 广告标题。 |
| `data.items[].advertiser_name` | 未固定；按运行时类型解析 | 广告主名称。 |
| `data.items[].button_text` | 未固定；按运行时类型解析 | 行动按钮文案。 |
| `data.items[].product_title` | 未固定；按运行时类型解析 | 商品标题。 |
| `data.items[].create_time` | 未固定；按运行时类型解析 | 记录创建时间。 |
| `data.items[].ad_create_time` | 未固定；按运行时类型解析 | 广告创建时间。 |
| `data.items[].last_update_time` | 未固定；按运行时类型解析 | 最后更新时间。 |
| `data.items[].duration` | 未固定；按运行时类型解析 | 广告时长。 |
| `data.items[].ad_day_count` | 未固定；按运行时类型解析 | 投放天数。 |
| `data.items[].video_play_count` | 未固定；按运行时类型解析 | 播放量。 |
| `data.items[].video_like_count` | 未固定；按运行时类型解析 | 点赞数。 |
| `data.items[].video_like_rate` | 未固定；按运行时类型解析 | 点赞率。 |
| `data.items[].video_engagement_rate` | 未固定；按运行时类型解析 | 互动率。 |
| `data.items[].video_popularity` | 未固定；按运行时类型解析 | 视频热度。 |
| `data.items[].total_sc` | 未固定；按运行时类型解析 | 累计销量指标（保留来源口径）。 |
| `data.items[].total_gmv` | 通常 object；以实际类型为准 | 累计 GMV；通常含 unit 和 value，不得当作纯数值。 |
| `data.items[].total_gmv.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.items[].total_gmv.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |
| `data.items[].video_gpm_30d` | 通常 object；以实际类型为准 | 近 30 天视频 GPM；通常含 unit 和 value，不得当作纯数值。 |
| `data.items[].video_gpm_30d.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.items[].video_gpm_30d.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |
| `data.items[].ad_maximum_cost` | 通常 object；以实际类型为准 | 广告最高花费指标；通常含 unit 和 value，不得当作纯数值。 |
| `data.items[].ad_maximum_cost.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.items[].ad_maximum_cost.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |
| `data.items[].ad_roas` | 未固定；按运行时类型解析 | 广告 ROAS。 |
| `data.items[].product_l1_category` | 未固定；按运行时类型解析 | 商品一级类目。 |
| `data.items[].product_l2_category` | 未固定；按运行时类型解析 | 商品二级类目。 |
| `data.items[].product_l3_category` | 未固定；按运行时类型解析 | 商品三级类目。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / HTTP | 含义 | 处理建议 |
|---|---|---|
| 400 | 必填参数缺失等请求错误 | 根据 errmsg 补齐或修正参数，不得原样重试。 |
| 501 | 参数校验或上游调用失败 | 展示 errmsg 并停止；需要重试时先说明额外算力消耗，由用户决定。 |

错误时保留已取得的数据并停止，不自动连续试探付费端点。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/ad-creative/ads/search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","page":1,"pageSize":3,"keyword":"beauty"}'
```

示例编号可能过时；实际任务优先使用本次搜索结果。每次请求 18 算力。

---

## 接口：广告详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/ad-creative/ads/detail`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `country` | string | 是 | 支持小写国家码 `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn` |
| `id` | string | 是 | 广告搜索返回的 `id` |
| `include` | string | 否 | 可选值 `core`；多个值语法为英文逗号分隔 |

网关字段使用 Java/MCP camelCase，再由服务端映射上游 snake_case；不得直接发送 `page_size`、`ad_type`、`has_product` 等上游字段。

必须使用广告搜索对象的 `id`，不得替换成 `video_id`、`product_id` 或 `advertiser_id`。

脚本选项、缓存、认证兼容与落盘行为见 [脚本运行约定](#脚本运行约定)。

### 响应结构

成功响应示例为 HTTP 200、`errcode=200`、`errmsg=ok`；成功判定遵循公共规则，不限于此示例。除明确列出类型外，业务字段按实际响应解析，允许 null 或缺失，不补造嵌套属性。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer / string / null | 网关状态，按下方基础规则判断；成功响应示例为 200。 |
| `errmsg` | string | 网关消息；成功响应示例为 ok。 |
| `request_id` | string | 请求追踪编号。 |
| `data` | object | 本接口业务数据。 |
| `data.total_count` | integer | 总匹配记录数；并非本页 data.items 长度，缺失时不推算。 |
| `data.items` | array<object> | 主业务记录列表。 |
| `data.core` | object | include=core 时返回的表现数据。 |
| `data.core.items` | array<object> | 广告表现记录列表。 |

#### `data.items[]` 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.items[].id` | 未固定；按运行时类型解析 | 广告基础记录编号。 |
| `data.items[].ad_title` | 未固定；按运行时类型解析 | 广告标题。 |
| `data.items[].advertiser_id` | 未固定；按运行时类型解析 | 广告主编号。 |
| `data.items[].advertiser_name` | 未固定；按运行时类型解析 | 广告主名称。 |
| `data.items[].advertiser_avatar` | object | 广告主头像嵌套对象；属性未约定，使用前检查。 |
| `data.items[].ad_cover` | object | 广告封面嵌套对象；属性未约定，使用前检查。 |
| `data.items[].ad_url` | 未固定；按运行时类型解析 | 广告公开链接。 |
| `data.items[].web_url` | 未固定；按运行时类型解析 | 落地页公开链接。 |
| `data.items[].button_text` | 未固定；按运行时类型解析 | 行动按钮文案。 |
| `data.items[].duration` | 未固定；按运行时类型解析 | 广告时长。 |
| `data.items[].ad_create_time` | 未固定；按运行时类型解析 | 广告创建时间。 |
| `data.items[].create_time` | 未固定；按运行时类型解析 | 记录创建时间。 |
| `data.items[].last_update_time` | 未固定；按运行时类型解析 | 最后更新时间。 |

#### `data.core.items[]` 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.core.items[].core_creative_id` | 未固定；按运行时类型解析 | 创意编号。 |
| `data.core.items[].core_ad_type` | 未固定；按运行时类型解析 | 广告类型。 |
| `data.core.items[].core_ad_day_count` | 未固定；按运行时类型解析 | 投放天数。 |
| `data.core.items[].core_ad_play_ratio` | 未固定；按运行时类型解析 | 广告播放占比。 |
| `data.core.items[].core_ad_gmv_ratio` | 未固定；按运行时类型解析 | 广告 GMV 占比。 |
| `data.core.items[].core_ad_maximum_cost` | 通常 object；以实际类型为准 | 广告最高花费指标；通常含 unit 和 value，不得当作纯数值。 |
| `data.core.items[].core_ad_maximum_cost.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.core.items[].core_ad_maximum_cost.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |
| `data.core.items[].core_ad_roas` | 未固定；按运行时类型解析 | 广告 ROAS。 |
| `data.core.items[].core_total_gmv` | 通常 object；以实际类型为准 | 累计 GMV；通常含 unit 和 value，不得当作纯数值。 |
| `data.core.items[].core_total_gmv.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.core.items[].core_total_gmv.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |
| `data.core.items[].core_total_sc` | 未固定；按运行时类型解析 | 累计销量指标（保留来源口径）。 |
| `data.core.items[].core_video_play_count` | 未固定；按运行时类型解析 | 播放量。 |
| `data.core.items[].core_video_like_count` | 未固定；按运行时类型解析 | 点赞数。 |
| `data.core.items[].core_video_comment_count` | 未固定；按运行时类型解析 | 评论数。 |
| `data.core.items[].core_video_share_count` | 未固定；按运行时类型解析 | 分享数。 |
| `data.core.items[].core_video_collect_count` | 未固定；按运行时类型解析 | 收藏数。 |
| `data.core.items[].core_video_gpm_30d` | 通常 object；以实际类型为准 | 近 30 天视频 GPM；通常含 unit 和 value，不得当作纯数值。 |
| `data.core.items[].core_video_gpm_30d.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.core.items[].core_video_gpm_30d.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |
| `data.core.items[].core_video_popularity` | 未固定；按运行时类型解析 | 视频热度。 |
| `data.core.items[].id` | 未固定；按运行时类型解析 | 当前扩展数据记录编号，保留来源值。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / HTTP | 含义 | 处理建议 |
|---|---|---|
| 400 | 必填参数缺失等请求错误 | 根据 errmsg 补齐或修正参数，不得原样重试。 |
| 501 | 参数校验或上游调用失败 | 展示 errmsg 并停止；需要重试时先说明额外算力消耗，由用户决定。 |

错误时保留已取得的数据并停止，不自动连续试探付费端点。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/ad-creative/ads/detail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7658119807128046879","include":"core"}'
```

示例编号可能过时；实际任务优先使用本次搜索结果。每次请求 9 算力。

---

## 接口：广告关联商品

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/ad-creative/ads/related-products`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `country` | string | 是 | - | 支持小写国家码 `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn` |
| `id` | string | 是 | - | 广告搜索返回的 `id` |
| `page` | integer | 否 | 1 | 页码，最小 1 |
| `pageSize` | integer | 否 | 上游默认 | 每页数量，最大 10 |

网关字段使用 Java/MCP camelCase，再由服务端映射上游 snake_case；不得直接发送 `page_size`、`ad_type`、`has_product` 等上游字段。

必须使用广告搜索对象的 `id`，不得替换成 `video_id`、`product_id` 或 `advertiser_id`。

脚本选项、缓存、认证兼容与落盘行为见 [脚本运行约定](#脚本运行约定)。

### 响应结构

成功响应示例为 HTTP 200、`errcode=200`、`errmsg=ok`；成功判定遵循公共规则，不限于此示例。除明确列出类型外，业务字段按实际响应解析，允许 null 或缺失，不补造嵌套属性。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer / string / null | 网关状态，按下方基础规则判断；成功响应示例为 200。 |
| `errmsg` | string | 网关消息；成功响应示例为 ok。 |
| `request_id` | string | 请求追踪编号。 |
| `data` | object | 本接口业务数据。 |
| `data.total_count` | integer | 总匹配记录数；并非本页 data.items 长度，缺失时不推算。 |
| `data.items` | array<object> | 主业务记录列表。 |

#### `data.items[]` 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.items[].tiktok_ads_detail_product_id` | 未固定；按运行时类型解析 | 关联商品编号，不替代搜索结果 id。 |
| `data.items[].tiktok_product_detail_product_name` | 未固定；按运行时类型解析 | 商品名称。 |
| `data.items[].tiktok_product_detail_product_images` | 未固定；按运行时类型解析 | 商品图片。 |
| `data.items[].tiktok_product_detail_region` | 未固定；按运行时类型解析 | 商品区域。 |
| `data.items[].tiktok_product_detail_product_status` | 未固定；按运行时类型解析 | 商品状态。 |
| `data.items[].tiktok_product_detail_l1_category` | 未固定；按运行时类型解析 | 一级类目。 |
| `data.items[].tiktok_product_detail_l2_category` | 未固定；按运行时类型解析 | 二级类目。 |
| `data.items[].tiktok_product_detail_l3_category` | 未固定；按运行时类型解析 | 三级类目。 |
| `data.items[].tiktok_product_detail_floor_price` | 未固定；按运行时类型解析 | 最低价格。 |
| `data.items[].tiktok_product_detail_ceiling_price` | 未固定；按运行时类型解析 | 最高价格。 |
| `data.items[].tiktok_product_detail_product_rating` | 未固定；按运行时类型解析 | 商品评分。 |
| `data.items[].tiktok_product_detail_product_sku_props` | 未固定；按运行时类型解析 | SKU 属性。 |
| `data.items[].tiktok_product_detail_product_skus` | 未固定；按运行时类型解析 | SKU 数据。 |
| `data.items[].tiktok_product_detail_commission_rate` | 未固定；按运行时类型解析 | 佣金比例。 |
| `data.items[].tiktok_ads_detail_video_id` | 未固定；按运行时类型解析 | 视频编号，不替代搜索结果 id。 |
| `data.items[].tiktok_ads_detail_product_total_sold_count` | 未固定；按运行时类型解析 | 商品累计销量。 |
| `data.items[].tiktok_ads_detail_product_total_gmv` | 通常 object；以实际类型为准 | 商品累计 GMV；通常含 unit 和 value，不得当作纯数值。 |
| `data.items[].tiktok_ads_detail_product_total_gmv.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.items[].tiktok_ads_detail_product_total_gmv.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |
| `data.items[].tiktok_ads_detail_video_30d_sold_count` | 未固定；按运行时类型解析 | 视频近 30 天销量。 |
| `data.items[].tiktok_ads_detail_video_30d_gmv` | 通常 object；以实际类型为准 | 视频近 30 天 GMV；通常含 unit 和 value，不得当作纯数值。 |
| `data.items[].tiktok_ads_detail_video_30d_gmv.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.items[].tiktok_ads_detail_video_30d_gmv.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |
| `data.items[].tiktok_ads_detail_product_launch_time` | 未固定；按运行时类型解析 | 商品上架时间。 |
| `data.items[].tiktok_ads_detail_product_country_code` | 未固定；按运行时类型解析 | 商品市场代码。 |
| `data.items[].id` | 未固定；按运行时类型解析 | 当前关联记录编号；继续查商品详情应使用 tiktok_ads_detail_product_id。 |

保留所有 `tiktok_ads_detail_` / `tiktok_product_detail_` 来源前缀，不改写成广告搜索字段。关联记录 `id` 与商品编号不同，继续查询商品时优先使用 `tiktok_ads_detail_product_id`。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / HTTP | 含义 | 处理建议 |
|---|---|---|
| 400 | 必填参数缺失等请求错误 | 根据 errmsg 补齐或修正参数，不得原样重试。 |
| 501 | 参数校验或上游调用失败 | 展示 errmsg 并停止；需要重试时先说明额外算力消耗，由用户决定。 |

错误时保留已取得的数据并停止，不自动连续试探付费端点。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/ad-creative/ads/related-products" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","page":1,"pageSize":3,"id":"7658119807128046879"}'
```

示例编号可能过时；实际任务优先使用本次搜索结果。每次请求 18 算力。

---

## 接口：创意搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/ad-creative/creatives/search`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `country` | string | 是 | - | 支持小写国家码 `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn` |
| `page` | integer | 否 | 1 | 页码，最小 1 |
| `pageSize` | integer | 否 | 上游默认 | 每页数量，最大 10 |
| `keyword` | string | 否 | - | 搜索关键词 |
| `category` | string | 否 | - | 素材分类 |
| `hasProduct` | boolean | 否 | - | 是否关联商品 |
| `isSponsored` | boolean | 否 | - | 是否为赞助内容 |
| `isAigc` | boolean | 否 | - | 是否为 AIGC |
| `sort` | string | 否 | `gmv:desc` | `field:asc` 或 `field:desc` |

网关字段使用 Java/MCP camelCase，再由服务端映射上游 snake_case；不得直接发送 `page_size`、`ad_type`、`has_product` 等上游字段。

`sort` 为 `field:asc` 或 `field:desc`，默认 `gmv:desc`；Java 层没有排序字段枚举，不臆造字段，未知时省略。`category` 为上游分类，不编造标签。

脚本选项、缓存、认证兼容与落盘行为见 [脚本运行约定](#脚本运行约定)。

### 响应结构

成功响应示例为 HTTP 200、`errcode=200`、`errmsg=ok`；成功判定遵循公共规则，不限于此示例。除明确列出类型外，业务字段按实际响应解析，允许 null 或缺失，不补造嵌套属性。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer / string / null | 网关状态，按下方基础规则判断；成功响应示例为 200。 |
| `errmsg` | string | 网关消息；成功响应示例为 ok。 |
| `request_id` | string | 请求追踪编号。 |
| `data` | object | 本接口业务数据。 |
| `data.total_count` | integer | 总匹配记录数；并非本页 data.items 长度，缺失时不推算。 |
| `data.items` | array<object> | 主业务记录列表。 |

#### `data.items[]` 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.items[].id` | 未固定；按运行时类型解析 | 创意查询编号；对应创意详情必须用此 id，不用 video_id 或 product_id。 |
| `data.items[].video_id` | 未固定；按运行时类型解析 | 视频编号，不替代搜索结果 id。 |
| `data.items[].product_id` | 未固定；按运行时类型解析 | 关联商品编号，不替代搜索结果 id。 |
| `data.items[].author_uid` | 未固定；按运行时类型解析 | 作者编号。 |
| `data.items[].author_unique_id` | 未固定；按运行时类型解析 | 作者账号标识。 |
| `data.items[].author_nickname` | 未固定；按运行时类型解析 | 作者昵称。 |
| `data.items[].user_avatar` | 未固定；按运行时类型解析 | 作者头像。 |
| `data.items[].follower_cnt` | 未固定；按运行时类型解析 | 粉丝数。 |
| `data.items[].video_desc` | 未固定；按运行时类型解析 | 视频描述。 |
| `data.items[].content_tag_v2` | 未固定；按运行时类型解析 | 内容标签。 |
| `data.items[].content_intent` | 未固定；按运行时类型解析 | 内容意图。 |
| `data.items[].platform` | 未固定；按运行时类型解析 | 平台。 |
| `data.items[].country_code` | 未固定；按运行时类型解析 | 市场代码。 |
| `data.items[].is_aigc_video` | 未固定；按运行时类型解析 | AIGC 标记。 |
| `data.items[].video_date` | 未固定；按运行时类型解析 | 视频日期。 |
| `data.items[].video_launch_time` | 未固定；按运行时类型解析 | 视频发布日期。 |
| `data.items[].video_duration` | 未固定；按运行时类型解析 | 视频时长。 |
| `data.items[].video_play_count` | 未固定；按运行时类型解析 | 播放量。 |
| `data.items[].video_like_count` | 未固定；按运行时类型解析 | 点赞数。 |
| `data.items[].video_comment_count` | 未固定；按运行时类型解析 | 评论数。 |
| `data.items[].video_share_count` | 未固定；按运行时类型解析 | 分享数。 |
| `data.items[].video_collect_count` | 未固定；按运行时类型解析 | 收藏数。 |
| `data.items[].video_engagement_rate` | 未固定；按运行时类型解析 | 互动率。 |
| `data.items[].video_30d_gmv` | 通常 object；以实际类型为准 | 视频近 30 天 GMV；通常含 unit 和 value，不得当作纯数值。 |
| `data.items[].video_30d_gmv.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.items[].video_30d_gmv.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |
| `data.items[].video_total_gmv` | 通常 object；以实际类型为准 | 视频累计 GMV；通常含 unit 和 value，不得当作纯数值。 |
| `data.items[].video_total_gmv.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.items[].video_total_gmv.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |
| `data.items[].video_30d_gpm` | 通常 object；以实际类型为准 | 视频近 30 天 GPM；通常含 unit 和 value，不得当作纯数值。 |
| `data.items[].video_30d_gpm.unit` | string | 当金额为对象时的原始单位，例如 US；保留返回值。 |
| `data.items[].video_30d_gpm.value` | number | 当金额为对象时的数值，计算前检查运行时类型。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / HTTP | 含义 | 处理建议 |
|---|---|---|
| 400 | 必填参数缺失等请求错误 | 根据 errmsg 补齐或修正参数，不得原样重试。 |
| 501 | 参数校验或上游调用失败 | 展示 errmsg 并停止；需要重试时先说明额外算力消耗，由用户决定。 |

本接口可能在带过滤条件时返回 `BACKEND_ERROR`，合法最小请求也可能成功；不要自动缩减过滤条件重试或连续试探付费端点，也不能据一次 5xx 推断参数枚举。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/ad-creative/creatives/search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","page":1,"pageSize":3,"hasProduct":true}'
```

示例编号可能过时；实际任务优先使用本次搜索结果。每次请求 18 算力。

---

## 接口：创意详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/ad-creative/creatives/detail`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `country` | string | 是 | 支持小写国家码 `br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn` |
| `id` | string | 是 | 创意搜索返回的 `id` |
| `include` | string | 否 | `analysis`、`embedding`；多个值用英文逗号分隔 |

网关字段使用 Java/MCP camelCase，再由服务端映射上游 snake_case；不得直接发送 `page_size`、`ad_type`、`has_product` 等上游字段。

必须使用创意搜索对象的 `id`，不得替换成视频或商品编号。`include` 可省略，`analysis` 用于内容结构；需要提取内容 `extracted_content`、匹配标签 `matched_tags`，或用于明确的相似度/机器学习下游任务的数值向量时，才请求 `embedding`。两者以英文逗号组合，例如 `analysis,embedding`。该扩展可能一并返回显著增大响应的向量；只需要内容或标签时按需提取，不在聊天中内联完整向量。

脚本选项、缓存、认证兼容与落盘行为见 [脚本运行约定](#脚本运行约定)。

### 响应结构

成功响应示例为 HTTP 200、`errcode=200`、`errmsg=ok`；成功判定遵循公共规则，不限于此示例。除明确列出类型外，业务字段按实际响应解析，允许 null 或缺失，不补造嵌套属性。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer / string / null | 网关状态，按下方基础规则判断；成功响应示例为 200。 |
| `errmsg` | string | 网关消息；成功响应示例为 ok。 |
| `request_id` | string | 请求追踪编号。 |
| `data` | object | 本接口业务数据。 |
| `data.total_count` | integer | 总匹配记录数；并非本页 data.items 长度，缺失时不推算。 |
| `data.items` | array<object> | 主业务记录列表。 |
| `data.analysis` | object | 按 include 返回内容分析。 |
| `data.analysis.items` | array<object> | 内容分析记录列表。 |
| `data.embedding` | object | 按 include 返回向量相关数据。 |
| `data.embedding.items` | array<object> | 向量相关记录列表。 |

#### `data.items[]` 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.items[].id` | 未固定；按运行时类型解析 | 创意基础记录编号。 |
| `data.items[].video_id` | 未固定；按运行时类型解析 | 视频编号，不替代搜索结果 id。 |
| `data.items[].uid` | 未固定；按运行时类型解析 | 作者编号。 |
| `data.items[].unique_id` | 未固定；按运行时类型解析 | 作者账号标识。 |
| `data.items[].nickname` | 未固定；按运行时类型解析 | 作者昵称。 |
| `data.items[].follower_count` | 未固定；按运行时类型解析 | 粉丝数。 |
| `data.items[].share_url` | 未固定；按运行时类型解析 | 分享链接。 |
| `data.items[].product_id` | 未固定；按运行时类型解析 | 关联商品编号，不替代搜索结果 id。 |
| `data.items[].product_name` | 未固定；按运行时类型解析 | 商品名称。 |
| `data.items[].product_images` | 未固定；按运行时类型解析 | 商品图片。 |

#### `data.analysis.items[]` 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.analysis.items[].id` | 未固定；按运行时类型解析 | 当前扩展数据记录编号，保留来源值。 |
| `data.analysis.items[].video_id` | 未固定；按运行时类型解析 | 视频编号，不替代搜索结果 id。 |
| `data.analysis.items[].video_uri` | 未固定；按运行时类型解析 | 视频资源 URI。 |
| `data.analysis.items[].video_cover` | 未固定；按运行时类型解析 | 视频封面。 |
| `data.analysis.items[].country_code` | 未固定；按运行时类型解析 | 市场代码。 |
| `data.analysis.items[].platform` | 未固定；按运行时类型解析 | 平台。 |
| `data.analysis.items[].is_aigc_video` | 未固定；按运行时类型解析 | AIGC 标记。 |
| `data.analysis.items[].hook_type` | 未固定；按运行时类型解析 | 开头钩子类型。 |
| `data.analysis.items[].hook_subtype` | 未固定；按运行时类型解析 | 开头钩子子类型。 |
| `data.analysis.items[].formula_type` | 未固定；按运行时类型解析 | 创意公式类型。 |
| `data.analysis.items[].formula_subtype` | 未固定；按运行时类型解析 | 创意公式子类型。 |
| `data.analysis.items[].angle_type` | 未固定；按运行时类型解析 | 内容角度类型。 |
| `data.analysis.items[].angle_subtype` | 未固定；按运行时类型解析 | 内容角度子类型。 |
| `data.analysis.items[].transcription_with_structure` | 未固定；按运行时类型解析 | 结构化转录；内部结构未约定。 |
| `data.analysis.items[].storyboards` | 未固定；按运行时类型解析 | 分镜；内部结构未约定。 |

#### `data.embedding.items[]` 字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.embedding.items[].id` | 未固定；按运行时类型解析 | 当前扩展数据记录编号，保留来源值。 |
| `data.embedding.items[].video_id` | 未固定；按运行时类型解析 | 视频编号，不替代搜索结果 id。 |
| `data.embedding.items[].video_uri` | 未固定；按运行时类型解析 | 视频资源 URI。 |
| `data.embedding.items[].video_cover` | 未固定；按运行时类型解析 | 视频封面。 |
| `data.embedding.items[].country_code` | 未固定；按运行时类型解析 | 市场代码。 |
| `data.embedding.items[].platform` | 未固定；按运行时类型解析 | 平台。 |
| `data.embedding.items[].extracted_content` | 未固定；按运行时类型解析 | 提取的内容。 |
| `data.embedding.items[].matched_tags` | 未固定；按运行时类型解析 | 匹配标签。 |
| `data.embedding.items[].embedding` | array<number> | 机器处理用数值向量，不在聊天内联。 |

`data.items[]` 还可包含以下组合数据；其确切键名与嵌套结构未约定，应保留真实返回，不能凭语义构造字段：

| 数据内容 | 类型 | 说明 |
|---|---|---|
| 商品类目、价格、评分、佣金、状态 | 未约定 | 键名、类型和内部属性未约定，以真实响应为准。 |
| 商品销量与 GMV | 未约定 | 按来源口径解析；金额通常为 unit/value 对象。 |
| 视频播放、互动及近 30 天销售指标 | 未约定 | 具体键名未约定，保留原始字段与单位。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / HTTP | 含义 | 处理建议 |
|---|---|---|
| 400 | 必填参数缺失等请求错误 | 根据 errmsg 补齐或修正参数，不得原样重试。 |
| 501 | 参数校验或上游调用失败 | 展示 errmsg 并停止；需要重试时先说明额外算力消耗，由用户决定。 |

错误时保留已取得的数据并停止，不自动连续试探付费端点。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/ad-creative/creatives/detail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7668708053428047118","include":"analysis,embedding"}'
```

示例编号可能过时；实际任务优先使用本次搜索结果。每次请求 9 算力。

---

## 脚本运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值与说明 |
|---|---|---|---|
| JSON 参数 | JSON | 是 | 原样传给网关，未知字段不擅自移除。 |
| --inline | CLI flag | 否 | 强制全量输出，同时保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存读写，强制请求，可能再次消耗算力；仅在用户明确同意额外消耗或调试时使用。 |

业务封装 `_chuhaijiang.py` 提供唯一的 24 小时本地缓存，缓存路径为 `<cwd>/linkfox/.cache/linkfox-chuhaijiang-tiktok-ads/`。缓存键由规范化 JSON 中的 version=1、apiBase、完整 apiPath、apiKeyFingerprint 和全部 params 生成，身份指纹使用 SHA-256；当前工作目录也自然隔离缓存。符合当前键格式和成功判定的有效缓存可命中，命中输出 `Cache hit`，不发送付费请求。仅 HTTP 200 且符合公共 errcode 基本规则、没有显式失败标志的对象可缓存；成功空列表可以缓存，HTTP、业务和连接失败均不缓存。损坏或超过 24 小时的缓存不复用。业务封装始终给 `call_api.run` 加 `--no-cache`，关闭公共调用器缓存，不叠加第二层缓存。

认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；基础地址支持 `LINKFOX_TOOL_GATEWAY` 覆盖，默认使用正式网关。透传头为 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置为空串。Windows 标准输出与错误输出使用 UTF-8。

完整原始响应落到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-ads-<timestamp>.json`，不移除未知字段，按 `SESSION_ID`（去除首尾空白）聚合；未设置时为进程内稳定的自动会话标识。维护会话 `_meta.json` 和根目录 `index.jsonl`。不回退到家目录或临时目录，当前目录不可写时在请求前报错；禁止将工作目录选在 `/tmp`。上游同名 `_cache` 字段原样保存，不作为本地缓存命中依据。小响应全量输出，大响应摘要优先 `data.items` / 业务 `*.items`，跳过 embedding/vector，最多取前三条记录。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-chuhaijiang-tiktok-ads",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
