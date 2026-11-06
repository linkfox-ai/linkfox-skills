# Shopee 删除视频 接口说明

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

## 接口：删除视频（delete_video）

> 官方：[delete_video](https://open.shopee.com/documents/v2/v2.video.delete_video?module=129&type=1)
> 对应脚本：`scripts/delete_video.py`；通用入口：`scripts/video_api.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| path | string | 是 | 固定 `api/v2/video/delete_video`，必须以 `api/v2` 开头，不含主机名。 |
| method | string | 是 | 上游方法固定 `POST`；LinkFox 外层始终 POST。 |
| shopId | string | 与 merchantId 至少一项 | 已授权店铺 ID，推荐使用；脚本转为字符串。本视频模块不适用 Public 接口可省略店铺的通用例外。 |
| merchantId | string | 与 shopId 至少一项 | 商户 ID；同传两者时保留，不擅自切换店铺。 |
| queryString | string | GET 视业务需要 | 不含 `?`；业务字段与编码规则见下方。 |
| body | string | 网关可选；本操作脚本须提供 | 上游请求体字符串；本视频 POST 操作的脚本要求提供 body 或 requestBody，具体规则见下方。 |
| contentType | string | 否 | 默认 `application/json`；脚本仅在 body 不为 null 时加入网关请求。 |

#### 脚本 JSON 参数与上游字段

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| shopId | string | 与 merchantId 至少一项 | 已授权店铺 ID，含义同上。 |
| merchantId | string | 与 shopId 至少一项 | 已授权商户 ID，含义同上。 |
| api | string | 仅通用入口必填 | 固定 `delete_video`；专用脚本已绑定该操作。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过已由外部验证的本地依赖检查。 |
| contentType | string | 否 | 默认 `application/json`，仅 POST 有请求体时使用。 |
| body | object / string | 与 requestBody 至少一项 | 优先使用；对象以紧凑 JSON 序列化，字符串原样转发。 |
| requestBody | object / string | 与 body 至少一项 | 未提供 body 时使用，编码规则相同。 |

runner 支持按注册表 body_fields 从顶层提取 POST 业务字段，但本模块三个 POST 操作均未配置 body_fields；因此必须提供 body 或 requestBody，不能仅将 video_id 等字段放顶层。显式 body 优先于 requestBody；上游字段和枚举须按有效请求或官方定义填写，不得臆造。

| body 业务字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| video_id | integer / string | 按上游删除要求 | 通过 body 传待删除视频标识；准确类型及是否支持批量删除须按上游要求确认，不推测。 |

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
| api | string | 固定 `delete_video`。 |
| developerProxy | object | 完整网关返回；错误时也保留。 |
| resolvedPath | string | 固定 `api/v2/video/delete_video`。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败时 null。 |
| queryString | string | 仅 GET 且有查询内容时返回，实际发送的查询串。 |
| requestBody | object / array / scalar / string / null | 仅 POST 返回，合法 JSON 字符串解析后展示；非 JSON 字符串原样保留。 |
| deleteVideo | object / array / scalar / null | 网关正常且上游 httpStatus=200 时解析完整 Shopee body；空白或非法 JSON 为 null。 |
| deleteVideoResponse | object / array / scalar | 仅上述解析结果为对象且 response 不为 null 时，提取其 response。 |
| deleteVideo.response | object / array / scalar | Shopee 业务响应；内部字段按实际返回保留，不假定固定结构。 |
| deleteVideo.error / deleteVideo.message | 未固定 | Shopee 如返回业务错误与消息，按原始内容解释；这些字段不保证必返，也不假定固定结构。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后先检查 `developerProxy.httpStatus`，仅上游为 200 才解析 `deleteVideo` 和可用的 `deleteVideoResponse`；上游非 200、空白响应或解析失败保留原始 body，不认定业务成功。
- 上游 body 能解析不等于发布、编辑或删除成功；仍须检查 Shopee 实际返回的业务错误与操作结果。写入结果不确定时不得自动重发。

| errcode | 含义 | 处理 |
|---|---|---|
| 1002 | 参数错误或未登录 | 核对店铺身份与 API Key。 |
| 1003 | 代理或网络异常 | 保留错误；不得自动重试写入，继续调用前按调用约束处理。 |
| 1004 | 无授权记录 | 回到授权技能核对目标店铺。 |
| 1005 | 路径未在白名单，或授权信息已失效 | 按实际 errmsg 区分：路径问题核对本操作的 `api/v2/video/...`；授权失效则回到授权技能重新授权。 |

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"path": "api/v2/video/delete_video", "method": "POST", "shopId": "67890", "body": "{\"video_id\":123456}", "contentType": "application/json"}'
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
