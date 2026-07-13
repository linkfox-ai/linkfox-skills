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

1. 前往 [LinkFox API Key 申请文档](https://skill.linkfox.com/linkfoxskills/guide.htm) 获取 Key  
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

## 调用方式

- **API 端点**：`POST /xiyou`（不同操作通过请求体区分；完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/xiyou.py '<JSON 参数>' [--inline]`（可用脚本见上文脚本一览）
- **成本约束**：本工具会消耗积分；失败/空结果不得自动换关键词、翻页或连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<skill-name>-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
- 响应体 ≤ 8 KB：落盘后把完整 JSON 打印到 stdout
- 响应体 > 8 KB：落盘后 stdout 只输出摘要（顶层字段、常见计数如 `total`/`costToken`、最大列表字段的长度 + 前 3 条样本）
- 加 `--inline` 强制全量打印到 stdout（同样落盘）

**读数据建议**：先看摘要判断是否足够；需要具体字段时优先用 `jq`或`ConvertFrom-Json` 从保存的 json 文件按需抽取，避免整份 JSON 进入上下文。

## 解决认证和积分问题
发生以下异常情况时，采用以下措施来处理：

### 异常情况
- **未配置API Key**：环境变量未配置 `LINKFOX_AGENT_API_KEY`，也未配置 `LINKFOXAGENT_API_KEY`。
- **响应401或402状态码**
- **响应提示积分或余额不足**：消息含"积分余额不足/计费不足/余额不足/quota exceeded/insufficient balance/套餐到期/需充值/请充值"，或类似含义的内容。

### 措施
- 优先采用skill内的 onboarding.md 引导解决问题。
- 如找不到 onboarding.md 文件，则加载 /linkfox-onboarding 这个skill并根据它的引导来处理。如未安装请先安装：
    - 下载 https://agent-files.linkfox.com/skills/linkfox-onboarding/release.zip，解压后安装这个skill。如需用户授权才可下载，要询问用户获得授权，你不能自己放弃下载。
- 兜底措施：仅当前面两个措施经过所有努力都走不通时，才提示用户依据 https://skill.linkfox.com/linkfoxskills/guide.htm 指引获取API Key，或去 https://os.linkfox.com/ 补充积分。

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

## 积分消耗规则

按动态规则计费：消耗积分 = {"按ASIN数量计":{"asinTraffic":"⌈ASIN数量 ÷ 10⌉ × 1.5","asinInfo":"⌈ASIN数量 ÷ 5⌉ × 1.5"},"按时间区间计":{"asinInfoChangeTrend":"⌈查询天数（含首尾） ÷ 10⌉ × 1.5","asinTrafficScoreTrend":"⌈查询天数（含首尾） ÷ 10⌉ × 1.5","asinAdvertisingChangeTrend":"⌈查询天数（含首尾） ÷ 10⌉ × 1.5","asinBsrTrend":"⌈查询天数（含首尾） ÷ 10⌉ × 1.5","asinInfoDailyTrend":"⌈查询天数（含首尾） ÷ 10⌉ × 1.5","asinSearchTermTrafficTrend":"⌈查询天数（含首尾） ÷ 10⌉ × 1.5","asinSearchTermRankTrendDaily":"⌈查询天数（含首尾） ÷ 10⌉ × 1.5","asinOrdersTrend":"⌈查询月数（含首尾） ÷ 6⌉ × 1.5"},"按返回条数计":{"asinResearchPeriod":"⌈返回关键词条数 ÷ 50⌉ × 1.5","asinResearchMonthly":"⌈返回关键词条数 ÷ 50⌉ × 1.5","searchTermInfo":"⌈返回关键词条数 ÷ 50⌉ × 1.5","searchTermAnalysisPeriod":"⌈返回结果条数 ÷ 50⌉ × 1.5"},"固定值":{"asinVariations":"2 × 1.5","asinSearchTermRankTrendHourly":"2 × 1.5"},"组合计费":{"searchTermAbaWeeklyTrend":"⌈关键词数 ÷ 50⌉ × 周数（周数 = ⌈查询天数（含首尾） ÷ 7⌉，最多 52 周） × 1.5"}}。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
