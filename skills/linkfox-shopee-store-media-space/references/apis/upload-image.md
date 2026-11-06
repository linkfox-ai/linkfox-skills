# 上传图片接口说明

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

## 接口：上传图片（upload_image）

> 官方：[upload_image](https://open.shopee.com/documents/v2/v2.media_space.upload_image?module=91&type=1)

对应脚本：`scripts/upload_image.py`。本地图片编码为 Base64，服务端解码并构造 Shopee 所需 multipart/form-data。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/shopee/uploadMediaSpaceImage`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shopId | string | 是 | 已授权店铺 ID，脚本去除首尾空白。 |
| fileBase64 | string | 是 | 本地图片字节编码的 Base64 ASCII；脚本自动生成。 |
| fileName | string | 是 | 本地图片的文件名，不含目录。 |
| contentType | string | 是 | image/jpeg、image/png 或 image/webp；脚本转小写并去首尾空白。 |

#### 脚本 JSON 参数与 CLI

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shopId | string | 是 | 已授权店铺 ID。 |
| filePath | string | 是 | 本地 JPEG、PNG 或 WebP 路径，支持展开 ~；必须是存在且非空的文件。 |
| contentType | string | 否 | 默认按扩展名推断；显式指定时仍只接受 image/jpeg、image/png、image/webp。 |
| skipDepCheck | boolean | 否 | 默认 false；仅跳过外部已确认的本地依赖检测，不绕过授权。 |
| api | string | 仅通用入口是 | 固定 upload_image。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终禁用响应缓存。 |

#### 参数与使用限制

- 单张最大 10 MB（10 × 1024 × 1024 字节）；零字节、超限、不存在或不支持 MIME 类型时本地退出 1。最终大小与素材限制以 Shopee 官方要求为准。
- 不接受 OSS 外链，不自行拼装 multipart；token、boundary 和上游签名均由服务端处理。Shopee 上游为 POST api/v2/media_space/upload_image。
- add_item 的图片字段使用上传返回的 imageId；本接口没有 developerProxy 响应层。
- 依赖检查、认证兼容、无缓存和会话落盘约定见 [模块运行约定](../api.md)。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息。 |
| httpStatus | integer | Shopee 上游状态。 |
| success | boolean | 上传成功标记，须结合 httpStatus 与 error 判断。 |
| error | string | Shopee 业务错误码；非空时不能判定上传成功。 |
| message | string | Shopee 业务消息或上游响应为空、无法解析等说明。 |
| requestId | string | Shopee 请求 ID，排查上传错误时保留。 |
| imageId | string | Shopee 图片 ID，成功后供商品 add_item 使用。 |
| imageUrl | string | 上游提供时返回的图片链接。 |
| upstreamBody | string | Shopee 原始响应正文，用于核对实际错误或未解析的返回。 |

#### 本地附加字段

| 字段 | 类型 | 说明 |
|------|------|------|
| error | string | 连接失败或非 JSON HTTP 错误时由公共调用器生成；结合 transportHttpStatus 区分上游业务错误。 |
| details | string | 非 JSON HTTP 错误原文，如有。 |
| transportHttpStatus | integer / null | 业务封装附加的 LinkFox 外层 HTTP 状态；连接失败为 null。 |
| rawResponse | any | 网关返回非对象时保留的原始值。 |

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| api | string | upload_image。 |
| uploadMediaSpaceImage | object | 上述完整网关返回及外层状态。 |
| uploadMediaSpaceImage.httpStatus / success / error | integer / boolean / string | 先检查这些字段，不仅凭存在 imageId 判定成功。 |
| uploadMediaSpaceImage.imageId | string | 成功后的图片标识。 |
| uploadMediaSpaceImage.imageUrl | string | 如有则保留，不能假定必有。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层网关正常后，仍须检查 uploadMediaSpaceImage.httpStatus、success 与 error；成功后才读取 imageId，不能将网关正常响应等同于图片上传成功。
- 本接口与 developerProxy 的返回层不同，禁止从 developerProxy 或 uploadImageResponse 读取图片 ID。
- 网关业务错误见 [模块总览](../api.md#网关业务错误)。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/shopee/uploadMediaSpaceImage" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '
{
  "shopId": "67890",
  "fileBase64": "${本地图片的Base64}",
  "fileName": "product.jpg",
  "contentType": "image/jpeg"
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
