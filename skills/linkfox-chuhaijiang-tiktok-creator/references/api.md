# 出海匠 TikTok 达人市场研究 接口说明

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

## 接口：达人搜索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/creators/search`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `page` | integer | 否 | 未约定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未约定 | 每页条数，最大 10。 |
| `keyword` | string | 否 | 未约定 | 搜索关键词。 |
| `category` | string | 否 | 未约定 | 达人分类。 |
| `minFollowers` | number | 否 | 未约定 | 粉丝数下限。 |
| `maxFollowers` | number | 否 | 未约定 | 粉丝数上限。 |
| `minGmv30d` | number | 否 | 未约定 | 30 天 GMV下限。 |
| `maxGmv30d` | number | 否 | 未约定 | 30 天 GMV上限。 |
| `minAvgViews` | number | 否 | 未约定 | 平均播放量下限。 |
| `maxAvgViews` | number | 否 | 未约定 | 平均播放量上限。 |
| `minEngagement` | number | 否 | 未约定 | 互动率下限。 |
| `maxEngagement` | number | 否 | 未约定 | 互动率上限。 |
| `hasContact` | boolean | 否 | 未约定 | 是否有联系方式。 |
| `sort` | string | 否 | `gmv_30d:desc` | 排序，格式 `field:asc` 或 `field:desc`。 |

#### 脚本选项与使用限制

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，同时仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过业务入口缓存读写，强制请求，可能再次消耗算力；仅在用户明确同意额外消耗或调试时使用。 |

请求使用 camelCase 参数名，不发送内部上游 snake_case 参数。认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；透传 `SESSION_ID`（去除首尾空白）、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串。

本接口每次消耗 18 算力。业务入口默认仅缓存成功响应 24 小时，成功的空结果也可缓存。缓存按当前工作目录、网关、密钥指纹、端点和完整参数隔离；命中输出 `Cache hit`，不发请求，不向响应体添加缓存字段。读取缓存时也校验基础及业务规则，不复用不符合规则的缓存。HTTP、连接及业务失败不缓存；显式 `error`、`success=false` 或失败 `errorCode` / `code` 同样不缓存。业务入口负责缓存，公共 `call_api.run` 始终加 `--no-cache`，不重复缓存。

完整响应仅保存在当前工作目录的会话数据目录；目录不可写时报错，不回退到用户目录或临时目录。摘要保留请求参数、顶层状态、`data.total_count`、各业务列表长度和首个非空业务列表的前 3 条，避免把图片数组当作业务主列表。

### 响应结构

字段清单展示 2026-08-29 生产响应中出现的字段，并非每次必返的固定 schema；标为“未约定”的字段未限定类型，按实际响应读取，不补造数据。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer（成功响应示例）；兼容 string / null | 网关状态；成功响应示例值为 200，按基础规则判断。 |
| errmsg | string | 网关消息，成功时通常为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 本接口业务数据。 |
| data.total_count | 未约定 | 返回时表示匹配总数；不从本页长度推算总数。 |
| data.items | array | 业务记录列表；元素字段见下表。 |

金额字段可能为 number 或包含 `unit`、`value` 的 object；先检查运行时类型并保留原币种及单位，不自行换算。

| 字段 | 类型 | 说明 |
|---|---|---|
| data.items[].account_type | 未约定 | 账号类型。 |
| data.items[].author_avg_engagement_rate | 未约定 | 达人平均互动率（原始比率）。 |
| data.items[].bio_email | 未约定 | 公开资料邮箱（受展示隐私规则约束）。 |
| data.items[].category_label | 未约定 | 类目标签。 |
| data.items[].country_code | 未约定 | 国家码。 |
| data.items[].ecom_video_avg_play_count | 未约定 | 电商视频平均播放量。 |
| data.items[].facebook_url | 未约定 | Facebook 账号链接。 |
| data.items[].follower_count | 未约定 | 粉丝数。 |
| data.items[].follower_count_growth_for_last_7_days | 未约定 | 近 7 天粉丝增长数。 |
| data.items[].has_live_product | 未约定 | 是否有直播带货。 |
| data.items[].has_shop_product | 未约定 | 是否有橱窗商品。 |
| data.items[].has_video_product | 未约定 | 是否有视频带货。 |
| data.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.items[].ins_id | 未约定 | Instagram 账号标识。 |
| data.items[].live_30d_gmv | number / object | 直播 30 天 GMV。 |
| data.items[].live_30d_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].live_30d_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].live_30d_gpm | 未约定 | 直播 30 天 GPM。 |
| data.items[].nickname | 未约定 | 达人昵称。 |
| data.items[].product_category_label_list | 未约定 | 商品类目标签集合。 |
| data.items[].total_favorited | 未约定 | 累计获赞数。 |
| data.items[].total_video_live_30d_gmv | number / object | 视频与直播合计 30 天 GMV。 |
| data.items[].total_video_live_30d_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].total_video_live_30d_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].unique_id | 未约定 | 达人账号标识。 |
| data.items[].user_avatar | 未约定 | 达人头像。 |
| data.items[].user_sell_product_l3_category | 未约定 | 推广商品三级类目。 |
| data.items[].video_30d_gmv | number / object | 视频 30 天 GMV。 |
| data.items[].video_30d_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].video_30d_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].video_30d_gpm | 未约定 | 视频 30 天 GPM。 |
| data.items[].video_avg_like_count | 未约定 | 视频平均点赞数。 |
| data.items[].video_avg_play_count | 未约定 | 视频平均播放量。 |
| data.items[].video_total_like_count_to_follower_count_ratio | 未约定 | 视频总点赞数与粉丝数之比。 |
| data.items[].youtube_channel_id | 未约定 | YouTube 频道标识。 |

`bio_email` 与外部社交账号只用于判断公开资料可用性；无明确、合规业务需求时不主动展示或汇总联系方式，不暴露私人信息。

比率、时间和累计、7 天、30 天或统计窗口指标按返回原值展示，不擅改百分比、时区或周期。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 成功且业务列表为空时说明当前条件无数据，不自动换词、翻页或修改条件连续试探付费接口。
- `403` 为无权限，停止调用并确认网关是否启用工具，不归入认证或充值流程。
- `501` 为参数校验失败，根据 `errmsg` 核对参数；其他异常按错误消息说明，不自动连续重试付费接口。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/creators/search" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","keyword":"beauty","page":1,"pageSize":5}'
```

## 接口：达人详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/creators/detail`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `id` | string | 是 | - | 达人 ID；复用搜索或达人榜单返回且适合本端点的标识。 |
| `include` | string | 否 | 未约定 | 可选 `channel`、`core`、`portrait`；多个值用英文逗号分隔。 |

#### 脚本选项与使用限制

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，同时仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过业务入口缓存读写，强制请求，可能再次消耗算力；仅在用户明确同意额外消耗或调试时使用。 |

请求使用 camelCase 参数名，不发送内部上游 snake_case 参数。认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；透传 `SESSION_ID`（去除首尾空白）、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串。

本接口每次消耗 9 算力。业务入口默认仅缓存成功响应 24 小时，成功的空结果也可缓存。缓存按当前工作目录、网关、密钥指纹、端点和完整参数隔离；命中输出 `Cache hit`，不发请求，不向响应体添加缓存字段。读取缓存时也校验基础及业务规则，不复用不符合规则的缓存。HTTP、连接及业务失败不缓存；显式 `error`、`success=false` 或失败 `errorCode` / `code` 同样不缓存。业务入口负责缓存，公共 `call_api.run` 始终加 `--no-cache`，不重复缓存。

完整响应仅保存在当前工作目录的会话数据目录；目录不可写时报错，不回退到用户目录或临时目录。摘要保留请求参数、顶层状态、`data.total_count`、各业务列表长度和首个非空业务列表的前 3 条，避免把图片数组当作业务主列表。

### 响应结构

字段清单展示 2026-08-29 生产响应中出现的字段，并非每次必返的固定 schema；标为“未约定”的字段未限定类型，按实际响应读取，不补造数据。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer（成功响应示例）；兼容 string / null | 网关状态；成功响应示例值为 200，按基础规则判断。 |
| errmsg | string | 网关消息，成功时通常为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 本接口业务数据。 |
| data.total_count | 未约定 | 返回时表示匹配总数；不从本页长度推算总数。 |
| data.items | array | 基础资料列表；元素字段见下表。 |
| data.core | object | 对应详情扩展；请求 include 后按实际响应读取。 |
| data.core.items | array | 业务记录列表；元素字段见下表。 |
| data.channel | object | 对应详情扩展；请求 include 后按实际响应读取。 |
| data.channel.items | array | 业务记录列表；元素字段见下表。 |
| data.portrait | object | 对应详情扩展；请求 include 后按实际响应读取。 |
| data.portrait.items | array | 业务记录列表；元素字段见下表。 |

金额字段可能为 number 或包含 `unit`、`value` 的 object；先检查运行时类型并保留原币种及单位，不自行换算。

| 字段 | 类型 | 说明 |
|---|---|---|
| data.items[].bio_email | 未约定 | 公开资料邮箱（受展示隐私规则约束）。 |
| data.items[].bio_url | 未约定 | 公开资料链接。 |
| data.items[].category_label | 未约定 | 类目标签。 |
| data.items[].enterprise_verify_reason | 未约定 | 企业认证说明。 |
| data.items[].facebook_url | 未约定 | Facebook 账号链接。 |
| data.items[].has_live_product | 未约定 | 是否有直播带货。 |
| data.items[].has_shop_product | 未约定 | 是否有橱窗商品。 |
| data.items[].has_video_product | 未约定 | 是否有视频带货。 |
| data.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.items[].ins_id | 未约定 | Instagram 账号标识。 |
| data.items[].last_update_time | 未约定 | 最近更新时间（原值）。 |
| data.items[].nickname | 未约定 | 达人昵称。 |
| data.items[].partnered_brand | 未约定 | 合作品牌。 |
| data.items[].product_category_label_list | 未约定 | 商品类目标签集合。 |
| data.items[].signature | 未约定 | 账号简介。 |
| data.items[].unique_id | 未约定 | 达人账号标识。 |
| data.items[].user_avatar | 未约定 | 达人头像。 |
| data.items[].youtube_channel_id | 未约定 | YouTube 频道标识。 |
| data.core.items[].core_author_avg_engagement_rate | 未约定 | 核心指标：达人平均互动率。 |
| data.core.items[].core_follower_count | 未约定 | 核心指标：粉丝数。 |
| data.core.items[].core_product_count | 未约定 | 核心指标：商品数。 |
| data.core.items[].core_total_favorited | 未约定 | 核心指标：累计获赞数。 |
| data.core.items[].core_uid | 未约定 | 核心指标：达人 UID。 |
| data.core.items[].core_video_total_like_count_to_follower_count | 未约定 | 核心指标：视频总点赞数与粉丝数之比。 |
| data.core.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.core.items[].tioktok_creator_detail_core_ec_video_count | 未约定 | 核心指标：电商视频数。 |
| data.core.items[].tioktok_creator_detail_core_ecom_video_avg_play_count | 未约定 | 核心指标：电商视频平均播放量。 |
| data.core.items[].tioktok_creator_detail_core_med_commission_rate | 未约定 | 核心指标：佣金率中位数。 |
| data.channel.items[].channel_country_code | 未约定 | 渠道指标：国家码。 |
| data.channel.items[].channel_ec_video_30d_avg_engagement_rate | 未约定 | 渠道指标：电商视频 30 天平均互动率。 |
| data.channel.items[].channel_ec_video_30d_avg_play_count | 未约定 | 渠道指标：电商视频 30 天平均播放量。 |
| data.channel.items[].channel_live_30d_gmv | number / object | 渠道指标：直播 30 天 GMV。 |
| data.channel.items[].channel_live_30d_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.channel.items[].channel_live_30d_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.channel.items[].channel_live_30d_gpm | 未约定 | 渠道指标：直播 30 天 GPM。 |
| data.channel.items[].channel_total_video_live_30d_gmv | number / object | 渠道指标：视频与直播合计 30 天 GMV。 |
| data.channel.items[].channel_total_video_live_30d_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.channel.items[].channel_total_video_live_30d_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.channel.items[].channel_uid | 未约定 | 渠道指标：达人 UID。 |
| data.channel.items[].channel_video_30d_gmv | number / object | 渠道指标：视频 30 天 GMV。 |
| data.channel.items[].channel_video_30d_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.channel.items[].channel_video_30d_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.channel.items[].channel_video_30d_gpm | 未约定 | 渠道指标：视频 30 天 GPM。 |
| data.channel.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.portrait.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.portrait.items[].portrait_age_distribution | 未约定 | 受众年龄分布（嵌套结构按实际响应）。 |
| data.portrait.items[].portrait_follower_count | 未约定 | 画像粉丝数。 |
| data.portrait.items[].portrait_gender_distribution | 未约定 | 受众性别分布（嵌套结构按实际响应）。 |
| data.portrait.items[].portrait_region_distribution | 未约定 | 受众地区分布（嵌套结构按实际响应）。 |
| data.portrait.items[].portrait_uid | 未约定 | 画像达人 UID。 |

`tioktok_*`、`titkok_*` 等上游拼写按真实字段原样读取，不改成 `tiktok_*`。

`bio_email` 与外部社交账号只用于判断公开资料可用性；无明确、合规业务需求时不主动展示或汇总联系方式，不暴露私人信息。

比率、时间和累计、7 天、30 天或统计窗口指标按返回原值展示，不擅改百分比、时区或周期。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 成功且业务列表为空时说明当前条件无数据，不自动换词、翻页或修改条件连续试探付费接口。
- `403` 为无权限，停止调用并确认网关是否启用工具，不归入认证或充值流程。
- `501` 为参数校验失败，根据 `errmsg` 核对参数；其他异常按错误消息说明，不自动连续重试付费接口。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/creators/detail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7302162228386776110","include":"channel,core,portrait"}'
```

## 接口：关联直播

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/creators/related-lives`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `id` | string | 是 | - | 达人 ID；复用搜索或达人榜单返回且适合本端点的标识。 |
| `page` | integer | 否 | 未约定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未约定 | 每页条数，最大 10。 |

#### 脚本选项与使用限制

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，同时仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过业务入口缓存读写，强制请求，可能再次消耗算力；仅在用户明确同意额外消耗或调试时使用。 |

请求使用 camelCase 参数名，不发送内部上游 snake_case 参数。认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；透传 `SESSION_ID`（去除首尾空白）、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串。

本接口每次消耗 18 算力。业务入口默认仅缓存成功响应 24 小时，成功的空结果也可缓存。缓存按当前工作目录、网关、密钥指纹、端点和完整参数隔离；命中输出 `Cache hit`，不发请求，不向响应体添加缓存字段。读取缓存时也校验基础及业务规则，不复用不符合规则的缓存。HTTP、连接及业务失败不缓存；显式 `error`、`success=false` 或失败 `errorCode` / `code` 同样不缓存。业务入口负责缓存，公共 `call_api.run` 始终加 `--no-cache`，不重复缓存。

完整响应仅保存在当前工作目录的会话数据目录；目录不可写时报错，不回退到用户目录或临时目录。摘要保留请求参数、顶层状态、`data.total_count`、各业务列表长度和首个非空业务列表的前 3 条，避免把图片数组当作业务主列表。

### 响应结构

字段清单展示 2026-08-29 生产响应中出现的字段，并非每次必返的固定 schema；标为“未约定”的字段未限定类型，按实际响应读取，不补造数据。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer（成功响应示例）；兼容 string / null | 网关状态；成功响应示例值为 200，按基础规则判断。 |
| errmsg | string | 网关消息，成功时通常为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 本接口业务数据。 |
| data.total_count | 未约定 | 返回时表示匹配总数；不从本页长度推算总数。 |
| data.items | array | 业务记录列表；元素字段见下表。 |

金额字段可能为 number 或包含 `unit`、`value` 的 object；先检查运行时类型并保留原币种及单位，不自行换算。

| 字段 | 类型 | 说明 |
|---|---|---|
| data.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.items[].tiktok_creator_detail_live_country_code | 未约定 | 关联直播：国家码。 |
| data.items[].tiktok_creator_detail_live_cover | 未约定 | 关联直播：封面。 |
| data.items[].tiktok_creator_detail_live_end_time | 未约定 | 关联直播：结束时间。 |
| data.items[].tiktok_creator_detail_live_gmv | number / object | 关联直播：GMV。 |
| data.items[].tiktok_creator_detail_live_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].tiktok_creator_detail_live_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].tiktok_creator_detail_live_gpm | 未约定 | 关联直播：GPM。 |
| data.items[].tiktok_creator_detail_live_max_user_count | 未约定 | 关联直播：最高同时在线人数。 |
| data.items[].tiktok_creator_detail_live_most_product_category_label | 未约定 | 关联直播：主要商品类目标签。 |
| data.items[].tiktok_creator_detail_live_new_follow_count | 未约定 | 关联直播：新增粉丝数。 |
| data.items[].tiktok_creator_detail_live_opm | 未约定 | 关联直播：OPM（原口径）。 |
| data.items[].tiktok_creator_detail_live_product_count | 未约定 | 关联直播：商品数。 |
| data.items[].tiktok_creator_detail_live_room_id | 未约定 | 关联直播：直播间标识。 |
| data.items[].tiktok_creator_detail_live_room_link | 未约定 | 关联直播：直播间链接。 |
| data.items[].tiktok_creator_detail_live_start_time | 未约定 | 关联直播：开始时间。 |
| data.items[].tiktok_creator_detail_live_title | 未约定 | 关联直播：标题。 |
| data.items[].tiktok_creator_detail_live_total_sold_count | 未约定 | 关联直播：总销量。 |
| data.items[].tiktok_creator_detail_live_total_user | 未约定 | 关联直播：累计观众指标。 |
| data.items[].tiktok_creator_detail_live_user_follower_count | 未约定 | 关联直播：达人粉丝数。 |

比率、时间和累计、7 天、30 天或统计窗口指标按返回原值展示，不擅改百分比、时区或周期。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 成功且业务列表为空时说明当前条件无数据，不自动换词、翻页或修改条件连续试探付费接口。
- `403` 为无权限，停止调用并确认网关是否启用工具，不归入认证或充值流程。
- `501` 为参数校验失败，根据 `errmsg` 核对参数；其他异常按错误消息说明，不自动连续重试付费接口。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/creators/related-lives" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7302162228386776110","page":1,"pageSize":5}'
```

## 接口：带货商品

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/creators/related-products`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `id` | string | 是 | - | 达人 ID；复用搜索或达人榜单返回且适合本端点的标识。 |
| `page` | integer | 否 | 未约定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未约定 | 每页条数，最大 10。 |

#### 脚本选项与使用限制

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，同时仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过业务入口缓存读写，强制请求，可能再次消耗算力；仅在用户明确同意额外消耗或调试时使用。 |

请求使用 camelCase 参数名，不发送内部上游 snake_case 参数。认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；透传 `SESSION_ID`（去除首尾空白）、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串。

本接口每次消耗 18 算力。业务入口默认仅缓存成功响应 24 小时，成功的空结果也可缓存。缓存按当前工作目录、网关、密钥指纹、端点和完整参数隔离；命中输出 `Cache hit`，不发请求，不向响应体添加缓存字段。读取缓存时也校验基础及业务规则，不复用不符合规则的缓存。HTTP、连接及业务失败不缓存；显式 `error`、`success=false` 或失败 `errorCode` / `code` 同样不缓存。业务入口负责缓存，公共 `call_api.run` 始终加 `--no-cache`，不重复缓存。

完整响应仅保存在当前工作目录的会话数据目录；目录不可写时报错，不回退到用户目录或临时目录。摘要保留请求参数、顶层状态、`data.total_count`、各业务列表长度和首个非空业务列表的前 3 条，避免把图片数组当作业务主列表。

### 响应结构

字段清单展示 2026-08-29 生产响应中出现的字段，并非每次必返的固定 schema；标为“未约定”的字段未限定类型，按实际响应读取，不补造数据。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer（成功响应示例）；兼容 string / null | 网关状态；成功响应示例值为 200，按基础规则判断。 |
| errmsg | string | 网关消息，成功时通常为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 本接口业务数据。 |
| data.total_count | 未约定 | 返回时表示匹配总数；不从本页长度推算总数。 |
| data.items | array | 业务记录列表；元素字段见下表。 |

金额字段可能为 number 或包含 `unit`、`value` 的 object；先检查运行时类型并保留原币种及单位，不自行换算。

| 字段 | 类型 | 说明 |
|---|---|---|
| data.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.items[].tiktok_creator_detail_by_live | 未约定 | 达人关联：是否通过直播推广。 |
| data.items[].tiktok_creator_detail_by_shop | 未约定 | 达人关联：是否通过橱窗推广。 |
| data.items[].tiktok_creator_detail_by_video | 未约定 | 达人关联：是否通过视频推广。 |
| data.items[].tiktok_creator_detail_live_30d_gmv | number / object | 达人关联：直播 30 天 GMV。 |
| data.items[].tiktok_creator_detail_live_30d_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].tiktok_creator_detail_live_30d_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].tiktok_creator_detail_live_30d_sold_count | 未约定 | 达人关联：直播 30 天销量。 |
| data.items[].tiktok_creator_detail_product_country_code | 未约定 | 关联商品：国家码。 |
| data.items[].tiktok_creator_detail_product_id | 未约定 | 关联商品：商品标识。 |
| data.items[].tiktok_creator_detail_product_launch_time | 未约定 | 关联商品：发布时间。 |
| data.items[].tiktok_creator_detail_total_video_live_30d_gmv | number / object | 达人关联：视频与直播合计 30 天 GMV。 |
| data.items[].tiktok_creator_detail_total_video_live_30d_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].tiktok_creator_detail_total_video_live_30d_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].tiktok_creator_detail_total_video_live_30d_sold_count | 未约定 | 达人关联：视频与直播合计 30 天销量。 |
| data.items[].tiktok_creator_detail_user_id | 未约定 | 达人关联：达人标识。 |
| data.items[].tiktok_creator_detail_video_30d_gmv | number / object | 达人关联：视频 30 天 GMV。 |
| data.items[].tiktok_creator_detail_video_30d_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].tiktok_creator_detail_video_30d_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].tiktok_creator_detail_video_30d_sold_count | 未约定 | 达人关联：视频 30 天销量。 |
| data.items[].tiktok_product_detail_ceiling_price | number / object | 商品资料：最高价格。 |
| data.items[].tiktok_product_detail_ceiling_price.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].tiktok_product_detail_ceiling_price.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].tiktok_product_detail_commission_rate | 未约定 | 商品资料：佣金率。 |
| data.items[].tiktok_product_detail_floor_price | number / object | 商品资料：最低价格。 |
| data.items[].tiktok_product_detail_floor_price.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].tiktok_product_detail_floor_price.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].tiktok_product_detail_l1_category | 未约定 | 商品资料：一级类目。 |
| data.items[].tiktok_product_detail_l2_category | 未约定 | 商品资料：二级类目。 |
| data.items[].tiktok_product_detail_l3_category | 未约定 | 商品资料：三级类目。 |
| data.items[].tiktok_product_detail_product_images | 未约定 | 商品资料：商品图片（嵌套结构按实际响应）。 |
| data.items[].tiktok_product_detail_product_name | 未约定 | 商品资料：商品名称。 |
| data.items[].tiktok_product_detail_product_rating | 未约定 | 商品资料：商品评分。 |
| data.items[].tiktok_product_detail_product_sku_props | 未约定 | 商品资料：商品 SKU 属性（嵌套结构按实际响应）。 |
| data.items[].tiktok_product_detail_product_skus | 未约定 | 商品资料：商品 SKU 集合（嵌套结构按实际响应）。 |
| data.items[].tiktok_product_detail_product_status | 未约定 | 商品资料：商品状态。 |
| data.items[].tiktok_product_detail_region | 未约定 | 商品资料：地区。 |

比率、时间和累计、7 天、30 天或统计窗口指标按返回原值展示，不擅改百分比、时区或周期。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 成功且业务列表为空时说明当前条件无数据，不自动换词、翻页或修改条件连续试探付费接口。
- `403` 为无权限，停止调用并确认网关是否启用工具，不归入认证或充值流程。
- `501` 为参数校验失败，根据 `errmsg` 核对参数；其他异常按错误消息说明，不自动连续重试付费接口。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/creators/related-products" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7302162228386776110","page":1,"pageSize":5}'
```

## 接口：关联视频

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/creators/related-videos`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `id` | string | 是 | - | 达人 ID；复用搜索或达人榜单返回且适合本端点的标识。 |
| `page` | integer | 否 | 未约定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未约定 | 每页条数，最大 10。 |

#### 脚本选项与使用限制

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，同时仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过业务入口缓存读写，强制请求，可能再次消耗算力；仅在用户明确同意额外消耗或调试时使用。 |

请求使用 camelCase 参数名，不发送内部上游 snake_case 参数。认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；透传 `SESSION_ID`（去除首尾空白）、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串。

本接口每次消耗 18 算力。业务入口默认仅缓存成功响应 24 小时，成功的空结果也可缓存。缓存按当前工作目录、网关、密钥指纹、端点和完整参数隔离；命中输出 `Cache hit`，不发请求，不向响应体添加缓存字段。读取缓存时也校验基础及业务规则，不复用不符合规则的缓存。HTTP、连接及业务失败不缓存；显式 `error`、`success=false` 或失败 `errorCode` / `code` 同样不缓存。业务入口负责缓存，公共 `call_api.run` 始终加 `--no-cache`，不重复缓存。

完整响应仅保存在当前工作目录的会话数据目录；目录不可写时报错，不回退到用户目录或临时目录。摘要保留请求参数、顶层状态、`data.total_count`、各业务列表长度和首个非空业务列表的前 3 条，避免把图片数组当作业务主列表。

### 响应结构

字段清单展示 2026-08-29 生产响应中出现的字段，并非每次必返的固定 schema；标为“未约定”的字段未限定类型，按实际响应读取，不补造数据。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer（成功响应示例）；兼容 string / null | 网关状态；成功响应示例值为 200，按基础规则判断。 |
| errmsg | string | 网关消息，成功时通常为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 本接口业务数据。 |
| data.total_count | 未约定 | 返回时表示匹配总数；不从本页长度推算总数。 |
| data.items | array | 业务记录列表；元素字段见下表。 |

金额字段可能为 number 或包含 `unit`、`value` 的 object；先检查运行时类型并保留原币种及单位，不自行换算。

| 字段 | 类型 | 说明 |
|---|---|---|
| data.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.items[].tiktok_creator_detail_is_ad | 未约定 | 达人关联：是否为广告。 |
| data.items[].tiktok_creator_detail_is_aigc_video | 未约定 | 达人关联：是否为 AIGC 视频。 |
| data.items[].tiktok_creator_detail_video_30d_gmv | number / object | 达人关联：视频 30 天 GMV。 |
| data.items[].tiktok_creator_detail_video_30d_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].tiktok_creator_detail_video_30d_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].tiktok_creator_detail_video_30d_sold_count | 未约定 | 达人关联：视频 30 天销量。 |
| data.items[].tiktok_creator_detail_video_ad_source | 未约定 | 关联视频：广告来源。 |
| data.items[].tiktok_creator_detail_video_author_category_label | 未约定 | 关联视频：作者类目标签。 |
| data.items[].tiktok_creator_detail_video_author_nickname | 未约定 | 关联视频：作者昵称。 |
| data.items[].tiktok_creator_detail_video_author_uid | 未约定 | 关联视频：作者 UID。 |
| data.items[].tiktok_creator_detail_video_author_unique_id | 未约定 | 关联视频：作者账号标识。 |
| data.items[].tiktok_creator_detail_video_collect_count | 未约定 | 关联视频：收藏数。 |
| data.items[].tiktok_creator_detail_video_comment_count | 未约定 | 关联视频：评论数。 |
| data.items[].tiktok_creator_detail_video_country_code | 未约定 | 关联视频：国家码。 |
| data.items[].tiktok_creator_detail_video_cover | 未约定 | 关联视频：封面。 |
| data.items[].tiktok_creator_detail_video_desc | 未约定 | 关联视频：视频描述。 |
| data.items[].tiktok_creator_detail_video_duration | 未约定 | 关联视频：视频时长（原单位）。 |
| data.items[].tiktok_creator_detail_video_engagement_rate | 未约定 | 关联视频：互动率（原值）。 |
| data.items[].tiktok_creator_detail_video_id | 未约定 | 关联视频：视频标识。 |
| data.items[].tiktok_creator_detail_video_launch_time | 未约定 | 关联视频：发布时间。 |
| data.items[].tiktok_creator_detail_video_like_count | 未约定 | 关联视频：点赞数。 |
| data.items[].tiktok_creator_detail_video_play_count | 未约定 | 关联视频：播放量。 |
| data.items[].tiktok_creator_detail_video_product_id | 未约定 | 关联视频：商品标识。 |
| data.items[].tiktok_creator_detail_video_product_images | 未约定 | 关联视频：商品图片（嵌套结构按实际响应）。 |
| data.items[].tiktok_creator_detail_video_product_l1_category | 未约定 | 关联视频：推广商品一级类目。 |
| data.items[].tiktok_creator_detail_video_product_l2_category | 未约定 | 关联视频：推广商品二级类目。 |
| data.items[].tiktok_creator_detail_video_product_l3_category | 未约定 | 关联视频：推广商品三级类目。 |
| data.items[].tiktok_creator_detail_video_product_title | 未约定 | 关联视频：推广商品标题。 |
| data.items[].tiktok_creator_detail_video_share_count | 未约定 | 关联视频：分享数。 |
| data.items[].tiktok_creator_detail_video_share_url | 未约定 | 关联视频：分享链接。 |
| data.items[].tiktok_creator_detail_video_total_like_count_to_follower_count_ratio | 未约定 | 关联视频：总点赞数与粉丝数之比。 |
| data.items[].tiktok_creator_detail_video_user_avatar | 未约定 | 关联视频：作者头像。 |

比率、时间和累计、7 天、30 天或统计窗口指标按返回原值展示，不擅改百分比、时区或周期。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 成功且业务列表为空时说明当前条件无数据，不自动换词、翻页或修改条件连续试探付费接口。
- `403` 为无权限，停止调用并确认网关是否启用工具，不归入认证或充值流程。
- `501` 为参数校验失败，根据 `errmsg` 核对参数；其他异常按错误消息说明，不自动连续重试付费接口。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/creators/related-videos" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","id":"7302162228386776110","page":1,"pageSize":5}'
```

## 接口：达人机构榜

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/creators/rankings/agencies`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `page` | integer | 否 | 未约定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未约定 | 每页条数，范围为 1–20。 |
| `category` | string | 否 | 未约定 | 机构分类。 |
| `sort` | string | 否 | `gmv_30d:desc` | 排序。 |

#### 脚本选项与使用限制

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，同时仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过业务入口缓存读写，强制请求，可能再次消耗算力；仅在用户明确同意额外消耗或调试时使用。 |

请求使用 camelCase 参数名，不发送内部上游 snake_case 参数。认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；透传 `SESSION_ID`（去除首尾空白）、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串。

本接口每次消耗 18 算力。业务入口默认仅缓存成功响应 24 小时，成功的空结果也可缓存。缓存按当前工作目录、网关、密钥指纹、端点和完整参数隔离；命中输出 `Cache hit`，不发请求，不向响应体添加缓存字段。读取缓存时也校验基础及业务规则，不复用不符合规则的缓存。HTTP、连接及业务失败不缓存；显式 `error`、`success=false` 或失败 `errorCode` / `code` 同样不缓存。业务入口负责缓存，公共 `call_api.run` 始终加 `--no-cache`，不重复缓存。

完整响应仅保存在当前工作目录的会话数据目录；目录不可写时报错，不回退到用户目录或临时目录。摘要保留请求参数、顶层状态、`data.total_count`、各业务列表长度和首个非空业务列表的前 3 条，避免把图片数组当作业务主列表。

### 响应结构

字段清单展示 2026-08-29 生产响应中出现的字段，并非每次必返的固定 schema；标为“未约定”的字段未限定类型，按实际响应读取，不补造数据。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer（成功响应示例）；兼容 string / null | 网关状态；成功响应示例值为 200，按基础规则判断。 |
| errmsg | string | 网关消息，成功时通常为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 本接口业务数据。 |
| data.total_count | 未约定 | 返回时表示匹配总数；不从本页长度推算总数。 |
| data.items | array | 业务记录列表；元素字段见下表。 |

金额字段可能为 number 或包含 `unit`、`value` 的 object；先检查运行时类型并保留原币种及单位，不自行换算。

| 字段 | 类型 | 说明 |
|---|---|---|
| data.items[].avg_commission_rate | 未约定 | 平均佣金率。 |
| data.items[].follower_count | 未约定 | 粉丝数。 |
| data.items[].has_email_address | 未约定 | 是否有邮箱。 |
| data.items[].has_phone | 未约定 | 是否有电话。 |
| data.items[].has_whats_app | 未约定 | 是否有 WhatsApp。 |
| data.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.items[].partner_icon | 未约定 | 机构图标。 |
| data.items[].partner_id | 未约定 | 机构标识；不能作为达人 ID 使用。 |
| data.items[].partner_name | 未约定 | 机构名称。 |
| data.items[].partner_top3_category | 未约定 | 机构前三类目。 |
| data.items[].partner_top3_category_list | 未约定 | 机构前三类目集合。 |
| data.items[].total_30d_video_live_gmv | number / object | 视频与直播合计 30 天 GMV。 |
| data.items[].total_30d_video_live_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].total_30d_video_live_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].total_30d_video_live_sold_count | 未约定 | 视频与直播合计 30 天销量。 |
| data.items[].total_related_creator_count | 未约定 | 关联达人数。 |
| data.items[].total_related_product_count | 未约定 | 关联商品数。 |
| data.items[].total_related_seller_count | 未约定 | 关联店铺数。 |
| data.items[].video_count | 未约定 | 视频数。 |

比率、时间和累计、7 天、30 天或统计窗口指标按返回原值展示，不擅改百分比、时区或周期。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 成功且业务列表为空时说明当前条件无数据，不自动换词、翻页或修改条件连续试探付费接口。
- `403` 为无权限，停止调用并确认网关是否启用工具，不归入认证或充值流程。
- `501` 为参数校验失败，根据 `errmsg` 核对参数；其他异常按错误消息说明，不自动连续重试付费接口。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/creators/rankings/agencies" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","page":1,"pageSize":10}'
```

## 接口：带货达人榜

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/creators/rankings/commercial`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `page` | integer | 否 | 未约定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未约定 | 每页条数，范围为 1–20。 |
| `date` | string | 是 | - | 统计日期，`YYYYMMDD`。 |
| `granularity` | string | 是 | - | `daily`、`weekly`、`monthly`、`0`、`1` 或 `2`。 |
| `creatorCategory` | string | 否 | 未约定 | 达人分类。 |
| `productCategory` | string | 否 | 未约定 | 商品分类。 |
| `sort` | string | 否 | `total_gmv:desc` | 排序。 |

#### 脚本选项与使用限制

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，同时仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过业务入口缓存读写，强制请求，可能再次消耗算力；仅在用户明确同意额外消耗或调试时使用。 |

请求使用 camelCase 参数名，不发送内部上游 snake_case 参数。认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；透传 `SESSION_ID`（去除首尾空白）、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串。

本接口每次消耗 18 算力。业务入口默认仅缓存成功响应 24 小时，成功的空结果也可缓存。缓存按当前工作目录、网关、密钥指纹、端点和完整参数隔离；命中输出 `Cache hit`，不发请求，不向响应体添加缓存字段。读取缓存时也校验基础及业务规则，不复用不符合规则的缓存。HTTP、连接及业务失败不缓存；显式 `error`、`success=false` 或失败 `errorCode` / `code` 同样不缓存。业务入口负责缓存，公共 `call_api.run` 始终加 `--no-cache`，不重复缓存。

完整响应仅保存在当前工作目录的会话数据目录；目录不可写时报错，不回退到用户目录或临时目录。摘要保留请求参数、顶层状态、`data.total_count`、各业务列表长度和首个非空业务列表的前 3 条，避免把图片数组当作业务主列表。

### 响应结构

字段清单展示 2026-08-29 生产响应中出现的字段，并非每次必返的固定 schema；标为“未约定”的字段未限定类型，按实际响应读取，不补造数据。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer（成功响应示例）；兼容 string / null | 网关状态；成功响应示例值为 200，按基础规则判断。 |
| errmsg | string | 网关消息，成功时通常为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 本接口业务数据。 |
| data.total_count | 未约定 | 返回时表示匹配总数；不从本页长度推算总数。 |
| data.items | array | 业务记录列表；元素字段见下表。 |

金额字段可能为 number 或包含 `unit`、`value` 的 object；先检查运行时类型并保留原币种及单位，不自行换算。

| 字段 | 类型 | 说明 |
|---|---|---|
| data.items[].bio_email | 未约定 | 公开资料邮箱（受展示隐私规则约束）。 |
| data.items[].category_label | 未约定 | 类目标签。 |
| data.items[].country_code | 未约定 | 国家码。 |
| data.items[].creator_oecuid | 未约定 | 达人电商标识。 |
| data.items[].follower_count | 未约定 | 粉丝数。 |
| data.items[].handle | 未约定 | 达人账号名称。 |
| data.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.items[].interval_ecom_video_play_count_growth | 未约定 | 统计区间电商视频播放增量。 |
| data.items[].interval_live_user | 未约定 | 统计区间直播观众指标。 |
| data.items[].interval_new_follower | 未约定 | 统计区间新增粉丝数。 |
| data.items[].l1_category_aggregated_live_gmv | number / object | 一级类目汇总直播 GMV。 |
| data.items[].l1_category_aggregated_live_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].l1_category_aggregated_live_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].l1_category_aggregated_total_gmv | number / object | 一级类目汇总总 GMV。 |
| data.items[].l1_category_aggregated_total_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].l1_category_aggregated_total_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].l1_category_aggregated_video_gmv | number / object | 一级类目汇总视频 GMV。 |
| data.items[].l1_category_aggregated_video_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].l1_category_aggregated_video_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].nickname | 未约定 | 达人昵称。 |
| data.items[].product_count | 未约定 | 商品数。 |
| data.items[].titkok_creator_commercial_interval_live_gmv | number / object | 带货榜统计区间直播 GMV。 |
| data.items[].titkok_creator_commercial_interval_live_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].titkok_creator_commercial_interval_live_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].titkok_creator_commercial_interval_total_video_live_gmv | number / object | 带货榜统计区间视频与直播合计 GMV。 |
| data.items[].titkok_creator_commercial_interval_total_video_live_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].titkok_creator_commercial_interval_total_video_live_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].titkok_creator_commercial_interval_video_gmv | number / object | 带货榜统计区间视频 GMV。 |
| data.items[].titkok_creator_commercial_interval_video_gmv.unit | 未约定 | 仅当金额为对象时读取；原始单位。 |
| data.items[].titkok_creator_commercial_interval_video_gmv.value | 未约定 | 仅当金额为对象时读取；金额原值。 |
| data.items[].uid | 未约定 | 达人 UID。 |
| data.items[].unique_id | 未约定 | 达人账号标识。 |
| data.items[].user_avatar | 未约定 | 达人头像。 |
| data.items[].user_sell_product_l1_category | 未约定 | 推广商品一级类目。 |

`tioktok_*`、`titkok_*` 等上游拼写按真实字段原样读取，不改成 `tiktok_*`。

`bio_email` 与外部社交账号只用于判断公开资料可用性；无明确、合规业务需求时不主动展示或汇总联系方式，不暴露私人信息。

比率、时间和累计、7 天、30 天或统计窗口指标按返回原值展示，不擅改百分比、时区或周期。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 成功且业务列表为空时说明当前条件无数据，不自动换词、翻页或修改条件连续试探付费接口。
- `403` 为无权限，停止调用并确认网关是否启用工具，不归入认证或充值流程。
- `501` 为参数校验失败，根据 `errmsg` 核对参数；其他异常按错误消息说明，不自动连续重试付费接口。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/creators/rankings/commercial" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","page":1,"pageSize":10,"date":"20260828","granularity":"daily"}'
```

## 接口：达人涨粉榜

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/chuhaijiang/creators/rankings/growth`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `country` | string | 是 | - | 小写国家码：`br,de,es,fr,gb,id,it,jp,mx,my,ph,sg,th,us,vn`。 |
| `page` | integer | 否 | 未约定 | 页码，最小 1。 |
| `pageSize` | integer | 否 | 未约定 | 每页条数，范围为 1–20。 |
| `date` | string | 是 | - | 统计日期，`YYYYMMDD`。 |
| `granularity` | string | 是 | - | `daily`、`weekly`、`monthly`、`0`、`1` 或 `2`。 |
| `creatorCategory` | string | 否 | 未约定 | 达人分类。 |
| `productCategory` | string | 否 | 未约定 | 商品分类。 |
| `sort` | string | 否 | `new_follower_count:desc` | 排序。 |

#### 脚本选项与使用限制

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| --inline | CLI flag | 否 | 关闭 | 强制全量输出，同时仍保存完整响应；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过业务入口缓存读写，强制请求，可能再次消耗算力；仅在用户明确同意额外消耗或调试时使用。 |

请求使用 camelCase 参数名，不发送内部上游 snake_case 参数。认证优先读取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；透传 `SESSION_ID`（去除首尾空白）、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`，未设置时为空串。

本接口每次消耗 18 算力。业务入口默认仅缓存成功响应 24 小时，成功的空结果也可缓存。缓存按当前工作目录、网关、密钥指纹、端点和完整参数隔离；命中输出 `Cache hit`，不发请求，不向响应体添加缓存字段。读取缓存时也校验基础及业务规则，不复用不符合规则的缓存。HTTP、连接及业务失败不缓存；显式 `error`、`success=false` 或失败 `errorCode` / `code` 同样不缓存。业务入口负责缓存，公共 `call_api.run` 始终加 `--no-cache`，不重复缓存。

完整响应仅保存在当前工作目录的会话数据目录；目录不可写时报错，不回退到用户目录或临时目录。摘要保留请求参数、顶层状态、`data.total_count`、各业务列表长度和首个非空业务列表的前 3 条，避免把图片数组当作业务主列表。

### 响应结构

字段清单展示 2026-08-29 生产响应中出现的字段，并非每次必返的固定 schema；标为“未约定”的字段未限定类型，按实际响应读取，不补造数据。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer（成功响应示例）；兼容 string / null | 网关状态；成功响应示例值为 200，按基础规则判断。 |
| errmsg | string | 网关消息，成功时通常为 `ok`。 |
| request_id | string | 请求追踪 ID。 |
| data | object | 本接口业务数据。 |
| data.total_count | 未约定 | 返回时表示匹配总数；不从本页长度推算总数。 |
| data.items | array | 业务记录列表；元素字段见下表。 |

金额字段可能为 number 或包含 `unit`、`value` 的 object；先检查运行时类型并保留原币种及单位，不自行换算。

| 字段 | 类型 | 说明 |
|---|---|---|
| data.items[].bio_email | 未约定 | 公开资料邮箱（受展示隐私规则约束）。 |
| data.items[].category_label | 未约定 | 类目标签。 |
| data.items[].channel_id | 未约定 | 频道标识。 |
| data.items[].creator_oecuid | 未约定 | 达人电商标识。 |
| data.items[].follower_count | 未约定 | 粉丝数。 |
| data.items[].handle | 未约定 | 达人账号名称。 |
| data.items[].id | 未约定 | 记录标识；按当前实体与后续接口要求核对用途。 |
| data.items[].interval_new_follower | 未约定 | 统计区间新增粉丝数。 |
| data.items[].nickname | 未约定 | 达人昵称。 |
| data.items[].tioktok_creator_growth_interval_new_follower_ratio | 未约定 | 涨粉榜统计区间新增粉丝比率（原值）。 |
| data.items[].uid | 未约定 | 达人 UID。 |
| data.items[].unique_id | 未约定 | 达人账号标识。 |
| data.items[].user_avatar | 未约定 | 达人头像。 |
| data.items[].user_sell_product_l1_category | 未约定 | 推广商品一级类目。 |
| data.items[].video_count | 未约定 | 视频数。 |

`tioktok_*`、`titkok_*` 等上游拼写按真实字段原样读取，不改成 `tiktok_*`。

`bio_email` 与外部社交账号只用于判断公开资料可用性；无明确、合规业务需求时不主动展示或汇总联系方式，不暴露私人信息。

比率、时间和累计、7 天、30 天或统计窗口指标按返回原值展示，不擅改百分比、时区或周期。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 成功且业务列表为空时说明当前条件无数据，不自动换词、翻页或修改条件连续试探付费接口。
- `403` 为无权限，停止调用并确认网关是否启用工具，不归入认证或充值流程。
- `501` 为参数校验失败，根据 `errmsg` 核对参数；其他异常按错误消息说明，不自动连续重试付费接口。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/chuhaijiang/creators/rankings/growth" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"country":"us","page":1,"pageSize":10,"date":"20260828","granularity":"daily"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-chuhaijiang-tiktok-creator",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
