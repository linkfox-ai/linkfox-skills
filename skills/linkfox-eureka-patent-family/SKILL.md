---
name: linkfox-eureka-patent-family
description: 通过Eureka专利数据平台查询专利家族信息，包括简单同族、INPADOC同族和PatSnap同族。当用户提到专利家族、专利家族搜索、简单同族、INPADOC同族、PatSnap家族、同族专利查找、专利等同、家族成员、查找跨国相关专利、Eureka专利家族、patent family, family patents, patent equivalents, cross-border patents, Eureka, INPADOC family, simple family时触发此技能。即使用户未明确说"专利家族"，只要其需求涉及查询一项或多项专利的家族成员、等同专利或相关跨国申请，也应触发此技能。
---

# Eureka Patent Family Explorer

This skill guides you on how to query patent family information via the Eureka patent data platform, helping users discover Simple Family, INPADOC Family, and PatSnap Family members for given patents.

## Core Concepts

A **patent family** is a collection of patent documents that are related to each other by priority claims. Different family definitions capture different scopes of relatedness:

- **Simple Family**: Patents sharing exactly the same set of priority applications. These are typically direct equivalents filed in different countries.
- **INPADOC Family**: A broader grouping defined by the European Patent Office that links patents sharing at least one common priority, even indirectly.
- **PatSnap Family**: A proprietary family definition that extends INPADOC logic with additional heuristics to capture continuations, divisionals, and other related filings.

Each patent in the response carries its own `simpleFamilyId`, `inpadocFamilyId`, and `patsnapFamilyId`, which serve as unique identifiers for the family group under each definition.

## Parameter Guide

You must supply at least one of the two lookup parameters. If both are provided, patent ID takes precedence.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patentId | string | Conditionally | Patent ID(s). Separate multiple values with commas. Maximum 100 entries. |
| patentNumber | string | Conditionally | Publication / announcement number(s). Separate multiple values with commas. Maximum 100 entries. |

**Rules**:
1. At least one of `patentId` or `patentNumber` must be provided.
2. If both are provided, the API uses `patentId` and ignores `patentNumber`.
3. Multiple values are comma-separated (e.g., `"US10000001B2,EP3000001A1"`).
4. The upper limit is 100 patents per request.

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| total | integer | Number of patent records returned |
| data | array | List of patent family result objects |
| data[].patentId | string | The patent ID for this record |
| data[].pn | string | Publication / announcement number |
| data[].simpleFamilyId | integer | Unique identifier for the Simple Family group |
| data[].simpleFamily | array | List of Simple Family member patents |
| data[].inpadocFamilyId | integer | Unique identifier for the INPADOC Family group |
| data[].inpadocFamily | array | List of INPADOC Family member patents |
| data[].patsnapFamilyId | integer | Unique identifier for the PatSnap Family group |
| data[].patsnapFamily | array | List of PatSnap Family member patents |
| columns | array | Column definitions for rendering |
| costToken | integer | Tokens consumed by this request |
| type | string | Rendering style hint |

## Usage Examples

**1. Look up family members by publication number**
> "Find the patent family for US10000001B2"

Call with:
```json
{"patentNumber": "US10000001B2"}
```

**2. Look up families for multiple patents at once**
> "Show the INPADOC family for these patents: EP3000001A1, CN112345678A, JP2020123456A"

Call with:
```json
{"patentNumber": "EP3000001A1,CN112345678A,JP2020123456A"}
```

**3. Look up by patent ID**
> "Get the patent family for patent ID 5af83e12-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

Call with:
```json
{"patentId": "5af83e12-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
```

**4. Compare family scopes**
> "I want to see how Simple Family vs. INPADOC Family differs for US20200012345A1"

Call with:
```json
{"patentNumber": "US20200012345A1"}
```
Then compare `simpleFamily` and `inpadocFamily` arrays in the response.

## Display Rules

1. **Present data clearly**: Show patent family results in well-structured tables. Group by family type (Simple, INPADOC, PatSnap) when the user asks for comparison.
2. **Summarize counts**: Always state how many family members were found under each family type so users can quickly gauge geographic spread.
3. **Highlight jurisdictions**: When listing family members, call out the countries/regions covered to help users understand the patent's geographic protection scope.
4. **Error handling**: When the API returns an error or empty results, explain the likely cause (invalid patent number format, patent not found in database, etc.) and suggest corrections.
5. **Batch result organization**: When querying multiple patents, organize results per patent so users can easily find each one.

## Important Limitations

- **Lookup only**: This tool retrieves family information for known patents. It cannot perform keyword-based patent searches or full-text queries.
- **Batch limit**: A maximum of 100 patent IDs or publication numbers per request.
- **Data source**: Family data comes from the Eureka patent platform and may have a slight delay relative to the very latest patent office publications.
- **Family member detail**: The family member arrays contain summary objects. For full bibliographic data on a specific family member, a separate lookup may be required.

## User Expression & Scenario Quick Reference

**Applicable** -- Patent family and equivalents lookup:

| User Says | Scenario |
|-----------|----------|
| "Patent family for XX" | Direct family lookup |
| "What are the equivalents of this patent" | Simple family search |
| "Which countries is this patent filed in" | Geographic coverage via family |
| "INPADOC family members" | Broad family lookup |
| "Related patents / sibling patents" | Family exploration |
| "Compare simple vs extended family" | Multi-definition comparison |
| "Batch check families for these patents" | Bulk family lookup |

**Not applicable** -- Needs beyond patent family lookup:
- Full-text patent search by keywords or classification codes
- Patent valuation or litigation data
- Freedom-to-operate or infringement analysis
- Patent application filing or prosecution


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

## 积分消耗规则

按动态规则计费：消耗积分 = 81 × max(返回条数, 1)。

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
