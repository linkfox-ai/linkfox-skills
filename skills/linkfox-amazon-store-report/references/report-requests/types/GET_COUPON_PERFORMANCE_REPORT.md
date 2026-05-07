# `GET_COUPON_PERFORMANCE_REPORT`

> **分类**：11. Performance Reports  
> **说明**：Coupon performance  
> **可用范围**：Both

> **说明**：Seller 与 Vendor 共用同一 `reportType` 字符串时，请按账号类型阅读 **Seller** 或 **Vendor** 专页。

## 官方索引（Report type values）

- **Schema 专页（请求体、`reportOptions`、结果 JSON）**：[`sellerCouponReport.md`](../sellerCouponReport.md)、[`vendorCouponReport.md`](../vendorCouponReport.md)
- **Amazon 文档（权限/站点等；与 Schema 专页技术描述重复处以 Schema 专页为准）**：[Performance Reports](https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#coupons-performance-report)（章节：**Coupons Performance Report**）

- **受限报告**：按当前小节文本为否（仍以官方为准）
- **Role**：[Brand Analytics](https://developer-docs.amazon.com/sp-api/docs/roles-in-the-selling-partner-api#brand-analytics)
- **Availability**：Sellers and Vendors
- **Requested/scheduled**：This report can only be requested.
- **Report output type**：JSON

- **官方直达**：<https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance#coupons-performance-report>


## 官方 JSON Schema 与请求/结果说明

技术细节（`reportSpecification`、`reportOptions`、下载结果的 JSON 结构）见本节上方 **Schema 专页**链接，此处不重复列出。


## CreateReport

**请优先以专页中的官方示例构造请求体**；下列仅为占位，**可能缺少必填 `reportOptions` 或日期规则**。

```json
{
  "reportType": "GET_COUPON_PERFORMANCE_REPORT",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## LinkFox

`scripts/get_report.py`、`references/api.md`。

## 另见

- `references/report-types.md`
