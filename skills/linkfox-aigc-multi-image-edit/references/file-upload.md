# AIGC 素材上传 接口说明

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


## 接口：素材 Base64 上传（uploadByBase64）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/aigc/uploadByBase64`

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| fileName | string | 是 | 保留真实格式的素材文件名；支持 jpg/jpeg/png/webp/mp4/mov。 |
| base64 | string | 是 | 源文件完整字节的 Base64 字符串；由 `upload_file.py` 在内存构造，不放 OS 命令行或请求文件。 |

#### 素材入口 CLI

运行 `python <skill-root>/scripts/upload_file.py '<JSON 参数>' [--inline]`。

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| filePath | string | 与 url 二选一 | 本地或附件路径；展开用户目录并解析绝对路径，必须存在。 |
| url | string | 与 filePath 二选一 | HTTP(S) 外部素材地址，先下载再编码；重定向也须使用 HTTP(S)。源主机不接收 API 凭证。 |
| fileName | string | 否 | 覆盖上传文件名，保持源素材扩展格式（jpg/jpeg 等价），只保留文件名部分。 |
| --inline | CLI flag | 否 | 全量打印响应，同时保存响应 JSON。 |
| --no-cache | CLI flag | 否 | 底层 `upload_by_base64.py` 可用；`upload_file.py` 内部始终传入，避免缓存或保存 Base64 请求。 |

底层上传入口仍支持 JSON、`--inline`、`--no-cache` 和 24 小时响应缓存；直接传 Base64 只供已有内嵌调用兼容，日常使用素材入口，避免素材编码暴露于进程命令行。业务封装总通过公共 `call_api.run(..., --no-cache)`，缓存只由业务层维护，不叠加第二份缓存。

#### 上传限制

- 支持 jpg/jpeg/png/webp/mp4/mov；解码后文件不超过 10 MB，图片最长边不超过 4096；生成接口自己的尺寸、数量和模型限制仍须满足。素材入口会检查非空及字节大小，图片尺寸最终由接口校验。
- 外部 URL 名称先按路径解码，缺少受支持扩展时依次参考内容类型和 PNG/JPEG/WEBP/MP4/MOV 文件头识别格式；识别失败停止。
- 文件名覆盖不得改素材格式，不能失败后擅自裁剪、压缩、改源文件再重试。
- 上传同步返回公开可访问 `viewUrl`，免费 （限时），不创建 `taskId`，不轮询。
- 使用主密钥环境变量 `LINKFOX_AGENT_API_KEY` 或备用 `LINKFOXAGENT_API_KEY`，网关为 `LINKFOX_TOOL_GATEWAY`。素材入口先检查凭证再下载，不输出或保存凭证、Base64、STS；不调用 `oss/getStsVoucherByAPI`。
- 用户要求用提供素材作图或生视频时，根据当前任务授权，只上传本次所需素材，不重复确认，也不上传无关文件。本技能仅创建多图图像任务。

#### 通用媒体字段兼容

通用编排识别 `imageUrl`、`imageList`、`modelImageUrl`、`sceneImageUrl`、`lastFrameImageUrl`、`refImageList`、`sourceVideoUrl`、`refVideoUrl`、`video`；这不表示创建接口接受所有字段，本技能仅按 [多图创建定义](api.md#请求参数) 构造请求。通用视频翻译只需源视频，视频编辑参考图片可选；这些兼容字段不使本技能成为视频创建入口，也不上传无关素材。完整流程见 [完整执行与交付流程](../SKILL.md#完整执行与交付流程)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| viewUrl | string | 上传后公开可访问的 HTTP(S) 地址，用于生成媒体字段。 |
| errcode | integer / string / null | 网关业务状态码，按基础规则解释。 |
| errmsg | string | 网关消息。 |
| code | integer / string / null | 响应兼容字段；若存在，业务编排仅接受 `0`、`"0"`、`200`、`"200"` 或 null，其他值停止依赖流程；不替代公共 HTTP / errcode 基础规则。 |
| error | string | 脚本连接、解析或非标准响应诊断。 |
| details | string / object / array | 非标准响应原始诊断内容。 |
| costToken / costCredit | integer / string | 仅实际返回时保留，分别以本次 `X-Cost-Token` / `X-Cost-Credit` 头为准，不补造费用。 |
| transportHttpStatus | integer / null | 业务封装保留的 HTTP 状态；连接失败为 null。 |
| _cache.hit | boolean | 仅底层入口命中缓存时出现，非服务端字段。 |

上传响应按上表和实际返回值处理，不假设存在其他字段。响应 JSON 落盘，不保存上传请求或源文件内容。保留 XML `ToolErrorResponse` 的 `errcode` 与 `errmsg` 标准化兼容。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 基础规则通过且 `viewUrl` 为非空 HTTP(S) 地址时才准备生成；缺少地址、上传失败或认证失败时停止，不创建收费任务。
- 不无限重试，不回退 STS/OSS 或其他上传方式；403 是权限问题，不通过充值解决。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/aigc/uploadByBase64" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"fileName":"product.png","base64":"<由素材入口在进程内构造>"}'
```

示例值只说明结构；执行前替换为本次真实素材和标识，不使用占位值请求收费测试。

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-aigc-multi-image-edit",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
