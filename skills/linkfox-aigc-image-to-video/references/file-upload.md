# AIGC 素材统一上传 接口说明

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

## 接口：Base64 上传（uploadByBase64）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/uploadByBase64`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| fileName | string | 是 | 文件名，扩展名为 jpg/jpeg/png/webp/mp4/mov；不得改变源格式，jpeg 与 jpg 兼容。 |
| base64 | string | 是 | 原文件内容的 Base64 编码，不使用 data URI；辅助脚本在进程内构造，不落盘请求。 |

#### 上传辅助 CLI

优先调用 `../scripts/upload_file.py '<JSON 参数>' [--inline]`，不依赖 STS、OSS SDK 或其他 skill。低层 `../scripts/upload_by_base64.py '<JSON 参数>' [--inline] [--no-cache]` 仅供显式使用，正式素材处理不把 Base64 放入操作系统命令行。

| 参数／选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| filePath | string | 与 url 二选一 | 本地文件或附件路径，支持 expanduser，读取实际文件。 |
| url | string | 与 filePath 二选一 | 外部 HTTP(S) URL，先下载再编码上传；不向源站发送 LinkFox 认证头。 |
| fileName | string | 否 | 指定文件名，必须保持源格式，jpeg 与 jpg 等价，文件名取 basename。 |
| --inline | CLI flag | 否 | 强制全量打印响应，仍保存完整 JSON。 |
| --no-cache | CLI flag | 否 | 低层入口提供 24h 缓存及关闭选项；upload_file.py 始终在进程内传 --no-cache，不持久化 Base64 缓存键或上传请求。 |

#### 素材限制与处理约定

- 本地文件和外部公开 HTTP(S) URL 一律先上传，取得 viewUrl 后填入生成字段；不能把路径、源 URL、Base64 或 data URI 直接作为生成素材地址。
- 原文件最大 35 MiB（36700160 字节）且非空，支持 jpg/jpeg/png/webp/mp4/mov；模型对图片／视频的大小、尺寸、数量等仍需分别满足，上传成功不保证生成兼容。此辅助上限与生成模型可接收的更大视频上限是不同限制，不自动绕过。
- 外部 URL 只允许 HTTP(S) 及同类重定向，150s 下载超时；按最终 URL 扩展名、Content-Type 或 PNG/JPEG/WEBP/MP4/MOV 文件头识别格式。识别或读取失败停止，不提交生成。
- 在下载源素材前检查主／备用密钥。源文件仅在进程内读取并编码；命令行只传路径／源 URL，不包含 Base64、凭证或请求文件；响应 JSON 可落盘，不保存源内容。
- 失败不得擅自裁剪、压缩、改图或无限重试；不回退 STS／OSS，不调用 oss/getStsVoucherByAPI。上传同步返回公开 URL，免费 （限时），不创建 taskId，不轮询；沿用用户本次处理素材的授权，不重复确认，不上传无关文件。
- 每个不同源路径／URL 上传一次，保存本次来源到 viewUrl 的映射；同一素材用于多字段时复用，多图保留顺序。查询不上传，不跨任务推断永久映射。
- 本技能当前实际素材字段为 imageUrl、imageList、lastFrameImageUrl、video。通用辅助运行时还兼容 modelImageUrl、sceneImageUrl、refImageList、sourceVideoUrl、refVideoUrl，但不得据此给图转视频接口添加未定义字段。其他既有流程中的视频翻译只上传源视频，视频编辑参考图可选，不上传无关图片。
- 完整生成流程见 SKILL.md 的执行流程。只检查响应和 viewUrl；缺少 URL、认证失败或业务失败均立即停止，不创建收费任务。输出目录必须位于可写 cwd/linkfox；环境与低层输出规则见 api.md 的 CLI 说明。
- 透传 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 环境头。仅从 LINKFOX_AGENT_API_KEY 或 LINKFOXAGENT_API_KEY 读取凭证，LINKFOX_TOOL_GATEWAY 选择网关；不输出或保存密钥、Authorization、Base64 或 STS。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| viewUrl | string | 同步上传成功后可公开访问的素材 URL，用于生成媒体字段。 |
| costToken | integer / string | 如实际返回 X-Cost-Token 则保留；此上传流程免费 （限时），不创建生成任务。 |
| errcode | integer / string / null | 网关业务状态，按公共基础规则判断；网关 XML ToolErrorResponse 转成此字段。 |
| errmsg | string | 网关消息或错误原因。 |
| code | integer / string / null | 如返回则保留原业务代码，异常时不得继续依赖链。 |
| error | string | 连接失败、无效响应或接口业务错误；出现时停止依赖链。 |
| details | string | 非 JSON/XML 响应的原始错误内容，如返回则保留。 |
| costCredit | integer / string | 脚本从 X-Cost-Credit 响应头保留的实际费用，缺失表示未知。 |
| transportHttpStatus | integer / null | 业务封装保存的真实外层 HTTP 状态；连接失败为 null，已有缓存可能未保存该字段。 |
| _cache.hit | boolean | 本地命中 24h 响应缓存时为 true，不是服务端字段。 |
### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 只有响应正常且 viewUrl 是非空 HTTP(S) URL 时才能继续依赖生成；没有 taskId 不代表上传失败，本接口是同步上传。
- 源下载或上传失败立即停止，不自动改素材或换上传方式；403 权限问题不归入充值流程。认证与用量异常按 onboarding.md 处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/uploadByBase64" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"fileName":"product.png","base64":"<仅为结构示意，实际由 upload_file.py 在进程内生成>"}'
```

以上仅为协议结构示意，实际使用上传辅助入口，禁止真实接口测试。反馈指引见 [api.md#Feedback](api.md#Feedback)。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-image-to-video",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
