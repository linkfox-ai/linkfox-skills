# Shopee 获取店铺视频列表 接口说明

公共约定见 [总览](../api.md)，认证和用量问题见 [引导](../onboarding.md)。文中 scripts/ 路径均相对于技能根目录。

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

## 接口：获取店铺视频列表（get_video_list）

> 官方：[get_video_list](https://open.shopee.com/documents/v2/v2.video.get_video_list?module=129&type=1)
> 对应脚本：`scripts/get_video_list.py`；通用入口：`scripts/video_api.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/video/get_video_list`，必须以 `api/v2` 开头，不含主机名。 |
| method | string | 是 | 上游方法固定 `GET`；LinkFox 外层始终 POST。 |
| shopId | string | 与 merchantId 至少一项 | 已授权店铺 ID，推荐使用；脚本转为字符串。本视频模块不适用 Public 接口可省略店铺的通用例外。 |
| merchantId | string | 与 shopId 至少一项 | 商户 ID；同传两者时保留，不擅自切换店铺。 |
| queryString | string | GET 视业务需要 | 不含 `?`；业务字段与编码规则见下方。 |
| body | string | 否 | 本 GET 操作的脚本不发送请求体；业务字段通过 queryString 传递。 |
| contentType | string | 否 | 默认 `application/json`；脚本仅在 body 不为 null 时加入网关请求。 |

#### 脚本 JSON 参数与上游字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一项 | 已授权店铺 ID，含义同上。 |
| merchantId | string | 与 shopId 至少一项 | 已授权商户 ID，含义同上。 |
| api | string | 仅通用入口必填 | 固定 `get_video_list`；专用脚本已绑定该操作。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过已由外部验证的本地依赖检查。 |
| contentType | string | 否 | 默认 `application/json`，仅 POST 有请求体时使用。 |
| 业务查询字段 | string / number / boolean | 由上游操作决定 | 放 JSON 顶层；跳过 null 与保留字段，布尔值编码为 true/false，值按百分号编码（空格为 %20，保留字符也编码），字典和数组不发送。注册表的 LIST_QUERY_FIELDS 为空，不擅自启用列表转换。 |

GET 不接受手写 queryString 作为替代入口；脚本会把顶层标量字段拼为 queryString。保留字段为 `shopId`、`merchantId`、`skipDepCheck`、`body`、`requestBody`、`api`、`contentType`，不会进入上游查询。

脚本 CLI、依赖检查与无缓存约定见 [脚本运行约定](../api.md#脚本运行约定)。本文未列出具体约定的上游分页、时间范围、指标筛选、字段类型、默认值及配额，须按已有有效参数与上游文档确定，不承诺未经确认的范围。

### 响应结构

#### 网关返回

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态；按公共基础规则判断。 |
| errmsg | string | 网关消息或错误说明。 |
| httpStatus | integer | Shopee 上游 HTTP 状态，与 LinkFox 外层 HTTP 状态不同。 |
| body | string | Shopee 原始 JSON 字符串，先检查网关和上游状态再解析。 |
| contentType | string | 上游响应内容类型（如返回）；不补造未返回字段。 |

#### 脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | 固定 `get_video_list`。 |
| developerProxy | object | 完整网关返回；错误时也保留。 |
| resolvedPath | string | 固定 `api/v2/video/get_video_list`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时 null。 |
| queryString | string | 仅 GET 且有查询内容时返回，实际发送的查询串。 |
| requestBody | object / array / scalar / string / null | 仅 POST 返回，合法 JSON 字符串解析后展示；非 JSON 字符串原样保留。 |
| getVideoList | object / array / scalar / null | 网关正常且上游 httpStatus=200 时解析完整 Shopee body；空白或非法 JSON 为 null。 |
| getVideoListResponse | object / array / scalar | 仅上述解析结果为对象且 response 不为 null 时，提取其 response。 |
| getVideoList.response | object / array / scalar | Shopee 业务响应；内部字段按实际返回保留，不假定固定结构。 |
| getVideoList.error / getVideoList.message | 未固定 | Shopee 如返回业务错误与消息，按原始内容解释；这些字段不保证必返，也不假定固定结构。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后先检查 `developerProxy.httpStatus`，仅上游为 200 才解析 `getVideoList` 和可用的 `getVideoListResponse`；上游非 200、空白响应或解析失败保留原始 body，不认定业务成功。
- 上游 body 能解析不等于业务成功；仍须检查 Shopee 实际返回的业务错误与查询结果。

| errcode | 含义 | 处理 |
|---|---|---|
| 1002 | 参数错误或未登录 | 核对店铺身份与 API Key。 |
| 1003 | 代理或网络异常 | 保留错误；继续查询前按调用约束决定是否重试。 |
| 1004 | 无授权记录 | 回到授权技能核对目标店铺。 |
| 1005 | 路径未在白名单，或授权信息已失效 | 按实际 errmsg 区分：路径问题核对本操作的 `api/v2/video/...`；授权失效则回到授权技能重新授权。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path": "api/v2/video/get_video_list", "method": "GET", "shopId": "67890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-video",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
