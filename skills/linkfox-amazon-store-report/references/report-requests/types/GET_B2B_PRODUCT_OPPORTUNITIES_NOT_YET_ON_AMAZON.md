# `GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON`

> **分类**：3. B2B 商品机会  
> **说明**：尚未在 Amazon 上架的 B2B 机会  
> **可用范围**：仅卖家

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：[`b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.md`](../b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.md)
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[B2B 商品机会 Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-b2b-product-opportunities#b2b-product-opportunities---not-yet-on-amazon)（章节：**B2B Product Opportunities - Not yet on Amazon**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **角色**：[Product Listing](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#product-listing)
- **站点范围**：仅限特定站点，请按本页 Amazon 文档链接核对可用站点清单。
- **按需/计划**：本报告仅可按需请求。
- **输出格式**：逗号分隔的平面文件

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-b2b-product-opportunities#b2b-product-opportunities---not-yet-on-amazon>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

`scripts/get_report.py`、`references/api.md`。

## 另见

- `references/report-types.md`
