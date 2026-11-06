# 完成视频上传接口说明

公共规则与运行约定见 [模块总览](../api.md)。

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

## 接口：完成视频上传（complete_video_upload）

> 官方：[complete_video_upload](https://open.shopee.com/documents/v2/v2.media_space.complete_video_upload?module=91&type=1)

对应脚本：`scripts/complete_video_upload.py`。全部分片发送完成后提交合并。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/developerProxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 固定为 `api/v2/media_space/complete_video_upload`，必须以 api/v2 开头。 |
| method | string | 是 | 上游方法固定 `POST`；外层网关始终 POST。 |
| shopId | string | 与 merchantId 至少一个 | 已授权店铺 ID，推荐使用。公共无店铺接口的省略约定不适用于本操作；本脚本拒绝两者均缺失。 |
| merchantId | string | 与 shopId 至少一个 | 商户 ID；允许与 shopId 同时提供，脚本均转换为字符串。 |
| queryString | string | 本操作不使用 | POST 脚本不发送；developer_proxy_call 辅助函数支持无 ? 前缀的 URL 编码查询串。 |
| body | string | POST 时是 | Shopee 请求体的 JSON 字符串；GET 脚本不发送。 |
| contentType | string | 传 body 时 | 默认 application/json；仅在存在 body 时发送。 |

#### 脚本 JSON 参数与 CLI

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shopId | string | 与 merchantId 至少一个 | 网关选店保留字段；脚本不拼入业务 query/body，服务端另注入 shop_id。 |
| merchantId | string | 与 shopId 至少一个 | 网关选店保留字段；脚本不拼入业务 query/body，服务端另注入 merchant_id。 |
| api | string | 仅通用入口是 | 固定 `complete_video_upload`；专用脚本无需此字段。 |
| skipDepCheck | boolean | 否 | 默认 false；仅在外部已确认依赖时跳过本地检测，不绕过服务端授权。 |
| contentType | string | 否 | 默认 application/json；网关保留字段。 |
| body | object / array / string / number / boolean / null | POST 时至少提供 body / requestBody 之一 | 优先于 requestBody；字符串原样发送，其他值紧凑 JSON 序列化。本操作的上游有效形状仍以官方规范为准。 |
| requestBody | object / array / string / number / boolean / null | POST 时至少提供 body / requestBody 之一 | body 不存在时使用；转换规则同 body。 |
| 顶层业务字段 | any | 本操作不使用 | POST 仅提取注册表 body_fields，本操作未配置此项；顶层业务字段不会自动组成请求体，必须显式提供 body 或 requestBody。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容通用调用选项；业务封装始终禁用响应缓存。 |

保留字段为 shopId、merchantId、skipDepCheck、body、requestBody、api、contentType；不要把 token 等认证数据当作顶层业务字段。请求组装、依赖与落盘规则见 [模块运行约定](../api.md)。

#### 参数与使用限制

- 本接口上游方法为 POST。请求体必须显式提供 body 或 requestBody；可同时提供，此时 body 优先；均未提供时本地退出 1。非空字符串必须是可解析的有效 JSON，否则本地退出 1，不发送请求；空字符串原样透传，不代表满足上游业务要求。
- 全部分片发送完成后提交合并。 视频分片链路为初始化 → 各分片 → 完成 → 查询；取消操作只处理进行中的上传。
- 大文件及二进制分片可能需要网关支持 multipart；本脚本只转发提供的请求体，不会自动读取、切片或编码本地视频，不应宣称已具备通用二进制上传能力。
- 视频上游请求字段、必填项及取值以本接口官方规范为准；本文描述网关与脚本的透传约定，不能据此推断完整的上游字段契约。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态；按公共基础规则判断，不等同于上游 httpStatus。 |
| errmsg | string | 网关消息；错误时保留完整返回。 |
| httpStatus | integer | Shopee 上游 HTTP 状态；脚本仅在网关正常且上游状态为 200 时解析 body。 |
| contentType | string | 上游响应内容类型，如有则原样保留。 |
| body | string | 上游完整 JSON 字符串；业务字段以实际返回为准，不补造缺失字段。 |

#### 本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | 连接或无法解析为 JSON 的 HTTP 错误描述（如有）。 |
| details | string | 非 JSON HTTP 错误原文（如有）。 |
| transportHttpStatus | integer / null | 业务封装附加的 LinkFox 外层 HTTP 状态；连接失败为 null。 |
| rawResponse | any | 仅网关响应不是对象时由业务封装保留原始值。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| api | string | `complete_video_upload`。 |
| developerProxy | object | 完整网关返回与外层状态，不丢弃错误信息。 |
| resolvedPath | string | 实际相对路径 `api/v2/media_space/complete_video_upload`。 |
| queryString | string | 本 POST 操作不生成此输出字段。 |
| requestBody | any | POST 时回显已解析 JSON 请求体；空字符串为 null。 |
| completeVideoUpload | object / array / scalar / null | 网关正常且上游 httpStatus=200 后解析的完整 Shopee body；空或非法 JSON 为 null；未满足状态条件不生成。 |
| completeVideoUploadResponse | any | 已解析对象含非 null response 时从中提取；保留原字段嵌套形状。 |
| completeVideoUpload.error | string | Shopee 业务错误（如有），非空不能判定操作成功。 |
| completeVideoUpload.message | string | Shopee 业务消息（如有）。 |
| completeVideoUpload.response | any | Shopee 业务结果（如有）；视频上传标识、状态及 URL 只在实际返回时使用。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先检查外层网关，再检查 developerProxy.httpStatus；上游不为 200 时不解析为成功。Shopee body 内 error 非空时按 message 解释，不能只依据解析成功宣称操作完成。
- 空 body 或非法 JSON 的解析结果为 null，原始 body 保留在 developerProxy；字段以实际返回和官方文档为准。
- 1002 / 1003 / 1004 / 1005 的含义与处理见 [网关业务错误](../api.md#网关业务错误)，不自动连续重试。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "shopId": "67890",
  "path": "api/v2/media_space/complete_video_upload",
  "method": "POST",
  "body": "${已按官方规范准备的JSON请求体}",
  "contentType": "application/json"
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-shopee-store-media-space",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
