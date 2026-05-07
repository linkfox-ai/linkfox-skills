# Amazon Ads Report Types

按 `adProduct` 分类。每个 `.md` 文件名即 `reportTypeId`，内容为官方原文 + YAML frontmatter 结构化字段，用于构造 `POST /reporting/reports` 请求体。

## 目录

| adProduct | 目录 |
|-----------|------|
| SPONSORED_PRODUCTS | [`sp/`](./sp/) |
| SPONSORED_BRANDS | [`sb/`](./sb/) |

> Sponsored Display (SD) / Sponsored Television (ST) / Amazon DSP 暂未覆盖，后续版本支持。

## 数据源

https://advertising.amazon.com/API/docs/en-us/guides/reporting/v3/report-types
