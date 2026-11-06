# EchoTik TikTok 批量视频详情 接口说明

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

## 接口：批量获取视频详情

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/batchVideoDetail`

### 请求参数

#### POST Body（JSON）

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| videoIds | array&lt;string&gt; | 否* | - | TikTok视频ID列表，最多1000个。从 `linkfox-echotik-list-video` 等结果获取 |
| videoUrls | array&lt;string&gt; | 否* | - | TikTok视频URL列表（形如 `https://www.tiktok.com/@<unique_id>/video/<videoId>` 或 `https://www.tiktok.com/video/<videoId>`），最多1000个；服务端从每个URL提取末尾 `videoId` 并合并到 `videoIds`，与 `videoIds` 不互斥 |

\* `videoIds` 与 `videoUrls` 至少传一个；两者可同时传入，服务端合并去重后查询。单次合计最多 1000 个。

#### 参数约束与使用限制

- 视频 URL 必须以视频 ID 结尾；支持带 `@<unique_id>` 的视频链接和 `/video/<videoId>` 形式，不在本技能内展开短链接或自动发现视频。
- 仅查询已有标识的视频详情，不支持按区域或其他筛选条件发现视频。
- 结果来自实时查询，不存入业务数据库，不支持服务端二次 SQL / 数据加工；本地响应文件可用于提取和展示。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 默认值 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 无 | 第一个位置参数，对应上述 POST Body。 |
| --inline | CLI flag | 关闭 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 关闭 | 禁用本地业务缓存的读取和写入。业务封装调用公共 `run` 时始终传入此项，防止启用第二层缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | https://tool-gateway.linkfox.com | 网关基础地址，去除末尾 `/` 后拼接接口路径。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 无 | 优先主变量，回退兼容变量；缓存命中时无需重新认证。 |
| SESSION_ID | 环境变量 | 自动生成 | 按任务聚合输出；未配置时在进程内生成稳定的会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 空字符串 | 与 SESSION_ID 一起透传为请求头。 |

缓存键计算方式：将参数按键排序，以保留中文的 JSON 编码计算 SHA-256，取前 16 位。缓存位于 `<cwd>/linkfox/.cache/linkfox-echotik-batch-video-detail/`，有效期 24 小时；损坏或过期时重新请求，命中时返回 `_cache.hit=true`。缓存保存完整响应（包括错误/空结果），不自动重试。

完整响应始终落盘并更新会话 `_meta.json` 与 `index.jsonl`。业务封装在请求前检查当前工作目录下的数据目录可写，不可写即报错；禁止回退家目录、ACPX_WORKSPACES 或临时目录。执行后核验完整响应文件；实际写入失败或文件内容不完整时返回退出码 1，保留已有缓存且不自动重发请求。Windows 标准输出使用 UTF-8，支持中文及 emoji。输出文件使用微秒时间戳，避免同秒查询互相覆盖。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码；200 为成功状态示例，完整判断见公共规则 |
| errmsg | string | 业务状态描述 |
| total | integer | 返回的视频条数 |
| columns | array | 渲染列定义（每项含 `field`/`title`/`cellType`/`filterable`/`sortable`） |
| videos | array | 视频详情列表（详见下方视频对象字段） |
| costToken | integer | 消耗token |
| type | string | 渲染样式（如 `tableListWorkbenches`） |

#### videos[*] 视频对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| videoId | string | 视频ID |
| videoDesc | string | 视频描述/文案 |
| officialUrl | string | TikTok官方视频地址 |
| coverUrl | string | 视频封面URL |
| duration | integer | 视频时长(秒) |
| width | string | 视频宽度(px) |
| height | string | 视频高度(px) |
| ratio | string | 视频清晰度(如 540p/720p) |
| dataSize | string | 视频文件大小 |
| createDate | string | 视频发布日期(yyyy-MM-dd HH:mm:ss) |
| userId | string | 达人ID |
| uniqueId | string | TikTok账号ID(unique_id) |
| avatar | string | 达人头像URL |
| totalViewsCnt | integer | 总播放量 |
| totalViews1dCnt | integer | 最近1天播放量增量 |
| totalViews7dCnt | integer | 最近7天播放量增量 |
| totalViews30dCnt | integer | 最近30天播放量增量 |
| totalDiggCnt | integer | 总点赞数 |
| totalDigg1dCnt | integer | 最近1天点赞增量 |
| totalDigg7dCnt | integer | 最近7天点赞增量 |
| totalDigg30dCnt | integer | 最近30天点赞增量 |
| totalCommentsCnt | integer | 总评论数 |
| totalSharesCnt | integer | 总分享数 |
| totalFavoritesCnt | integer | 总收藏数 |
| totalVideoSaleCnt | integer | 视频销量(件,估算) |
| totalVideoSaleGmvAmt | integer | 视频销售GMV(估算金额) |
| salesFlagText | string | 是否带货视频(是/否) |
| isAdText | string | 是否投流视频(是/否) |
| createdByAiText | string | 是否AI视频(是/否/未知) |
| productCategoryList | string | 关联商品分类(JSON字符串,空为`[]`) |
| videoProducts | string | 视频带货商品(JSON字符串,空为`[]`) |
| region | string | 视频所在区域代码 |
| sourceType | string | 数据来源(如 Tiktok) |
| sourceTool | string | 来源工具(如 EchoTik-视频列表) |

#### columns[*] 渲染列定义

渲染列包含下列键；各键的类型和可用取值以实际响应为准，不预设固定类型或枚举。

| 字段 | 类型 | 说明 |
|------|------|------|
| field | 以实际响应为准 | 渲染字段标识。 |
| title | 以实际响应为准 | 列标题。 |
| cellType | 以实际响应为准 | 单元格展示类型。 |
| filterable | 以实际响应为准 | 是否支持筛选。 |
| sortable | 以实际响应为准 | 是否支持排序。 |

`productCategoryList` 和 `videoProducts` 为 JSON 字符串，无数据时为字符串 `[]`，展示前可解析；字符串内元素的结构以实际响应为准。销量、GMV 及归因数据均为估算值。`createdByAiText` 保留“是 / 否 / 未知”三种含义。

#### 缓存命中附加字段（脚本）

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 缓存命中时附加的本地元数据，不是服务端视频字段。 |
| _cache.hit | boolean | 缓存命中时为 true。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 400 | 参数校验错误 | 参数取值非法，例如视频 URL 格式不合规；根据 `errmsg` 核对具体字段和合法值。 |
| 10000 | 无符合要求的视频 | 输入 ID / URL 均无匹配数据，例如空列表或不存在的 ID；提示核对输入，继续查询遵守成本约束。 |

### 响应示例

```json
{"errcode": 10000, "errmsg": "没有符合要求相关的视频信息"}
```

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/echotik/batchVideoDetail" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"videoIds": ["7030893014180531462"], "videoUrls": ["https://www.tiktok.com/video/6768504823336815877"]}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-batch-video-detail",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
