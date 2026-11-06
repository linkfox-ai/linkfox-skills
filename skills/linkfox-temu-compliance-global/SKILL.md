---
name: linkfox-temu-compliance-global
description: 管理 Temu 全球站商品合规资料，支持查询治理属性与 GPSR 等合规模板、编辑合规信息、查询待上传资质项、上传和查询商品资质、上传实拍图及合规文件、识别图片和获取加签资源。适用于已授权店铺的商品合规维护与资质提交；不适用于商品库存、价格、促销管理或一般性法律合规咨询。
---
# Temu 全球站商品合规

## 适用范围

### 适用

处理已授权 Temu Global 店铺的商品合规资料、资质和图片。覆盖 Partner Global 的 Product Compliance 菜单。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 这个商品需要填写哪些治理属性或 GPSR 资料 | 查询合规模板与属性要求。 |
| 按这些资料更新合规信息 | 编辑目标商品合规资料。 |
| 还缺哪些证书，帮我上传已有资质 | 查询待上传项，准备文件并提交资质。 |
| 看看证书状态和驳回原因 | 查询商品资质与可用审核信息。 |
| 上传实拍图并检查图片规则 | 上传与识别合规图片。 |
| 读取合规标签或获取加签资源 | 查询标签或获取文件下载响应。 |

### 边界

商品详情、类目、编辑和库存辅助查询使用 `linkfox-temu-manage-product-global`；价格和促销分别使用 `linkfox-temu-price-global`、`linkfox-temu-promotion-global`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 待上传资质项查询（`bg.arbok.open.cert.queryNeedUploadItems`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.arbok.open.cert.queryNeedUploadItems` | [references/apis/bg-arbok-open-cert-query-need-upload-items.md](references/apis/bg-arbok-open-cert-query-need-upload-items.md) | `scripts/global_compliance_arbok_cert_query_need_upload_items.py` | 待上传资质项查询。 |
| 上传商品资质（`bg.arbok.open.cert.uploadProductCert`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.arbok.open.cert.uploadProductCert` | [references/apis/bg-arbok-open-cert-upload-product-cert.md](references/apis/bg-arbok-open-cert-upload-product-cert.md) | `scripts/global_compliance_arbok_cert_upload_product_cert.py` | 上传商品资质。 |
| 商品资质查询（`bg.arbok.open.product.cert.query`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.arbok.open.product.cert.query` | [references/apis/bg-arbok-open-product-cert-query.md](references/apis/bg-arbok-open-product-cert-query.md) | `scripts/global_compliance_arbok_product_cert_query.py` | 商品资质查询。 |
| 合规文件上传（`bg.arbok.open.upload.uploadFile`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.arbok.open.upload.uploadFile` | [references/apis/bg-arbok-open-upload-upload-file.md](references/apis/bg-arbok-open-upload-upload-file.md) | `scripts/global_compliance_arbok_upload_upload_file.py` | 合规文件上传。 |
| 合规编辑（`bg.compliance.edit`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.compliance.edit` | [references/apis/bg-compliance-edit.md](references/apis/bg-compliance-edit.md) | `scripts/global_compliance_edit.py` | 合规编辑。 |
| 合规模板元数据查询（`bg.compliance.metadata.get`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.compliance.metadata.get` | [references/apis/bg-compliance-metadata-get.md](references/apis/bg-compliance-metadata-get.md) | `scripts/global_compliance_metadata_get.py` | 合规模板元数据查询。 |
| 实拍图上传（Flash）（`bg.flash.open.upload.real.image`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.flash.open.upload.real.image` | [references/apis/bg-flash-open-upload-real-image.md](references/apis/bg-flash-open-upload-real-image.md) | `scripts/global_compliance_flash_upload_real_image.py` | 实拍图上传（Flash）。 |
| 上传识别（Flash）（`bg.flash.open.upload.recognize`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.flash.open.upload.recognize` | [references/apis/bg-flash-open-upload-recognize.md](references/apis/bg-flash-open-upload-recognize.md) | `scripts/global_compliance_flash_upload_recognize.py` | 上传识别（Flash）。 |
| 合规标签查询（`bg.goods.compliancelabel.get`） | POST `/temu/proxy` -> 上游 path：`/openapi/router`，Body `type=bg.goods.compliancelabel.get` | [references/apis/bg-goods-compliancelabel-get.md](references/apis/bg-goods-compliancelabel-get.md) | `scripts/global_compliance_goods_compliancelabel_get.py` | 合规标签查询。 |
| 加签文件下载 | POST `/temu/fileDownload` | [references/api.md](references/api.md) | `scripts/temu_global_file_download.py` / `scripts/temu_file_download.py` | 下载 Temu 加签资源。 |

## 前置条件

确认目标店铺、商品及本次读取或提交范围，准备对应 Temu 授权。LinkFox 用户密钥与 Temu 店铺令牌是两套凭证。Temu 手动授权、令牌保存和本地选店见 [references/access-token.md](references/access-token.md) 与 [references/authorization-flow.md](references/authorization-flow.md)；具体参数、默认值和兼容选项见接口文档。

## 合规处理流程

1. 确认店铺、商品和操作目的；缺少 Temu 授权时，先按授权流程引导用户在后台取得令牌，再按需保存到本地。
2. 按用户任务选择查询：读取合规模板、商品资质、待上传项或合规标签，准备已知资料；只查询完成任务需要的数据。
3. 需要提交时，按对应接口文档组织合规属性、资质文件或实拍图；按需先上传素材或识别图片，再执行用户授权范围内的合规编辑或资质提交。
4. 按接口参考依次检查网关与 Temu 业务结果，保留完整响应并展示已返回的资料、错误或审核信息。需要加签资源时使用下载入口，依据实际响应说明结果。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；脚本不读写接口响应缓存。失败或空结果不自动重试或更换参数连续试探；需要继续查询时说明原因和范围，写操作结果不确定时先核对状态，避免重复提交。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-compliance-global-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 格式化 JSON 的 UTF-8 编码不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 格式化 JSON 的 UTF-8 编码超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、已返回的常见计数或状态（如 `total`、`costToken`、`success`）、最大列表字段的长度和前 3 条样本。
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

- **区分授权概念**：Temu 令牌由卖家后台手动获取，不能用 LinkFox 用户密钥替代；本地保存令牌不代表已经验证业务权限。授权应用和站点应与目标店铺一致。
- **清晰展示合规结果**：注明店铺与商品，用表格展示已有属性、待补资料、图片检查结果或资质状态；缺失的说明和枚举标注为“未声明”，不自行解释为审核通过。
- **区分提交与审核**：上传成功、提交成功和资质审核通过是不同结果，以实际业务字段为准。写操作只覆盖用户指定商品和资料，结果不确定时保留响应并说明状态。
- **脚本运行约定**：全局默认、通用代理、双头认证、本地令牌组合定位和无响应缓存约定见 [references/api.md](references/api.md#脚本兼容与运行约定)。
- **按需读取响应**：先看摘要，需要属性或资质明细时从保存文件提取；未展开的对象以实际响应为准，不补成自拟结构。
- **完整文档来源**：Partner 菜单标识和原始文档地址见 [references/partner-global-catalog.md](references/partner-global-catalog.md)，分接口入口见 [references/apis/README.md](references/apis/README.md)。

## 使用示例

### 核对商品需要的合规资料

用户：看看这个全球站商品的合规属性和缺少的证书。

确认店铺与商品，查询模板、现有资质及需要补交的项目，展示返回的属性和缺口。

### 提交用户提供的资质与实拍图

用户：把这些证书和实拍图补到指定商品。

按已查询的要求准备文件与图片，执行必要的上传、识别和提交，说明接口返回的结果及审核信息。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
