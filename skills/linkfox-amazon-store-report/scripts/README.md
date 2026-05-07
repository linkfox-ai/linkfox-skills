# Amazon Store Report Scripts Usage Guide

本目录包含 **报告获取** 相关的 Python 脚本。若需要授权、查看店铺或获取令牌，请使用依赖 skill `linkfox-amazon-store-auth` 的脚本。

## Prerequisites

- Python 3.6+
- `LINKFOXAGENT_API_KEY` 环境变量
- 可访问 LinkFox 后端 API（默认 `https://tool-gateway.linkfox.com`）
- ⚠️ **依赖 skill `linkfox-amazon-store-auth` 已安装**（`get_report.py` 启动会自动校验）

```bash
export LINKFOXAGENT_API_KEY="your-api-key-here"
```

## Available Scripts

### 1. check_auth_dependency.py ⭐

探测依赖 skill `linkfox-amazon-store-auth` 是否可用。

```bash
python check_auth_dependency.py            # 默认输出
python check_auth_dependency.py --json     # JSON 输出
```

**退出码**：
- `0` → 依赖已满足
- `42` → `DEPENDENCY_MISSING`：依赖未安装，agent 需触发安装流程

**stderr 信号**：
- 成功：`DEPENDENCY_OK: {...}`
- 缺失：`DEPENDENCY_MISSING: {...}`

Agent 检测到 `exit 42` 或 `DEPENDENCY_MISSING:` 时，应当：
1. 优先调用本地的 skill 安装工具（如有）自动安装 `linkfox-amazon-store-auth`
2. 否则向用户说明并建议从 https://skill.linkfox.com/ 安装

### 2. get_report.py ⭐

自动化的端到端报告获取脚本。

**脚本启动时会先跑 `check_auth_dependency.py`**；若依赖缺失，会以退出码 `42` 退出并在 stderr 输出 `DEPENDENCY_MISSING:` 结构化信号。

#### Basic Usage

```bash
python get_report.py '{
  "sellerId": "A1EC6SZ7XAMURH",
  "region": "NA",
  "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}'
```

#### Advanced Usage with Date Range

```bash
python get_report.py '{
  "sellerId": "A1EC6SZ7XAMURH",
  "region": "NA",
  "reportType": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-01-01T00:00:00Z",
  "dataEndTime": "2024-01-31T23:59:59Z"
}'
```

#### `reportOptions` / Brand Analytics / Sales & Traffic（见 `references/report-requests/`）

```bash
python get_report.py '{
  "sellerId": "A1EC6SZ7XAMURH",
  "region": "NA",
  "reportType": "GET_SALES_AND_TRAFFIC_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2024-06-01T00:00:00Z",
  "dataEndTime": "2024-06-07T23:59:59Z",
  "reportOptions": {"dateGranularity": "DAY", "asinGranularity": "SKU"}
}'
```

```bash
python get_report.py '{
  "sellerId": "A1EC6SZ7XAMURH",
  "region": "NA",
  "reportType": "GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "dataStartTime": "2025-01-05",
  "dataEndTime": "2025-01-11",
  "reportOptions": {"reportPeriod": "WEEK", "asin": "B123456789"}
}'
```

（`reportPeriod` 与 `dataStartTime`/`dataEndTime` 的周起止须符合官方 schema，见 [sellingPartnerSearchQueryPerformanceReport.md](../references/report-requests/sellingPartnerSearchQueryPerformanceReport.md)。）

#### Custom Polling

```bash
python get_report.py '{
  "sellerId": "A1EC6SZ7XAMURH",
  "region": "NA",
  "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"],
  "pollInterval": 15,
  "maxAttempts": 40
}'
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sellerId | string | Yes | Amazon Seller ID |
| region | string | Yes | NA / EU / FE |
| reportType | string | Yes | Amazon report type enum |
| marketplaceIds | array | Yes | 目标 marketplace IDs |
| dataStartTime | string | No | ISO 8601 |
| dataEndTime | string | No | ISO 8601 |
| lastUpdatedDate | string | No | 部分 Vendor 报告；写入 createReport 请求体 |
| reportOptions | object | No | 与 SP-API `reportOptions` 一致；键见 `references/report-requests/*.md` |
| pollInterval | int | No | 轮询间隔秒数（默认 30） |
| maxAttempts | int | No | 最大轮询次数（默认 20） |
| skipDepCheck | bool | No | 跳过依赖检查（仅在确认依赖已满足时使用） |
| serveExtractedFileHttp | bool | No | 是否为**已解压**文件启动本机临时 HTTP（默认 `true`） |
| serveHost | string | No | 绑定地址，默认 `127.0.0.1` |
| servePort | int | No | 端口；`0` 表示由系统分配空闲端口（默认 `0`） |
| serveSeconds | int | No | JSON 打印后 HTTP 服务保持秒数（默认 `300`，最少 `10`） |
| includeAmazonSourceUrl | bool | No | 为 `true` 时在 JSON 中附带 `amazonDownloadUrl`（Amazon 源，多为压缩包；默认 `false`） |
| omitAmazonDownloadUrl | bool | No | **兼容旧参数**：`true` 等价于不输出 Amazon URL；`false` 等价于 `includeAmazonSourceUrl: true` |

#### 成功后的输出

- **stderr**：人类可读进度；结束时打印 **本地绝对路径**、**本机 `file://` URI**、**`extractedFileHttpUrl`**（浏览器下载已解压文件）；随后脚本会**阻塞** `serveSeconds` 秒以保持服务可用，结束后打印服务已停止。
- **stdout**：JSON（便于管道解析），字段示例见下。

```json
{
  "success": true,
  "reportId": "amzn1.spdoc.1.4.na.xxx",
  "reportDocumentId": "amzn1.spdoc.1.4.na.yyy",
  "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
  "downloadPath": "/tmp/amazon_report_xxx/report_data.txt",
  "fileName": "report_data.txt",
  "localFileUri": "file:///tmp/amazon_report_xxx/report_data.txt",
  "extractedFileHttpUrl": "http://127.0.0.1:52431/download",
  "extractedFileHttpServeSeconds": 300,
  "extractedFileHttpNote": "本机临时 HTTP…",
  "compressionAlgorithm": "GZIP",
  "tempDirectory": "/tmp/amazon_report_xxx",
  "fileSize": 1234
}
```

`extractedFileHttpUrl` 由脚本在**本机**起的短时 HTTP 服务提供，用于下载**已解压**后的文件；**仅在 `serveSeconds` 内、且与脚本同一台机器**可用。不需要给终端用户展示 Amazon 源地址时，不要设置 `includeAmazonSourceUrl`。

#### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | 成功 |
| 1 | 业务错误：参数错误、API 错误、报告 FATAL、超时等 |
| 42 | **DEPENDENCY_MISSING**：依赖 skill `linkfox-amazon-store-auth` 未安装 |

## Common Report Types

| Report Type | Description |
|-------------|-------------|
| GET_MERCHANT_LISTINGS_ALL_DATA | 当前在售 listing |
| GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL | 按下单日期的全部订单 |
| GET_SALES_AND_TRAFFIC_REPORT | 销售与流量 |
| GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE | 财务结算 |
| GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA | FBA 库存 |

完整清单：`../references/report-types.md`。

## Marketplace IDs

| Region | Country | Marketplace ID |
|--------|---------|----------------|
| NA | US | ATVPDKIKX0DER |
| NA | Canada | A2EUQ1WTGCTBG2 |
| NA | Mexico | A1AM78C64UM0Y8 |
| EU | UK | A1F83G8C2ARO7P |
| EU | Germany | A1PA6795UKMFR9 |
| FE | Japan | A1VC38T7YXB528 |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| LINKFOXAGENT_API_KEY | API 鉴权 key | 必需 |
| STORE_API_BASE_URL / SPAPI_BASE_URL | 后端网关 base URL（优先读前者） | https://tool-gateway.linkfox.com |
| LINKFOX_SKILLS_DIR / SKILLS_DIR / CURSOR_SKILLS_DIR | 可选：显式指定**扁平** skill 根目录（`<root>/<slug>/SKILL.md`） | — |
| OPENCLAW_WORKSPACE / OPENCLAW_ROOT / OPENCLAW_WORKDIR | OpenClaw 工作区；会额外探测 `<ws>/skills` 与 `<ws>/.agents/skills` | — |
| OPENCLAW_SKILLS_DIR | OpenClaw 全局 skills 目录（覆盖或补充 `~/.openclaw/skills`） | — |
| HERMES_SKILLS_EXTERNAL_DIRS | 等价于 Hermes `config.yaml` 的 `skills.external_dirs`；用系统路径分隔符（macOS/Linux 为 `:`，Windows 为 `;`）拼接多个路径 | — |
| HERMES_SKILLS_HOME | 若 Hermes 的 category 根不在默认 `~/.hermes/skills`，可指向该根目录 | — |

## Troubleshooting

**`DEPENDENCY_MISSING:` 或退出码 42**
- 安装依赖 skill `linkfox-amazon-store-auth`
- 或设置 `LINKFOX_SKILLS_DIR` 指向正确的 skill 根目录

**403 Unauthorized**
- 店铺缺少报告类型的权限
- Brand Analytics 报告需要品牌备案
- 重新授权时勾选更完整权限

**FATAL 状态**
- 该报告类型对该店铺不可用
- 数据不足 / 时间范围无数据
- **不要擅自改换报告类型**，按用户意图停下来回报

**Report 耗时过长**
- 增大 `maxAttempts` 或 `pollInterval`
- 财务/结算类报告常常需要 10–30 分钟

## Further Documentation

- API Reference: `../references/api.md`
- Report Types: `../references/report-types.md`
- Skill 文档: `../SKILL.md`
