# 出海匠 TikTok 直播带货情报 接口说明

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

## 接口：直播搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/lives/search`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未声明 | 必填小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| page | integer | 否 | 1 | 页码，最小 1。 |
| pageSize | integer | 否 | 未声明 | 每页数量最大 10；Java 路由未声明默认值。 |
| keyword | string | 否 | 未声明 | 搜索关键词。 |
| category | string | 否 | 未声明 | 直播分类。 |
| productCategory | string | 否 | 未声明 | 商品分类。 |
| isLiving | boolean | 否 | 未声明 | 是否正在直播；筛选条件不保证稍后展示时仍在直播。 |
| isCommercial | boolean | 否 | 未声明 | 是否带货。 |
| minSold | number | 否 | 未声明 | 最低销量。 |
| maxSold | number | 否 | 未声明 | 最高销量。 |
| minGmv | number | 否 | 未声明 | 最低GMV。 |
| maxGmv | number | 否 | 未声明 | 最高GMV。 |
| minAudience | number | 否 | 未声明 | 最低观众数。 |
| maxAudience | number | 否 | 未声明 | 最高观众数。 |
| sort | string | 否 | `gmv:desc` | 格式为 `field:asc` 或 `field:desc`；`gmv:desc` 为已验证示例。 |

#### 脚本选项与运行约定

| 选项 / 行为 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 脚本第一个位置参数；使用上表的 camelCase 请求字段，不能发送上游 snake_case 别名，网关负责映射。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存读写并发起真实请求，可能再次计费；仅在用户明确同意额外消耗或调试时使用。 |
| 业务响应缓存 | 本地文件 | 否 | 默认 24 小时；按当前工作目录、API Key 指纹、网关、端点及完整参数隔离，缓存键由上述调用信息生成；命中输出 `Cache hit`，不会新发付费请求。HTTP 或业务失败不缓存，业务成功的空结果可以缓存。 |
| 缓存成功过滤 | 运行规则 | 否 | 满足公共正常响应规则，且无非空 `error`、无 `success=false`；另须存在业务脚本识别的成功标记（`success=true` 或 `errcode` / `errorCode` / `code`）。其中 `errorCode` / `code` 如存在，仅接受业务脚本接受的 `0`、`200`、`ok`、`success`，不用于放宽 `errcode` 的公共规则。 |
| 公共调用器 | 内部运行规则 | 否 | 业务封装调用 `call_api.run` 时固定传入 `--no-cache`，只由业务层管理业务响应缓存，不另存第二层响应缓存。 |
| 会话与输出 | 本地文件 | 否 | 完整响应写入当前工作目录的 `linkfox/<日期>/<session>/data/`，按 `SESSION_ID` 聚合；未设置时生成进程内稳定会话标识。文件使用微秒时间戳避免同秒覆盖；工作目录不可写时报错，不回退到家目录或临时目录。 |

认证优先使用 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`；网关由 `LINKFOX_TOOL_GATEWAY` 覆盖，未设置时使用公共默认值。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串；`SESSION_ID` 去除两端空白。HTTP 错误和网络失败以结构化内容展示，不自动重试。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务码，按公共响应码基本规则判断；成功示例为 200。 |
| errmsg | string | 网关消息；成功示例为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 业务数据，结构见本接口下表。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| data.total_count | integer | 匹配直播总数。 |
| data.items | array | 直播记录列表；可为空。 |
| data.items[].id | string | 直播房间 ID，后续详情或关联商品查询沿用此值。 |
| data.items[].title | string | 直播标题。 |
| data.items[].room_link | string | 公共直播链接。 |
| data.items[].user_id | string | 主播 ID。 |
| data.items[].user_unique_id | string | 主播账号。 |
| data.items[].user_nickname | string | 主播昵称。 |
| data.items[].user_category_label | string | 主播分类标签。 |
| data.items[].country_code | string | 记录实际国家代码，优先于请求市场作为记录所属市场。 |
| data.items[].start_time | integer | 开始时间，epoch 毫秒时间戳。 |
| data.items[].end_time | integer | 结束时间，epoch 毫秒时间戳。 |
| data.items[].cover | object | 直播封面，含 `url`、`thumb_url`。 |
| data.items[].product_count | integer | 直播推广商品数。 |
| data.items[].total_sold_count | integer | 直播总销量。 |
| data.items[].total_user | integer | 总观众数。 |
| data.items[].max_user_count | integer | 峰值观众数。 |
| data.items[].new_follow_count | integer | 新增粉丝数。 |
| data.items[].gmv | object | 直播 GMV，含金额 `unit`、`value`。 |
| data.items[].gpm | object | 每千观众 GMV，含金额 `unit`、`value`。 |
| data.items[].opm | number | 每千观众订单数。 |
| data.items[].most_product_category_label | string | 主要商品分类标签。 |
| data.items[].cover.url | string | 原图 URL。 |
| data.items[].cover.thumb_url | string | 缩略图 URL。 |
| data.items[].gmv.unit | string | 服务商返回的原始金额单位，例如 `US`；不自行换算或改标。 |
| data.items[].gmv.value | number | 原始金额数值。 |
| data.items[].gpm.unit | string | 服务商返回的原始金额单位，例如 `US`；不自行换算或改标。 |
| data.items[].gpm.value | number | 原始金额数值。 |

字段可能缺失或为 `null`；入口保留完整原始 JSON 和未知字段，不补造缺失值。金额对象保留 `unit` 和 `value`。成功响应示例（2026-08-29）为 HTTP 200、`errcode=200`、`errmsg=ok`；该日期的示例不代表实时状态。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `data.items[]` 为空时如实报告无匹配直播，`data.total_count` 为匹配总数。`isLiving` 只是筛选，不作为展示时仍在直播的证明。
- `501` 表示参数校验失败，依据 `errmsg` 修正字段，不自动连续试探付费接口。其他异常保留完整消息并停止；需要重试时先说明可能再次计费并取得用户同意。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/lives/search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","isCommercial":true,"sort":"gmv:desc","page":1,"pageSize":3}'
```

## 接口：直播详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/lives/detail`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未声明 | 必填小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| id | string | 是 | 未声明 | 直播房间 ID；从搜索记录的 `data.items[].id` 取得。19 位标识必须作为 JSON 字符串传递，避免精度损失。 |
| include | string | 否 | 未声明 | 可选扩展 `core`；多个值用英文逗号分隔，本技能仅说明 `core` 的含义，不推断其他扩展值。 |

#### 脚本选项与运行约定

| 选项 / 行为 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 脚本第一个位置参数；使用上表的 camelCase 请求字段，不能发送上游 snake_case 别名，网关负责映射。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存读写并发起真实请求，可能再次计费；仅在用户明确同意额外消耗或调试时使用。 |
| 业务响应缓存 | 本地文件 | 否 | 默认 24 小时；按当前工作目录、API Key 指纹、网关、端点及完整参数隔离，缓存键由上述调用信息生成；命中输出 `Cache hit`，不会新发付费请求。HTTP 或业务失败不缓存，业务成功的空结果可以缓存。 |
| 缓存成功过滤 | 运行规则 | 否 | 满足公共正常响应规则，且无非空 `error`、无 `success=false`；另须存在业务脚本识别的成功标记（`success=true` 或 `errcode` / `errorCode` / `code`）。其中 `errorCode` / `code` 如存在，仅接受业务脚本接受的 `0`、`200`、`ok`、`success`，不用于放宽 `errcode` 的公共规则。 |
| 公共调用器 | 内部运行规则 | 否 | 业务封装调用 `call_api.run` 时固定传入 `--no-cache`，只由业务层管理业务响应缓存，不另存第二层响应缓存。 |
| 会话与输出 | 本地文件 | 否 | 完整响应写入当前工作目录的 `linkfox/<日期>/<session>/data/`，按 `SESSION_ID` 聚合；未设置时生成进程内稳定会话标识。文件使用微秒时间戳避免同秒覆盖；工作目录不可写时报错，不回退到家目录或临时目录。 |

认证优先使用 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`；网关由 `LINKFOX_TOOL_GATEWAY` 覆盖，未设置时使用公共默认值。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串；`SESSION_ID` 去除两端空白。HTTP 错误和网络失败以结构化内容展示，不自动重试。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务码，按公共响应码基本规则判断；成功示例为 200。 |
| errmsg | string | 网关消息；成功示例为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 业务数据，结构见本接口下表。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| data.items | array | 基础详情与主播信息列表。 |
| data.items[].id | string | 直播房间 ID。 |
| data.items[].title | string | 直播标题。 |
| data.items[].room_link | string | 公共直播链接。 |
| data.items[].country_code | string | 记录国家代码；保留原值。 |
| data.items[].start_time | integer | 开始时间，epoch 毫秒时间戳。 |
| data.items[].end_time | integer | 结束时间，epoch 毫秒时间戳。 |
| data.items[].cover | object | 直播封面，含 `url`、`thumb_url`。 |
| data.items[].user_avatar | object | 主播头像，含 `url`、`thumb_url`。 |
| data.items[].user_id | string | 主播 ID。 |
| data.items[].user_nickname | string | 主播昵称。 |
| data.items[].user_follower_count | integer | 主播粉丝数。 |
| data.items[].user_live_count | integer | 主播直播场次。 |
| data.items[].user_avg_audience_count | number | 主播历史平均观众。 |
| data.items[].user_avg_max_audience_count | number | 主播历史平均峰值观众。 |
| data.items[].most_product_category_label | string | 主要商品分类标签。 |
| data.items[].cover.url | string | 原图 URL。 |
| data.items[].cover.thumb_url | string | 缩略图 URL。 |
| data.items[].user_avatar.url | string | 原图 URL。 |
| data.items[].user_avatar.thumb_url | string | 缩略图 URL。 |

#### 核心指标 `data.core.items[]`

| 字段 | 类型 | 说明 |
|---|---|---|
| data.core | object | 请求 `include=core` 时可返回的核心指标数据集。 |
| data.core.items | array | 标准化核心指标列表。 |
| data.core.items[].id | 以实际返回类型为准 | 核心记录标识；保留实际返回类型，长标识按字符串处理。 |
| data.core.items[].core_room_id | 以实际返回类型为准 | 关联直播房间标识；长标识按字符串处理。 |
| data.core.items[].core_country_code | 以实际返回类型为准 | 核心指标所属国家代码。 |
| data.core.items[].core_gmv | object | GMV 金额对象。 |
| data.core.items[].core_gpm | object | 每千观众 GMV 金额对象。 |
| data.core.items[].core_avg_price | object | 平均价格金额对象。 |
| data.core.items[].core_product_count | 以实际返回类型为准 | 推广商品数。 |
| data.core.items[].core_sold_product_id_count | 以实际返回类型为准 | 有成交的商品标识数。 |
| data.core.items[].core_total_sold_count | 以实际返回类型为准 | 总销量。 |
| data.core.items[].core_total_user | 以实际返回类型为准 | 总观众数。 |
| data.core.items[].core_avg_online_viewer | 以实际返回类型为准 | 平均在线观众数。 |
| data.core.items[].core_max_user_count | 以实际返回类型为准 | 峰值观众数。 |
| data.core.items[].core_new_follow_count | 以实际返回类型为准 | 新增粉丝数。 |
| data.core.items[].core_follower_conversion_rate | 小数比率（JSON 类型以实际返回为准） | 粉丝转化率，例如 `0.0007` 表示 `0.07%`。 |
| data.core.items[].core_gmv.unit | string | 服务商返回的原始金额单位，例如 `US`；不自行换算或改标。 |
| data.core.items[].core_gmv.value | number | 原始金额数值。 |
| data.core.items[].core_gpm.unit | string | 服务商返回的原始金额单位，例如 `US`；不自行换算或改标。 |
| data.core.items[].core_gpm.value | number | 原始金额数值。 |
| data.core.items[].core_avg_price.unit | string | 服务商返回的原始金额单位，例如 `US`；不自行换算或改标。 |
| data.core.items[].core_avg_price.value | number | 原始金额数值。 |

字段可能缺失或为 `null`；入口保留完整原始 JSON 和未知字段，不补造缺失值。金额对象保留 `unit` 和 `value`。成功响应示例（2026-08-29）为 HTTP 200、`errcode=200`、`errmsg=ok`；该日期的示例不代表实时状态。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 基础信息位于 `data.items[]`；核心指标位于 `data.core.items[]`，仅请求 `include=core` 时可返回。不得把基础信息缺失或核心指标缺失解释为全零。
- `501` 表示参数校验失败，依据 `errmsg` 修正字段，不自动连续试探付费接口。其他异常保留完整消息并停止；需要重试时先说明可能再次计费并取得用户同意。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/lives/detail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7643101948819835678","include":"core"}'
```

## 接口：直播关联商品

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/lives/related-products`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| country | string | 是 | 未声明 | 必填小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| id | string | 是 | 未声明 | 直播房间 ID；从搜索记录的 `data.items[].id` 取得。19 位标识必须作为 JSON 字符串传递，避免精度损失。 |
| page | integer | 否 | 1 | 页码，最小 1。 |
| pageSize | integer | 否 | 未声明 | 每页数量最大 10；Java 路由未声明默认值。 |

#### 脚本选项与运行约定

| 选项 / 行为 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 脚本第一个位置参数；使用上表的 camelCase 请求字段，不能发送上游 snake_case 别名，网关负责映射。 |
| --inline | CLI flag | 否 | 强制完整打印，仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存读写并发起真实请求，可能再次计费；仅在用户明确同意额外消耗或调试时使用。 |
| 业务响应缓存 | 本地文件 | 否 | 默认 24 小时；按当前工作目录、API Key 指纹、网关、端点及完整参数隔离，缓存键由上述调用信息生成；命中输出 `Cache hit`，不会新发付费请求。HTTP 或业务失败不缓存，业务成功的空结果可以缓存。 |
| 缓存成功过滤 | 运行规则 | 否 | 满足公共正常响应规则，且无非空 `error`、无 `success=false`；另须存在业务脚本识别的成功标记（`success=true` 或 `errcode` / `errorCode` / `code`）。其中 `errorCode` / `code` 如存在，仅接受业务脚本接受的 `0`、`200`、`ok`、`success`，不用于放宽 `errcode` 的公共规则。 |
| 公共调用器 | 内部运行规则 | 否 | 业务封装调用 `call_api.run` 时固定传入 `--no-cache`，只由业务层管理业务响应缓存，不另存第二层响应缓存。 |
| 会话与输出 | 本地文件 | 否 | 完整响应写入当前工作目录的 `linkfox/<日期>/<session>/data/`，按 `SESSION_ID` 聚合；未设置时生成进程内稳定会话标识。文件使用微秒时间戳避免同秒覆盖；工作目录不可写时报错，不回退到家目录或临时目录。 |

认证优先使用 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`；网关由 `LINKFOX_TOOL_GATEWAY` 覆盖，未设置时使用公共默认值。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串；`SESSION_ID` 去除两端空白。HTTP 错误和网络失败以结构化内容展示，不自动重试。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务码，按公共响应码基本规则判断；成功示例为 200。 |
| errmsg | string | 网关消息；成功示例为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 业务数据，结构见本接口下表。 |

| 字段 | 类型 | 说明 |
|---|---|---|
| data.total_count | integer | 匹配商品总数。 |
| data.items | array | 该直播关联的商品列表；没有索引关系时可能为空。 |
| data.items[].id | string | 商品 ID（此处不是直播房间 ID）。 |
| data.items[].tiktok_live_detail_product_id | string | 商品 ID。 |
| data.items[].tiktok_live_detail_product_title | string | 商品标题。 |
| data.items[].tiktok_live_detail_product_images | object | 商品图片，含 `url`、`thumb_url`。 |
| data.items[].tiktok_live_detail_product_country_code | string | 商品实际国家代码。 |
| data.items[].tiktok_live_detail_product_floor_price | object | 最低价，含金额 `unit`、`value`。 |
| data.items[].tiktok_live_detail_product_ceiling_price | object | 最高价，含金额 `unit`、`value`。 |
| data.items[].tiktok_live_detail_product_sold_count | integer | 本场直播关联销量，不代表全市场销量。 |
| data.items[].tiktok_live_detail_product_gmv | object | 本场直播关联 GMV，含金额 `unit`、`value`。 |
| data.items[].tiktok_live_detail_product_commission_rate_num | number | 佣金率小数；可能缺失。 |
| data.items[].tiktok_live_detail_product_conversion_rate | number | 转化率小数。 |
| data.items[].tiktok_live_detail_product_seller_id | string | 卖家 ID。 |
| data.items[].tiktok_live_detail_product_seller_name | string | 卖家名称。 |
| data.items[].tiktok_live_detail_product_seller_avatar | object | 卖家头像；子字段以实际返回为准，不推断未列出的字段。 |
| data.items[].tiktok_live_detail_product_seller_info | array | 卖家说明文本列表。 |
| data.items[].tiktok_live_detail_product_l1_category | string | 一级商品分类标签。 |
| data.items[].tiktok_live_detail_product_l2_category | string | 二级商品分类标签。 |
| data.items[].tiktok_live_detail_product_l3_category | string | 三级商品分类标签。 |
| data.items[].tiktok_live_detail_product_seller_category_name_label | string | 卖家分类标签。 |
| data.items[].tiktok_live_detail_product_images.url | string | 原图 URL。 |
| data.items[].tiktok_live_detail_product_images.thumb_url | string | 缩略图 URL。 |
| data.items[].tiktok_live_detail_product_floor_price.unit | string | 服务商返回的原始金额单位，例如 `US`；不自行换算或改标。 |
| data.items[].tiktok_live_detail_product_floor_price.value | number | 原始金额数值。 |
| data.items[].tiktok_live_detail_product_ceiling_price.unit | string | 服务商返回的原始金额单位，例如 `US`；不自行换算或改标。 |
| data.items[].tiktok_live_detail_product_ceiling_price.value | number | 原始金额数值。 |
| data.items[].tiktok_live_detail_product_gmv.unit | string | 服务商返回的原始金额单位，例如 `US`；不自行换算或改标。 |
| data.items[].tiktok_live_detail_product_gmv.value | number | 原始金额数值。 |

字段可能缺失或为 `null`；入口保留完整原始 JSON 和未知字段，不补造缺失值。金额对象保留 `unit` 和 `value`。成功响应示例（2026-08-29）为 HTTP 200、`errcode=200`、`errmsg=ok`；该日期的示例不代表实时状态。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 仅返回服务商已索引的本场商品关系；空列表不能证明直播没有卖过商品。销量和 GMV 为本场直播关联数据。`ceiling_price`、`seller_name`、`l2_category`、`l3_category` 等后缀在本表中带有 `tiktok_live_detail_product_` 前缀；解析以实际返回字段为准，不补造别名。
- `501` 表示参数校验失败，依据 `errmsg` 修正字段，不自动连续试探付费接口。其他异常保留完整消息并停止；需要重试时先说明可能再次计费并取得用户同意。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/lives/related-products" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7643101948819835678","page":1,"pageSize":3}'
```

示例中的直播 ID 为 2026-08-29 的查询示例值，公开市场标识可能失效；任务需要搜索时使用新搜索记录，不为复现示例自动额外付费查询。

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-chuhaijiang-tiktok-live",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
