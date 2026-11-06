# EchoTik TikTok 视频下载地址解析 接口说明

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

## 接口：解析 TikTok 视频下载地址

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/echotik/getVideoDownloadUrl`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| url | string | 是 | 无 | TikTok 视频地址，支持 `https://vt.tiktok.com/xxx` 短链或 `https://www.tiktok.com/@user/video/xxx` 完整链接；最大长度 1000。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|-------------|------|------|--------|------|
| JSON 参数 | JSON | 是 | 无 | 首个位置参数，原样传递请求字段。 |
| --inline | CLI flag | 否 | 关闭 | 强制完整打印到 stdout，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 关闭 | 禁用响应缓存读写；默认使用 24 小时缓存。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | https://tool-gateway.linkfox.com | 覆盖网关基础地址，自动移除末尾斜杠。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是（至少一个） | 无 | 优先使用前者，也接受后者；两者均为空时退出并提示配置密钥。 |
| SESSION_ID | 环境变量 | 否 | 自动生成 | 聚合同一任务的落盘数据；同进程生成的编号保持稳定。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 空字符串 | 随请求头透传调用上下文。 |

- 入口：`python scripts/echotik_get_video_download_url.py '<JSON 参数>' [--inline] [--no-cache]`。
- 业务脚本使用公共 `call_api.run` 的单层缓存，路径为 `<cwd>/linkfox/.cache/linkfox-echotik-get-video-download-url/`，缓存键为 JSON 参数排序后计算的 SHA-256 前 16 位，有效期为 24 小时；命中时标记 `_cache.hit=true`。缓存也会保存接口返回的错误对象；不得据此自动重试。
- 业务入口将响应按 UTF-8 保存到 `<cwd>/linkfox`；JSON 校验通过后、发起请求前检查当前目录可写性，不可写时报错，不回退到家目录或临时目录；禁止写入 `/tmp`。输出阈值按 UTF-8 字节数计算（8000 字节），摘要、落盘及调用成本约束见 `SKILL.md`。
- Windows 未启用长路径支持时，应在路径较短的工作目录运行，避免缓存文件路径超出系统限制。缓存写入失败会被静默忽略，因此再次执行可能重新请求并产生消耗；不要将缓存视为必然写入成功。

### 响应结构

成功示例中的 HTTP 状态为 200、`errcode=200`、`errmsg="ok"`；是否正常响应统一按公共规则判断。接口媒体字段位于顶层，不包裹在 `data` 中。

| 字段 | 类型 | 是否必返 | 说明 |
|------|------|----------|------|
| noWatermarkDownloadUrl | string | 条件返回 | 视频无水印下载地址，并非所有视频均返回；部分视频受区域、隐私、可用性或源站限制而缺省，此时无法提供无水印下载。 |
| downloadUrl | string | 条件返回 | 视频含水印下载地址，并非所有视频均返回；与无水印地址一同缺省或出现，展示时仍逐项检查。 |
| playUrl | string | 始终返回 | 视频播放地址；下载地址缺省时可用于播放或预览兜底。 |
| coverUrl | string | 始终返回 | 视频静态封面地址。 |
| dynamicCoverUrl | string | 始终返回 | 视频动态封面地址。 |
| videoId | string | 始终返回 | 视频 ID。 |
| columns | array | 始终返回 | 渲染列定义，元素字段见下表，供前端表格渲染使用。 |
| type | string | 始终返回 | 渲染样式，例如 `tableListWorkbenches`。 |
| costToken | integer | 始终返回 | 响应中的 token 消耗计量字段。 |
| errcode | integer | 始终返回 | 业务码；成功值为 200，统一判断见公共规则。 |
| errmsg | string | 始终返回 | 业务信息，成功示例为 `ok`。 |
| url | string | 错误时可能返回 | 参数缺失示例回显空字符串。 |

#### columns 元素字段

元数据键见下表；各键的具体类型和必返性不作保证，以实际响应为准。

| 字段 | 类型 | 说明 |
|------|------|------|
| field | 以实际响应为准 | 对应业务字段名称。 |
| title | 以实际响应为准 | 展示列标题。 |
| cellType | 以实际响应为准 | 单元格渲染类型。 |
| filterable | 以实际响应为准 | 是否支持筛选。 |
| sortable | 以实际响应为准 | 是否支持排序。 |

#### 脚本本地输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| _cache | object | 缓存命中时附加的本地元数据，不是服务端媒体字段。 |
| _cache.hit | boolean | 缓存命中时为 true。 |
| error | string | 网络失败或 HTTP 错误无法解析为 JSON 时的本地错误说明。 |
| details | string | HTTP 错误体非空且无法解析为 JSON 时保留的原始内容。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 400 | 参数错误 | 根据 `errmsg` 补充或修正 `url`，例如 `url 为必填参数`；确认传入非空有效视频链接。 |
| 10000 | 未获取到视频下载地址 | 可能不是有效 TikTok 视频链接、视频不可访问或已删除；提示核对 URL 格式与视频可访问性。 |

### 响应示例

下例中的媒体长地址已缩略，仅用于说明结构，不能直接下载；示例 `costToken` 数值不等同于技能算力报价。

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "videoId": "7096674515245206810",
  "noWatermarkDownloadUrl": "https://v45.tiktokcdn-eu.com/51678f6e0de3...",
  "downloadUrl": "https://v45.tiktokcdn-eu.com/626c5d3d5a7d...",
  "playUrl": "https://v45.tiktokcdn-eu.com/51678f6e0de3...",
  "coverUrl": "https://agent-files.linkfox.com/tiktok/20260629/7096674515245206810.jpg",
  "dynamicCoverUrl": "https://p16-common-sign.tiktokcdn-eu.com/tos-useast2a-p-0037...",
  "type": "tableListWorkbenches",
  "costToken": 12000,
  "columns": []
}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/echotik/getVideoDownloadUrl" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"url":"https://www.tiktok.com/@user/video/1234567890"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-echotik-get-video-download-url",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
