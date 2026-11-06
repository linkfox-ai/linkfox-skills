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

## 接口：素材上传（uploadByBase64）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/uploadByBase64`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| fileName | string | 是 | 带实际素材扩展名的文件名，支持 jpg/jpeg/png/webp/mp4/mov。 |
| base64 | string | 是 | 原文件字节的 Base64 编码；不将源路径、源 URL 或 data URI 直接当成生成地址。 |

#### upload_file.py 源素材封装

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| filePath | string | 二选一 | 本地文件路径，展开用户目录并解析为绝对路径。 |
| url | string | 二选一 | 外部 HTTP(S) URL，先下载再编码上传；不可与 filePath 同时提供。 |
| fileName | string | 否 | 默认源文件名；必须保留实际媒体格式，jpeg/jpg 视为相同。 |
| --inline | CLI flag | 否 | 完整打印上传响应，同时落盘。 |
| --no-cache | CLI flag | 否 | 低层上传入口支持；upload_file.py 始终启用，避免响应缓存保存源 Base64 请求。 |

#### 使用限制与工作流

1. 本地文件或附件通过 filePath，外部公开 HTTP(S) URL 通过 url，均使用本目录 `scripts/upload_file.py`；不用 STS、OSS SDK 或其他技能。远端下载和重定向须为 HTTP(S)，不向素材主机发送接口凭证。
2. 文件非空、解码后不超过 10MB；图片最长边不超过 4096。生成接口另有尺寸、比例和数量限制，见 [修图接口](api.md)。失败不得擅自裁剪、压缩或修改源文件后重试。
3. 远端无扩展名时按响应 Content-Type 或文件头识别格式；无法识别支持格式时停止。不支持的格式、缺失文件或过大文件在提交前停止。
4. 对每个不同源文件或 URL 上传一次，保存来源与 viewUrl 映射；同一来源用于多个字段时复用，列表保留原顺序。处理本次实际提供且需要的素材，不上传无关图片或文件。已有视频素材同样先上传，参考图仅在实际需要时提供。
5. 仅取得 viewUrl 后填入需要的 imageUrl、imageList、modelImageUrl、sceneImageUrl、lastFrameImageUrl、refImageList、sourceVideoUrl、refVideoUrl 或 video。单图修图只需要其业务字段；不要因为通用准备器支持这些名称就向修图接口添加无关字段。
6. 上传失败、缺少 viewUrl、认证错误时停止，不创建收费任务、不无限重试或回退其他上传方式。全部素材准备好才创建一次；轮询不重复上传。

脚本只在进程内读取或下载素材并构造 Base64，操作系统命令行仅包含源路径或 URL，不包含文件编码或凭证；不保存上传请求和源文件内容。底层通过 call_api.run 请求、保存响应，只使用一层业务缓存；源文件封装绕过缓存。API Key 优先 LINKFOX_AGENT_API_KEY、兼容 LINKFOXAGENT_API_KEY，网关 LINKFOX_TOOL_GATEWAY。

返回 viewUrl 公开可访问。用户已要求使用所提供素材时，按已授权任务完成必要上传，不重复确认，不上传无关内容。不输出或保存凭证、Base64、STS，该流程不调用 oss/getStsVoucherByAPI。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| viewUrl | string | 同步返回的公开素材地址；生成接口只使用此值。 |
| errcode | integer / string / null | 网关状态；按公共响应码基本规则判断。 |
| errmsg | string | 网关消息或具体错误原因。 |
| error | 未限定 | 脚本连接或响应解析错误；出现非空错误时停止依赖链。 |
| code | 未限定 | 其他业务状态码，按实际响应解释，不能仅看退出码。 |
| costToken | number / string | 实际 Token 消耗；响应头 X-Cost-Token 优先，缺失表示未知。 |
| costCredit | number / string | 实际积分消耗；响应头 X-Cost-Credit 优先，缺失表示未知。 |
| transportHttpStatus | integer / null | 业务封装保存的外层 HTTP 状态；连接失败为 null。 |
| details | string | 仅非 JSON/XML 可解析响应时保留原始错误文本。 |
| _cache.hit | boolean | 仅命中业务缓存时为 true。 |

上传免费 （限时），不创建 taskId、不轮询。其他上传业务字段以实际响应为准，不假定额外结构。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 必须取得非空 HTTP(S) viewUrl 才继续生成；非对象、缺失 URL 或上传错误均停止。
- 403 归属或权限问题不归入充值；认证、余额或套餐错误按 [onboarding.md](onboarding.md) 处理。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/uploadByBase64" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  --data '{"fileName":"product.png","base64":"替换为真实文件编码"}'
```

示例仅说明结构；实际操作须替换为本次任务标识和真实素材，不使用占位值执行收费测试。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-image-edit",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
