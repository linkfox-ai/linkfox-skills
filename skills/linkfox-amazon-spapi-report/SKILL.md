---
name: linkfox-amazon-spapi-report
description: 亚马逊SP-API报告自动化获取技能，支持库存报告、订单报告、销售流量报告、FBA报告、财务结算报告等95+种报告类型的全流程自动获取（请求→轮询→下载→解压）；完成后默认启动本机短时HTTP服务，生成extractedFileHttpUrl供浏览器下载已解压文件。本技能依赖 linkfox-amazon-spapi-auth（授权与令牌管理）。当用户提到拉取亚马逊报告、下载Amazon报告、获取库存报告、获取订单报告、FBA报告、销售流量报告、财务结算报告、Brand Analytics报告、ABA搜索词报告、pull Amazon report, download Amazon report, fetch inventory report, fetch orders report, FBA report, sales and traffic report, settlement report, SP-API report时触发此技能。即使用户未明确提及"SP-API"或"报告"，只要其需求涉及从亚马逊卖家后台拉取任何形式的结构化数据（库存、订单、销量、财务、退货等），也应触发此技能。
---

# Amazon SP-API 报告获取

本 skill 提供 **亚马逊 SP-API 报告的端到端自动化获取**：请求 → 轮询 → 下载 → 解压 → 预览。支持 95+ 种报告类型（库存 / 订单 / 销售 / 财务 / FBA / 退货 / Brand Analytics 等）。

---

## ⚠️ Prerequisites — MUST READ FIRST

本 skill **依赖** `linkfox-amazon-spapi-auth`（授权与店铺/令牌管理）。

> 🛑 **如果 `linkfox-amazon-spapi-auth` 未安装 / 未加载，请先安装它，再回到本 skill。**

### 怎样判断 `linkfox-amazon-spapi-auth` 是否可用

在执行任何报告任务之前，agent **必须**先进行依赖检查：

1. **读取下列任一路径**（skill 加载路径取决于运行环境；`scripts/check_auth_dependency.py` 会按相同规则自动探测）：
   - 仓库 / 通用扁平目录：`<skills_dir>/linkfox-amazon-spapi-auth/SKILL.md`
   - Claude：`~/.claude/skills/linkfox-amazon-spapi-auth/SKILL.md`
   - Cursor：`~/.cursor/skills/...`、`~/.cursor/skills-cursor/...`
   - **OpenClaw**：`<OPENCLAW_WORKSPACE>/skills/...`、`~/.openclaw/skills/...`、`~/.agents/skills/...`（与 [OpenClaw Skills 文档](https://docs.openclaw.ai/tools/skills) 的常见路径一致）
   - **Hermes Agent**：`~/.hermes/skills/<category>/linkfox-amazon-spapi-auth/SKILL.md`，以及 `~/.hermes/plugins/<plugin>/skills/linkfox-amazon-spapi-auth/SKILL.md`（与 [Hermes Skills 文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) 的布局一致）
2. **或直接运行脚本**：`python scripts/check_auth_dependency.py`，脚本会在缺失时以 **exit code `42`** 退出，并在 stderr 输出结构化提示（以 `DEPENDENCY_MISSING:` 开头）。脚本已内置 **OpenClaw / Hermes** 路径判断；若在 Hermes 的 `config.yaml` 里配置了 `skills.external_dirs`，请设置环境变量 `HERMES_SKILLS_EXTERNAL_DIRS`（使用系统路径分隔符串联多个目录）以便探测。
3. 如果上述检查**全部失败**，则判定为 **`linkfox-amazon-spapi-auth` 未安装**。

### 发现未安装时的标准处置

当检测到 `linkfox-amazon-spapi-auth` 未安装时，agent **必须**按以下顺序执行：

1. **尝试自动安装**（优先）：
   - 如果当前运行时具备 skill 安装工具（例如 skill 市场 / skill 管理 MCP / `install_skill` 类工具），**立即调用**安装 `linkfox-amazon-spapi-auth`。
   - 安装成功后，重新加载并从头执行本 skill。
2. **引导用户手动安装**（兜底）：
   - 向用户说明：「本技能依赖 `linkfox-amazon-spapi-auth`，尚未安装。请前往 [LinkFox Skills](https://skill.linkfox.com/) 安装该 skill，安装完成后告诉我一声，我会继续为你拉取报告。」
   - **不要**绕过依赖直接去调 `/spApi/authorizeUrl`、`/spApi/storeTokens`、`/spApi/authorizedStores` 等接口——这些接口的选店铺、令牌流程属于 `linkfox-amazon-spapi-auth` 的职责，本 skill 只负责报告业务本身。
3. **不得静默降级**：如果既无法自动安装也未获得用户确认，必须**停止执行**并把依赖缺失的事实回报给用户，不要擅自尝试替代方案。

### 依赖已满足后的协作方式

- 本 skill 会在内部调用依赖 skill 提供的 `/spApi/storeTokens` 取 `accessToken`，然后走 `/spApi/developerProxy` 执行报告生命周期。
- 授权、授权的前置选店铺、令牌刷新等操作——**交由 `linkfox-amazon-spapi-auth`**；本 skill 不重复做这些事。

---

## Core Concepts

- **Report Type（报告类型）**：Amazon SP-API 定义的枚举值，例如 `GET_MERCHANT_LISTINGS_ALL_DATA`、`GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL`。完整列表见 `references/report-types.md`。
- **Marketplace ID**：区域内具体站点 ID，例如 US = `ATVPDKIKX0DER`。
- **Report lifecycle**：请求报告 → 轮询 `processingStatus`（`IN_QUEUE` / `IN_PROGRESS` / `DONE` / `FATAL` / `CANCELLED`）→ `DONE` 后拿到 `reportDocumentId` → 取下载 URL → 下载（多为 gzip TSV）→ 解压。
- **Rate limits**：Reports API 约 0.0222 req/s；轮询需保留间隔（默认 30s）。

## Data Fields

### Report Request Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| sellerId | string | Yes | 已授权的 Amazon Seller ID |
| region | string | Yes | NA / EU / FE |
| reportType | string | Yes | SP-API 报告类型 |
| marketplaceIds | array | Yes | 目标 marketplace ID 列表 |
| dataStartTime | string | No | ISO 8601，报告起始时间 |
| dataEndTime | string | No | ISO 8601，报告结束时间 |
| pollInterval | int | No | 轮询间隔秒数（默认 30） |
| maxAttempts | int | No | 最大轮询次数（默认 20） |

### Report Output

| Field | Type | Description |
|-------|------|-------------|
| reportId | string | 报告请求 ID |
| reportDocumentId | string | 报告文档 ID |
| downloadPath | string | 本地下载后的**绝对路径**（已解压，含文件名） |
| fileName | string | 保存文件名（与 `downloadPath` 末段一致） |
| localFileUri | string | 本机 `file://` URI，便于客户端打开本地文件 |
| extractedFileHttpUrl | string | **本机临时 HTTP** 直链，用于在浏览器中下载**已解压**后的文件（默认 `serveExtractedFileHttp` 开启） |
| extractedFileHttpServeSeconds | int | 本地 HTTP 服务保持时长（默认 300，最少 10） |
| extractedFileHttpNote | string | 说明该链接仅本机、限时有效 |
| amazonDownloadUrl | string | （可选）仅当 `includeAmazonSourceUrl: true` 时出现：Amazon 源地址，一般为压缩包，通常不必给终端用户 |
| compressionAlgorithm | string | 若 SP-API 返回了压缩算法则带上（如 GZIP） |
| tempDirectory | string | 临时目录 |
| fileSize | int | 文件大小（字节） |

## API Usage

本 skill 主要调用 `/spApi/developerProxy`（SP-API 代理），并复用 `linkfox-amazon-spapi-auth` 的 `/spApi/storeTokens` 获取 `accessToken`。详见 `references/api.md`。

### Available Scripts

- `scripts/get_report.py` ⭐ — 端到端自动化报告获取（**推荐**）
- `scripts/check_auth_dependency.py` — 主动检测依赖 skill `linkfox-amazon-spapi-auth` 是否已安装

## Usage Scenarios

### Scenario 0: Dependency Check (MUST run first)

**每次进入本 skill 都要先跑这一步。**

1. 尝试读取 `linkfox-amazon-spapi-auth/SKILL.md`（若工具允许）
2. 或执行：
   ```bash
   python scripts/check_auth_dependency.py
   ```
3. 若 exit code 非 0 或 stderr 含 `DEPENDENCY_MISSING:`，按上文「发现未安装时的标准处置」流程处理
4. 依赖满足后再进入正常业务场景

### Scenario 1: Pull Amazon Report (Automated, Recommended)

**User request**：「我要拉库存报告」/「获取订单报告」/「下载销售流量报告」等

**Steps**：
1. **依赖检查**（Scenario 0）
2. **前置选店铺 + 取令牌**：委托 `linkfox-amazon-spapi-auth`
   - 调 `/spApi/authorizedStores` 让用户选店铺
   - 调 `/spApi/storeTokens` 获取令牌（本 skill 的脚本会自动完成此步，无需手动调）
3. **识别报告类型**：按用户诉求匹配 `reportType`
   - 库存：`GET_MERCHANT_LISTINGS_ALL_DATA`、`GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA`
   - 订单：`GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL`
   - 销售流量：`GET_SALES_AND_TRAFFIC_REPORT`
   - 财务：`GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE`
   - 完整清单：`references/report-types.md`
4. **执行脚本**：
   ```bash
   python scripts/get_report.py '{
     "sellerId": "A1EC6SZ7XAMURH",
     "region": "NA",
     "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
     "marketplaceIds": ["ATVPDKIKX0DER"]
   }'
   ```
5. 脚本会自动：取令牌 → 请求报告 → 轮询 → 下载 → 解压 → 预览 → 输出 JSON；**完成后**在 stderr 与 JSON 中给出 **本地绝对路径**（`downloadPath`）、**本机 file URI**（`localFileUri`），并默认启动短时本机 HTTP 服务，生成 **`extractedFileHttpUrl`**（用于在**同一台机器**的浏览器里下载**已解压**文件）。向用户展示时至少给出 **`extractedFileHttpUrl`**、**`downloadPath`** 与 **`fileName`**；脚本在 `serveSeconds` 计时结束后会关闭服务，链接随即失效。若需 Amazon 源地址（多为压缩包），仅调试时设 `includeAmazonSourceUrl: true`。

### Scenario 2: Manual Report Flow (Advanced)

对需要精细控制的场景，可通过 `/spApi/developerProxy` 手工驱动：

1. **取现有报告**（更快）：
   ```
   path: reports/2021-06-30/reports
   method: GET
   queryString: reportTypes=<type>&marketplaceIds=<ids>
   ```
2. **创建新报告**：
   ```
   path: reports/2021-06-30/reports
   method: POST
   body: {"reportType": "...", "marketplaceIds": [...]}
   ```
3. **查状态**：
   ```
   path: reports/2021-06-30/reports/{reportId}
   method: GET
   ```
4. **取下载链接**：
   ```
   path: reports/2021-06-30/documents/{reportDocumentId}
   method: GET
   ```

### Scenario 3: Custom Date Range / Polling

```bash
python scripts/get_report.py '{
  "sellerId": "A1EC6SZ7XAMURH",
  "region": "NA",
  "reportType": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z",
  "pollInterval": 15,
  "maxAttempts": 40
}'
```

## Marketplace IDs by Region

| Region | Country | Marketplace ID |
|--------|---------|----------------|
| NA | United States | ATVPDKIKX0DER |
| NA | Canada | A2EUQ1WTGCTBG2 |
| NA | Mexico | A1AM78C64UM0Y8 |
| EU | United Kingdom | A1F83G8C2ARO7P |
| EU | Germany | A1PA6795UKMFR9 |
| FE | Japan | A1VC38T7YXB528 |

更多 marketplace ID 详见 `references/report-types.md`。

## Display Rules

1. **先依赖后业务**：依赖检查未通过前，**不得**开始任何报告相关调用。
2. **只呈现数据**：展示报告获取进度、下载路径、前几行预览；不做业务解读。
3. **尊重用户选择的报告类型**：用户指定了报告类型就只拉那一种，不得擅自换其他类型。
4. **错误清晰**：报告失败（`FATAL` / 403 等）时，解释原因并把决定权交还用户。
5. **安全**：日志中 accessToken 掩码展示。
6. **完成后展示地址与本机下载链接**：脚本成功结束后，必须把 **`extractedFileHttpUrl`**（已解压文件的本机 HTTP 下载，限时）、**`downloadPath`**（本地绝对路径）、**`fileName`**（文件名）及 **`localFileUri`** 告知用户；并说明「仅在运行脚本的同一台电脑、在服务保持时间内可用」。不要默认把 Amazon 源 URL 当作用户下载入口；仅在用户明确要求或排障需要时使用 `includeAmazonSourceUrl`。

## CRITICAL: Report Failure Handling Rules

- **NEVER automatically try alternative report types** when user's specified report fails.
- 报告请求失败（`FATAL`、403 等）时，**立即停止并把失败事实告知用户**。
- **不要**替用户决定去拉别的报告类型。
- 把失败原因说清楚，让用户决定下一步（重试 / 换类型 / 查权限等）。
- 例：`GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT` 失败时，**不要**自动改拉 `GET_MERCHANT_LISTINGS_ALL_DATA`。

### Common Report Failure Reasons

- `403 Unauthorized`：缺少 API 权限或未加入 Amazon Brand Registry
- `FATAL`：该店铺不支持此报告类型或数据不足
- Brand Analytics 类报告需要品牌备案
- Vendor 类报告仅限 Vendor 账号

## Important Limitations

- **依赖 `linkfox-amazon-spapi-auth`**：未安装则必须先安装，见 Prerequisites。
- **Token expiration**：`accessToken` 1 小时过期，脚本内部自动取最新令牌。
- **Rate limits**：Reports API 0.0222 req/s，默认 30s 轮询是安全间隔。
- **Report 时效**：部分财务报告可能需要 10–30 分钟，按需调大 `maxAttempts`。
- **Path 白名单**：后端 `sp-api.developer-proxy.allowed-path-prefixes` 必须允许 `reports/2021-06-30/reports`。

## User Expression & Scenario Quick Reference

**Applicable** — 报告获取场景：

| User Says | Scenario |
|-----------|----------|
| "拉亚马逊库存报告" / "pull inventory report" | Scenario 1 |
| "下载订单数据" / "download orders report" | Scenario 1 |
| "获取销售流量报告" / "sales and traffic report" | Scenario 1 |
| "拉财务结算报告" / "settlement report" | Scenario 1 |
| "查 FBA 库存" / "FBA inventory report" | Scenario 1 |
| "拉某时间段的订单报告" / "orders from 2024-01-01 to ..." | Scenario 3 |

**Not applicable** — 超出本 skill：

- 授权新店铺、列已授权店铺、刷新/查询令牌 → 请使用 `linkfox-amazon-spapi-auth`
- 商品 listing 管理、订单处理、广告投放 → 由其他 skill 负责

**Boundary judgment**：
- 本 skill 只负责「依赖检查 + 报告获取业务」，**授权/令牌属于依赖 skill**。
- 任何进入本 skill 的调用都要先跑 Scenario 0。

---

**Feedback**：

出现以下任一情况时，自动调用 Feedback API 上报：
1. 本 skill 功能描述与实际不符
2. 结果与用户意图不符
3. 用户表达了不满或赞赏
4. 其他你认为可改进的点

按 `references/api.md` 中的规范调用 Feedback API，不要打断用户主流程。

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
