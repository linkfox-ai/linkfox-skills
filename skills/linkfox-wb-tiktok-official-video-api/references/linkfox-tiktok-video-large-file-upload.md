# Shoppable Video 大文件分片上传

适用于 >10MB 视频；旧请求头特殊参数方案已于 2026-01-31 停止支持。流程为 Initialize → 顺序 PUT 分片并合并 → Bind，最终取得 `file_id`。

## Step 1 Initialize（当前阻塞）

- 上游：`POST open/202505/file/init`（版本以官方文档为准）
- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 精确 `toolName`：`tiktokVideo/developerProxy`
- 阻塞：`open/` 不在当前 `developerProxy` 白名单，预期返回 `1005`。未获后端确认前不得调用、改猜路径或声称初始化成功。

若白名单获正式放行，调用形态如下；WorkBuddy 自动处理认证，不传 headers 或凭证：

| `body` 字段 | 类型 | 说明 |
|---|---|---|
| file_size | int64 | 文件总字节数 |
| chunk_size | int64 | 分片大小（字节） |
| file_name | string | 文件名 |
| content_type | string | MIME，如 `video/mp4` |

```json
{"toolName":"tiktokVideo/developerProxy","arguments":{"openId":"<creator_open_id>","path":"open/202505/file/init","method":"POST","contentType":"application/json","body":"{\"file_size\":50000000,\"chunk_size\":10000000,\"file_name\":\"video.mp4\",\"content_type\":\"video/mp4\"}"}}
```

| 预期响应字段路径 | 类型 | 说明 |
|---|---|---|
| upload_url | string | 分片上传目标完整 URL，含 query；Step 2 使用 |
| upload_token | string | 本次上传会话标识；Step 2/3 使用 |

## Step 2 顺序 PUT（本地 helper）

这不是 MCP 或工具网关调用。只有在 Step 1 返回可信的完整 `upload_url` 后，运行：

```text
python scripts/large_file_upload.py --upload-url <complete_upload_url> --file <video_path> --chunk-size 10485760 --content-type video/mp4
```

helper 逐片读取本地文件，依序向同一 `upload_url` PUT，并设置：

| Header | 说明 |
|---|---|
| Content-Type | 视频 MIME |
| Content-Length | 当前分片字节数 |
| Content-Range | `bytes {first}-{last}/{total}` |

分片建议 5MB~64MB，至少 1 片、最多约 1000 片，最后一片包含余数。脚本拒绝工具网关域名和非 HTTPS URL，不读取 LinkFox API Key，也不自动重试失败分片。完整 `upload_url` 已含所需 query；由于来源未明确 `upload_token` 的独立 header/query 放置方式，helper 不自行添加它。

| 分片 PUT 响应字段路径 | 类型 | 说明 |
|---|---|---|
| （响应体） | 来源未说明 | 来源未定义成功响应字段；以 HTTP 2xx 作为该分片传输完成信号 |

## Step 3 Bind（当前阻塞）

- 上游候选：`POST open/202505/file/bind`
- 精确 `toolName`：`tiktokVideo/developerProxy`
- 阻塞：`open/` 未放行，且来源明确称路径也可能为 `complete`/`commit`，必须以官方最新版确认，不得猜测或调用。

| `body` 字段 | 类型 | 说明 |
|---|---|---|
| upload_token | string | Step 1 返回的上传会话标识 |
| resource_type / biz_type | string | 可购物视频业务资源类型；准确字段名和枚举来源未说明 |

仅在路径、字段及白名单均获确认后才可构造 MCP 调用。

| 预期 TikTok 响应字段路径 | 类型 | 说明 |
|---|---|---|
| code | integer | 业务状态码（来源示例确认） |
| data | object | 返回信息（来源示例确认） |
| data.video_file | object | 视频文件信息（来源示例确认） |
| data.video_file.id | string | 绑定所得文件 id，供预检/发布使用 |
| data.video_file.md5 | string | 文件 MD5（来源示例确认；说明未另行定义） |
| message | string | 业务消息（来源示例确认） |

## 安全、错误与成本

Step 1/3 的 MCP 错误按 `onboarding.md` 分层；`1005` 是路径白名单错误。相同调用不重试。Step 2 只访问 Step 1 返回的 HTTPS 文件网关 URL，失败立即停止，保留已完成分片范围并由用户决定后续动作。不得自动重新初始化、重新上传或绑定。

## 响应字段来源

仅据 `skills/linkfox-tiktok-video/references/large-file-upload.md` 的 Step 1 Success Response、Step 2 明示内容和 Step 3 Success Response 示例恢复。来源未说明的类型、准确 bind path/字段名和分片响应均明确标为未说明或阻塞。
