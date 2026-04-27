# Amazon SP-API Complete Report Types Reference

This document lists ALL report types available in Amazon Selling Partner API, organized by category.

**Total**: 95+ Report Types

---

## 1. Amazon Business Reports

Business-related fee and discount reports.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `FEE_DISCOUNTS_REPORT` | Amazon Business fee discounts | Seller only |

---

## 2. Analytics Reports

Sales, traffic, and business intelligence reports.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT` | Search catalog performance metrics | Seller only |
| `GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT` | Search query performance data | Seller only |
| `GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT` | Products frequently purchased together | Both |
| `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT` | Top search terms for products | Both |
| `GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT` | Repeat purchase behavior analysis | Both |
| `GET_VENDOR_REAL_TIME_INVENTORY_REPORT` | Real-time vendor inventory | Vendor only |
| `GET_VENDOR_REAL_TIME_TRAFFIC_REPORT` | Real-time vendor traffic | Vendor only |
| `GET_VENDOR_REAL_TIME_SALES_REPORT` | Real-time vendor sales | Vendor only |
| `GET_VENDOR_SALES_REPORT` | Vendor sales report | Vendor only |
| `GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT` | Vendor product margins | Vendor only |
| `GET_VENDOR_TRAFFIC_REPORT` | Vendor traffic report | Vendor only |
| `GET_VENDOR_FORECASTING_REPORT` | Vendor forecasting data | Vendor only |
| `GET_VENDOR_INVENTORY_REPORT` | Vendor inventory report | Vendor only |
| `GET_SALES_AND_TRAFFIC_REPORT` | Sales and traffic by date | Seller only |

---

## 3. B2B Product Opportunities

Business-to-business product opportunity insights.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU` | Personalized B2B product recommendations | Seller only |
| `GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON` | B2B opportunities not yet on Amazon | Seller only |

---

## 4. Browse Tree Reports

Product category and browse node data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_XML_BROWSE_TREE_DATA` | Browse tree hierarchy (XML format) | Seller only |

---

## 5. Easy Ship Reports

Amazon Easy Ship program reports (India marketplace).

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_EASYSHIP_DOCUMENTS` | Easy Ship shipping documents | Seller only |
| `GET_EASYSHIP_PICKEDUP` | Easy Ship picked up orders | Seller only |
| `GET_EASYSHIP_WAITING_FOR_PICKUP` | Orders waiting for Easy Ship pickup | Seller only |

---

## 6. FBA (Fulfillment by Amazon) Reports

Comprehensive FBA inventory, shipment, fees, and fulfillment data.

### 6.1 FBA Shipments

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL` | FBA fulfilled shipments (general) | Seller only |
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING` | FBA shipments for invoicing | Seller only |
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX` | FBA shipments tax data | Seller only |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA` | FBA customer shipment sales | Seller only |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA` | FBA shipment promotion data | Seller only |
| `GET_FBA_FULFILLMENT_CUSTOMER_TAXES_DATA` | FBA customer taxes | Seller only |

### 6.2 FBA Inventory

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_AFN_INVENTORY_DATA` | Amazon Fulfilled Network inventory | Seller only |
| `GET_AFN_INVENTORY_DATA_BY_COUNTRY` | AFN inventory by country | Seller only |
| `GET_LEDGER_SUMMARY_VIEW_DATA` | Inventory ledger summary | Seller only |
| `GET_LEDGER_DETAIL_VIEW_DATA` | Inventory ledger detail | Seller only |
| `GET_RESERVED_INVENTORY_DATA` | Reserved inventory data | Seller only |
| `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` | FBA Manage Your Inventory (active) | Seller only |
| `GET_FBA_MYI_ALL_INVENTORY_DATA` | FBA all inventory status | Seller only |
| `GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT` | FBA restock recommendations | Seller only |
| `GET_STRANDED_INVENTORY_UI_DATA` | Stranded inventory (UI format) | Seller only |
| `GET_STRANDED_INVENTORY_LOADER_DATA` | Stranded inventory (bulk format) | Seller only |
| `GET_FBA_INVENTORY_PLANNING_DATA` | FBA inventory planning | Seller only |
| `GET_REMOTE_FULFILLMENT_ELIGIBILITY` | Remote fulfillment eligibility | Seller only |

### 6.3 FBA Fees & Charges

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FBA_STORAGE_FEE_CHARGES_DATA` | FBA storage fee charges | Seller only |
| `GET_FBA_OVERAGE_FEE_CHARGES_DATA` | FBA overage fee charges | Seller only |
| `GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA` | Estimated FBA fees | Seller only |
| `GET_FBA_FULFILLMENT_LONGTERM_STORAGE_FEE_CHARGES_DATA` | Long-term storage fees | Seller only |

### 6.4 FBA Returns & Reimbursements

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` | FBA customer returns | Seller only |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA` | FBA shipment replacements | Seller only |
| `GET_FBA_REIMBURSEMENTS_DATA` | FBA reimbursements | Seller only |

### 6.5 FBA Removals

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FBA_RECOMMENDED_REMOVAL_DATA` | Recommended removal inventory | Seller only |
| `GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA` | Removal order details | Seller only |
| `GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA` | Removal shipment details | Seller only |

### 6.6 FBA Compliance

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA` | Inbound non-compliance issues | Seller only |

---

## 7. Inventory Reports

Listing and inventory management reports.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FLAT_FILE_OPEN_LISTINGS_DATA` | Open listings (flat file) | Seller only |
| `GET_MERCHANT_LISTINGS_ALL_DATA` | All active listings | Seller only |
| `GET_MERCHANT_LISTINGS_DATA` | Active listings (standard) | Seller only |
| `GET_MERCHANT_LISTINGS_INACTIVE_DATA` | Inactive listings | Seller only |
| `GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT` | Listings (backwards compatible) | Seller only |
| `GET_MERCHANT_LISTINGS_DATA_LITE` | Listings (lite version) | Seller only |
| `GET_MERCHANT_LISTINGS_DATA_LITER` | Listings (lighter version) | Seller only |
| `GET_MERCHANT_CANCELLED_LISTINGS_DATA` | Cancelled listings | Seller only |
| `GET_MERCHANTS_LISTINGS_FYP_REPORT` | Fix Your Products report | Seller only |
| `GET_PAN_EU_OFFER_STATUS` | Pan-European offer status | Seller only |
| `GET_MFN_PANEU_OFFER_STATUS` | MFN Pan-EU offer status | Seller only |
| `GET_REFERRAL_FEE_PREVIEW_REPORT` | Referral fee preview | Seller only |

---

## 8. Invoice Reports

VAT invoice data for tax compliance.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT` | VAT invoice data (flat file) | Seller only |
| `GET_XML_VAT_INVOICE_DATA_REPORT` | VAT invoice data (XML) | Seller only |

---

## 9. Order Reports

Order processing and fulfillment data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING` | Actionable orders for shipping | Seller only |
| `GET_ORDER_REPORT_DATA_INVOICING` | Order data for invoicing | Seller only |
| `GET_ORDER_REPORT_DATA_TAX` | Order tax data | Seller only |
| `GET_ORDER_REPORT_DATA_SHIPPING` | Order shipping data | Seller only |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING` | Order invoicing (flat file) | Seller only |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING` | Order shipping (flat file) | Seller only |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_TAX` | Order tax (flat file) | Seller only |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | All orders by last update | Seller only |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | All orders by order date | Seller only |
| `GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE` | Archived orders | Seller only |
| `GET_XML_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | All orders (XML, by update) | Seller only |
| `GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | All orders (XML, by date) | Seller only |
| `GET_FLAT_FILE_PENDING_ORDERS_DATA` | Pending orders (flat file) | Seller only |
| `GET_PENDING_ORDERS_DATA` | Pending orders | Seller only |
| `GET_CONVERGED_FLAT_FILE_PENDING_ORDERS_DATA` | Converged pending orders | Seller only |

---

## 10. Payment Reports

Financial holds and payment data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_DATE_RANGE_FINANCIAL_HOLDS_DATA` | Financial holds by date range | Seller only |

---

## 11. Performance Reports

Seller performance metrics and feedback.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_SELLER_FEEDBACK_DATA` | Customer feedback | Seller only |
| `GET_V1_SELLER_PERFORMANCE_REPORT` | Seller performance v1 | Seller only |
| `GET_V2_SELLER_PERFORMANCE_REPORT` | Seller performance v2 | Seller only |
| `GET_PROMOTION_PERFORMANCE_REPORT` | Promotion performance | Both |
| `GET_COUPON_PERFORMANCE_REPORT` | Coupon performance | Both |

---

## 12. Regulatory Compliance Reports

Compliance and regulatory reporting.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `END_USER_DATA_REPORT` | End user data report | Seller only |
| `FBA_BULK_INVOICE` | FBA bulk invoice | Seller only |
| `MARKETPLACE_ASIN_PAGE_VIEW_METRICS` | ASIN page view metrics | Seller only |
| `GET_EPR_MONTHLY_REPORTS` | Extended Producer Responsibility (monthly) | Seller only |
| `GET_EPR_QUARTERLY_REPORTS` | EPR quarterly reports | Seller only |
| `GET_EPR_ANNUAL_REPORTS` | EPR annual reports | Seller only |

---

## 13. Returns Reports

Return and replacement order data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_XML_RETURNS_DATA_BY_RETURN_DATE` | Returns by date (XML) | Seller only |
| `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE` | Returns by date (flat file) | Seller only |
| `GET_XML_MFN_PRIME_RETURNS_REPORT` | MFN Prime returns (XML) | Seller only |
| `GET_CSV_MFN_PRIME_RETURNS_REPORT` | MFN Prime returns (CSV) | Seller only |
| `GET_XML_MFN_SKU_RETURN_ATTRIBUTES_REPORT` | MFN SKU return attributes (XML) | Seller only |
| `GET_FLAT_FILE_MFN_SKU_RETURN_ATTRIBUTES_REPORT` | MFN SKU return attributes (flat file) | Seller only |

---

## 14. Settlement/Payments Reports

Financial settlement and transaction data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` | Settlement report v2 (flat file) | Seller only |
| `GET_V2_SETTLEMENT_REPORT_DATA_XML` | Settlement report v2 (XML) | Seller only |
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2` | Enhanced settlement report | Seller only |

---

## 15. Tax Reports

Tax compliance and transaction data.

| Report Type | Description | Availability |
|-------------|-------------|--------------|
| `GST_MTR_STOCK_TRANSFER_REPORT` | GST stock transfer report | Seller only |
| `GST_MTR_B2B` | GST Monthly Tax Report B2B | Seller only |
| `GST_MTR_B2C` | GST Monthly Tax Report B2C | Seller only |
| `GET_FLAT_FILE_SALES_TAX_DATA` | Sales tax collection data | Seller only |
| `SC_VAT_TAX_REPORT` | Seller Central VAT tax report | Seller only |
| `GET_VAT_TRANSACTION_DATA` | VAT transaction data | Seller only |
| `GET_GST_MTR_B2B_CUSTOM` | Custom GST MTR B2B | Seller only |
| `GET_GST_MTR_B2C_CUSTOM` | Custom GST MTR B2C | Seller only |
| `GET_GST_STR_ADHOC` | GST Adhoc report | Seller only |

---

## Report Request Best Practices

1. **Schedule Frequency**: Most reports can be requested on-demand, but some have rate limits
2. **Date Ranges**: Use reasonable date ranges (typically 1-90 days)
3. **Retention**: Reports are retained for 90 days unless specified otherwise
4. **Rate Limits**: Respect API rate limits (typically 0.0222 requests/second)
5. **Marketplace-Specific**: Some reports are only available in certain marketplaces

## Common Marketplace IDs

| Region | Country | Marketplace ID |
|--------|---------|----------------|
| NA | United States | ATVPDKIKX0DER |
| NA | Canada | A2EUQ1WTGCTBG2 |
| NA | Mexico | A1AM78C64UM0Y8 |
| NA | Brazil | A2Q3Y263D00KWC |
| EU | United Kingdom | A1F83G8C2ARO7P |
| EU | Germany | A1PA6795UKMFR9 |
| EU | France | A13V1IB3VIYZZH |
| EU | Italy | APJ6JRA9NG5V4 |
| EU | Spain | A1RKKUPIHCS9HS |
| EU | Netherlands | A1805IZSGTT6HS |
| EU | Poland | A1C3SOZRARQ6R3 |
| EU | Sweden | A2NODRKZP88ZB9 |
| EU | Turkey | A33AVAJ2PDY3EV |
| FE | Japan | A1VC38T7YXB528 |
| FE | Australia | A39IBJ37TRP1C6 |
| FE | Singapore | A19VAU5U5O7RUS |
| FE | India | A21TJRUUN4KGV |
| FE | UAE | A2VIGQ35RCS4UG |

## Quick Reference by Use Case

**Inventory Management**:
- `GET_MERCHANT_LISTINGS_ALL_DATA`
- `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA`
- `GET_STRANDED_INVENTORY_UI_DATA`

**Order Processing**:
- `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL`
- `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING`

**Financial Analysis**:
- `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE`
- `GET_SALES_AND_TRAFFIC_REPORT`
- `GET_FBA_STORAGE_FEE_CHARGES_DATA`

**Performance Monitoring**:
- `GET_V2_SELLER_PERFORMANCE_REPORT`
- `GET_SELLER_FEEDBACK_DATA`
- `GET_SALES_AND_TRAFFIC_REPORT`

**Returns Management**:
- `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE`
- `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA`

**Tax Compliance**:
- `GET_FLAT_FILE_SALES_TAX_DATA`
- `GET_VAT_TRANSACTION_DATA`
- `GET_GST_MTR_B2B_CUSTOM`

---

**Official Documentation**: https://developer-docs.amazon.com/sp-api/docs/report-type-values

**Last Updated**: Based on Amazon SP-API documentation as of April 2026
