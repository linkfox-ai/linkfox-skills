# EchoTik TikTok 视频搜索 接口说明

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

## 接口：TikTok 视频列表（listVideo）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/listVideo`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| region | string | 是 | - | 区域码。可选值：US（美国）、ID（印度尼西亚）、TH（泰国）、PH（菲律宾）、MY（马来西亚）、VN（越南）、GB（英国）、MX（墨西哥）、SG（新加坡）、SA（沙特阿拉伯）、BR（巴西）、ES（西班牙）、JP（日本）、DE（德国）、IT（意大利）、FR（法国） |
| userId | string | 否 | - | 达人ID筛选。最大长度 1000 |
| productId | string | 否 | - | 视频关联商品ID。最大长度 1000 |
| productCategoryId | string | 否 | - | 关联商品类目ID。最大长度 1000 |
| minTotalViewsCnt | integer | 否 | - | 视频播放量筛选（最小值） |
| maxTotalViewsCnt | integer | 否 | - | 视频播放量筛选（最大值） |
| minDuration | integer | 否 | - | 视频时长范围筛选(秒)-最小值 |
| maxDuration | integer | 否 | - | 视频时长范围筛选(秒)-最大值 |
| minCreateTime | integer | 否 | - | 发布时间范围筛选(Unix 秒级时间戳)-最小值 |
| maxCreateTime | integer | 否 | - | 发布时间范围筛选(Unix 秒级时间戳)-最大值 |
| salesFlag | integer | 否 | - | 是否带货视频：0=非带货视频、1=带货视频 |
| isAd | integer | 否 | - | 是否投流视频：0=非投流视频、1=投流视频 |
| createdByAi | string | 否 | - | 是否AI视频，字符串 `"true"`=AI视频、`"false"`=非AI视频（正则 `^(true\|false)$`，非布尔型） |
| videoSortField | integer | 否 | 3 | 排序字段：1=total_digg_cnt(点赞数)、2=create_time(发布时间)、3=total_views_cnt(播放量) |
| sortType | integer | 否 | 1 | 排序方式：0=升序(asc)、1=降序(desc) |
| pageNum | integer | 否 | 1 | 分页页码，从1开始 |
| pageSize | integer | 否 | 50 | 每页条数。**须为10的倍数，最大100**；不符合时可能被拒绝或调整。第三方接口单页上限10，内部按10每页多次拉取后合并 |

### 使用限制

- `region` 为必填，接口本身不设默认站点；技能层默认美国站时仍需显式传入 `US`。
- `userId`、`productId`、`productCategoryId` 是内部编号，应从先前查询结果获取。
- 查询结果为实时数据，不存入数据库，不提供服务端二次 SQL 或数据加工；可从本地保存的响应提取字段。
- 此处 `productId` 只是站点视频列表内的筛选条件；已知单个商品的关联视频优先使用 `linkfox-echotik-product-video`。
- 排序不支持视频销量或 GMV；不能把播放量排序解释为销量、GMV 或转化率排行。

#### 脚本选项与运行约定

| 选项 / 配置 | 类型 | 默认值 | 说明 |
|-------------|------|--------|------|
| JSON 参数 | CLI 参数 | 无 | 首个位置参数为请求 JSON，字段见上表。 |
| --inline | CLI flag | 关闭 | 强制全量打印到标准输出，同时保存完整响应。 |
| --no-cache | CLI flag | 关闭 | 禁用本次响应缓存读取和写入。默认启用 24 小时缓存，缓存键按排序后的参数 JSON 计算 SHA-256，取前 16 位；仅使用公共调用器这一层缓存。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 无 | 前者优先，未配置前者时读取后者。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | https://tool-gateway.linkfox.com | 自定义网关基础地址，去掉末尾 `/` 后拼接接口路径。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 空字符串 | 原样作为同名请求头传递；SESSION_ID 同时用于聚合会话输出。 |

响应缓存位于 `<cwd>/linkfox/.cache/linkfox-echotik-list-video/`，命中时标记 `_cache.hit=true`；启用缓存时，失败和空结果也会缓存，不自动重试。完整响应写入当前工作目录下的会话数据目录，使用微秒级时间戳命名以保留同一秒内的多次响应；当前目录不可写时在请求前报错，不回退到家目录或临时目录。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功；完整判断见「响应码规则」 |
| errmsg | string | 业务状态描述 |
| total | integer | 记录数 |
| data | array | 视频列表（详见下方视频字段） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

#### data[*] 视频对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| videoId | string | 视频ID |
| videoDesc | string | 视频描述 |
| officialUrl | string | TikTok官方视频地址 |
| coverUrl | string | 视频封面URL |
| duration | integer | 视频时长(秒) |
| width | string | 视频宽度（像素，如 576） |
| height | string | 视频高度（像素，如 1090） |
| ratio | string | 视频清晰度（分辨率，如 540p/720p） |
| dataSize | string | 视频文件大小 |
| createDate | string | 视频发布日期 |
| userId | string | 达人ID |
| uniqueId | string | TikTok账号ID(unique_id) |
| avatar | string | 达人头像 |
| totalViewsCnt | integer | 总播放量 |
| totalViews1dCnt | integer | 近1天播放量 |
| totalViews7dCnt | integer | 近7天播放量 |
| totalViews30dCnt | integer | 近30天播放量 |
| totalDiggCnt | integer | 总点赞数 |
| totalDigg1dCnt | integer | 近1天点赞数 |
| totalDigg7dCnt | integer | 近7天点赞数 |
| totalDigg30dCnt | integer | 近30天点赞数 |
| totalCommentsCnt | integer | 总评论数 |
| totalSharesCnt | integer | 总分享数 |
| totalFavoritesCnt | integer | 总收藏数 |
| totalVideoSaleCnt | integer | 视频销量(件数) |
| totalVideoSaleGmvAmt | integer | 视频销量GMV(金额) |
| salesFlagText | string | 是否带货视频（是/否） |
| isAdText | string | 是否投流视频（是/否） |
| createdByAiText | string | 是否AI视频（是/否/未知） |
| productCategoryList | string | 商品分类 |
| videoProducts | string | 视频关联商品 |
| region | string | 区域编码 |
| sourceType | string | 商品来源 |
| sourceTool | string | 来源工具 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode / 情况 | 含义 | 处理建议 |
|---------------|------|----------|
| 400 | 参数校验错误 | 检查站点、AI 字符串和分页约定；依据 `errmsg` 中的具体字段及合法值修正。 |
| 消息含 `authorized error` | 认证失败提示 | 按 `onboarding.md` 处理，不自动重复查询。 |

### curl 示例

```bash
curl -X POST ${LINKFOX_TOOL_GATEWAY}/echotik/listVideo \
  -H "Authorization: $LINKFOX_AGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "region": "US",
    "videoSortField": 3,
    "sortType": 1,
    "pageSize": 20,
    "pageNum": 1
  }'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-list-video",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```