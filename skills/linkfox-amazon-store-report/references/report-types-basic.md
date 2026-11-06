# Amazon 店铺常用报告类型索引

本文说明 Amazon SP-API 中常用的报告类型。

## 报告分类

Amazon 店铺报告按以下主要类别组织。

### 1. 库存报告

跟踪库存、刊登状态与库存水平。

| 报告类型 | 说明 | 更新频率 |
|-------------|-------------|------------------|
| `GET_MERCHANT_LISTINGS_ALL_DATA` | 有效刊登报告，包含 SKU、ASIN、价格与数量 | 近实时 |
| `GET_MERCHANT_LISTINGS_DATA` | 制表符分隔的有效刊登文件 | 近实时 |
| `GET_MERCHANT_LISTINGS_INACTIVE_DATA` | 失效刊登报告 | 近实时 |
| `GET_MERCHANT_CANCELLED_LISTINGS_DATA` | 已取消刊登 | 近实时 |
| `GET_FLAT_FILE_OPEN_LISTINGS_DATA` | 开放刊登（SKU、价格、数量） | 近实时 |
| `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` | FBA 库存管理报告 | 近实时 |
| `GET_FBA_INVENTORY_AGED_DATA` | FBA 库龄报告 | 每日 |
| `GET_FBA_INVENTORY_PLANNING_DATA` | FBA 库存规划报告 | 每日 |

**常见用途：**
- 监控当前库存
- 识别失效刊登或滞留库存
- 规划补货
- 核对刊登准确性

### 2. 订单报告

获取订单数据供后续处理和分析。

| 报告类型 | 说明 | 更新频率 |
|-------------|-------------|------------------|
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | 按下单日期的全部订单（通用格式） | 近实时 |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | 按最后更新日期的全部订单 | 近实时 |
| `GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE` | XML 格式的全部订单 | 近实时 |
| `GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE` | 已归档订单数据 | 历史数据 |
| `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA` | 需要处理的订单 | 近实时 |
| `GET_ORDER_REPORT_DATA_SHIPPING` | 含配送信息的订单 | 近实时 |

**常见用途：**
- 导出订单用于 ERP/WMS
- 跟踪订单履约状态
- 分析订单规律
- 生成配送标签

### 3. 财务报告

获取结算与财务交易数据。

| 报告类型 | 说明 | 更新频率 |
|-------------|-------------|------------------|
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` | 结算报告 v2（平面文件） | 每 14 天 |
| `GET_V2_SETTLEMENT_REPORT_DATA_XML` | 结算报告 v2（XML 格式） | 每 14 天 |
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2` | 增强结算报告 | 每 14 天 |

**常见用途：**
- 核对 Amazon 收款
- 跟踪费用与退款
- 生成财务报表
- 会计系统集成

### 4. 销售报告

分析销售表现与流量指标。

| 报告类型 | 说明 | 更新频率 |
|-------------|-------------|------------------|
| `GET_SALES_AND_TRAFFIC_REPORT` | 按日期汇总的销售与流量 | 每日 |
| `GET_FLAT_FILE_SALES_TAX_DATA` | 销售税收取数据 | 近实时 |

**常见用途：**
- 跟踪每日销售指标
- 监控流量与转化率
- 分析销售趋势
- 税务申报

### 5. FBA（亚马逊配送）报告

管理 FBA 库存与货件。

| 报告类型 | 说明 | 更新频率 |
|-------------|-------------|------------------|
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL` | FBA 配送货件 | 近实时 |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA` | FBA 客户货件销售 | 每日 |
| `GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA` | FBA 移除订单明细 | 每日 |
| `GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA` | FBA 移除货件明细 | 每日 |
| `GET_FBA_STORAGE_FEE_CHARGES_DATA` | FBA 仓储收费 | 每月 |
| `GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA` | FBA 费用估算 | 按需 |

**常见用途：**
- 跟踪 FBA 货件
- 监控仓储费用
- 处理移除订单
- 分析履约成本

### 6. 退货报告

跟踪客户退货与退款。

| 报告类型 | 说明 | 更新频率 |
|-------------|-------------|------------------|
| `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE` | 按退货日期的数据 | 每日 |
| `GET_XML_RETURNS_DATA_BY_RETURN_DATE` | XML 格式的退货数据 | 每日 |
| `GET_FLAT_FILE_ALL_RETURNS_DATA_BY_RETURN_DATE` | 全部退货数据 | 每日 |
| `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` | FBA 客户退货 | 每日 |

**常见用途：**
- 处理退货申请
- 跟踪退货率
- 分析退货原因
- 管理退款

### 7. 绩效报告

监控卖家绩效指标。

| 报告类型 | 说明 | 更新频率 |
|-------------|-------------|------------------|
| `GET_V1_SELLER_PERFORMANCE_REPORT` | 卖家绩效指标 | 每日 |
| `GET_FLAT_FILE_FEEDBACK_DATA` | 客户反馈 | 每日 |

**常见用途：**
- 监控账户状况
- 跟踪客户满意度
- 识别绩效问题
- 回应反馈

## 报告请求流程

### 创建报告

1. **请求报告**
   - 上游端点： `POST /reports/2021-06-30/reports`
   - 指定 reportType、marketplaceIds 和可选日期范围。
   - 保存响应的 reportId。

2. **查询报告状态**
   - 上游端点： `GET /reports/2021-06-30/reports/{reportId}`
   - 状态值： `IN_QUEUE`, `IN_PROGRESS`, `DONE`, `CANCELLED`, `FATAL`

3. **下载报告文档**
   - 状态为 DONE 后取得 reportDocumentId。
   - 上游端点： `GET /reports/2021-06-30/documents/{reportDocumentId}`
   - 取得下载 URL，按文档要求解压或处理文件。

### 获取已有报告

- 上游端点： `GET /reports/2021-06-30/reports`
- 可按 reportTypes、processingStatuses、marketplaceIds 筛选。
- 可按 createdSince、createdUntil 筛选创建日期。

## 常用参数

| 参数 | 说明 | 必填 | 示例 |
|-----------|-------------|----------|---------|
| `reportType` | 待生成的报告类型 | 是 | `GET_MERCHANT_LISTINGS_ALL_DATA` |
| `marketplaceIds` | 目标站点 | 是 | `["ATVPDKIKX0DER"]` (US) |
| `dataStartTime` | 数据范围起点 | 否 | `2024-01-01T00:00:00Z` |
| `dataEndTime` | 数据范围终点 | 否 | `2024-01-31T23:59:59Z` |

## 站点 ID

| 区域 | 国家 | 站点 ID |
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

## 使用建议

1. **请求频率**
   - 参考速率约 0.0222 次/秒（约每 45 秒一次），实际请求间隔须遵循对应接口配额及响应提示。
   - 谨慎使用突发配额。
   - 周期报告可在低峰时间安排。

2. **日期范围**
   - 日期范围通常按 1–90 天合理选择。
   - 部分报告有最大日期范围限制，以专页为准。
   - 用 dataStartTime 和 dataEndTime 缩小范围。

3. **错误处理**
   - 下载前检查报告状态。
   - FATAL 时停止并说明原因。
   - 用户决定重试时采用退避，遵循店铺保护，不自动重建报告。

4. **数据处理**
   - 报告通常为 TSV（制表符分隔）格式。
   - 大文件使用流式处理。
   - 处理前校验数据。

## 示例：请求库存报告

上游端点：`POST /reports/2021-06-30/reports`

```json
{
  "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
  "marketplaceIds": ["ATVPDKIKX0DER"]
}
```

## 示例：列出现有报告

```
GET /reports/2021-06-30/reports?reportTypes=GET_MERCHANT_LISTINGS_ALL_DATA&marketplaceIds=ATVPDKIKX0DER
```

## 补充资源

- 官方文档：https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference
- 报告类型值：https://developer-docs.amazon.com/sp-api/docs/report-type-values
- Reports API 使用指引：https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-use-case-guide

---

**注意**：可用性与更新频率因站点、账号类型而异，以对应报告专页和官方文档为准。

本摘要中的枚举写法须在实际请求前按 [109 类型总表](report-types.md) 和 [逐类型专页](report-requests/types/README.md) 核对，不根据本摘要自动试错。当前网关请求与参数见 [接口说明](api.md)。
