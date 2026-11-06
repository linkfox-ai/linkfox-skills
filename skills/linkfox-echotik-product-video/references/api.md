# EchoTik TikTok 商品带货视频 接口说明

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

## 接口：查询商品关联带货视频

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/listProductVideo`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productId | string | 是 | 商品ID。最大长度 1000 |
| userId | string | 否 | 达人ID，用于筛选特定达人的带货视频。最大长度 1000 |
| productVideoSortField | integer | 否 | 排序字段：1=播放量、2=点赞数、3=分享数、4=视频销量、5=视频销售GMV、6=发布时间。默认 `1` |
| sortType | integer | 否 | 排序方式：0=升序、1=降序。默认 `1` |
| minCreateTime | integer | 否 | 视频发布时间区间-开始（秒级时间戳） |
| maxCreateTime | integer | 否 | 视频发布时间区间-结束（秒级时间戳） |
| pageNum | integer | 否 | 分页页码。默认 `1` |
| pageSize | integer | 否 | 分页条数（须为10的倍数，最大100；官方接口单页上限10，内部按10每页多次拉取后合并）。默认 `50` |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | JSON | 是 | CLI 的首个位置参数，内容为上表请求体；排序、分页和时间筛选交由服务端执行，脚本不自行拆页。 |
| --inline | CLI flag | 否 | 强制完整打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁用本次响应缓存读取与写入；默认复用 24 小时本地缓存。 |
| --help / -h | CLI flag | 否 | 显示本地用法，不发起请求。 |

- 缓存以请求参数按键排序序列化后的 SHA-256 前 16 位作为键，位置为 `<cwd>/linkfox/.cache/linkfox-echotik-product-video/linkfox-echotik-product-video-<hash>.json`。通过公共 `call_api.run` 管理同一份缓存，不另设业务缓存层；有效缓存可直接复用。
- 透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头；密钥、自定义网关及超时遵循公共调用规范。
- 原始数据按当前目录的会话路径保存，禁止回退到家目录或临时目录；请求前检查根目录与实际会话的 `data` 目录，目录无法创建或不可写时直接报错，不发起请求。认证或算力问题按 `onboarding.md` 处理。
- 脚本以序列化响应的 UTF-8 大小 8000 字节为阈值。大响应摘要保留顶层字段、常见计数、最大列表的长度及前 3 条样本；`--inline` 强制完整打印。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 记录数 |
| data | array | 视频列表（见下方视频对象） |
| columns | array | 渲染的列 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

#### data[*] 视频对象

| 字段 | 类型 | 说明 |
|------|------|------|
| videoId | string | 视频ID |
| productId | string | 商品ID |
| userId | string | 达人ID |
| videoDesc | string | 视频描述 |
| officialUrl | string | TikTok官方视频地址 |
| covet | integer | 分享数 |
| totalFavoritesCnt | integer | 收藏数 |
| totalVideoSaleCnt | integer | 视频销量（估算） |
| totalVideoSaleGmvAmt | integer | 视频销售GMV（估算） |
| hashTag | string | 话题标签 |
| createDate | string (date) | 视频发布日期 |
| region | string | 区域代码 |
| sourceTool | string | 来源工具 |
| sourceType | string | 商品来源 |

#### 状态字段与兼容说明

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态字段，按公共规则判断。 |
| errmsg | string | 错误原因，例如 `authorized error`。 |
| errorCode | 类型未限定，以实际返回为准 | 兼容性状态字段名；与 `errcode` 命名不同，不另设成功判断条件，实际响应按公共规则处理。 |

#### 可选视频信息

| 字段 / 信息 | 类型 | 说明 |
|------|------|------|
| coverUrl | 类型未限定，以实际返回为准 | 视频封面链接；实际返回时可提供缩略图。 |
| duration | 类型未限定，以实际返回为准 | 视频时长，单位秒。 |
| playAddr | 类型未限定，以实际返回为准 | 播放地址，可能很快过期；分享优先使用 `officialUrl`。 |
| 播放量、点赞数、评论数、分辨率 | 字段名和类型以实际返回为准 | 可用于展示的指标或元数据，未约定固定字段名和类型；仅按实际响应展示，不推造字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

### 响应示例

认证错误示例：

```json
{"errcode": 401, "errmsg": "authorized error"}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/echotik/listProductVideo" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"productId":"1729382310407603945","productVideoSortField":1,"sortType":1,"pageSize":20}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-product-video",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
