# Google Trends + Web Search — Tool Reference

## Google Trends Keyword Trend Analysis

**Endpoint**: `POST https://tool-gateway.linkfox.com/googleTrend/getTrendByKeys`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | Yes | Search keyword (max 100 chars). **Must be in the target country's language** (e.g. English for US, German for DE, Japanese for JP) |
| region | string | No | Country/region code, default `US`. Values: US, GB, JP, CA, MX, DE, FR, IT, ES, NL, AU, SG, AE, BR, IN, TR, PL, SE |
| dayRangeStart | string | No | Start date (YYYY-MM-DD, from 2004 onward) |
| dayRangeEnd | string | No | End date (YYYY-MM-DD, from 2004 onward) |

When both `dayRangeStart` and `dayRangeEnd` are provided, the custom time range takes priority.

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| trendInfoForKeys | array | Keyword trend info array |
| trendInfoForKeys[].keyword | string | The keyword |
| trendInfoForKeys[].trendValues | array | Trend value array |
| trendInfoForKeys[].trendValues[].timeRange | string | Date (yyyy-MM-dd) |
| trendInfoForKeys[].trendValues[].value | string | Normalized search interest (0-100) |
| chartOption | object | Chart render metadata |
| chartOption.type | string | Data type |
| chartOption.fieldX | string | X-axis field |
| chartOption.fieldY | array | Y-axis fields |
| chartOption.data | array | Chart data points |
| costToken | integer | Token cost |

### Key Usage Notes
- Values are normalized (0-100 scale), not absolute search volumes. 100 = peak popularity.
- Keywords **must match the target region's language** — translate first if needed.
- Data available from 2004 onward.
- Single keyword per call — for multi-keyword comparison, make separate calls.
- 18 regions supported.

---

## Google Trends Rising Topics (Time-Range Analysis)

**Endpoint**: `POST https://tool-gateway.linkfox.com/googleTrend/getTrendByTime`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| days | integer | No | 7 | Time range in days. Common values: 1 (last 24h), 2, 7 (past week) |
| region | string | No | US | Country/region code. Values: US, GB, JP, CA, MX, DE, FR, IT, ES, NL, AU, SG, AE, BR, IN, TR, PL, SE |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| costToken | integer | Token cost |
| chartOption | object | Chart config for visualization |
| chartOption.data | array | Chart data points |
| chartOption.fieldX | string | X-axis field |
| chartOption.fieldY | array | Y-axis fields |
| chartOption.type | string | Data type |
| chartOption.title | string | Chart title |
| trendValues | array | Trending query list |

**trendValues element:**

| Field | Type | Description |
|-------|------|-------------|
| query | string | Trending search term |
| searchVolume | integer | Relative search volume |
| increasePercentage | integer | Change percentage (-100 to 100, unit: %) |
| startTime | string | Observation window start timestamp |
| endTime | string | Observation window end timestamp |

### Key Usage Notes
- Designed for **recent/real-time** trend discovery, not long historical analysis.
- Positive `increasePercentage` = rising interest; negative = declining. Near 100 = explosive spike.
- Search volumes are relative, not absolute counts.
- 18 regions supported (same as Keyword Trend).
- Short time windows only (1, 2, 7 days typical).

---

## Web Search & Online Retrieval

**Endpoint**: `POST https://tool-gateway.linkfox.com/tsearch/search`
**Auth**: Header `Authorization: <api_key>` (env: LINKFOXAGENT_API_KEY)

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword | string | Yes | Search query keyword(s), max 1000 chars |

### Response Fields

**Top-level:**

| Field | Type | Description |
|-------|------|-------------|
| searchList | array | Search result list |
| costToken | integer | Token cost |

**searchList element:**

| Field | Type | Description |
|-------|------|-------------|
| score | number | Relevance score |
| title | string | Page title |
| url | string | Source page URL |
| content | string | Extracted page content |

### Key Usage Notes
- Performs both search AND content extraction in a single call — no need for a separate web-extract step.
- Returns unstructured text — summarize directly, do not route to data analysis tools.
- Single keyword string per call. For multi-faceted research, make multiple calls.
- Useful for current events, product research, community discussions (Reddit), competitor analysis, fact-checking, and trending topics.
- Always cite source title and URL when presenting results.
