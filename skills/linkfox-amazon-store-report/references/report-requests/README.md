# 报告请求与文档格式（按 GitHub schema 分文件）

> 与 [amzn/selling-partner-api-models/schemas/reports](https://github.com/amzn/selling-partner-api-models/tree/main/schemas/reports) 中的 JSON Schema **一一对应**。

## `reportType` 全覆盖（含无 JSON 的 Flat File）

`references/report-types.md` 表格中的 **每一个** `reportType` 均有专页 → **[types/README.md](./types/README.md)**（109 个：`types/<REPORT_TYPE>.md`）。  
有 GitHub JSON 的条目会链回下表中的 `*.md`；其余条目给出最小 CreateReport 模板并指向 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)。

## 索引（仅含官方 `schemas/reports/*.json`）

| 文档 | 上游 Schema | 涉及 `reportType` |
|------|-------------|-------------------|
| [accountHealthReport-2020-11-18.md](./accountHealthReport-2020-11-18.md) | [`accountHealthReport-2020-11-18.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/accountHealthReport-2020-11-18.json) | 见专页（账户状况结果 JSON；`reportType` 以官方 Report Type Values 为准） |
| [b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.md](./b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.md) | [`b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/b2bProductOpportunitiesNotYetOnAmazonReport-2020-11-19.json) | `GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON` |
| [b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.md](./b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.md) | [`b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/b2bProductOpportunitiesRecommendedForYouReport-2020-11-19.json) | `GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU` |
| [endUserDataReport.md](./endUserDataReport.md) | [`endUserDataReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/endUserDataReport.json) | `END_USER_DATA_REPORT` |
| [marketplaceAsinPageViewMetrics.md](./marketplaceAsinPageViewMetrics.md) | [`marketplaceAsinPageViewMetrics.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/marketplaceAsinPageViewMetrics.json) | `MARKETPLACE_ASIN_PAGE_VIEW_METRICS` |
| [promotionReport.md](./promotionReport.md) | [`promotionReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/promotionReport.json) | `GET_PROMOTION_PERFORMANCE_REPORT` |
| [sellerCouponReport.md](./sellerCouponReport.md) | [`sellerCouponReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellerCouponReport.json) | `GET_COUPON_PERFORMANCE_REPORT` |
| [sellerSalesAndTrafficReport.md](./sellerSalesAndTrafficReport.md) | [`sellerSalesAndTrafficReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellerSalesAndTrafficReport.json) | `GET_SALES_AND_TRAFFIC_REPORT` |
| [sellingPartnerMarketBasketAnalysisReport.md](./sellingPartnerMarketBasketAnalysisReport.md) | [`sellingPartnerMarketBasketAnalysisReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerMarketBasketAnalysisReport.json) | `GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT`（搜索词见 `sellingPartnerSearchTermsReport`） |
| [sellingPartnerRepeatPurchaseReport.md](./sellingPartnerRepeatPurchaseReport.md) | [`sellingPartnerRepeatPurchaseReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerRepeatPurchaseReport.json) | `GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT` |
| [sellingPartnerSearchCatalogPerformanceReport.md](./sellingPartnerSearchCatalogPerformanceReport.md) | [`sellingPartnerSearchCatalogPerformanceReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerSearchCatalogPerformanceReport.json) | `GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT` |
| [sellingPartnerSearchQueryPerformanceReport.md](./sellingPartnerSearchQueryPerformanceReport.md) | [`sellingPartnerSearchQueryPerformanceReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerSearchQueryPerformanceReport.json) | `GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT` |
| [sellingPartnerSearchTermsReport.md](./sellingPartnerSearchTermsReport.md) | [`sellingPartnerSearchTermsReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/sellingPartnerSearchTermsReport.json) | `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT` |
| [vendorCouponReport.md](./vendorCouponReport.md) | [`vendorCouponReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorCouponReport.json) | `GET_COUPON_PERFORMANCE_REPORT` |
| [vendorForecastingReport.md](./vendorForecastingReport.md) | [`vendorForecastingReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorForecastingReport.json) | `GET_VENDOR_FORECASTING_REPORT` |
| [vendorInventoryReport.md](./vendorInventoryReport.md) | [`vendorInventoryReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorInventoryReport.json) | `GET_VENDOR_INVENTORY_REPORT` |
| [vendorNetPureProductMarginReport.md](./vendorNetPureProductMarginReport.md) | [`vendorNetPureProductMarginReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorNetPureProductMarginReport.json) | `GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT` |
| [vendorRealTimeInventoryReport.md](./vendorRealTimeInventoryReport.md) | [`vendorRealTimeInventoryReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorRealTimeInventoryReport.json) | `GET_VENDOR_REAL_TIME_INVENTORY_REPORT` |
| [vendorRealTimeSalesReport.md](./vendorRealTimeSalesReport.md) | [`vendorRealTimeSalesReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorRealTimeSalesReport.json) | `GET_VENDOR_REAL_TIME_SALES_REPORT` |
| [vendorRealTimeTrafficReport.md](./vendorRealTimeTrafficReport.md) | [`vendorRealTimeTrafficReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorRealTimeTrafficReport.json) | `GET_VENDOR_REAL_TIME_TRAFFIC_REPORT` |
| [vendorSalesReport.md](./vendorSalesReport.md) | [`vendorSalesReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorSalesReport.json) | `GET_VENDOR_SALES_REPORT` |
| [vendorTrafficReport.md](./vendorTrafficReport.md) | [`vendorTrafficReport.json`](https://raw.githubusercontent.com/amzn/selling-partner-api-models/main/schemas/reports/vendorTrafficReport.json) | `GET_VENDOR_TRAFFIC_REPORT` |

## 通用说明

- **创建报告**：`references/api.md` 中的 `developerProxy` + `path=reports/2021-06-30/reports` + `method=POST`。
- **本目录**：每个 `*.md` 对应一个 `*.json`，给出 `createReport` 请求体要点及 schema 摘要。
- **未出现在上表中的 reportType**：见 **[types/](./types/)** 目录下按枚举命名的专页（全覆盖 `report-types.md`）。
