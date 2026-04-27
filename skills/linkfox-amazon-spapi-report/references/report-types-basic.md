# Amazon SP-API Report Types Reference

This document describes the common report types available in Amazon Selling Partner API.

## Report Categories

Amazon SP-API reports are organized into the following main categories:

### 1. Inventory Reports (库存报告)

Track your inventory status, listings, and stock levels.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_MERCHANT_LISTINGS_ALL_DATA` | Active listings report including SKU, ASIN, price, quantity | Near real-time |
| `GET_MERCHANT_LISTINGS_DATA` | Active listings in tab-delimited flat file format | Near real-time |
| `GET_MERCHANT_LISTINGS_INACTIVE_DATA` | Inactive listings report | Near real-time |
| `GET_MERCHANT_CANCELLED_LISTINGS_DATA` | Cancelled listings | Near real-time |
| `GET_FLAT_FILE_OPEN_LISTINGS_DATA` | Open listings report (SKU, price, quantity) | Near real-time |
| `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` | FBA Manage Inventory Report | Near real-time |
| `GET_FBA_INVENTORY_AGED_DATA` | FBA Inventory Age Report | Daily |
| `GET_FBA_INVENTORY_PLANNING_DATA` | FBA Inventory Planning Report | Daily |

**Common Use Cases:**
- Monitor current inventory levels
- Identify inactive or stranded inventory
- Plan inventory replenishment
- Audit listing accuracy

### 2. Order Reports (订单报告)

Retrieve order data for processing and analysis.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | All orders by order date (general format) | Near real-time |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | All orders by last update date | Near real-time |
| `GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE` | All orders in XML format | Near real-time |
| `GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE` | Archived orders data | Historical |
| `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA` | Actionable orders requiring processing | Near real-time |
| `GET_ORDER_REPORT_DATA_SHIPPING` | Orders with shipping information | Near real-time |

**Common Use Cases:**
- Export orders for ERP/WMS systems
- Track order fulfillment status
- Analyze order patterns
- Generate shipping labels

### 3. Financial Reports (财务报告)

Access settlement and financial transaction data.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` | Settlement report v2 (flat file) | Every 14 days |
| `GET_V2_SETTLEMENT_REPORT_DATA_XML` | Settlement report v2 (XML format) | Every 14 days |
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2` | Enhanced settlement report | Every 14 days |

**Common Use Cases:**
- Reconcile Amazon payments
- Track fees and refunds
- Generate financial statements
- Accounting integration

### 4. Sales Reports (销售报告)

Analyze sales performance and traffic metrics.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_SALES_AND_TRAFFIC_REPORT` | Sales and traffic by date | Daily |
| `GET_FLAT_FILE_SALES_TAX_DATA` | Sales tax collection data | Near real-time |

**Common Use Cases:**
- Track daily sales metrics
- Monitor traffic and conversion rates
- Analyze sales trends
- Tax reporting

### 5. FBA (Fulfillment by Amazon) Reports

Manage FBA inventory and shipments.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL` | FBA fulfilled shipments | Near real-time |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA` | FBA customer shipment sales | Daily |
| `GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA` | FBA removal order details | Daily |
| `GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA` | FBA removal shipment details | Daily |
| `GET_FBA_STORAGE_FEE_CHARGES_DATA` | FBA storage fee charges | Monthly |
| `GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA` | Estimated FBA fees | On-demand |

**Common Use Cases:**
- Track FBA shipments
- Monitor storage fees
- Process removal orders
- Analyze fulfillment costs

### 6. Returns Reports (退货报告)

Track customer returns and refunds.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE` | Returns data by return date | Daily |
| `GET_XML_RETURNS_DATA_BY_RETURN_DATE` | Returns data in XML format | Daily |
| `GET_FLAT_FILE_ALL_RETURNS_DATA_BY_RETURN_DATE` | All returns data | Daily |
| `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` | FBA customer returns | Daily |

**Common Use Cases:**
- Process return requests
- Track return rates
- Analyze return reasons
- Manage refunds

### 7. Performance Reports (绩效报告)

Monitor seller performance metrics.

| Report Type | Description | Update Frequency |
|-------------|-------------|------------------|
| `GET_V1_SELLER_PERFORMANCE_REPORT` | Seller performance metrics | Daily |
| `GET_FLAT_FILE_FEEDBACK_DATA` | Customer feedback | Daily |

**Common Use Cases:**
- Monitor account health
- Track customer satisfaction
- Identify performance issues
- Respond to feedback

## Report Request Workflow

### Creating a Report

1. **Request a Report**
   - Endpoint: `POST /reports/2021-06-30/reports`
   - Specify `reportType`, `marketplaceIds`, and optional date range
   - Receive a `reportId` in response

2. **Check Report Status**
   - Endpoint: `GET /reports/2021-06-30/reports/{reportId}`
   - Status values: `IN_QUEUE`, `IN_PROGRESS`, `DONE`, `CANCELLED`, `FATAL`

3. **Download Report Document**
   - When status is `DONE`, get `reportDocumentId`
   - Endpoint: `GET /reports/2021-06-30/documents/{reportDocumentId}`
   - Get download URL and decrypt if needed

### Getting Existing Reports

- Endpoint: `GET /reports/2021-06-30/reports`
- Filter by `reportTypes`, `processingStatuses`, `marketplaceIds`
- Filter by date range: `createdSince`, `createdUntil`

## Common Parameters

| Parameter | Description | Required | Example |
|-----------|-------------|----------|---------|
| `reportType` | Type of report to generate | Yes | `GET_MERCHANT_LISTINGS_ALL_DATA` |
| `marketplaceIds` | Target marketplace(s) | Yes | `["ATVPDKIKX0DER"]` (US) |
| `dataStartTime` | Start date for data range | No | `2024-01-01T00:00:00Z` |
| `dataEndTime` | End date for data range | No | `2024-01-31T23:59:59Z` |

## Marketplace IDs

| Region | Country | Marketplace ID |
|--------|---------|----------------|
| NA | United States | ATVPDKIKX0DER |
| NA | Canada | A2EUQ1WTGCTBG2 |
| NA | Mexico | A1AM78C64UM0Y8 |
| EU | United Kingdom | A1F83G8C2ARO7P |
| EU | Germany | A1PA6795UKMFR9 |
| EU | France | A13V1IB3VIYZZH |
| EU | Italy | APJ6JRA9NG5V4 |
| EU | Spain | A1RKKUPIHCS9HS |
| FE | Japan | A1VC38T7YXB528 |
| FE | Australia | A39IBJ37TRP1C6 |
| FE | Singapore | A19VAU5U5O7RUS |
| FE | India | A21TJRUUN4KGV |

## Best Practices

1. **Request Frequency**
   - Respect rate limits: typically 0.0222 requests/second (1 request per 45 seconds)
   - Use burst capacity wisely
   - Schedule recurring reports during off-peak hours

2. **Date Ranges**
   - Keep date ranges reasonable (typically 1-90 days)
   - Some reports may have maximum date range restrictions
   - Use `dataStartTime` and `dataEndTime` to narrow results

3. **Error Handling**
   - Check report status before downloading
   - Handle `FATAL` status reports gracefully
   - Retry failed requests with exponential backoff

4. **Data Processing**
   - Reports are typically in TSV (tab-separated values) format
   - Handle large files efficiently (streaming)
   - Validate data before processing

## Example: Request Inventory Report

```json
POST /reports/2021-06-30/reports
{
  "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## Example: Get Reports List

```
GET /reports/2021-06-30/reports?reportTypes=GET_MERCHANT_LISTINGS_ALL_DATA&marketplaceIds=ATVPDKIKX0DER
```

## Additional Resources

- Official Documentation: https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference
- Report Type Values: https://developer-docs.amazon.com/sp-api/docs/report-type-values
- Reports API Use Case Guide: https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-use-case-guide

---

**Note**: Report availability and update frequency may vary by marketplace and seller account type. Always check the official Amazon SP-API documentation for the most current information.
