# 出海匠 TikTok Shop 店铺情报 接口说明

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

## 接口：店铺搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/sellers/search`

### 请求参数

本接口每次请求消耗 18 算力，命中业务缓存时不发起新的付费请求。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `page` | integer | 否 | 未指定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未指定 | 搜索/关联最大 10。 |
| `keyword` | string | 否 | - | 店铺搜索关键词。 |
| `category` | string | 否 | - | 商品分类 ID。 |
| `sellerType` | string | 否 | - | 卖家类型；使用服务支持的类型值，不预设枚举；不可与榜单 shopType 互换。 |
| `minRating` | number | 否 | - | 最低店铺评分。 |
| `maxRating` | number | 否 | - | 最高店铺评分。 |
| `minSold7d` | number | 否 | - | 近 7 天销量下限。 |
| `maxSold7d` | number | 否 | - | 近 7 天销量上限。 |
| `minGmv7d` | number | 否 | - | 近 7 天 GMV 下限。 |
| `maxGmv7d` | number | 否 | - | 近 7 天 GMV 上限。 |
| `sort` | string | 否 | `gmv_7d:desc` | field:asc 或 field:desc；服务默认 gmv_7d:desc，该排序值有成功调用样本。 |

#### 脚本选项与运行约定

| 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `--inline` | CLI flag | 否 | 默认关闭；强制完整打印，同时仍保存响应，不绕过缓存。 |
| `--no-cache` | CLI flag | 否 | 默认关闭；跳过业务缓存读写并强制请求，可能再次消耗算力，仅在用户明确同意额外消耗或调试时使用。 |

请求 JSON 使用 camelCase；网关再映射为上游 snake_case，不传 page_size、seller_type、shop_type 等内部别名。不编造未支持的过滤条件，也不通过反复调用其他付费接口补足条件。

业务入口提供 24 小时成功响应缓存，按当前工作目录、网关、API Key 的 SHA-256 指纹、端点和完整参数隔离；命中输出 `Cache hit`，不产生新请求。HTTP 或业务失败不缓存，业务成功的空结果可缓存；不会自动更改条件或连续重试。缓存读写均校验业务状态：响应必须是对象且无 error、无 success=false，并具有 success=true 或 errcode/errorCode/code 标记。存在的 errcode 按响应码基础规则判定：null、空字符串（含纯空白）或 200–299（数字或三位 ASCII 数字字符串）可缓存，0、false 及其他非空值不可缓存；存在的 errorCode/code 保留兼容判定，只接受 0、200、ok、success。旧缓存中的失败状态也不复用。

业务封装经公共 `call_api.run` 调用，始终传入 `--no-cache`，关闭公共调用器的第二层缓存及重复落盘；业务入口负责完整响应、摘要和会话文件。响应写入当前目录的 `linkfox/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-shop-<微秒时间戳>.json`，session 优先使用去除首尾空白的 SESSION_ID，否则进程内生成稳定值；同步维护 `_meta.json` 和 `index.jsonl`。禁止写入 /tmp，不回退到家目录或临时目录，当前目录不可写时报错。

完整 JSON 以 UTF-8 保存；响应不超过 8000 字节时完整打印，超过时只打印摘要，含顶层字段、可用计数、最大列表长度与前 3 条样本。签名 URL 可能过期，未知字段不删除；不输出 API Key。

Authorization 密钥优先读取 LINKFOX_AGENT_API_KEY，未配置时回退 LINKFOXAGENT_API_KEY；透传 SESSION_ID（去首尾空白）、MESSAGE_ID、MODE_ID、APP_NAME，未设置为空字符串。网关基础地址去尾部斜杠，请求超时 150 秒。

### 响应结构

2026-08-29 的七个接口调用样本均为 HTTP 200、errcode=200 且含非空业务数据；样本不保证后续查询有数据。脚本 `chuhaijiang_seller_search.py` 保留完整原始 JSON。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer；兼容 string / null | 网关业务码；成功样本为 200，统一按响应码基础规则判断。 |
| `errmsg` | string | 网关消息；成功样本为 ok。 |
| `request_id` | string | 请求追踪 ID。 |
| `data` | object | 接口业务数据。 |
| `data.total_count` | 未限定 | 匹配记录总数；类型以实际返回为准。 |
| `data.items` | array<object> | 主列表；元素见下表。 |

#### data.items[] 记录字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 店铺 ID，可传给详情和三个关联接口。 |
| `shop_name` | string | 店铺名称。 |
| `region` | string | 店铺市场。 |
| `shop_rating` | number | 店铺评分。 |
| `shop_main_category` | string | 主营分类 ID。 |
| `shop_product_count` | integer | 商品数。 |
| `shop_total_sold_count` | number | 累计销量。 |
| `shop_total_gmv` | object | 累计 GMV，含 unit、value。 |
| `shop_sold_count_for_last_7_days` | number | 近 7 天销量。 |
| `shop_gmv_for_last_7_days` | object | 近 7 天 GMV。 |
| `total_related_creator_count` | number | 累计关联达人数。 |
| `seller_business_info` | array<string> | 商家主体信息。 |
| `sold_count_trend` | array<object> | 销量趋势点，含 timestamp、value。 |

#### sold_count_trend[] 趋势点

| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | 未限定 | 趋势时间戳，单位以实际响应为准。 |
| `value` | 未限定 | 对应时间点的销量。 |

#### 金额对象（适用于本接口实际返回的金额字段）

| 字段 | 类型 | 说明 |
|---|---|---|
| `unit` | 未限定 | 返回的单位标识，示例为字符串 US；保留原值，不自行转换币种。 |
| `value` | 未限定 | 金额值，示例为数字 31；按运行时类型解析。 |

金额通常为 `{ "unit": "US", "value": 31 }`，并不保证所有金额字段均为此结构。字段可缺失、为 null 或新增；标为“未限定”的类型不作为服务端固定 schema，按实际响应解析。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode=501` 表示参数校验失败；非法国家码可返回此码。根据 errmsg 核对参数，不自动改条件重试付费接口。
- 空结果根据 data.total_count 与 data.items 判断，不因空列表判定系统错误。HTTP 或业务错误均保存并回显，不缓存失败结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/sellers/search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","keyword":"beauty","minRating":4,"page":1,"pageSize":3,"sort":"gmv_7d:desc"}'
```

## 接口：店铺详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/sellers/detail`

### 请求参数

本接口每次请求消耗 9 算力，命中业务缓存时不发起新的付费请求。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `id` | string | 是 | - | 店铺 ID；作为字符串发送和保存，避免 64 位标识精度丢失。 |
| `include` | string | 否 | - | core、channel，或用英文逗号组合 core,channel / channel,core。 |

#### 脚本选项与运行约定

| 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `--inline` | CLI flag | 否 | 默认关闭；强制完整打印，同时仍保存响应，不绕过缓存。 |
| `--no-cache` | CLI flag | 否 | 默认关闭；跳过业务缓存读写并强制请求，可能再次消耗算力，仅在用户明确同意额外消耗或调试时使用。 |

请求 JSON 使用 camelCase；网关再映射为上游 snake_case，不传 page_size、seller_type、shop_type 等内部别名。不编造未支持的过滤条件，也不通过反复调用其他付费接口补足条件。

业务入口提供 24 小时成功响应缓存，按当前工作目录、网关、API Key 的 SHA-256 指纹、端点和完整参数隔离；命中输出 `Cache hit`，不产生新请求。HTTP 或业务失败不缓存，业务成功的空结果可缓存；不会自动更改条件或连续重试。缓存读写均校验业务状态：响应必须是对象且无 error、无 success=false，并具有 success=true 或 errcode/errorCode/code 标记。存在的 errcode 按响应码基础规则判定：null、空字符串（含纯空白）或 200–299（数字或三位 ASCII 数字字符串）可缓存，0、false 及其他非空值不可缓存；存在的 errorCode/code 保留兼容判定，只接受 0、200、ok、success。旧缓存中的失败状态也不复用。

业务封装经公共 `call_api.run` 调用，始终传入 `--no-cache`，关闭公共调用器的第二层缓存及重复落盘；业务入口负责完整响应、摘要和会话文件。响应写入当前目录的 `linkfox/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-shop-<微秒时间戳>.json`，session 优先使用去除首尾空白的 SESSION_ID，否则进程内生成稳定值；同步维护 `_meta.json` 和 `index.jsonl`。禁止写入 /tmp，不回退到家目录或临时目录，当前目录不可写时报错。

完整 JSON 以 UTF-8 保存；响应不超过 8000 字节时完整打印，超过时只打印摘要，含顶层字段、可用计数、最大列表长度与前 3 条样本。签名 URL 可能过期，未知字段不删除；不输出 API Key。

Authorization 密钥优先读取 LINKFOX_AGENT_API_KEY，未配置时回退 LINKFOXAGENT_API_KEY；透传 SESSION_ID（去首尾空白）、MESSAGE_ID、MODE_ID、APP_NAME，未设置为空字符串。网关基础地址去尾部斜杠，请求超时 150 秒。

### 响应结构

2026-08-29 的七个接口调用样本均为 HTTP 200、errcode=200 且含非空业务数据；样本不保证后续查询有数据。脚本 `chuhaijiang_seller_detail.py` 保留完整原始 JSON。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer；兼容 string / null | 网关业务码；成功样本为 200，统一按响应码基础规则判断。 |
| `errmsg` | string | 网关消息；成功样本为 ok。 |
| `request_id` | string | 请求追踪 ID。 |
| `data` | object | 接口业务数据。 |
| `data.total_count` | 未限定 | 匹配记录总数；类型以实际返回为准。 |
| `data.items` | array<object> | 主列表；元素见下表。 |
| `data.core` | object | 可选核心数据。 |
| `data.core.total_count` | 未限定 | 核心记录数；单店响应样本为 1。 |
| `data.core.items` | array<object> | 可选核心列表。 |
| `data.channel` | object | 可选渠道数据。 |
| `data.channel.total_count` | 未限定 | 渠道记录数；单店响应样本为 1。 |
| `data.channel.items` | array<object> | 可选渠道列表。 |

#### data.items[] 基础详情

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 店铺 ID。 |
| `seller_id` | string | 店铺 ID。 |
| `shop_name` | string | 店铺名称。 |
| `region` | string | 店铺市场。 |
| `shop_rating` | number | 店铺评分。 |
| `shop_total_gmv` | object | 累计 GMV。 |
| `shop_main_category` | string | 主营分类 ID。 |
| `business_info` | array<string> | 商家主体。 |
| `seller_avatar` | object | 头像对象，含 thumb_url、url。 |
| `create_time` | integer | 创建时间，毫秒时间戳。 |
| `last_update_time` | integer | 最近更新时间，毫秒时间戳。 |
| `creator_user_id` | string | 店铺关联账号 ID。 |
| `creator_user_name` | string | 店铺关联账号用户名。 |
| `creator_nickname` | string | 店铺关联账号昵称。 |
| `creator_role` | integer | 账号角色值。 |

#### seller_avatar 头像

| 字段 | 类型 | 说明 |
|---|---|---|
| `thumb_url` | 未限定 | 缩略图链接。 |
| `url` | 未限定 | 原图链接。 |

#### data.core.items[] 核心详情

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 未限定 | 记录标识。 |
| `core_seller_id` | 未限定 | 核心数据的店铺标识。 |
| `core_region` | 未限定 | 市场。 |
| `core_seller_shop_product_count` | 未限定 | 当前商品数。 |
| `core_seller_shop_total_product_count` | 未限定 | 累计商品数。 |
| `core_shop_total_sold_count` | 未限定 | 累计销量。 |
| `core_seller_shop_total_gmv` | 未限定 | 累计 GMV。 |
| `core_seller_sold_count_for_last_30_days` | 未限定 | 近 30 天销量。 |
| `core_seller_gmv_for_last_30_days` | 未限定 | 近 30 天 GMV。 |
| `core_seller_total_related_creator_count` | 未限定 | 累计关联达人数。 |
| `core_seller_total_related_live_creator_count` | 未限定 | 累计直播关联达人数。 |
| `core_seller_total_related_video_creator_count` | 未限定 | 累计视频关联达人数。 |
| `core_seller_total_related_shop_creator_count` | 未限定 | 累计橱窗关联达人数。 |

#### data.channel.items[] 渠道详情

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 未限定 | 记录标识。 |
| `channel_seller_id` | 未限定 | 渠道数据的店铺标识。 |
| `channel_seller_sold_count_for_last_30_days` | 未限定 | 近 30 天店铺销量。 |
| `channel_seller_gmv_for_last_30_days` | 未限定 | 近 30 天店铺 GMV。 |
| `channel_video_30d_sold_count` | 未限定 | 近 30 天视频销量。 |
| `channel_video_30d_gmv` | 未限定 | 近 30 天视频 GMV。 |
| `channel_live_30d_sold_count` | 未限定 | 近 30 天直播销量。 |
| `channel_live_30d_gmv` | 未限定 | 近 30 天直播 GMV。 |
| `channel_product_card_30d_sold_count` | 未限定 | 近 30 天商品卡销量。 |
| `channel_product_card_30d_gmv` | 未限定 | 近 30 天商品卡 GMV。 |
| `channel_personal_creator_30d_sold_count` | 未限定 | 近 30 天个人达人销量。 |
| `channel_personal_creator_30d_gmv` | 未限定 | 近 30 天个人达人 GMV。 |
| `channel_seller_creator_30d_sold_count` | 未限定 | 近 30 天商家达人销量。 |
| `channel_seller_creator_30d_gmv` | 未限定 | 近 30 天商家达人 GMV。 |

#### 金额对象（适用于本接口实际返回的金额字段）

| 字段 | 类型 | 说明 |
|---|---|---|
| `unit` | 未限定 | 返回的单位标识，示例为字符串 US；保留原值，不自行转换币种。 |
| `value` | 未限定 | 金额值，示例为数字 31；按运行时类型解析。 |

金额通常为 `{ "unit": "US", "value": 31 }`，并不保证所有金额字段均为此结构。字段可缺失、为 null 或新增；标为“未限定”的类型不作为服务端固定 schema，按实际响应解析。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode=501` 表示参数校验失败；非法国家码可返回此码。根据 errmsg 核对参数，不自动改条件重试付费接口。
- 空结果根据 data.total_count 与 data.items 判断，不因空列表判定系统错误。HTTP 或业务错误均保存并回显，不缓存失败结果。
- 请求包含 core、channel 时读取 data.items、data.core.items 和 data.channel.items 三个分支；核心与渠道指标保留各自时间口径。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/sellers/detail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7495205878591949358","include":"core,channel"}'
```

## 接口：关联达人

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/sellers/related-creators`

### 请求参数

本接口每次请求消耗 18 算力，命中业务缓存时不发起新的付费请求。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `id` | string | 是 | - | 店铺 ID；作为字符串发送和保存，避免 64 位标识精度丢失。 |
| `page` | integer | 否 | 未指定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未指定 | 搜索/关联最大 10。 |

#### 脚本选项与运行约定

| 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `--inline` | CLI flag | 否 | 默认关闭；强制完整打印，同时仍保存响应，不绕过缓存。 |
| `--no-cache` | CLI flag | 否 | 默认关闭；跳过业务缓存读写并强制请求，可能再次消耗算力，仅在用户明确同意额外消耗或调试时使用。 |

请求 JSON 使用 camelCase；网关再映射为上游 snake_case，不传 page_size、seller_type、shop_type 等内部别名。不编造未支持的过滤条件，也不通过反复调用其他付费接口补足条件。

业务入口提供 24 小时成功响应缓存，按当前工作目录、网关、API Key 的 SHA-256 指纹、端点和完整参数隔离；命中输出 `Cache hit`，不产生新请求。HTTP 或业务失败不缓存，业务成功的空结果可缓存；不会自动更改条件或连续重试。缓存读写均校验业务状态：响应必须是对象且无 error、无 success=false，并具有 success=true 或 errcode/errorCode/code 标记。存在的 errcode 按响应码基础规则判定：null、空字符串（含纯空白）或 200–299（数字或三位 ASCII 数字字符串）可缓存，0、false 及其他非空值不可缓存；存在的 errorCode/code 保留兼容判定，只接受 0、200、ok、success。旧缓存中的失败状态也不复用。

业务封装经公共 `call_api.run` 调用，始终传入 `--no-cache`，关闭公共调用器的第二层缓存及重复落盘；业务入口负责完整响应、摘要和会话文件。响应写入当前目录的 `linkfox/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-shop-<微秒时间戳>.json`，session 优先使用去除首尾空白的 SESSION_ID，否则进程内生成稳定值；同步维护 `_meta.json` 和 `index.jsonl`。禁止写入 /tmp，不回退到家目录或临时目录，当前目录不可写时报错。

完整 JSON 以 UTF-8 保存；响应不超过 8000 字节时完整打印，超过时只打印摘要，含顶层字段、可用计数、最大列表长度与前 3 条样本。签名 URL 可能过期，未知字段不删除；不输出 API Key。

Authorization 密钥优先读取 LINKFOX_AGENT_API_KEY，未配置时回退 LINKFOXAGENT_API_KEY；透传 SESSION_ID（去首尾空白）、MESSAGE_ID、MODE_ID、APP_NAME，未设置为空字符串。网关基础地址去尾部斜杠，请求超时 150 秒。

### 响应结构

2026-08-29 的七个接口调用样本均为 HTTP 200、errcode=200 且含非空业务数据；样本不保证后续查询有数据。脚本 `chuhaijiang_seller_related_creators.py` 保留完整原始 JSON。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer；兼容 string / null | 网关业务码；成功样本为 200，统一按响应码基础规则判断。 |
| `errmsg` | string | 网关消息；成功样本为 ok。 |
| `request_id` | string | 请求追踪 ID。 |
| `data` | object | 接口业务数据。 |
| `data.total_count` | 未限定 | 匹配记录总数；类型以实际返回为准。 |
| `data.items` | array<object> | 主列表；元素见下表。 |

#### data.items[] 记录字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 未限定 | 关联记录标识。 |
| `tiktok_seller_detail_creator_user_id` | 未限定 | 达人用户 ID。 |
| `tiktok_seller_detail_creator_unique_id` | 未限定 | 达人唯一账号标识。 |
| `tiktok_seller_detail_creator_nickname` | 未限定 | 达人昵称。 |
| `tiktok_seller_detail_creator_country_code` | 未限定 | 达人国家码。 |
| `tiktok_seller_detail_creator_account_type` | 未限定 | 账号类型值。 |
| `tiktok_seller_detail_creator_category_label` | 未限定 | 分类标签。 |
| `tiktok_seller_detail_creator_user_avatar` | 未限定 | 达人头像；嵌套结构以实际返回为准。 |
| `tiktok_seller_detail_creator_seller_id` | 未限定 | 关联店铺 ID。 |
| `tiktok_seller_detail_creator_youtube_channel_id` | 未限定 | YouTube 频道 ID。 |
| `tiktok_seller_detail_creator_follower_count` | 未限定 | 粉丝数。 |
| `tiktok_seller_detail_creator_total_favorited` | 未限定 | 累计获赞数。 |
| `tiktok_seller_detail_creator_video_count` | 未限定 | 视频数。 |
| `tiktok_seller_detail_creator_related_total_video` | 未限定 | 关联视频总数。 |
| `tiktok_seller_detail_creator_author_avg_like_cnt` | 未限定 | 平均点赞数。 |
| `tiktok_seller_detail_creator_author_avg_play_cnt` | 未限定 | 平均播放数。 |
| `tiktok_seller_detail_creator_author_total_play_cnt` | 未限定 | 累计播放数。 |
| `tiktok_seller_detail_creator_author_avg_engagement_rate` | 未限定 | 平均互动率。 |
| `tiktok_seller_detail_creator_by_live` | 未限定 | 直播带货渠道标记。 |
| `tiktok_seller_detail_creator_by_shop` | 未限定 | 橱窗带货渠道标记。 |
| `tiktok_seller_detail_creator_by_video` | 未限定 | 视频带货渠道标记。 |
| `tiktok_seller_detail_creator_video_7d_gmv` | 未限定 | 近 7 天视频 GMV。 |
| `tiktok_seller_detail_creator_video_30d_gmv` | 未限定 | 近 30 天视频 GMV。 |
| `tiktok_seller_detail_live_7d_gmv` | 未限定 | 近 7 天直播 GMV；字段名不含 creator，不得纠正名称。 |
| `tiktok_seller_detail_creator_live_30d_gmv` | 未限定 | 近 30 天直播 GMV。 |
| `tiktok_seller_detail_total_video_live_7d_gmv` | 未限定 | 近 7 天视频和直播总 GMV；保留原字段名。 |
| `tiktok_seller_detail_creator_total_video_live_30d_gmv` | 未限定 | 近 30 天视频和直播总 GMV。 |
| `tiktok_seller_detail_creator_bio_email` | 未限定 | 简介邮箱，可能为空或缺失。 |

#### 金额对象（适用于本接口实际返回的金额字段）

| 字段 | 类型 | 说明 |
|---|---|---|
| `unit` | 未限定 | 返回的单位标识，示例为字符串 US；保留原值，不自行转换币种。 |
| `value` | 未限定 | 金额值，示例为数字 31；按运行时类型解析。 |

金额通常为 `{ "unit": "US", "value": 31 }`，并不保证所有金额字段均为此结构。字段可缺失、为 null 或新增；标为“未限定”的类型不作为服务端固定 schema，按实际响应解析。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode=501` 表示参数校验失败；非法国家码可返回此码。根据 errmsg 核对参数，不自动改条件重试付费接口。
- 空结果根据 data.total_count 与 data.items 判断，不因空列表判定系统错误。HTTP 或业务错误均保存并回显，不缓存失败结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/sellers/related-creators" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7495205878591949358","page":1,"pageSize":10}'
```

## 接口：关联商品

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/sellers/related-products`

### 请求参数

本接口每次请求消耗 18 算力，命中业务缓存时不发起新的付费请求。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `id` | string | 是 | - | 店铺 ID；作为字符串发送和保存，避免 64 位标识精度丢失。 |
| `page` | integer | 否 | 未指定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未指定 | 搜索/关联最大 10。 |

#### 脚本选项与运行约定

| 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `--inline` | CLI flag | 否 | 默认关闭；强制完整打印，同时仍保存响应，不绕过缓存。 |
| `--no-cache` | CLI flag | 否 | 默认关闭；跳过业务缓存读写并强制请求，可能再次消耗算力，仅在用户明确同意额外消耗或调试时使用。 |

请求 JSON 使用 camelCase；网关再映射为上游 snake_case，不传 page_size、seller_type、shop_type 等内部别名。不编造未支持的过滤条件，也不通过反复调用其他付费接口补足条件。

业务入口提供 24 小时成功响应缓存，按当前工作目录、网关、API Key 的 SHA-256 指纹、端点和完整参数隔离；命中输出 `Cache hit`，不产生新请求。HTTP 或业务失败不缓存，业务成功的空结果可缓存；不会自动更改条件或连续重试。缓存读写均校验业务状态：响应必须是对象且无 error、无 success=false，并具有 success=true 或 errcode/errorCode/code 标记。存在的 errcode 按响应码基础规则判定：null、空字符串（含纯空白）或 200–299（数字或三位 ASCII 数字字符串）可缓存，0、false 及其他非空值不可缓存；存在的 errorCode/code 保留兼容判定，只接受 0、200、ok、success。旧缓存中的失败状态也不复用。

业务封装经公共 `call_api.run` 调用，始终传入 `--no-cache`，关闭公共调用器的第二层缓存及重复落盘；业务入口负责完整响应、摘要和会话文件。响应写入当前目录的 `linkfox/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-shop-<微秒时间戳>.json`，session 优先使用去除首尾空白的 SESSION_ID，否则进程内生成稳定值；同步维护 `_meta.json` 和 `index.jsonl`。禁止写入 /tmp，不回退到家目录或临时目录，当前目录不可写时报错。

完整 JSON 以 UTF-8 保存；响应不超过 8000 字节时完整打印，超过时只打印摘要，含顶层字段、可用计数、最大列表长度与前 3 条样本。签名 URL 可能过期，未知字段不删除；不输出 API Key。

Authorization 密钥优先读取 LINKFOX_AGENT_API_KEY，未配置时回退 LINKFOXAGENT_API_KEY；透传 SESSION_ID（去首尾空白）、MESSAGE_ID、MODE_ID、APP_NAME，未设置为空字符串。网关基础地址去尾部斜杠，请求超时 150 秒。

### 响应结构

2026-08-29 的七个接口调用样本均为 HTTP 200、errcode=200 且含非空业务数据；样本不保证后续查询有数据。脚本 `chuhaijiang_seller_related_products.py` 保留完整原始 JSON。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer；兼容 string / null | 网关业务码；成功样本为 200，统一按响应码基础规则判断。 |
| `errmsg` | string | 网关消息；成功样本为 ok。 |
| `request_id` | string | 请求追踪 ID。 |
| `data` | object | 接口业务数据。 |
| `data.total_count` | 未限定 | 匹配记录总数；类型以实际返回为准。 |
| `data.items` | array<object> | 主列表；元素见下表。 |

#### data.items[] 记录字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 未限定 | 关联记录标识。 |
| `tiktok_seller_product_product_id` | 未限定 | 商品 ID。 |
| `tiktok_seller_product_product_name` | 未限定 | 商品名称。 |
| `tiktok_seller_detail_product_link` | 未限定 | 商品链接。 |
| `tiktok_seller_detail_product_detail_link` | 未限定 | 商品详情链接。 |
| `tiktok_seller_product_region` | 未限定 | 商品市场。 |
| `tiktok_seller_product_l1_category` | 未限定 | 一级分类。 |
| `tiktok_seller_product_l2_category` | 未限定 | 二级分类。 |
| `tiktok_seller_product_l3_category` | 未限定 | 三级分类。 |
| `tiktok_seller_product_product_status` | 未限定 | 商品状态值。 |
| `tiktok_seller_product_create_time` | 未限定 | 创建时间；时间单位以实际响应为准。 |
| `tiktok_seller_product_product_sold_count` | 未限定 | 累计销量。 |
| `tiktok_seller_product_product_sold_count_for_last_7_days` | 未限定 | 近 7 天销量。 |
| `tiktok_seller_product_product_gmv` | 未限定 | 累计 GMV。 |
| `tiktok_seller_product_product_gmv_for_last_7_days` | 未限定 | 近 7 天 GMV。 |
| `tiktok_seller_product_product_rating` | 未限定 | 商品评分。 |
| `tiktok_seller_product_review_count` | 未限定 | 评论数。 |
| `tiktok_seller_product_commission_rate` | 未限定 | 佣金比例；保留原返回口径。 |
| `tiktok_seller_product_total_related_creator_count` | 未限定 | 累计关联达人数。 |
| `tiktok_seller_product_total_related_video_count` | 未限定 | 累计关联视频数。 |
| `tiktok_seller_product_floor_price` | 未限定 | 价格下限。 |
| `tiktok_seller_product_ceiling_price` | 未限定 | 价格上限。 |
| `tiktok_seller_product_product_images[]` | array | 商品图片列表，元素含 thumb_url、url。 |
| `tiktok_seller_product_product_skus[]` | array | SKU 列表，嵌套字段见下表。 |
| `tiktok_seller_product_product_sku_props[]` | array | 规格列表，嵌套字段见下表。 |

#### tiktok_seller_product_product_images[] 图片元素

| 字段 | 类型 | 说明 |
|---|---|---|
| `thumb_url` | 未限定 | 缩略图链接。 |
| `url` | 未限定 | 原图链接。 |

#### tiktok_seller_product_product_skus[] SKU 元素

| 字段 | 类型 | 说明 |
|---|---|---|
| `sku_id` | 未限定 | SKU 标识，保留完整精度。 |
| `price` | object | SKU 价格信息，字段见下表。 |
| `sku_sale_props[]` | array | SKU 销售属性；元素字段以实际返回为准。 |
| `stock` | 未限定 | 库存。 |
| `sale_prop_value_ids` | 未限定 | 销售规格值标识集合；容器类型以实际返回为准。 |
| `status` | 未限定 | SKU 状态值。 |

#### SKU 元素的 price

| 字段 | 类型 | 说明 |
|---|---|---|
| `original_price` | 未限定 | 原价表示。 |
| `original_price_value` | 未限定 | 原价值。 |
| `real_price` | 未限定 | 实际价格。 |
| `discount` | 未限定 | 折扣值。 |
| `unit_price_desc` | 未限定 | 单价说明。 |

#### tiktok_seller_product_product_sku_props[] 规格元素

| 字段 | 类型 | 说明 |
|---|---|---|
| `prop_id` | 未限定 | 规格 ID。 |
| `prop_name` | 未限定 | 规格名称。 |
| `has_image` | 未限定 | 是否有图标记。 |
| `sale_prop_values[]` | array | 规格值列表。 |

#### sale_prop_values[] 规格值元素

| 字段 | 类型 | 说明 |
|---|---|---|
| `prop_value_id` | 未限定 | 规格值 ID。 |
| `prop_value` | 未限定 | 规格值。 |
| `image` | 未限定 | 规格图片；嵌套结构以实际返回为准。 |

#### 金额对象（适用于本接口实际返回的金额字段）

| 字段 | 类型 | 说明 |
|---|---|---|
| `unit` | 未限定 | 返回的单位标识，示例为字符串 US；保留原值，不自行转换币种。 |
| `value` | 未限定 | 金额值，示例为数字 31；按运行时类型解析。 |

金额通常为 `{ "unit": "US", "value": 31 }`，并不保证所有金额字段均为此结构。字段可缺失、为 null 或新增；标为“未限定”的类型不作为服务端固定 schema，按实际响应解析。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode=501` 表示参数校验失败；非法国家码可返回此码。根据 errmsg 核对参数，不自动改条件重试付费接口。
- 空结果根据 data.total_count 与 data.items 判断，不因空列表判定系统错误。HTTP 或业务错误均保存并回显，不缓存失败结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/sellers/related-products" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7495205878591949358","page":1,"pageSize":10}'
```

## 接口：关联视频

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/sellers/related-videos`

### 请求参数

本接口每次请求消耗 18 算力，命中业务缓存时不发起新的付费请求。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `id` | string | 是 | - | 店铺 ID；作为字符串发送和保存，避免 64 位标识精度丢失。 |
| `page` | integer | 否 | 未指定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未指定 | 搜索/关联最大 10。 |

#### 脚本选项与运行约定

| 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `--inline` | CLI flag | 否 | 默认关闭；强制完整打印，同时仍保存响应，不绕过缓存。 |
| `--no-cache` | CLI flag | 否 | 默认关闭；跳过业务缓存读写并强制请求，可能再次消耗算力，仅在用户明确同意额外消耗或调试时使用。 |

请求 JSON 使用 camelCase；网关再映射为上游 snake_case，不传 page_size、seller_type、shop_type 等内部别名。不编造未支持的过滤条件，也不通过反复调用其他付费接口补足条件。

业务入口提供 24 小时成功响应缓存，按当前工作目录、网关、API Key 的 SHA-256 指纹、端点和完整参数隔离；命中输出 `Cache hit`，不产生新请求。HTTP 或业务失败不缓存，业务成功的空结果可缓存；不会自动更改条件或连续重试。缓存读写均校验业务状态：响应必须是对象且无 error、无 success=false，并具有 success=true 或 errcode/errorCode/code 标记。存在的 errcode 按响应码基础规则判定：null、空字符串（含纯空白）或 200–299（数字或三位 ASCII 数字字符串）可缓存，0、false 及其他非空值不可缓存；存在的 errorCode/code 保留兼容判定，只接受 0、200、ok、success。旧缓存中的失败状态也不复用。

业务封装经公共 `call_api.run` 调用，始终传入 `--no-cache`，关闭公共调用器的第二层缓存及重复落盘；业务入口负责完整响应、摘要和会话文件。响应写入当前目录的 `linkfox/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-shop-<微秒时间戳>.json`，session 优先使用去除首尾空白的 SESSION_ID，否则进程内生成稳定值；同步维护 `_meta.json` 和 `index.jsonl`。禁止写入 /tmp，不回退到家目录或临时目录，当前目录不可写时报错。

完整 JSON 以 UTF-8 保存；响应不超过 8000 字节时完整打印，超过时只打印摘要，含顶层字段、可用计数、最大列表长度与前 3 条样本。签名 URL 可能过期，未知字段不删除；不输出 API Key。

Authorization 密钥优先读取 LINKFOX_AGENT_API_KEY，未配置时回退 LINKFOXAGENT_API_KEY；透传 SESSION_ID（去首尾空白）、MESSAGE_ID、MODE_ID、APP_NAME，未设置为空字符串。网关基础地址去尾部斜杠，请求超时 150 秒。

### 响应结构

2026-08-29 的七个接口调用样本均为 HTTP 200、errcode=200 且含非空业务数据；样本不保证后续查询有数据。脚本 `chuhaijiang_seller_related_videos.py` 保留完整原始 JSON。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer；兼容 string / null | 网关业务码；成功样本为 200，统一按响应码基础规则判断。 |
| `errmsg` | string | 网关消息；成功样本为 ok。 |
| `request_id` | string | 请求追踪 ID。 |
| `data` | object | 接口业务数据。 |
| `data.total_count` | 未限定 | 匹配记录总数；类型以实际返回为准。 |
| `data.items` | array<object> | 主列表；元素见下表。 |

#### data.items[] 记录字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 未限定 | 关联记录标识。 |
| `tiktok_seller_detail_video_id` | 未限定 | 视频 ID。 |
| `tiktok_seller_detail_video_seller_id` | 未限定 | 关联店铺 ID。 |
| `tiktok_seller_detail_video_desc` | 未限定 | 视频描述。 |
| `tiktok_seller_detail_video_launch_time` | 未限定 | 发布时间；单位以实际响应为准。 |
| `tiktok_seller_detail_video_duration` | 未限定 | 视频时长；单位以实际响应为准。 |
| `tiktok_seller_detail_cover_url` | 未限定 | 视频封面链接。 |
| `tiktok_seller_detail_share_url` | 未限定 | 视频分享链接。 |
| `tiktok_seller_detail_video_play_count` | 未限定 | 累计播放数。 |
| `tiktok_seller_detail_video_30d_play_count` | 未限定 | 近 30 天播放数。 |
| `tiktok_seller_detail_video_like_count` | 未限定 | 点赞数。 |
| `tiktok_seller_detail_video_comment_count` | 未限定 | 评论数。 |
| `tiktok_seller_detail_video_engagement_rate` | 未限定 | 互动率。 |
| `tiktok_seller_detail_video_30d_sold_count` | 未限定 | 近 30 天带货销量。 |
| `tiktok_seller_detail_video_30d_gmv` | 未限定 | 近 30 天带货 GMV。 |
| `tiktok_seller_detail_is_ad` | 未限定 | 广告标记；值类型以实际返回为准。 |
| `tiktok_seller_detail_video_ad_source` | 未限定 | 广告来源。 |
| `tiktok_seller_detail_is_aigc_video` | 未限定 | AIGC 视频标记；值类型以实际返回为准。 |
| `tiktok_seller_detail_user_id` | 未限定 | 发布者用户 ID。 |
| `tiktok_seller_detail_user_unique_id` | 未限定 | 发布者唯一账号标识。 |
| `tiktok_seller_detail_user_nickname` | 未限定 | 发布者昵称。 |
| `tiktok_seller_detail_user_avatar` | 未限定 | 发布者头像，嵌套结构以实际返回为准。 |
| `tiktok_seller_detail_follower_count` | 未限定 | 发布者粉丝数。 |

#### 金额对象（适用于本接口实际返回的金额字段）

| 字段 | 类型 | 说明 |
|---|---|---|
| `unit` | 未限定 | 返回的单位标识，示例为字符串 US；保留原值，不自行转换币种。 |
| `value` | 未限定 | 金额值，示例为数字 31；按运行时类型解析。 |

金额通常为 `{ "unit": "US", "value": 31 }`，并不保证所有金额字段均为此结构。字段可缺失、为 null 或新增；标为“未限定”的类型不作为服务端固定 schema，按实际响应解析。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode=501` 表示参数校验失败；非法国家码可返回此码。根据 errmsg 核对参数，不自动改条件重试付费接口。
- 空结果根据 data.total_count 与 data.items 判断，不因空列表判定系统错误。HTTP 或业务错误均保存并回显，不缓存失败结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/sellers/related-videos" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7495205878591949358","page":1,"pageSize":10}'
```

## 接口：店铺热推榜

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/sellers/rankings/most-promoted`

### 请求参数

本接口每次请求消耗 18 算力，命中业务缓存时不发起新的付费请求。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `date` | string | 是 | - | YYYYMMDD。 |
| `granularity` | string | 是 | - | daily、weekly、monthly、0、1 或 2（均按 string 传递）。 |
| `page` | integer | 否 | 未指定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未指定 | 榜单为 1–20。 |
| `category` | string | 否 | - | 商品分类 ID。 |
| `shopType` | string | 否 | - | 店铺类型：1、2、3 或 4；不可与搜索 sellerType 互换。 |
| `sort` | string | 否 | `related_creator_count:desc` | field:asc 或 field:desc。 |

#### 脚本选项与运行约定

| 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `--inline` | CLI flag | 否 | 默认关闭；强制完整打印，同时仍保存响应，不绕过缓存。 |
| `--no-cache` | CLI flag | 否 | 默认关闭；跳过业务缓存读写并强制请求，可能再次消耗算力，仅在用户明确同意额外消耗或调试时使用。 |

请求 JSON 使用 camelCase；网关再映射为上游 snake_case，不传 page_size、seller_type、shop_type 等内部别名。不编造未支持的过滤条件，也不通过反复调用其他付费接口补足条件。

业务入口提供 24 小时成功响应缓存，按当前工作目录、网关、API Key 的 SHA-256 指纹、端点和完整参数隔离；命中输出 `Cache hit`，不产生新请求。HTTP 或业务失败不缓存，业务成功的空结果可缓存；不会自动更改条件或连续重试。缓存读写均校验业务状态：响应必须是对象且无 error、无 success=false，并具有 success=true 或 errcode/errorCode/code 标记。存在的 errcode 按响应码基础规则判定：null、空字符串（含纯空白）或 200–299（数字或三位 ASCII 数字字符串）可缓存，0、false 及其他非空值不可缓存；存在的 errorCode/code 保留兼容判定，只接受 0、200、ok、success。旧缓存中的失败状态也不复用。

业务封装经公共 `call_api.run` 调用，始终传入 `--no-cache`，关闭公共调用器的第二层缓存及重复落盘；业务入口负责完整响应、摘要和会话文件。响应写入当前目录的 `linkfox/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-shop-<微秒时间戳>.json`，session 优先使用去除首尾空白的 SESSION_ID，否则进程内生成稳定值；同步维护 `_meta.json` 和 `index.jsonl`。禁止写入 /tmp，不回退到家目录或临时目录，当前目录不可写时报错。

完整 JSON 以 UTF-8 保存；响应不超过 8000 字节时完整打印，超过时只打印摘要，含顶层字段、可用计数、最大列表长度与前 3 条样本。签名 URL 可能过期，未知字段不删除；不输出 API Key。

Authorization 密钥优先读取 LINKFOX_AGENT_API_KEY，未配置时回退 LINKFOXAGENT_API_KEY；透传 SESSION_ID（去首尾空白）、MESSAGE_ID、MODE_ID、APP_NAME，未设置为空字符串。网关基础地址去尾部斜杠，请求超时 150 秒。

### 响应结构

2026-08-29 的七个接口调用样本均为 HTTP 200、errcode=200 且含非空业务数据；样本不保证后续查询有数据。脚本 `chuhaijiang_seller_rank_most_promoted.py` 保留完整原始 JSON。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer；兼容 string / null | 网关业务码；成功样本为 200，统一按响应码基础规则判断。 |
| `errmsg` | string | 网关消息；成功样本为 ok。 |
| `request_id` | string | 请求追踪 ID。 |
| `data` | object | 接口业务数据。 |
| `data.total_count` | 未限定 | 匹配记录总数；类型以实际返回为准。 |
| `data.items` | array<object> | 主列表；元素见下表。 |

#### data.items[] 记录字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 未限定 | 榜单记录标识，可作为店铺查询线索。 |
| `seller_id` | 未限定 | 店铺标识。 |
| `shop_name` | 未限定 | 店铺名称。 |
| `region` | 未限定 | 店铺市场。 |
| `shop_rating` | 未限定 | 店铺评分。 |
| `shop_product_count` | 未限定 | 店铺商品数。 |
| `seller_main_category` | 未限定 | 店铺主营分类。 |
| `seller_business_info` | 未限定 | 商家主体信息。 |
| `seller_avatar` | 未限定 | 商家头像；嵌套结构以实际返回为准。 |
| `biz_type` | 未限定 | 业务类型值。 |
| `interval_related_creator_count` | 未限定 | 榜单区间关联达人数。 |
| `interval_total_related_creator_count` | 未限定 | 榜单区间累计关联达人数。 |
| `interval_total_related_video_creator_count` | 未限定 | 榜单区间累计视频关联达人数。 |
| `interval_total_related_shop_creator_count` | 未限定 | 榜单区间累计橱窗关联达人数。 |
| `interval_total_related_videos_count` | 未限定 | 榜单区间累计关联视频数。 |

#### 金额对象（适用于本接口实际返回的金额字段）

| 字段 | 类型 | 说明 |
|---|---|---|
| `unit` | 未限定 | 返回的单位标识，示例为字符串 US；保留原值，不自行转换币种。 |
| `value` | 未限定 | 金额值，示例为数字 31；按运行时类型解析。 |

金额通常为 `{ "unit": "US", "value": 31 }`，并不保证所有金额字段均为此结构。字段可缺失、为 null 或新增；标为“未限定”的类型不作为服务端固定 schema，按实际响应解析。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode=501` 表示参数校验失败；非法国家码可返回此码。根据 errmsg 核对参数，不自动改条件重试付费接口。
- 空结果根据 data.total_count 与 data.items 判断，不因空列表判定系统错误。HTTP 或业务错误均保存并回显，不缓存失败结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/sellers/rankings/most-promoted" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","date":"20260824","granularity":"daily","page":1,"pageSize":10}'
```

## 接口：店铺销量榜

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/sellers/rankings/top-selling`

### 请求参数

本接口每次请求消耗 18 算力，命中业务缓存时不发起新的付费请求。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `date` | string | 是 | - | YYYYMMDD。 |
| `granularity` | string | 是 | - | daily、weekly、monthly、0、1 或 2（均按 string 传递）。 |
| `page` | integer | 否 | 未指定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未指定 | 榜单为 1–20。 |
| `category` | string | 否 | - | 商品分类 ID。 |
| `shopType` | string | 否 | - | 店铺类型：1、2、3 或 4；不可与搜索 sellerType 互换。 |
| `sort` | string | 否 | `interval_sold_count:desc` | field:asc 或 field:desc。 |

#### 脚本选项与运行约定

| 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `--inline` | CLI flag | 否 | 默认关闭；强制完整打印，同时仍保存响应，不绕过缓存。 |
| `--no-cache` | CLI flag | 否 | 默认关闭；跳过业务缓存读写并强制请求，可能再次消耗算力，仅在用户明确同意额外消耗或调试时使用。 |

请求 JSON 使用 camelCase；网关再映射为上游 snake_case，不传 page_size、seller_type、shop_type 等内部别名。不编造未支持的过滤条件，也不通过反复调用其他付费接口补足条件。

业务入口提供 24 小时成功响应缓存，按当前工作目录、网关、API Key 的 SHA-256 指纹、端点和完整参数隔离；命中输出 `Cache hit`，不产生新请求。HTTP 或业务失败不缓存，业务成功的空结果可缓存；不会自动更改条件或连续重试。缓存读写均校验业务状态：响应必须是对象且无 error、无 success=false，并具有 success=true 或 errcode/errorCode/code 标记。存在的 errcode 按响应码基础规则判定：null、空字符串（含纯空白）或 200–299（数字或三位 ASCII 数字字符串）可缓存，0、false 及其他非空值不可缓存；存在的 errorCode/code 保留兼容判定，只接受 0、200、ok、success。旧缓存中的失败状态也不复用。

业务封装经公共 `call_api.run` 调用，始终传入 `--no-cache`，关闭公共调用器的第二层缓存及重复落盘；业务入口负责完整响应、摘要和会话文件。响应写入当前目录的 `linkfox/<YYYY-MM-DD>/<session>/data/linkfox-chuhaijiang-tiktok-shop-<微秒时间戳>.json`，session 优先使用去除首尾空白的 SESSION_ID，否则进程内生成稳定值；同步维护 `_meta.json` 和 `index.jsonl`。禁止写入 /tmp，不回退到家目录或临时目录，当前目录不可写时报错。

完整 JSON 以 UTF-8 保存；响应不超过 8000 字节时完整打印，超过时只打印摘要，含顶层字段、可用计数、最大列表长度与前 3 条样本。签名 URL 可能过期，未知字段不删除；不输出 API Key。

Authorization 密钥优先读取 LINKFOX_AGENT_API_KEY，未配置时回退 LINKFOXAGENT_API_KEY；透传 SESSION_ID（去首尾空白）、MESSAGE_ID、MODE_ID、APP_NAME，未设置为空字符串。网关基础地址去尾部斜杠，请求超时 150 秒。

### 响应结构

2026-08-29 的七个接口调用样本均为 HTTP 200、errcode=200 且含非空业务数据；样本不保证后续查询有数据。脚本 `chuhaijiang_seller_rank_top_selling.py` 保留完整原始 JSON。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer；兼容 string / null | 网关业务码；成功样本为 200，统一按响应码基础规则判断。 |
| `errmsg` | string | 网关消息；成功样本为 ok。 |
| `request_id` | string | 请求追踪 ID。 |
| `data` | object | 接口业务数据。 |
| `data.total_count` | 未限定 | 匹配记录总数；类型以实际返回为准。 |
| `data.items` | array<object> | 主列表；元素见下表。 |

#### data.items[] 记录字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 未限定 | 榜单记录标识，可作为店铺查询线索。 |
| `seller_id` | 未限定 | 店铺标识。 |
| `shop_name` | 未限定 | 店铺名称。 |
| `region` | 未限定 | 店铺市场。 |
| `shop_rating` | 未限定 | 店铺评分。 |
| `shop_product_count` | 未限定 | 店铺商品数。 |
| `seller_main_category` | 未限定 | 店铺主营分类。 |
| `seller_business_info` | 未限定 | 商家主体信息。 |
| `seller_avatar` | 未限定 | 商家头像；嵌套结构以实际返回为准。 |
| `biz_type` | 未限定 | 业务类型值。 |
| `interval_sold_count` | 未限定 | 榜单区间销量。 |
| `interval_total_sold_count` | 未限定 | 榜单区间累计销量。 |
| `interval_sold_count_growth_rate` | 未限定 | 榜单区间销量增长率。 |
| `interval_gmv` | 未限定 | 榜单区间 GMV。 |
| `interval_total_gmv` | 未限定 | 榜单区间累计 GMV。 |
| `interval_gmv_pop_growth_rate` | 未限定 | 榜单区间 GMV 环比增长率。 |
| `interval_related_creator_count` | 未限定 | 榜单区间关联达人数。 |
| `interval_total_related_creator_count` | 未限定 | 榜单区间累计关联达人数。 |

#### 金额对象（适用于本接口实际返回的金额字段）

| 字段 | 类型 | 说明 |
|---|---|---|
| `unit` | 未限定 | 返回的单位标识，示例为字符串 US；保留原值，不自行转换币种。 |
| `value` | 未限定 | 金额值，示例为数字 31；按运行时类型解析。 |

金额通常为 `{ "unit": "US", "value": 31 }`，并不保证所有金额字段均为此结构。字段可缺失、为 null 或新增；标为“未限定”的类型不作为服务端固定 schema，按实际响应解析。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errcode=501` 表示参数校验失败；非法国家码可返回此码。根据 errmsg 核对参数，不自动改条件重试付费接口。
- 空结果根据 data.total_count 与 data.items 判断，不因空列表判定系统错误。HTTP 或业务错误均保存并回显，不缓存失败结果。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/sellers/rankings/top-selling" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","date":"20260824","granularity":"daily","page":1,"pageSize":10}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-chuhaijiang-tiktok-shop",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
