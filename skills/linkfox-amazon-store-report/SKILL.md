---
name: linkfox-amazon-store-report
description: 获取亚马逊已授权店铺的经营报告，支持库存、订单、销售与流量、FBA、财务结算、退货和 Brand Analytics 等报告的请求、状态跟踪、下载、解压与文件交付。适用于拉取或下载 Amazon Seller Central 报告、Business Report、ABA 搜索词，以及批量导出指定时间段的结构化经营数据。少量实时订单、商品或价格查询、商品刊登管理和广告操作使用对应技能；授权与令牌管理由授权技能负责。
---
# Amazon 店铺报告获取

## 适用范围

### 适用

为已授权亚马逊店铺获取经营报告。支持报告类型索引中的 109 个枚举，实际可用性取决于报告权限、账号类型与站点。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 拉亚马逊库存报告 / FBA inventory report | 获取库存或 FBA 报告。 |
| 下载订单数据 / download orders report | 批量导出订单数据。 |
| 获取销售流量报告 / Business Report | 获取销售与流量报告。 |
| 拉财务结算报告 / settlement report | 按指定类型获取结算数据。 |
| 下载 Brand Analytics / ABA 搜索词 | 获取账号有权限的品牌分析报告。 |
| 拉某个时间段的经营数据 | 按用户指定报告类型和日期范围获取。 |

### 边界

授权新店铺、列出已授权店铺、查询或刷新令牌交给 `linkfox-amazon-store-auth`。少量实时订单、商品、价格查询、商品刊登管理、订单处理与广告投放使用对应技能。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 列出现有报告（getReports） | POST `/spApi/developerProxy` -> method：GET；path：`reports/2021-06-30/reports` | `references/api.md` | 直接调用网关 | 手工流程复用已有报告；端到端脚本默认新建。 |
| 创建报告（createReport） | POST `/spApi/developerProxy` -> method：POST；path：`reports/2021-06-30/reports` | `references/api.md`；`references/report-requests/types/README.md`；`references/report-requests/README.md` | `scripts/get_report.py` | 请求指定报告。 |
| 查询报告状态（getReport） | POST `/spApi/developerProxy` -> method：GET；path：`reports/2021-06-30/reports/{reportId}` | `references/api.md` | `scripts/get_report.py` | 跟踪同一个报告任务。 |
| 获取报告文档（getReportDocument） | POST `/spApi/developerProxy` -> method：GET；path：`reports/2021-06-30/documents/{reportDocumentId}` | `references/api.md` | `scripts/get_report.py` | 获取下载元数据后下载、解压并交付。 |

## 前置条件

**先完成依赖检查和选店**：每次进入本技能先执行 `python scripts/check_auth_dependency.py`，或读取认证技能的 `SKILL.md` 确认已安装。缺失时先尝试当前运行时提供的技能安装工具；无法自动安装时，引导用户前往 [LinkFox Skills](https://skill.linkfox.com/) 安装，安装后重新进入本技能。缺失时停止，不静默降级，不绕过依赖调用授权或令牌接口。

依赖满足后委托 `linkfox-amazon-store-auth` 选店，确定店铺和区域，再确认站点、报告类型与时间范围。认证流程及检测路径约定见 [接口说明](references/api.md#运行约定)。

## 报告获取流程

1. **依赖检查**：按前置条件确认认证技能可用。脚本启动时也会执行检查。
2. **选店与核对需求**：由认证技能完成前置选店；业务流程直接交给网关解析店铺令牌，不先取 raw token。
3. **匹配报告类型**：尊重用户指定的类型；按 [完整类型索引](references/report-types.md)、[逐类型请求说明](references/report-requests/types/README.md) 和 [Schema 索引](references/report-requests/README.md) 核对所需信息。
4. **执行报告获取**：推荐 `scripts/get_report.py`，依次创建报告、轮询原任务、取得文档、下载、解压和预览。需要精细控制时可按接口说明先列出现有报告，再查状态与取文档，避免无必要的新建。
5. **处理等待或失败**：保持同一个任务标识；报告失败、权限不足或未知状态时立即停止，解释原因并让用户决定重试、查权限或更换类型。不得自动换类型或重建任务。轮询、超时及店铺保护规则见 [接口说明](references/api.md)。
6. **交付文件**：展示已解压文件的本机 HTTP 地址（若成功启动）、绝对路径、文件名和本机 file URI，并说明 HTTP 地址仅在运行脚本的同一台电脑、服务保持期间有效。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：本工具不消耗算力 （限时）。报告业务封装始终禁用响应缓存；创建任务与状态轮询均使用实时响应。按报告获取流程轮询同一个任务；失败或空结果时，不自动更换报告类型、翻页试探或重复创建任务，后续动作由用户决定。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-amazon-store-report-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、响应头的`X-Cost-Credit`）、最大列表字段的长度和前 3 条样本。
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

- **报告概念**：报告类型描述要导出的经营数据；Marketplace ID 表示区域内具体站点。请求报告、生成报告和下载文件是不同阶段，创建被接受不等于文件已就绪。
- **响应缓存**：业务封装始终禁用响应缓存，创建任务和持续轮询均不复用已保存响应；`--no-cache` 等选项及输出约定见 [接口说明](references/api.md#运行约定)。
- **清晰展示数据**：展示获取进度、文件信息及前几行预览，不附加业务解读。空结果如实说明，缺失字段不补造。
- **尊重报告类型**：用户指定类型失败时不改拉其他类型，例如 ABA 搜索词报告失败后不得改拉库存报告。
- **保护认证信息**：报告业务只使用选定店铺与区域，不输出、不传递 raw token；令牌由服务端后台管理。
- **文件交付**：优先提供已解压文件的本机地址与路径。临时 HTTP 服务启动失败时说明原因，交付已有本地路径与 file URI。Amazon 源地址一般是压缩包，不作为默认下载入口，仅在用户要求或排障需要时提供。
- **解释权限与异常**：品牌分析可能要求品牌备案，Vendor 报告仅对相应账号开放。遵循 [店铺保护与重试](references/spapi-protection.md)，先说明保护原因和等待时间，再给出处理动作。

## 使用示例

### 获取库存报告

```bash
python scripts/get_report.py '{"sellerId":"A1EC6SZ7XAMURH","region":"NA","reportType":"GET_MERCHANT_LISTINGS_ALL_DATA","marketplaceIds":["ATVPDKIKX0DER"]}'
```

### 获取指定日期的销售与流量报告

```bash
python scripts/get_report.py '{"sellerId":"A1EC6SZ7XAMURH","region":"NA","reportType":"GET_SALES_AND_TRAFFIC_REPORT","marketplaceIds":["ATVPDKIKX0DER"],"dataStartTime":"2024-06-01T00:00:00Z","dataEndTime":"2024-06-07T23:59:59Z","reportOptions":{"dateGranularity":"DAY","asinGranularity":"SKU"}}' --inline
```

### 调整等待和交付方式

长时间生成的报告可按 [脚本参数](references/api.md#运行约定) 调整轮询预算；无需本机 HTTP 下载时可关闭临时服务。失败后保留原任务，后续决定交给用户。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
