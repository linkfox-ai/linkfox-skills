---
name: linkfox-tsearch-search
description: 网络搜索、在线检索、实时信息查询、搜索引擎搜索、Reddit等社区平台讨论、外部站点帖子和热门话题。当用户需要搜索网络上的最新信息、查找近期新闻或趋势、查询实时数据、通过搜索引擎调研话题、浏览Reddit或社区讨论、发现外部站点帖子和热门话题、获取任何在线内容、web search, online lookup, real-time information, news search, Reddit, trending topics, search engine时触发此技能。即使用户未明确说"搜索"，只要其意图涉及获取实时网络信息或核实当前事实，也应触发此技能。
---

# Web Search & Online Retrieval

This skill performs web searches and automatically extracts content from the results. It returns unstructured content ready for direct summarization — no sandbox analysis is needed.

## Core Concepts

This tool acts as an intelligent web search engine that both searches and extracts page content in a single call. When you use this tool, it automatically:

1. Performs a web search using the provided keyword
2. Extracts and returns content from the top results

**Important**: Because content extraction is built-in, there is no need to separately call a browser/web-extract tool after using this search. The returned content is unstructured text — summarize it directly rather than attempting structured data analysis.

## Response Data Fields

| Field | Description | Type | Example |
|-------|-------------|------|---------|
| searchList | Array of search results | array | (see below) |
| searchList[].score | Relevance score of the result | number | 0.95 |
| searchList[].title | Page title of the result | string | "Best wireless chargers 2026" |
| searchList[].url | URL of the source page | string | "https://example.com/article" |
| searchList[].content | Extracted page content | string | "Full text of the article..." |
| costToken | Tokens consumed by this request | integer | 1500 |

## Parameter Guide

This tool accepts a single parameter:

| Parameter | Type | Required | Max Length | Description |
|-----------|------|----------|------------|-------------|
| keyword | string | Yes | 1000 chars | The search query keyword(s) |

### Tips for Effective Keywords

1. **Be specific**: "best budget wireless earbuds 2026" works better than "earbuds"
2. **Use natural language or key phrases**: Both "what is the capital of France" and "capital France" are valid
3. **Include context when needed**: Add qualifiers like year, region, or domain to narrow results
4. **Combine terms for precision**: "iPhone 16 Pro Max battery life review" targets more relevant pages than "iPhone battery"
5. **Use English or the target language**: Match the language to the content you want to find

### Keyword Examples by Scenario

**Current events / News**
```
latest AI regulation policy 2026
```

**Product research**
```
best robot vacuum cleaner under $300 Reddit
```

**Technical lookup**
```
Python asyncio tutorial beginner guide
```

**Community discussions / Reddit**
```
Reddit best budget mechanical keyboard 2026
```

**Trending topics**
```
trending topics on social media this week
```

**Fact checking / Real-time data**
```
current Bitcoin price USD
```

**Competitor or brand research**
```
Anker vs Baseus portable charger comparison
```

## Display Rules

1. **Summarize directly**: The returned content is unstructured text. Provide a clear, concise summary rather than dumping raw content.
2. **Cite sources**: Always include the title and URL of each result so the user can verify information.
3. **Present multiple perspectives**: When results contain diverse viewpoints, present them fairly.
4. **Indicate freshness**: Note when information appears to be very recent or potentially outdated.
5. **Handle empty results**: If the search returns no results or irrelevant content, suggest refining the keyword and offer alternative search terms.
6. **No sandbox analysis**: Never route the output to a data analysis sandbox. Summarize inline.
## Important Limitations

- **Unstructured output**: Results are free-form text, not structured data tables. Do not attempt SQL-like processing.
- **No persistent storage**: Search results are not saved to any database for later querying.
- **Single keyword input**: The tool takes one keyword string per call. For multi-faceted research, make multiple calls with different keywords.
- **Content extraction included**: Do not call a separate web-extract tool on these results — extraction is already done.

## User Expression & Scenario Quick Reference

**Applicable** — Any task requiring live web information:

| User Says | Scenario |
|-----------|----------|
| "Search for...", "Look up...", "Google..." | Direct web search |
| "What's the latest news on..." | Current events lookup |
| "Find information about..." | General information retrieval |
| "What are people saying about... on Reddit" | Community discussion research |
| "What's trending right now" | Trending topic discovery |
| "Check the current price of..." | Real-time data lookup |
| "Find reviews for..." | Product/service review search |
| "What happened with... today" | Breaking news / recent events |
| "Research competitors for..." | Competitive intelligence via web |
| "External site posts about...", "Hot threads on..." | Forum and community content |

**Not applicable** — Tasks that don't need web search:

- Querying internal databases or structured datasets (use appropriate data query tools)
- Analyzing files the user has already uploaded locally
- Performing calculations or data transformations on existing data
- Generating creative content without needing external references
- Tasks involving Amazon ABA data (use the ABA data explorer instead)

**Boundary judgment**: When users say "find out about" or "research", if they need current, external web information, this skill applies. If they are referring to internal data, historical databases, or local file analysis, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
