---
name: linkfox-sellersprite-traffic-keyword
description: 使用卖家精灵流量词反查能力，按ASIN查询关键词流量来源、流量占比类型、转化类型、自然位与广告位等指标，支持历史月份与多维排序。当用户提到ASIN反查流量词、流量关键词列表、关键词流量结构、自然词/广告词分析、关键词转化类型、SellerSprite traffic keyword、Amazon traffic keywords、reverse ASIN keywords时触发此技能。即使用户未明确提及"卖家精灵"，只要需求是围绕某个ASIN查看其关键词流量来源与词列表，也应触发此技能。
---

# SellerSprite Traffic Keyword

This skill helps query and analyze traffic keyword lists for an Amazon ASIN via SellerSprite.

## Core Concepts

- **ASIN 反查词**：以商品 ASIN 为输入，查看该商品获得流量的关键词列表。
- **流量占比类型**（`trafficKeywordTypes`）：如主要流量词、精准流量词、长尾词等。
- **转化类型**（`conversionKeywordTypes`）：如转化优质词、平稳词、流失词等。
- **词标签**（`badges`）：如自然搜索词、Amazon Choice 推荐词等。

## API Usage

- Endpoint: `POST https://tool-gateway.linkfox.com/sellersprite/traffic/keyword`
- Auth: Header `Authorization: <api_key>` (`LINKFOXAGENT_API_KEY`)
- See full details in `references/api.md`.
- Runnable script: `scripts/sellersprite_traffic_keyword.py`

## Key Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| marketplace | string | Yes | 市场站点，默认 `US` |
| asin | string | Yes | 要反查的商品 ASIN |
| month | string | No | 历史月份，格式 `yyyyMM`；不传默认最近30天 |
| page | integer | No | 页码，默认 1 |
| size | integer | No | 每页数量，默认 50，最大 100 |
| keyword | string | No | 关键词筛选 |
| badges | string | No | 词标签，多值逗号分隔 |
| trafficKeywordTypes | string | No | 流量占比类型，多值逗号分隔 |
| conversionKeywordTypes | string | No | 转化类型，多值逗号分隔 |
| orderField | string | No | 排序字段，默认 `rankPosition` |
| orderDesc | boolean | No | 是否倒序，默认 `false` |

## Usage Examples

```json
{
  "marketplace": "US",
  "asin": "B0XXXXXXXXX",
  "size": 50,
  "orderField": "rankPosition",
  "orderDesc": false
}
```

```json
{
  "marketplace": "US",
  "asin": "B0XXXXXXXXX",
  "month": "202507",
  "trafficKeywordTypes": "primary,precise",
  "conversionKeywordTypes": "excellent,stable",
  "page": 1,
  "size": 100
}
```

## Display Rules

1. 结果优先展示：关键词、自然位、广告位、流量占比类型、转化类型。
2. 明确标注查询周期（最近30天或历史月份）。
3. 当存在分页时，告知总数与当前页。
4. 不输出与接口无关的主观商业建议，除非用户明确要求。

## Important Limitations

- 必填参数：`marketplace`、`asin`
- 单次每页最多 100 条
- 历史查询需传 `yyyyMM`

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.
