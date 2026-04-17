---
name: linkfox-junglescout-sales-estimates
description: Jungle Scout ASIN销售估算查询，按日维度返回指定ASIN在一段时间内的每日预估销量与最新已知价格，覆盖美国、英国、德国、日本等10个站点。当用户提到ASIN销量预估、ASIN日销量、销售估算、竞品销量监控、日均销量、销量趋势、产品销量追踪、Jungle Scout销量数据、sales estimates, daily sales, estimated units sold, ASIN sales tracking, competitor sales monitoring, product sales trend, daily unit sales时触发此技能。即使用户未明确提及"Jungle Scout"，只要其需求涉及查看某个亚马逊ASIN在一段时间内的每日销量估算数据，也应触发此技能。
---

# Jungle Scout — ASIN 销售估算

This skill queries daily sales estimates and last known price for a given Amazon ASIN via the Jungle Scout data source, returning day-level data points over a specified date range across 10 Amazon marketplaces.

## Core Concepts

Jungle Scout ASIN 销售估算工具提供亚马逊各站点单个 ASIN 的**日维度预估销量**及**最近已知价格**。卖家可以通过查询指定时间范围内的销量变化来：

- **监控竞品销量**：了解竞品每日出单量，评估其市场份额
- **验证选品机会**：用实际销量数据验证产品需求是否足够大
- **追踪季节性规律**：观察产品在不同月份的销量波动，判断旺淡季
- **评估定价影响**：结合价格与销量的变化关系，辅助定价决策
- **新品表现跟踪**：追踪新品上架后的销量爬升曲线

**数据粒度**：每条记录代表 **1 天**，包含该日的预估售出件数和最近已知价格（美元）。

## Data Fields

### Output Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| ASIN | asin | 查询的 ASIN | B0CXXX1234 |
| 数据标识 | id | 数据点标识 | sales_estimate_B0CXXX1234_20260301 |
| 资源类型 | type | 固定值 | sales_estimate_result |
| 父 ASIN | parentAsin | 父体 ASIN（变体场景） | B0CXXX0000 |
| 是否父体 | isParent | 是否为父体商品 | true / false |
| 是否变体 | isVariant | 是否为变体商品 | true / false |
| 是否独立 | isStandalone | 是否为独立商品（非变体） | true / false |
| 变体列表 | variants | 该父体下的变体 ASIN 数组 | ["B0CX1", "B0CX2"] |
| 每日估算 | dailyEstimates | 每日数据数组 | 见下方 |
| 消耗 Token | costToken | 本次调用消耗的 token 数 | 1 |

### dailyEstimates 数组中每个对象

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| 日期 | date | 数据日期（YYYY-MM-DD） | 2026-03-15 |
| 预估日销量 | estimatedUnitsSold | 当日预估售出件数 | 42 |
| 最近已知价格 | lastKnownPrice | 最近已知价格（USD） | 29.99 |

## Supported Marketplaces

10 个亚马逊站点：`us`（美国）、`uk`（英国）、`de`（德国）、`in`（印度）、`ca`（加拿大）、`fr`（法国）、`it`（意大利）、`es`（西班牙）、`mx`（墨西哥）、`jp`（日本）。默认站点为 **us**。当用户未指定站点时，使用 us。

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/junglescout_sales_estimates.py` directly to run queries.

## How to Build Queries

所有四个参数均为**必填**：`marketplace`、`asin`、`startDate`、`endDate`。

### Principles for Building API Calls

1. **站点映射**：用户说"美国站"→ `us`，"日本站"→ `jp`，"德国站"→ `de`；未指定时默认 `us`
2. **日期格式**：必须为 `YYYY-MM-DD`，如 `2026-03-01`
3. **endDate 限制**：`endDate` 必须早于当前日期（不能包含今天及未来日期）
4. **ASIN 格式**：标准亚马逊 ASIN，通常以 B0 开头，共 10 位
5. **常用时间推算**：
   - "过去30天" → endDate 取昨天，startDate 取30天前
   - "上个月" → 上月1日到上月末日
   - "Q3 vs Q4" → 分两次调用，分别查 7-9 月和 10-12 月

### Common Query Scenarios

**1. 查看竞品最近30天的销量**
```json
{
  "marketplace": "us",
  "asin": "B0CXXX1234",
  "startDate": "2026-03-18",
  "endDate": "2026-04-16"
}
```

**2. 对比 Q3 与 Q4 销量表现**

分两次调用：
- Q3：`startDate=2025-07-01`, `endDate=2025-09-30`
- Q4：`startDate=2025-10-01`, `endDate=2025-12-31`

**3. 验证选品机会——查看产品全年销量**
```json
{
  "marketplace": "us",
  "asin": "B0CXXX5678",
  "startDate": "2025-04-01",
  "endDate": "2026-03-31"
}
```

**4. 追踪新品上架表现**
```json
{
  "marketplace": "de",
  "asin": "B0DYYY9999",
  "startDate": "2026-01-15",
  "endDate": "2026-04-15"
}
```

**5. 监控大促期间销量变化（如 Prime Day）**
```json
{
  "marketplace": "us",
  "asin": "B0CXXX1234",
  "startDate": "2025-07-01",
  "endDate": "2025-07-21"
}
```

## Display Rules

1. **折线图优先**：建议以折线图展示每日销量变化，横轴为日期，纵轴为预估日销量；如有价格数据可叠加第二 Y 轴显示价格走势
2. **表格辅助**：同时提供数据表格供精确查阅，列包括：日期、预估销量、最近已知价格
3. **汇总统计**：在数据之后汇总关键指标——总销量、日均销量、预估总收入（总销量 × 均价）
4. **趋势总结**：简要总结趋势方向（上升/下降/平稳/周期性波动），标注销量峰值和谷值日期
5. **Error handling**: When a query fails, explain the reason based on the error response and suggest adjusting parameters（如 endDate 不能包含今天或未来日期）

## Important Limitations

- **endDate 不可包含今天**：`endDate` 必须早于当前日期，不能查询今天及未来的销量
- **单次单 ASIN**：每次调用只能查询一个 ASIN；对比多个 ASIN 需分多次调用
- **所有参数必填**：`marketplace`、`asin`、`startDate`、`endDate` 缺一不可
- **价格为美元**：`lastKnownPrice` 单位为 USD，非本地货币

## User Expression & Scenario Quick Reference

**Applicable** - ASIN 销售估算与销量趋势分析：

| User Says | Scenario |
|-----------|----------|
| "这个ASIN一天能卖多少" | 查询近期日销量估算 |
| "竞品最近卖得怎么样" | 监控竞品近30天销量 |
| "这个产品有没有季节性" | 全年销量数据判断季节规律 |
| "帮我看看这个品的销量趋势" | 指定时间段的销量走势 |
| "Q4旺季销量如何" | 特定季度销量查询 |
| "这个产品值不值得做" | 通过历史销量验证选品机会 |
| "大促期间卖了多少" | 活动期间销量监控 |

**Not applicable** - 超出 ASIN 销售估算范围：
- 关键词搜索量（需要关键词历史搜索量工具）
- BSR 排名历史（需要 BSR 追踪工具）
- 类目整体销量/市场规模
- 非亚马逊平台的销量数据
- 实时/当前时刻的销量（数据有滞后，不含今天）

**Boundary judgment**: When users say "销量", "日销", or "卖了多少", if they want to see a specific ASIN's daily estimated sales over a time range, this skill applies. If they want keyword search volume, category rankings, or real-time live sales, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, visit [LinkFox Skills](https://skill.linkfox.com/).*
