---
name: linkfox-xiyou-dongcha
description: 西柚找词（西柚洞察）亚马逊 ASIN 与关键词分析，经 LinkFox 网关转发西柚 OpenAPI。覆盖 ASIN 流量得分、反查关键词、词排名/流量趋势、BSR、ABA 周趋势、关键词竞争度与建议竞价等 17 个接口，支持 US/UK/DE 等 13 个站点。当用户提到西柚找词、西柚洞察、Xiyou、ASIN 反查关键词、关键词分析、ABA 周搜索量、流量得分、词排名趋势、xiyou keyword research, ASIN traffic score, reverse ASIN lookup, search term analysis 时触发。即使用户未写「西柚」，只要需求是通过西柚找词查亚马逊 ASIN/关键词流量与排名数据，也应触发。使用前须配置 LINKFOXAGENT_API_KEY 以及环境变量 XIYOU_CLIENT_ID、XIYOU_CLIENT_SECRET。
---

# Xiyou (西柚找词) — Amazon ASIN & Keyword Analytics

This skill queries **Xiyou Insights** (西柚洞察 / 西柚找词) data for Amazon ASINs and search terms via the **LinkFox tool gateway**. The gateway forwards requests to Xiyou OpenAPI (`https://openapi.xiyouzhaoci.com`).

## Environment Variables (Required)

本 skill 需要 **三组凭证**，缺一不可：

| Variable | Required | Description |
|----------|----------|-------------|
| `LINKFOXAGENT_API_KEY` | Yes | LinkFox Agent API Key（与其它 LinkFox skill 相同） |
| `XIYOU_CLIENT_ID` | Yes | 西柚 OpenAPI Client ID（16 位字符） |
| `XIYOU_CLIENT_SECRET` | Yes | 西柚 OpenAPI Client Secret（24 位字符） |

### 1. LinkFox API Key

1. 前往 [LinkFox API Key 申请文档](https://yxgb3sicy7.feishu.cn/wiki/GIkkweGghiyzkqkRXQKc2n0Tnre) 获取 Key  
2. 写入环境变量 `LINKFOXAGENT_API_KEY`

### 2. 西柚找词 Client ID / Client Secret

1. 打开 [西柚洞察 OpenAPI 控制台](https://www.xydc.com/openapi?xiyou-insights-web=%2Fopenapi)  
2. 登录后在控制台创建或查看应用，复制 **Client ID**（16 位）与 **Client Secret**（24 位）  
3. 写入环境变量 `XIYOU_CLIENT_ID` 与 `XIYOU_CLIENT_SECRET`  
4. **请勿**将 Secret 提交到 Git、写入 SKILL 参数或聊天记录；仅通过环境变量供本地脚本读取

### 3. 配置示例

**macOS / Linux（当前终端会话）**

```bash
export LINKFOXAGENT_API_KEY="your-linkfox-api-key"
export XIYOU_CLIENT_ID="your-16-char-id"
export XIYOU_CLIENT_SECRET="your-24-char-secret"
```

**macOS / Linux（持久化，写入 `~/.zshrc` 或 `~/.bashrc`）**

```bash
echo 'export LINKFOXAGENT_API_KEY="your-linkfox-api-key"' >> ~/.zshrc
echo 'export XIYOU_CLIENT_ID="your-16-char-id"' >> ~/.zshrc
echo 'export XIYOU_CLIENT_SECRET="your-24-char-secret"' >> ~/.zshrc
source ~/.zshrc
```

**Windows PowerShell（当前会话）**

```powershell
$env:LINKFOXAGENT_API_KEY = "your-linkfox-api-key"
$env:XIYOU_CLIENT_ID = "your-16-char-id"
$env:XIYOU_CLIENT_SECRET = "your-24-char-secret"
```

**Windows（系统环境变量）**：设置 → 系统 → 关于 → 高级系统设置 → 环境变量 → 新建上述三个用户变量。

**Cursor / Agent 运行环境**：在 IDE 或 Agent 所在环境的 env 配置中添加上述三个变量，否则脚本会报错并提示缺少哪一项。

> 脚本 `scripts/xiyou.py` 与 `scripts/_xiyou_common.py` 会自动把 `XIYOU_CLIENT_ID` / `XIYOU_CLIENT_SECRET` 注入请求 Body；调用时 **不要** 在 `--params` 里重复传 `clientId` / `clientSecret`。

## Core Concepts

西柚找词提供亚马逊 **ASIN 维度** 与 **关键词维度** 的流量、排名、ABA、竞争度等数据，典型用途：

- **ASIN 反查关键词**：看某 ASIN 近 7 天或指定月份带来流量的搜索词
- **关键词分析**：看某词下哪些 ASIN 占流量、排名与获得率
- **趋势分析**：ASIN 流量得分、BSR、广告变动、词排名/流量随时间变化
- **选词辅助**：关键词 ABA 周搜索量、竞争难度、建议 CPC

## Supported Marketplaces

`country` 常用 2 位大写代码：`US`、`CA`、`MX`、`BR`、`UK`、`DE`、`ES`、`IT`、`FR`、`JP`、`AU`、`SA`、`AE`。默认 `US`。

**例外**：`asinSearchTermRankTrendHourly` 仅支持 `US`、`UK`、`DE`。

## API Usage

- 完整参数与响应结构：**`references/api.md`**
- 命令行（在本 skill 根目录执行）：

```bash
python scripts/xiyou.py --list-apis
python scripts/xiyou.py --api asinResearchPeriod --params '{"country":"US","asin":"B06XZTZ7GB","page":1,"pageSize":50}'
python scripts/xiyou.py --api searchTermInfo --params '{"country":"US","searchTerms":"yoga mat,fitness mat"}'
```

网关路径：`POST https://tool-gateway.linkfox.com/xiyou/<apiName>`

## API Quick Index

| `--api` | 用途 |
|---------|------|
| `asinTraffic` | 批量 ASIN 近 7 天流量得分 |
| `asinInfo` | 批量 ASIN 商品信息 |
| `asinResearchPeriod` | ASIN 反查关键词（最近天） |
| `asinResearchMonthly` | ASIN 反查关键词（月） |
| `searchTermAnalysisPeriod` | 关键词下 ASIN 分析列表 |
| `searchTermInfo` | 关键词信息（ABA、竞争度、CPC） |
| `searchTermAbaWeeklyTrend` | 关键词 ABA 周趋势 |
| `asinSearchTermTrafficTrend` | ASIN+词 流量趋势（天） |
| `asinSearchTermRankTrendDaily` | ASIN+词 排名趋势（天） |
| `asinSearchTermRankTrendHourly` | ASIN+词 排名趋势（小时） |
| `asinTrafficScoreTrend` | ASIN 流量得分趋势（天） |
| `asinBsrTrend` | ASIN BSR 趋势（天） |
| `asinOrdersTrend` | ASIN 订单量趋势（月） |
| `asinVariations` | ASIN 变体关系 |
| 其它 | 见 `--list-apis` 与 `references/api.md` |

## How to Build Queries

1. **选接口**：反查词 → `asinResearchPeriod` / `asinResearchMonthly`；查词下竞品 → `searchTermAnalysisPeriod`；词属性 → `searchTermInfo` / `searchTermAbaWeeklyTrend`
2. **站点**：用户说「美国站」→ `country: "US"`；未指定默认 `US`
3. **ASIN**：10 位，如 `B06XZTZ7GB`；批量接口用 `entities: [{"country":"US","asin":"..."}]`
4. **日期**：天趋势用 `startDate`/`endDate`（`YYYY-MM-DD`）；月趋势用 `startMonth`/`endMonth`（`YYYY-MM`）
5. **分页**：列表类接口用 `page`、`pageSize`（最大 10000）
6. **排序**：`sortField` + `sortOrder`（`asc`/`desc`），可选值见 `references/api.md` 各接口说明

### Example Scenarios

**反查 ASIN 近 7 天流量词（按流量降序）**

```json
{"country": "US", "asin": "B06XZTZ7GB", "page": 1, "pageSize": 100, "sortField": "traffic", "sortOrder": "desc"}
```

**查关键词下 Top ASIN**

```json
{"searchTerm": "yoga mat", "country": "US", "page": 1, "pageSize": 50}
```

**批量查 ASIN 流量得分**

```json
{"entities": [{"country": "US", "asin": "B06XZTZ7GB"}, {"country": "US", "asin": "B0XXXXXXXX"}]}
```

## Display Rules

1. 列表类结果优先表格展示：关键词/ASIN、流量、排名、占比等核心字段
2. 趋势类结果建议时间序列展示，标注峰值与变化方向
3. 失败时根据 `error` / 网关响应说明原因；常见：环境变量未配置、ASIN 格式错误、日期区间无效、站点不支持

## Important Limitations

- 须同时配置 LinkFox Key **与** 西柚 Client 凭证
- `asinSearchTermRankTrendHourly` 仅 US/UK/DE
- 批量 ASIN 接口 `entities` 最多 100 个；`searchTerms` 逗号分隔最多 100 个词
- 大结果集优先用下方 Large Response 模式落盘读取

## User Expression & Scenario Quick Reference

| User Says | API / Scenario |
|-----------|----------------|
| 「这个 ASIN 有哪些流量词」 | `asinResearchPeriod` |
| 「这个词下哪些 ASIN 在抢流量」 | `searchTermAnalysisPeriod` |
| 「关键词搜索量/ABA 趋势」 | `searchTermAbaWeeklyTrend` / `searchTermInfo` |
| 「ASIN 流量得分多少」 | `asinTraffic` |
| 「某个词排名怎么变」 | `asinSearchTermRankTrendDaily` |
| 「BSR 历史」 | `asinBsrTrend` |

**Not applicable**: 非亚马逊平台、Jungle Scout/卖家精灵等其它数据源、SP-API 订单/库存、Temu/Shopee 选品。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/xiyou.py --out-dir <DIR> '{"api":"asinResearchPeriod","country":"US","asin":"B06XZTZ7GB","page":1,"pageSize":50}'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
