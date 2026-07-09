---
name: linkfox-amazon-store-uploads
description: 亚马逊店铺文件上传（与 linkfox-amazon-store-auth 等同系列），经 /spApi/developerProxy 调用 Uploads API v2020-11-01 的 createUploadDestinationForResource，再向返回 URL 上传文件，供 A+ Content、Messaging 等 API 使用。当用户提到上传文件、createUploadDestinationForResource、upload destination、contentMD5、预签名上传、SP-API 上传、A+ 图片上传、Messaging 附件上传 时触发。
---

# Amazon 店铺 Uploads（文件上传）

本 skill 专用于 **向 Amazon 申请上传目的地并上传文件**，与 **`linkfox-amazon-store-auth`** 同系列：先 **`storeTokens`**，再 **`developerProxy`** 调用 **createUploadDestinationForResource**，最后用 **`upload_to_destination.py`** 对返回的 URL 执行 **PUT**（不经网关）。

> 这是 **Uploads API**，不是 Orders 订单接口。订单见 **`linkfox-amazon-store-orders`**；批量 Feed 文件见 **`linkfox-amazon-store-feeds`**。

## 调用方式

- **API 端点**：`POST /spApi/developerProxy`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/<脚本名>.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-uploads-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 官方参考

[createUploadDestinationForResource](https://developer-docs.amazon.com/sp-api/reference/createuploaddestinationforresource) · [Create an upload destination](https://developer-docs.amazon.com/sp-api/docs/create-an-upload-destination)

---

## Prerequisites

1. 依赖 **`linkfox-amazon-store-auth`**。
2. **`resource`** 须与下游 API 文档一致（例如 A+：`aplus/2020-11-01/contentDocuments`；Messaging 为对应 messages 资源路径）。
3. **`contentMD5`** 为待上传文件内容的 **Base64 MD5 摘要**；传 **`filePath`** / **`content`** 时脚本可自动计算。

---

## 工作流

```text
create_upload_destination_for_resource  →  uploadDestination { uploadDestinationId, url, headers }
upload_to_destination (PUT url + headers)  →  在 A+/Messaging 等 API 中引用 uploadDestinationId
```

---

## Scripts

| 脚本 | 说明 |
|------|------|
| `create_upload_destination_for_resource.py` | POST `uploads/2020-11-01/uploadDestinations/{resource}` |
| `upload_to_destination.py` | PUT 到返回的 `url`（带 `headers`） |
| `_spapi_uploads_common.py` | 内部公共模块 |

---

## 示例

```bash
export LINKFOXAGENT_API_KEY="<your-key>"

# 1) 创建上传目的地（自动根据 filePath 计算 contentMD5）
python scripts/create_upload_destination_for_resource.py '{
  "sellerId":"A1...",
  "region":"NA",
  "resource":"aplus/2020-11-01/contentDocuments",
  "marketplaceId":"ATVPDKIKX0DER",
  "filePath":"/path/to/banner.jpg",
  "contentType":"image/jpeg"
}'

# 2) 上传文件（将上一步 stdout 中的 uploadDestination 传入）
python scripts/upload_to_destination.py '{
  "uploadDestination": { "url": "...", "headers": { } },
  "filePath": "/path/to/banner.jpg"
}'
```

---

## Display Rules

1. 成功创建目的地常为 **HTTP 201**；先看 **`developerProxy`**，再看 **`uploadDestination`**。
2. **`resource`** 不要带前导 `/`；path 中会对 `/` 做编码。
3. 网关需放行 **`uploads/2020-11-01/`** 前缀。

**Feedback：** `skillName`：`linkfox-amazon-store-uploads`。

---
*更多跨境 skill：[LinkFox Skills](https://skill.linkfox.com/)*

