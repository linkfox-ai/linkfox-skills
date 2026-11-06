---
name: linkfox-amazon-store-uploads
description: 为亚马逊卖家 A+ 内容、Messaging 等业务准备图片、视频或附件，申请上传目的地、计算文件摘要并完成 PUT 或 multipart POST 预签名上传，取得后续业务可引用的上传资源标识。适用于亚马逊通用文件上传、A+ 图片与视频上传及 Messaging 附件准备；不适用于订单查询或批量 Feed 文档上传。
---

# Amazon 店铺文件上传

## 适用范围

### 适用

为已授权亚马逊卖家的 A+ 内容、Messaging 等业务上传图片、视频或附件。用户希望获得可供后续业务引用的上传资源时使用，无需明确提及 Uploads API。

**场景速查**

| 用户表达 | 使用场景 |
|---|---|
| 为 A+ 内容上传一张图片 | 申请上传目的地并上传素材。 |
| 为 Messaging 准备附件 | 按下游业务要求完成附件上传。 |
| 已有 upload destination，帮我上传文件 | 使用返回地址和请求头上传原始文件。 |
| 根据本地文件生成 contentMD5 | 计算文件摘要并准备上传申请。 |

### 边界

订单查询使用 `linkfox-amazon-store-orders`；批量 Feed 文档上传使用 `linkfox-amazon-store-feeds` 的专用流程。

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 创建上传目的地（`createUploadDestinationForResource`） | POST `/spApi/developerProxy` -> path：`uploads/2020-11-01/uploadDestinations/{resource}`，上游方法 POST | `scripts/create_upload_destination_for_resource.py` | 获得上传地址、请求头和资源标识。 |
| 上传文件（非 LinkFox 接口，不计入业务接口数） | PUT 或 multipart POST `uploadDestination.url` | `scripts/upload_to_destination.py` | 直接上传到 Amazon 返回的预签名地址。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-amazon-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖。准备用户的文件及对应下游业务，具体参数与运行约定见 `references/api.md`。

## 上传流程

1. 确认目标店铺、站点及下游业务，准备待上传素材。
2. 运行 `scripts/create_upload_destination_for_resource.py` 申请上传目的地，按需由脚本计算文件摘要。
3. 检查创建结果，再将取得的目的地交给 `scripts/upload_to_destination.py` 上传同一份文件；独立入口默认 PUT，A+ 表单目的地传 `method: "POST"`。也可在创建时传 `uploadFile: true`，同一进程申请并上传，A+ 默认 POST，其他资源默认 PUT。
4. 确认上传结果后，在 A+ 或 Messaging 等后续业务中引用 `uploadDestinationId`。上传完成与下游业务提交是两个阶段。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；创建目的地和文件上传均不读取或保存响应缓存。失败或空结果时，先检查响应、素材及目标资源，不自动修改参数连续试探；结果不确定时先核验状态，避免重复写入。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-uploads-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **理解上传资源**：目的地包含后续引用标识、上传地址与请求头；文件摘要用于校验上传内容。字段和编码规则见 `references/api.md`。
- **先展示创建结果，再展示上传结果**：先检查 `developerProxy`，再展示 `uploadDestination`；注明店铺、站点、上传阶段、资源标识和实际结果，不把创建目的地当作文件已上传。
- **查看运行约定**：本技能的缓存例外、CLI 和认证兼容说明见 `references/api.md`。
- **处理错误与保护状态**：保留已取得的资源标识，按接口参考解释原因与店铺保护要求；结果不确定时不直接重复写入。

## 使用示例

### 从本地文件准备 A+ 图片

```bash
python scripts/create_upload_destination_for_resource.py '{"sellerId":"A1...","region":"NA","resource":"aplus/2020-11-01/contentDocuments","marketplaceId":"ATVPDKIKX0DER","filePath":"/path/to/banner.jpg","contentType":"image/jpeg","uploadFile":true}'
```

### 上传到已返回的目的地

将创建结果中的完整 `uploadDestination` 对象（含 `payload` 包装时也可直接使用）或 `resolvedUploadDestination` 传给上传脚本，使用同一份文件。原始输出可能含有临时签名凭据，不要对外分享：

```bash
python scripts/upload_to_destination.py '{"uploadDestination":{"url":"https://example.invalid/presigned","headers":{}},"filePath":"/path/to/banner.jpg"}' --inline
```

A+ 表单上传使用完整返回 URL，显式指定 POST：

```bash
python scripts/upload_to_destination.py '{"method":"POST","uploadDestination":{"url":"https://example.invalid/presigned?key=YOUR_KEY&policy=YOUR_POLICY","headers":{}},"filePath":"/path/to/banner.jpg","contentType":"image/jpeg"}' --inline
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
