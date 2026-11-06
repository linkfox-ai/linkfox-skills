---
name: linkfox-amazon-store-external-fulfillment
description: 管理亚马逊 External Fulfillment 外部履约，支持按 location 查询或发布库存、处理货件、维护包裹和状态、查询配送选项、生成面单与发票及查询退货。适用于 Seller Flex、FBA Onsite、Multi Seller Flex、Easy Ship、Self Ship、MFN Self Delivery、Amazon Pharmacy 等已开通项目及 SmartConnect 场景；不适用于普通卖家订单、FBA 或 MCF 履约。
---
# Amazon 店铺外部履约管理

## 适用范围

### 适用

管理已授权亚马逊店铺 External Fulfillment 项目的库存查询与绝对库存发布、货件处理、包裹维护、配送选项、面单、发票及退货查询。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 查仓库 SKU 库存，或同步库存 | 按 location 查询或发布库存。 |
| 查看并确认外部履约货件 | 查询货件列表、单件详情并按需求确认或拒绝。 |
| 为货件创建包裹、更新配送状态 | 创建或修改包裹及 Self Delivery 状态。 |
| 查询配送方案、生成面单和发票 | 按渠道准备配送与单据。 |
| 查看 EF 退货 | 查询退货列表或单个退货详情。 |

### 边界

普通卖家订单使用 `linkfox-amazon-store-orders`；Feed 改库存使用 `linkfox-amazon-store-feeds`，库存报告使用 `linkfox-amazon-store-report`；FBA / MCF 使用对应履约技能。

## 接口清单

| 接口 | 端点 | 对应脚本 | 说明 |
|---|---|---|---|
| 按 location 查询或发布库存（`batchInventory`） | POST `/spApi/developerProxy` -> POST path：`externalFulfillment/inventory/2024-09-11/inventories` | `scripts/post_batch_inventory.py` | 按 location 查询或发布库存。 |
| 查询货件列表（`getShipments`） | POST `/spApi/developerProxy` -> GET path：`externalFulfillment/2024-09-11/shipments` | `scripts/get_shipments.py` | 查询货件列表。 |
| 查询单个货件（`getShipment`） | POST `/spApi/developerProxy` -> GET path：`externalFulfillment/2024-09-11/shipments/{shipmentId}` | `scripts/get_shipment.py` | 查询单个货件。 |
| 确认或拒绝货件（`processShipment`） | POST `/spApi/developerProxy` -> POST path：`externalFulfillment/2024-09-11/shipments/{shipmentId}?operation={operation}` | `scripts/process_shipment.py` | 确认或拒绝货件。 |
| 创建包裹（`createPackages`） | POST `/spApi/developerProxy` -> POST path：`externalFulfillment/2024-09-11/shipments/{shipmentId}/packages` | `scripts/create_packages.py` | 创建包裹。 |
| 更新包裹（`updatePackage`） | POST `/spApi/developerProxy` -> PUT path：`externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}` | `scripts/update_package.py` | 更新包裹。 |
| 更新包裹状态（`updatePackageStatus`） | POST `/spApi/developerProxy` -> PATCH path：`externalFulfillment/2024-09-11/shipments/{shipmentId}/packages/{packageId}` | `scripts/update_package_status.py` | 更新包裹状态。 |
| 查询配送选项（`retrieveShippingOptions`） | POST `/spApi/developerProxy` -> GET path：`externalFulfillment/2024-09-11/shipments/{shipmentId}/shippingOptions?packageId={packageId}` | `scripts/retrieve_shipping_options.py` | 查询配送选项。 |
| 生成发票（`generateInvoice`） | POST `/spApi/developerProxy` -> POST path：`externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice` | `scripts/generate_invoice.py` | 生成发票。 |
| 读取发票（`retrieveInvoice`） | POST `/spApi/developerProxy` -> GET path：`externalFulfillment/2024-09-11/shipments/{shipmentId}/invoice` | `scripts/retrieve_invoice.py` | 读取发票。 |
| 生成或重新生成面单（`generateShipLabels`） | POST `/spApi/developerProxy` -> PUT path：`externalFulfillment/2024-09-11/shipments/{shipmentId}/shipLabels?operation={operation}` | `scripts/generate_ship_labels.py` | 生成或重新生成面单。 |
| 查询退货列表（`listReturns`） | POST `/spApi/developerProxy` -> GET path：`externalFulfillment/2024-09-11/returns` | `scripts/list_returns.py` | 查询退货列表。 |
| 查询单个退货（`getReturn`） | POST `/spApi/developerProxy` -> GET path：`externalFulfillment/2024-09-11/returns/{returnId}` | `scripts/get_return.py` | 查询单个退货。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-amazon-store-auth` 选店与授权。先运行 `python scripts/check_auth_dependency.py`；依赖缺失时先安装，不在本技能内另行实现授权或令牌逻辑。确认用户指定的店铺、渠道、仓库及货件或退货；角色、allowlist 和依赖检测约定见 `references/api.md`。

## 履约流程

1. 检查授权依赖并选定店铺，明确本次是库存、货件、包裹、单据还是退货任务。
2. 典型履约顺序：查询货件 → 确认货件 → 创建包裹 → 查询配送选项 → 生成发票 → 生成面单 → 更新 Self Delivery 包裹状态；按用户任务与渠道能力选择所需步骤。
3. 查询当前状态后再处理拒绝、修改或重新生成；写入结果不确定时先查状态，不直接重放请求。保留已取得的任务和资源标识。
4. 按接口参考判定网关与上游结果，展示本次完成内容和分页范围；失败或空结果停止连续试探。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；本技能业务脚本不读取或写入响应缓存，相同参数再次运行仍会发起请求。失败或空结果时，不得自动翻页或修改参数连续试探；需要继续时，先说明原因和后续查询范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-external-fulfillment-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、可用的顶层计数或状态、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）（以网关实际计费为准；若网关计费则按算力规则处理）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **响应缓存**：本技能所有业务脚本始终使用 `--no-cache`，不读取或写入响应缓存。相同参数再次运行仍会发起请求，执行前按调用约束判断是否必要。
- **渠道概念**：External Fulfillment 覆盖 Seller Flex / FBA Onsite、Multi Seller Flex、Easy Ship、Self Ship、MFN Self Delivery、Amazon Pharmacy 等；具体可用能力见接口参考。
- **展示结果**：先说明店铺和渠道，用表格展示库存、货件、包裹或退货及操作结果，保留单据位置与可用标识。
- **区分多项结果**：批次请求逐条展示成功与失败；无正文成功也应说明完成的动作，判断依据见 `references/api.md`。
- **控制大文档输出**：发票和面单可能包含 Base64 或预签名 URL，避免反复把整段 Base64 粘贴到上下文；按需从落盘文件提取。
- **解释店铺保护**：先说明正在保护店铺，再说明原因、处理动作和等待时间，避免只说服务器繁忙；具体冷却规则见 `references/spapi-protection.md`。

## 使用示例

### 查询仓库库存

用户：查这个 location 下指定 SKU 的库存。

确认店铺与渠道，按接口参考准备库存查询，展示每个 SKU 的返回结果。

### 处理货件与包裹

用户：确认这些 EF 货件并按我提供的包裹资料生成面单。

读取货件当前状态，按用户指定范围依次处理确认、包裹、配送及面单；按渠道能力判断是否需要发票。

### 查看退货

用户：查看新退货，并展开其中一个退货详情。

查询列表，再读取用户指定的退货，展示状态和逆向物流信息。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
