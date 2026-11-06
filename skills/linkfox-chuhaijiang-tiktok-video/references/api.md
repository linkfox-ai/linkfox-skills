# 出海匠 TikTok 视频市场情报 接口说明

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

## 业务脚本约定

四个接口共用以下 CLI、缓存和落盘行为。

### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | object | 是 | 首个位置参数，使用对应接口请求表。脚本不改写筛选值。 |
| --inline | CLI flag | 否 | 强制完整打印，仍落盘且仍复用有效缓存。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存读写；可能再次消耗算力，仅在用户明确同意额外消耗或调试时使用。 |

Python 3.9+，业务脚本仅使用标准库。优先读取 LINKFOX_AGENT_API_KEY，兼容 LINKFOXAGENT_API_KEY；网关未配置时回退正式地址。透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME，会话标识去除首尾空白。

业务缓存 TTL 为 24 小时，位于 `<cwd>/linkfox/.cache/linkfox-chuhaijiang-tiktok-video/`；按当前目录、密钥 SHA-256 指纹、去尾斜线网关、接口端点和完整参数隔离。命中输出 `Cache hit`，成功空结果可缓存，HTTP 或业务失败不缓存，过期/损坏缓存视为未命中。公共调用器始终传 `--no-cache`，仅由业务封装负责缓存；此内部选项不关闭业务默认缓存。

落盘路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-video-<timestamp>.json`，并维护 `_meta.json` 与 `index.jsonl`；缺少 SESSION_ID 时进程内生成稳定会话标识。当前目录不可写时报错，不回退 /tmp；请求前检查输出可写性。响应不超过 8000 UTF-8 字节完整打印，超过则显示摘要及最大列表前 3 条；连续调用保留微秒级文件名。

### 失败处理与缓存限制

- HTTP/业务 403 为无权限，不归入普通认证或充值流程。HTTP 4xx 核对对应接口字段、类型、站点与分页；HTTP 5xx 或超时保留错误并停止，不自动连续重试付费请求。
- 业务 401/402 或消息显示鉴权/算力不足时读取 `onboarding.md`。响应消息、追踪标识和原始错误应保留；脚本以 JSON 回显网关错误，不打印网络异常堆栈。
- 基础响应状态与可缓存性分开：顶层 `error`、`success=false` 或失败的 `code` / `errorCode` 标记不写业务缓存；不改变公共响应码判断。

## 接口：视频搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/videos/search`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| country | string | 是 | 小写请求上下文/站点码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`；返回行的 `country_code` 可不同，分别保留。 |
| keyword | string | 否 | 视频描述或相关关键词。 |
| category | string | 否 | 视频分类，只能使用供应商认可值；Java 契约未公开枚举。 |
| isCommercial | boolean | 否 | 是否带货。 |
| minViews | number | 否 | 播放量下限。 |
| maxViews | number | 否 | 播放量上限。 |
| minLikes | number | 否 | 点赞量下限。 |
| maxLikes | number | 否 | 点赞量上限。 |
| minGmv30d | number | 否 | 30 天 GMV 下限。 |
| maxGmv30d | number | 否 | 30 天 GMV 上限。 |
| minEngagement | number | 否 | 互动率下限；契约未声明单位或范围，保持原始口径，不自行换算百分比。 |
| maxEngagement | number | 否 | 互动率上限；契约未声明单位或范围，保持原始口径，不自行换算百分比。 |
| accountType | integer | 否 | 只允许 `0`、`3`、`4`，业务名称未公开。 |
| sort | string | 否 | `field:asc` 或 `field:desc`，默认 `views:desc`；除 views 外的完整字段枚举未公开。 |
| page | integer | 否 | 页码，从 1 开始；默认值未声明。 |
| pageSize | integer | 否 | 每页数量，最大 10；默认值未声明。先使用小页验证，再按用户范围查询。 |

#### 参数约束与使用限制

只发送用户明确要求的筛选字段，不为了空结果自动放宽范围、换关键词或翻页。网关使用 camelCase；上游别名 `is_commercial`、`min_views`、`max_views`、`min_likes`、`max_likes`、`min_gmv_30d`、`max_gmv_30d`、`min_engagement`、`max_engagement`、`account_type`、`page_size` 不用于网关调用。上述范围筛选可与 `accountType=0`、`sort=views:desc` 组合使用。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 业务状态；正常响应示例为 200；判断遵守公共响应码基本规则。 |
| errmsg | string | 消息，正常响应示例为 `ok`。 |
| request_id | string | 请求追踪标识，示例格式为 UUID。 |
| error | string / 未声明 | 本地连接或解析失败时的错误信息，仅错误场景可能存在；其他顶层 error 标记按原值保留。 |
| details | 任意 JSON / string | 非对象 JSON 响应或 HTTP 非 JSON 错误正文等诊断内容，仅错误场景可能存在。 |
| success / code / errorCode | 未声明 | 脚本兼容的可选业务标记，并非已确认的正常响应字段；失败标记不缓存，正常响应状态仍按公共规则判断。 |
| data | object | 本接口数据容器。 |
| data.total_count | integer | 业务总条数，可大于本页列表长度。 |
| data.items | array<object> | 本页记录；字段可能缺失或为 null，不补零。 |

#### data.items[] 记录字段

字段可缺失或为 null。表中标注“解释性类型”的类型仅用于理解字段，不代表接口保证；以实际响应为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | string | 视频 ID。 |
| video_desc | string（解释性类型，非契约保证） | 视频文案。 |
| share_url | string（解释性类型，非契约保证） | 公开 TikTok 链接。 |
| video_launch_time | number（时间戳）（解释性类型，非契约保证） | 发布时间，单位未声明；保留原值。 |
| video_duration | number（解释性类型，非契约保证） | 视频时长，单位未声明。 |
| author_id | string（解释性类型，非契约保证） | 作者 ID。 |
| author_unique_id | string（解释性类型，非契约保证） | 作者账号。 |
| author_nickname | string（解释性类型，非契约保证） | 作者昵称。 |
| country_code | string（解释性类型，非契约保证） | 返回行地区，不保证等于请求 country。 |
| account_type | integer（解释性类型，非契约保证） | 账号类型。 |
| video_play_count | number（解释性类型，非契约保证） | 累计播放数。 |
| video_like_count | number（解释性类型，非契约保证） | 累计点赞数。 |
| video_comment_count | number（解释性类型，非契约保证） | 评论数。 |
| video_share_count | number（解释性类型，非契约保证） | 分享数。 |
| video_collect_count | number（解释性类型，非契约保证） | 收藏数。 |
| video_engagement_rate | number（解释性类型，非契约保证） | 十进制互动率。 |
| video_total_like_count_to_follower_count_ratio | number（解释性类型，非契约保证） | 点赞与粉丝比率。 |
| video_30d_gpm | object | 30 天每千次播放 GMV，含 unit、value；不是百分比。 |
| video_30d_gpm.unit | string | 供应商返回单位，例如 US；不擅自等同货币代码。 |
| video_30d_gpm.value | number | 供应商返回原始值。 |
| is_ad | boolean（解释性类型，非契约保证） | 广告标记，可能缺失，以实际返回为准。 |
| is_aigc_video | boolean（解释性类型，非契约保证） | AIGC 标记，可能缺失，以实际返回为准。 |
| 商品、30 天销量和 GMV 相关字段（字段名未声明） | 未声明（解释性类型，非契约保证） | isCommercial=true 时可返回这些指标；只按实际返回展示，不补造名称或类型。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 分类枚举未公开；使用未经供应商确认的 beauty 或作者分类标签可能返回 `errcode=501`，消息含上游 HTTP 502 / BACKEND_ERROR。停止并要求供应商认可的分类值，不猜值重试。

### curl 示例

```bash
curl --request POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/videos/search"  \
  --header "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"  \
  --header "Content-Type: application/json"  \
  --header "User-Agent: LinkFox-Skill/2.0"  \
  --data '{"country":"us","keyword":"beauty","isCommercial":true,"sort":"views:desc","page":1,"pageSize":3}'  \
  --max-time 150
```

## 接口：视频详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/videos/detail`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| country | string | 是 | 小写请求上下文/站点码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`；返回行的 `country_code` 可不同，分别保留。 |
| id | string | 是 | 视频 ID，19 位标识必须按 JSON 字符串传递，避免精度损失。 |
| include | string | 否 | 仅需要标准化核心指标时使用 `core`。 |

#### 参数约束与使用限制

资料在 data.items[]；include=core 才额外提供 data.core.items[]。资料和核心字段的完整类型与所有键未声明，表内未声明内容以实际响应为准，不臆造枚举。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 业务状态；正常响应示例为 200；判断遵守公共响应码基本规则。 |
| errmsg | string | 消息，正常响应示例为 `ok`。 |
| request_id | string | 请求追踪标识，示例格式为 UUID。 |
| error | string / 未声明 | 本地连接或解析失败时的错误信息，仅错误场景可能存在；其他顶层 error 标记按原值保留。 |
| details | 任意 JSON / string | 非对象 JSON 响应或 HTTP 非 JSON 错误正文等诊断内容，仅错误场景可能存在。 |
| success / code / errorCode | 未声明 | 脚本兼容的可选业务标记，并非已确认的正常响应字段；失败标记不缓存，正常响应状态仍按公共规则判断。 |
| data | object | 本接口数据容器。 |
| data.total_count | integer | 业务总条数，可大于本页列表长度。 |
| data.items | array<object> | 本页记录；字段可能缺失或为 null，不补零。 |
| data.core | object | include=core 时可返回核心指标容器。 |
| data.core.items | array<object> | 标准化核心指标列表。 |
| data.core.items[].core_video_play_count | number（解释性类型，非契约保证） | 核心播放数。 |
| data.core.items[].core_video_like_count | number（解释性类型，非契约保证） | 核心点赞数。 |
| data.core.items[].core_video_comment_count | number（解释性类型，非契约保证） | 核心评论数。 |
| data.core.items[].core_video_share_count | number（解释性类型，非契约保证） | 核心分享数。 |
| data.core.items[].core_video_collect_count | number（解释性类型，非契约保证） | 核心收藏数。 |
| data.core.items[].core_video_engagement_rate | number（解释性类型，非契约保证） | 核心互动率。 |
| data.core.items[].core_video_like_play_ratio | number（解释性类型，非契约保证） | 点赞播放比。 |
| data.core.items[].core_video_30d_gpm | object | 核心 30 天 GPM，保留 unit/value。 |
| data.core.items[].core_video_30d_gpm.unit | string（解释性类型，非契约保证） | 原始单位。 |
| data.core.items[].core_video_30d_gpm.value | number（解释性类型，非契约保证） | 原始值。 |
| data.core.items[].core_country_code | string（解释性类型，非契约保证） | 核心指标返回地区。 |

#### data.items[] 记录字段

字段可缺失或为 null。表中标注“解释性类型”的类型仅用于理解字段，不代表接口保证；以实际响应为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| video_cover | 未声明 | 视频封面，保留实际结构。 |
| user_avatar | 未声明 | 达人头像，保留实际结构。 |
| video_duration | number（解释性类型，非契约保证） | 视频时长，单位未声明。 |
| unique_id | string（解释性类型，非契约保证） | 达人账号。 |
| nickname | string（解释性类型，非契约保证） | 达人昵称。 |
| follower_count | number（解释性类型，非契约保证） | 粉丝数。 |
| had_product | 未声明 | 是否有关联商品标记，不替代关联商品实际查询。 |
| has_comment | 未声明 | 是否有评论标记。 |
| share_url | string（解释性类型，非契约保证） | 公开视频链接。 |
| video_count | number（解释性类型，非契约保证） | 达人视频数。 |
| video_avg_play_count | number（解释性类型，非契约保证） | 平均播放。 |
| video_avg_like_count | number（解释性类型，非契约保证） | 平均点赞。 |
| author_avg_engagement_rate | number（解释性类型，非契约保证） | 达人平均互动率。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 示例视频标识可能失效；需要重新定位时使用用户指定的新标识或按其要求搜索，不无条件替换目标。

### curl 示例

```bash
curl --request POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/videos/detail"  \
  --header "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"  \
  --header "Content-Type: application/json"  \
  --header "User-Agent: LinkFox-Skill/2.0"  \
  --data '{"country":"us","id":"6788833646091504902","include":"core"}'  \
  --max-time 150
```

## 接口：视频带货商品

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/videos/related-products`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| country | string | 是 | 小写请求上下文/站点码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`；返回行的 `country_code` 可不同，分别保留。 |
| id | string | 是 | 视频 ID，19 位标识必须按 JSON 字符串传递，避免精度损失。 |
| page | integer | 否 | 页码，从 1 开始；默认值未声明。 |
| pageSize | integer | 否 | 每页数量，最大 10；默认值未声明。先使用小页验证，再按用户范围查询。 |

#### 参数约束与使用限制

仅供应商索引中关联商品的视频有带货商品数据。保留返回商品地区、价格与金额对象及字段前缀；未声明的类型和字段名不能由展示概念反推。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 业务状态；正常响应示例为 200；判断遵守公共响应码基本规则。 |
| errmsg | string | 消息，正常响应示例为 `ok`。 |
| request_id | string | 请求追踪标识，示例格式为 UUID。 |
| error | string / 未声明 | 本地连接或解析失败时的错误信息，仅错误场景可能存在；其他顶层 error 标记按原值保留。 |
| details | 任意 JSON / string | 非对象 JSON 响应或 HTTP 非 JSON 错误正文等诊断内容，仅错误场景可能存在。 |
| success / code / errorCode | 未声明 | 脚本兼容的可选业务标记，并非已确认的正常响应字段；失败标记不缓存，正常响应状态仍按公共规则判断。 |
| data | object | 本接口数据容器。 |
| data.total_count | integer | 业务总条数，可大于本页列表长度。 |
| data.items | array<object> | 本页记录；字段可能缺失或为 null，不补零。 |

#### data.items[] 记录字段

字段可缺失或为 null。表中标注“解释性类型”的类型仅用于理解字段，不代表接口保证；以实际响应为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| tiktok_video_detail_product_id | string（解释性类型，非契约保证） | 商品 ID，标识按字符串保留。 |
| tiktok_product_detail_product_name | string（解释性类型，非契约保证） | 商品名称。 |
| tiktok_product_detail_product_rating | number（解释性类型，非契约保证） | 商品评分。 |
| 类目、图片、SKU、库存与状态（字段名未声明） | 未声明 | 响应可包含这些商品信息，具体字段名和结构未声明；按实际返回保留，不猜测。 |
| tiktok_product_detail_floor_price | object | 价格下限，保留 unit/value。 |
| ceiling_price（完整键名未声明） | object | 价格上限；完整键名未声明，保留实际返回键名，不将推定的前缀视为契约。 |
| tiktok_video_detail_product_total_gmv | object | 商品总 GMV，金额原始结构不变。 |
| tiktok_video_detail_video_30d_gmv | object | 视频 30 天 GMV，金额原始结构不变。 |
| tiktok_product_detail_commission_rate | number（解释性类型，非契约保证） | 佣金率，未声明单位，不自行缩放。 |
| tiktok_video_detail_product_total_sold_count | number（解释性类型，非契约保证） | 商品总销量。 |
| tiktok_video_detail_video_id | string（解释性类型，非契约保证） | 关联视频 ID。 |
| tiktok_video_detail_video_30d_sold_count | number（解释性类型，非契约保证） | 视频 30 天销量。 |
| 地区（字段名未声明） | 未声明 | 展示商品返回的地区，保留实际键名和值。 |
| tiktok_product_detail_floor_price.unit | string（解释性类型，非契约保证） | 供应商返回单位，不擅自等同币种或换汇。 |
| tiktok_product_detail_floor_price.value | number（解释性类型，非契约保证） | 供应商返回的原始数值。 |
| ceiling_price.unit（完整键名未声明） | string（解释性类型，非契约保证） | 供应商返回单位，不擅自等同币种或换汇。 |
| ceiling_price.value（完整键名未声明） | number（解释性类型，非契约保证） | 供应商返回的原始数值。 |
| tiktok_video_detail_product_total_gmv.unit | string（解释性类型，非契约保证） | 供应商返回单位，不擅自等同币种或换汇。 |
| tiktok_video_detail_product_total_gmv.value | number（解释性类型，非契约保证） | 供应商返回的原始数值。 |
| tiktok_video_detail_video_30d_gmv.unit | string（解释性类型，非契约保证） | 供应商返回单位，不擅自等同币种或换汇。 |
| tiktok_video_detail_video_30d_gmv.value | number（解释性类型，非契约保证） | 供应商返回的原始数值。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 普通非带货视频可能返回 errcode=200、total_count=0、items=[]，是有效空结果；不得宣称带货或擅自替换视频。

### curl 示例

```bash
curl --request POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/videos/related-products"  \
  --header "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"  \
  --header "Content-Type: application/json"  \
  --header "User-Agent: LinkFox-Skill/2.0"  \
  --data '{"country":"us","id":"7672655263672864013","page":1,"pageSize":3}'  \
  --max-time 150
```

## 接口：视频评论

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/videos/reviews`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| country | string | 是 | 小写请求上下文/站点码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`；返回行的 `country_code` 可不同，分别保留。 |
| id | string | 是 | 视频 ID，19 位标识必须按 JSON 字符串传递，避免精度损失。 |
| page | integer | 否 | 页码，从 1 开始；默认值未声明。 |
| pageSize | integer | 否 | 每页数量，最大 10；默认值未声明。先使用小页验证，再按用户范围查询。 |

#### 参数约束与使用限制

公开评论可能不完整、被删除、多语言或暂不可用。标识按字符串保留，头像对象保留 thumb_url 和 url；时间戳单位未声明。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 业务状态；正常响应示例为 200；判断遵守公共响应码基本规则。 |
| errmsg | string | 消息，正常响应示例为 `ok`。 |
| request_id | string | 请求追踪标识，示例格式为 UUID。 |
| error | string / 未声明 | 本地连接或解析失败时的错误信息，仅错误场景可能存在；其他顶层 error 标记按原值保留。 |
| details | 任意 JSON / string | 非对象 JSON 响应或 HTTP 非 JSON 错误正文等诊断内容，仅错误场景可能存在。 |
| success / code / errorCode | 未声明 | 脚本兼容的可选业务标记，并非已确认的正常响应字段；失败标记不缓存，正常响应状态仍按公共规则判断。 |
| data | object | 本接口数据容器。 |
| data.total_count | integer | 业务总条数，可大于本页列表长度。 |
| data.items | array<object> | 本页记录；字段可能缺失或为 null，不补零。 |

#### data.items[] 记录字段

字段可缺失或为 null。表中标注“解释性类型”的类型仅用于理解字段，不代表接口保证；以实际响应为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| tiktok_video_detail_comment_id | string（解释性类型，非契约保证） | 评论 ID。 |
| tiktok_video_detail_comment_text | string（解释性类型，非契约保证） | 评论文本。 |
| tiktok_video_detail_comment_create_time | number（时间戳，单位未声明） | 创建时间，保留原始时间戳。 |
| tiktok_video_detail_comment_like_count | number（解释性类型，非契约保证） | 点赞数。 |
| tiktok_video_detail_comment_reply_count | number（解释性类型，非契约保证） | 回复数。 |
| tiktok_video_detail_comment_unique_id | string（解释性类型，非契约保证） | 评论者账号。 |
| tiktok_video_detail_comment_nickname | string（解释性类型，非契约保证） | 评论者昵称。 |
| tiktok_video_detail_comment_user_avatar | object | 头像对象。 |
| tiktok_video_detail_comment_user_avatar.thumb_url | string（解释性类型，非契约保证） | 头像缩略图 URL。 |
| tiktok_video_detail_comment_user_avatar.url | string（解释性类型，非契约保证） | 头像 URL。 |
| tiktok_video_detail_video_id | string（解释性类型，非契约保证） | 所属视频 ID。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 空评论列表如实报告，不据此断言视频从未有评论，不自动翻页或更换目标。

### curl 示例

```bash
curl --request POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/videos/reviews"  \
  --header "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}"  \
  --header "Content-Type: application/json"  \
  --header "User-Agent: LinkFox-Skill/2.0"  \
  --data '{"country":"us","id":"6788833646091504902","page":1,"pageSize":3}'  \
  --max-time 150
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-chuhaijiang-tiktok-video",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
