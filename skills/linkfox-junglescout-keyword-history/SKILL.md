---
name: linkfox-junglescout-keyword-history
description: Jungle Scout关键词历史搜索量查询，按7天周期返回亚马逊关键词的精确搜索量趋势，覆盖美国、英国、德国、日本等10个站点。当用户提到关键词搜索量趋势、历史搜索量、搜索热度变化、关键词季节性、搜索量波动、Jungle Scout搜索量、keyword search volume history, keyword trend, search volume over time, seasonal search volume, keyword popularity trend时触发此技能。即使用户未明确提及"Jungle Scout"，只要其需求涉及查看某个亚马逊关键词在一段时间内的搜索量变化趋势，也应触发此技能。
---

# Jungle Scout — 关键词历史搜索量

This skill queries the historical exact search volume for Amazon keywords via the Jungle Scout data source, returning weekly search volume data points over a specified date range across 10 Amazon marketplaces.

## Core Concepts

Jungle Scout 关键词历史搜索量工具提供亚马逊各站点关键词的**周维度精确匹配搜索量**历史数据。卖家可以通过查询指定时间范围内的搜索量变化来判断：

- **季节性规律**：关键词在哪些月份是旺季/淡季
- **趋势方向**：搜索量是持续上升、下降还是平稳
- **波动幅度**：判断市场需求的稳定性
- **节假日效应**：大促、节日前后的搜索量飙升

**数据粒度**：每条记录代表一个 **7 天周期**，包含该周内的精确匹配搜索量估算值。

## Data Fields

### Output Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| 周期标识 | id | 数据周期标识（市场/关键词/日期范围） | us_sushi_20250105_20250111 |
| 周期开始日期 | estimateStartDate | 7天统计周期的起点 | 2025-01-05 |
| 周期结束日期 | estimateEndDate | 7天统计周期的终点 | 2025-01-11 |
| 精确搜索量 | estimatedExactSearchVolume | 该周期内精确匹配搜索量（次/周） | 12500 |
| 资源类型 | type | 固定值 | historical_keyword_search_volume |
| 消耗Token | costToken | 本次调用消耗的 token 数 | 1 |

## Supported Marketplaces

| 站点 | marketplace 值 | 说明 |
|------|---------------|------|
| 美国 | us | Amazon.com |
| 英国 | uk | Amazon.co.uk |
| 德国 | de | Amazon.de |
| 印度 | in | Amazon.in |
| 加拿大 | ca | Amazon.ca |
| 法国 | fr | Amazon.fr |
| 意大利 | it | Amazon.it |
| 西班牙 | es | Amazon.es |
| 墨西哥 | mx | Amazon.com.mx |
| 日本 | jp | Amazon.co.jp |

默认站点为 **us**。当用户未指定站点时，使用 us。

## 调用方式

- **API 端点**：`POST /tool-jungle-scout/keywords/historical-search-volume`（完整参数/响应/错误码见 `references/api.md`）
- **Python 脚本**：`python scripts/junglescout_keyword_history.py '<JSON 参数>' [--inline]`
- **成本约束**：本工具会消耗积分；同一会话同一参数组合默认只调用一次，脚本带 24h 本地缓存。失败/空结果不得自动换关键词、翻页或改邮编连续试探；需要继续检索时先向用户说明会产生额外消耗。

**输出策略（脚本默认行为）**：
- **始终**将完整响应写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-junglescout-keyword-history-<timestamp>.json`（`<cwd>` 为脚本执行时的工作目录，在 Claude Code 里即当前项目目录；`<session>` 取自环境变量 `SESSION_ID`，按用户任务自动聚合；**禁止写入 /tmp**，当前目录不可写则报错）
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

## How to Build Queries

所有四个参数均为**必填**：`marketplace`、`keyword`、`startDate`、`endDate`。

### Principles for Building API Calls

1. **站点映射**：用户说"美国站"→ `us`，"日本站"→ `jp`，"德国站"→ `de`；未指定时默认 `us`
2. **日期格式**：必须为 `YYYY-MM-DD`，如 `2025-01-05`
3. **时间跨度**：`startDate` 到 `endDate` 最长 **366 天**；超过时需拆分为多次请求
4. **关键词**：原样传入用户提供的关键词（英文小写为佳）
5. **常用时间推算**：
   - "过去3个月" → endDate 取今天，startDate 取约90天前
   - "去年全年" → `2025-01-01` 到 `2025-12-31`
   - "旺季" → 根据品类判断，如 Q4 为 `10-01` 到 `12-31`

### Common Query Scenarios

**1. 查看关键词近半年搜索趋势**
```json
{
  "marketplace": "us",
  "keyword": "yoga mat",
  "startDate": "2025-10-01",
  "endDate": "2026-03-31"
}
```

**2. 判断关键词季节性（查全年数据）**
```json
{
  "marketplace": "us",
  "keyword": "christmas decorations",
  "startDate": "2025-01-01",
  "endDate": "2025-12-31"
}
```

**3. 对比旺季与淡季搜索量**

分两次调用：
- 淡季：`startDate=2025-02-01`, `endDate=2025-04-30`
- 旺季：`startDate=2025-10-01`, `endDate=2025-12-31`

**4. 多站点对比**

对同一关键词分别查询不同 marketplace（如 `us`、`de`、`jp`），比较各站搜索量规模。

**5. 验证市场需求是否增长**
```json
{
  "marketplace": "de",
  "keyword": "luftreiniger",
  "startDate": "2025-04-01",
  "endDate": "2026-03-31"
}
```

## Display Rules

1. **趋势可视化优先**：建议以时间线/折线图方式展示搜索量变化，横轴为日期周期，纵轴为搜索量
2. **表格辅助**：同时提供数据表格供精确查阅，列包括：周期开始日期、周期结束日期、搜索量
3. **趋势总结**：在数据之后简要总结趋势方向（上升/下降/平稳/周期性波动），标注峰值和谷值周期
4. **峰值标注**：高亮搜索量最高和最低的周期，便于用户快速判断旺淡季
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters（如日期范围超 366 天）

## Important Limitations

- **时间跨度上限**：单次查询 `startDate` 到 `endDate` 最长 366 天，超过需拆分查询
- **数据粒度**：周维度（7天一个数据点），非日维度
- **搜索量类型**：精确匹配搜索量（Exact Match），非广泛匹配
- **所有参数必填**：`marketplace`、`keyword`、`startDate`、`endDate` 缺一不可

## User Expression & Scenario Quick Reference

**Applicable** - 关键词搜索量历史趋势分析：

| User Says | Scenario |
|-----------|----------|
| "这个词搜索量怎么变化的" | 搜索量趋势查询 |
| "这个品类有没有季节性" | 全年数据判断季节规律 |
| "搜索量最近在涨还是跌" | 近期趋势判断 |
| "什么时候是旺季" | 峰值周期识别 |
| "去年Q4搜索量多少" | 指定时间段搜索量查询 |
| "这个词在德国站热不热" | 非美国站搜索量查询 |
| "对比两个时间段的搜索量" | 旺淡季/同比对比 |

**Not applicable** - 超出关键词历史搜索量范围：
- 关键词建议/拓词（需要关键词挖掘工具）
- 实时/当前搜索量排名（需要 ABA 或 SIF 工具）
- 关键词竞争度、CPC 出价
- 商品销量、listing 分析
- 非亚马逊平台的搜索量

**Boundary judgment**: When users say "搜索量", "关键词热度", or "市场需求趋势", if they specifically want to see how a keyword's search volume changes over a period of time (historical trend), this skill applies. If they want the current ranking or a list of trending keywords, it does not apply.

## 积分消耗规则

消耗 63.75 积分。

> 用户会因积分消耗而支付费用。请充分评估：当需要高频调用本技能，或用户对积分消耗量预期不足时，务必提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
