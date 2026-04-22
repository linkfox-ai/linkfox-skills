---
name: linkfox-aba-data-explorer
version: 1.0.3
category: product-sourcing
description: 亚马逊ABA（品牌分析）搜索词数据的查询与分析，涵盖15个站点近3年的周维度数据。当用户提到ABA数据、亚马逊搜索词分析、关键词挖掘、搜索排名趋势、市场机会分析、季节性关键词、高点击低转化分析、蓝海词发现、竞品关键词分析、ABA data, search term report, keyword mining, search ranking trends, blue ocean keywords, click share, conversion share, seasonal keywords, market opportunity analysis, competitor keywords时触发此技能。即使用户未明确提及"ABA"，只要其需求涉及亚马逊搜索词数据和排名分析，也应触发此技能。
---

# ABA Data Explorer

This skill guides you on how to query and analyze ABA search term data, helping Amazon sellers extract valuable insights from ABA search term reports.

## Core Concepts

ABA (Amazon Brand Analytics) Search Term Report is official Amazon search behavior data that reflects real consumer search activity on Amazon. This tool holds nearly 3 years of **weekly-granularity** data across 15 Amazon marketplaces.

**Ranking logic**: A smaller `searchFrequencyRank` value means higher search popularity. Rank 1 is the most popular search term. This is an easy point of confusion - when a user says "ranking improved," it means the numeric value decreased; "ranking dropped" means the value increased.

## Data Fields

| Field | API Name | Description | Example |
|-------|----------|-------------|---------|
| Search Term | searchTerm | Consumer search keyword | rimel loreal |
| Report Start Date | reportStartDate | Week start date for data collection | 2025-10-26 |
| Region | region | Amazon marketplace code | US |
| Search Frequency Rank | searchFrequencyRank | Search popularity rank (lower = better) | 82135 |
| Clicked ASIN | clickedAsin | ASIN of the clicked product | B0XXXXXXXX |
| Clicked Item Name | clickedItemName | Name of the clicked product | xxx |
| Click Share Rank | clickShareRank | This ASIN's click share rank for the search term | 1 |
| Click Share | clickShare | Click share captured by this ASIN (0~1) | 0.28 |
| Conversion Share | conversionShare | Conversion share captured by this ASIN (0~1) | 0.3333 |

## Supported Marketplaces

US (United States), DE (Germany), BR (Brazil), CA (Canada), AU (Australia), JP (Japan), AE (United Arab Emirates), ES (Spain), FR (France), IT (Italy), SA (Saudi Arabia), TR (Turkey), MX (Mexico), SE (Sweden), NL (Netherlands) 

Default marketplace is **US**. Use US when the user doesn't specify a marketplace.

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/aba_query.py` directly to run queries.

## How to Build Queries

The key parameter when calling this tool is `analysisDescription` - a natural language description of the data you want to query. This description is converted into a structured query on the backend, so it needs to be **precise and specific**.

### Principles for Writing analysisDescription

1. **Specify the marketplace**: Always state the marketplace at the beginning, e.g., "筛选美国站" (Filter US marketplace)
2. **Use precise filter criteria**: Use specific numeric ranges rather than vague descriptions. "排名在5万以内" (rank within 50,000) is far more effective than "排名较好" (good ranking)
3. **Specify time ranges**: Use concrete time descriptions, e.g., "过去12周" (past 12 weeks), "2024年1-9月" (Jan-Sep 2024), "近3个月" (last 3 months)
4. **Specify comparison baselines**: For trend analysis, clearly state the time points being compared, e.g., "4周前的排名比8周前提升30%" (rank 4 weeks ago improved 30% vs 8 weeks ago)
5. **Handle deduplication logic**: When there are multiple records for the same search term + ASIN combination, specify which to keep, e.g., "相同搜索词相同ASIN值保留最新的一个" (keep only the latest for identical search term + ASIN)
6. **Stay faithful to user intent**: Don't misinterpret or overextend the user's query - reflect exactly what they want

### analysisDescription Examples for Common Scenarios

**1. Search Term Popularity Trend**
```
筛选美国站，关键词"gift"在过去12周的搜索热度排名。
```

**2. Rising Dark Horse Keywords**
```
筛选美国站，关键词包含"gift"，2025年Q1和全年的平均搜索排名都大于50万，但最新排名冲进5万-10万的搜索词。
```

**3. Sustained Growth Trend Discovery**
```
筛选美国站，最新排名在20万以内，且4周前的排名比8周前提升30%，本周的排名比4周前提升30%的搜索词。
```

**4. Market Opportunity Discovery (High Search Volume, Low Monopoly)**
```
筛选美国站，筛选当前搜索排名在20000以内，近三个月点击占比Top 1的Asin的转化率占比低于5%的搜索词。相同搜索词相同Asin值保留最新的一个。
```

**5. Seasonal / Holiday Keyword Targeting**
```
筛选美国站，包含"cup"的关键词中，去年（2024年）1-9月份排名未进入50万，10-11月份连续进入20万的词。
```

**6. High-Click Low-Conversion ASIN Mining**
```
筛选美国站关键词包含"hat"的，最新搜索排名在5万-20万之间，且近3个月来点击占比大于20%，转化占比小于10%的ASIN。相同搜索词和ASIN仅保留点击占比和转化占比的比例最小数据。
```

**7. High-ROAS Long-Tail Blue Ocean Keywords**
```
筛选美国站，关键词包含"charger"的，当前排名在20万开外的，近2个月的平均转化占比大于平均转化占比1.5倍的关键词，以及相应的ASIN。
```

**8. New Market Terms & Emerging Demand Detection**
```
找到美国站"charger"的长尾词中，近一个月才进入排名榜单，且当前排名在50万以内的所有词。
```

**9. Niche Trend / Variant Growth Capture**
```
筛选美国站中"table"的长尾词中，排名在10万-30万之间，且近4周的搜索排名增长50%以上的搜索词。
```

## Display Rules

1. **Present data only**: Show query results in clear tables without subjective business advice
2. **Ranking clarification**: When showing ranking data, remind users that lower values mean better rankings
3. **Volume notice**: When results are large, show core data and remind users they can get the full dataset via the download link
4. **Download guidance**: If the response includes a `downloadUrl`, clearly inform the user of the download address; if the user needs full data but hasn't requested a download, proactively suggest generating a download link
5. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest adjusting query criteria
## Important Limitations

- **Result cap**: Download links contain a maximum of 10,000 records
- **Data granularity**: Data is at weekly granularity, not daily
- **Data range**: Approximately 3 years of historical data

## User Expression & Scenario Quick Reference

**Applicable** - Data queries around Amazon search terms:

| User Says | Scenario |
|-----------|----------|
| "How's the search volume/popularity for XX keyword" | Ranking trend |
| "Recently trending keywords", "newly emerging terms" | Dark horse / new term detection |
| "Blue ocean keywords", "low competition terms" | Market opportunity discovery |
| "Which keywords convert well", "high-conversion long-tail" | High-ROAS keyword library |
| "Seasonal keywords", "what terms surge in peak season" | Seasonal keywords |
| "Who's capturing the traffic", "any monopoly" | Click share / monopoly analysis |
| "ASINs with high clicks but low conversion" | High-click low-conversion diagnosis |

**Not applicable** - Needs beyond ABA search term data:
- Advertising / PPC (bids, campaign strategy)
- Product reviews, listing copywriting
- ASIN sales estimation
- User already has local ABA files to process

**Boundary judgment**: When users say "product research", "competitor analysis", or "is there market opportunity", if it boils down to search-term-level data queries (finding blue ocean keywords, analyzing competitor traffic distribution under keywords), then this skill applies. If they're asking about profit margins, pricing strategy, or comprehensive market reports, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
