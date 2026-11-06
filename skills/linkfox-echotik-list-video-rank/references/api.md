# EchoTik TikTok 视频排行 接口说明

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

## 接口：视频排行（listVideoRank）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/listVideoRank`

### 请求参数

网关 POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| date | string | 是 | - | 榜单查询日期，格式 `YYYY-MM-DD` |
| rankType | integer | 是 | - | 榜单类型：`1` = 日榜，`2` = 周榜，`3` = 月榜 |
| region | string | 是 | - | 区域码。可选值：US（美国）、ID（印度尼西亚）、TH（泰国）、PH（菲律宾）、MY（马来西亚）、VN（越南）、GB（英国）、MX（墨西哥）、SG（新加坡）、SA（沙特阿拉伯）、BR（巴西）、ES（西班牙）、JP（日本）、DE（德国）、IT（意大利）、FR（法国） |
| videoRankField | integer | 是 | - | 视频排名指标：`1` = 按播放量（`totalViewsCnt`）排名，`2` = 按视频销量（`totalVideoSaleCnt`）排名；两种取值分别获取高播放量和高销量视频，成功时返回 `errcode:200` |
| productCategoryId | string | 否 | - | 商品一级类目 ID，用于带货视频榜单的商品分类筛选 |
| createdByAi | string | 否 | - | 是否 AI 视频，可选字符串 `true` / `false` |
| pageNum | integer | 否 | 1 | 分页页码，从1开始 |
| pageSize | integer | 否 | 50 | 每页条数。**须为10的倍数，最大100**；官方接口单页上限10，内部按10每页多次拉取后合并 |

#### 参数约定与使用限制

- `date`、`rankType`、`region`、`videoRankField` 均为必填，接口和脚本不自动补默认值。用户未指定站点时，助手可询问，或明确说明采用美国站 `US` 后传入请求。
- 数据通常滞后 1–2 天，过近日期可能没有可用榜单。可建议较早日期，后续查询须遵守 SKILL.md 的成本约束，不自动改日期重试。
- 本接口查询指定周期的实时榜单，不提供服务端二次 SQL 或数据加工能力；不影响从本地保存的 JSON 中提取字段用于展示。
- `pageSize` 的上游分页合并由服务端完成，脚本不额外实现循环抓取。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | string | 是 | 命令行首个位置参数，内容为上述请求体。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 跳过本地缓存读取与响应缓存保存；不影响会话数据落盘。 |

- 脚本调用公共 `call_api.run`，仅使用公共调用器的一层 24 小时本地缓存；缓存目录为 `<cwd>/linkfox/.cache/linkfox-echotik-list-video-rank/`，缓存键为按参数排序后计算的 SHA-256 前 16 位，缓存文件名为 `linkfox-echotik-list-video-rank-<缓存键>.json`；过期或损坏的缓存视为未命中。
- 缓存完整响应，错误及空结果也可能被缓存；复用时解释缓存内容，不自动绕过缓存连续试探。命中缓存时标注 `_cache.hit` 并输出缓存路径。
- 认证优先使用 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；网关优先使用 `LINKFOX_TOOL_GATEWAY`，省略时采用公共规则的基础地址。透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。
- 完整数据、会话元信息与索引写入当前工作目录的 `linkfox/`；业务包装在请求前拒绝 `/tmp` 及其子目录，以真实文件名长度检查会话数据目录可写（包括 Windows 完整路径长度），并固定公共调用器的输出根目录，不使用其家目录或临时目录回退，也不被 `ACPX_WORKSPACES` 改写输出位置。无法保存完整响应时直接报错，不发出业务请求。缓存文件写入失败时忽略该缓存写入错误，不影响已读取的有效缓存或完整响应落盘。
- 会话优先采用 `SESSION_ID`，缺省按时间与随机后缀生成；生成 `_meta.json`、`index.jsonl`，登记调用的技能和数据文件。小响应完整打印，大响应显示摘要与最大列表的前 3 条样本，阈值为 8000 字节。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功；完整判断见下方响应码规则 |
| errmsg | string | 业务状态描述 |
| total | integer | 记录数 |
| data | array | 视频列表（已按 `videoRankField` 排序，详见下方视频字段） |
| columns | array | 渲染的列（前端渲染元数据，长度可能大于 `data`，取数据请以 `data` 为准） |
| type | string | 渲染的样式 |
| costToken | integer | 消耗 Token 数量 |

#### data[*] 视频对象字段

> 以下 25 个字段为 `data[*]` 返回字段，与 `columns` 定义对应。指标字段名虽以 `total` 开头，但表示**所选排行周期内**的累计值（`columns` 列标题为"周期…"）。

| 字段 | 类型 | 说明 |
|------|------|------|
| videoId | string | 视频ID |
| officialUrl | string | TikTok官方视频地址 |
| userId | string | 达人ID |
| uniqueId | string | TikTok账号ID |
| nickName | string | 达人昵称 |
| avatar | string | 达人头像 |
| category | string | 达人分类 |
| videoDesc | string | 视频描述 |
| createDate | string | 视频发布日期 |
| coverUrl | string | 视频封面URL |
| region | string | 区域代码 |
| duration | integer | 视频时长(秒) |
| createdByAiText | string | 是否AI视频（是/否） |
| salesFlagText | string | 是否带货视频（是/否） |
| productCategoryList | string | 带货商品分类 |
| videoProducts | string | 视频带货商品 |
| totalCommentsCnt | integer | 周期评论数 |
| totalDiggCnt | integer | 周期点赞数 |
| totalFavoritesCnt | integer | 周期收藏数 |
| totalSharesCnt | integer | 周期分享数 |
| totalViewsCnt | integer | 周期播放量 |
| totalVideoSaleCnt | integer | 周期视频销量(估算) |
| totalVideoSaleGmvAmt | number | 周期视频销售GMV(估算) |
| sourceTool | string | 来源工具 |
| sourceType | string | 商品来源 |

指标稀疏约定：按 `videoRankField` 排序时，其他指标可能返回 0；按销量排名时播放、点赞、评论等可能为 0，按播放量排名时销量与 GMV 可能为 0。以 `data` 为业务数据依据，不因 `columns` 更长就推断有更多视频。当前字段表不包含画面宽高、比例、1/7/30 日拆分或 `isAdText`，不要套用自由筛选视频列表的结构。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / 现象 | 含义 | 处理建议 |
|------|------|------|
| 400 | 参数校验错误 | 检查四个必填参数以及取值范围，依据 `errmsg` 补充或修正参数。 |
| 10000 / no matching data | 无匹配榜单 | 可能与数据滞后有关，解释日期与筛选范围；如需查询更早日期，先说明额外消耗。 |

### curl 示例

指定日期的美国视频播放量日榜：

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/echotik/listVideoRank" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "date": "2026-08-10",
    "rankType": 1,
    "region": "US",
    "videoRankField": 1,
    "pageNum": 1,
    "pageSize": 20
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-list-video-rank",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
