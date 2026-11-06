# Amazon 店铺完整报告类型索引

本文按类别整理 Amazon SP-API 报告类型。

**总计**：本页表格共 **109** 个 `reportType` 枚举（与 `report-requests/types/` 专页一一对应）；Amazon 文档中可能另有增减，以 [Report type values](https://developer-docs.amazon.com/sp-api/docs/report-type-values) 为准。

**全覆盖请求说明**：下表每一个 `报告类型` 在仓库中均有独立专页（CreateReport 要点、是否有官方 JSON Schema、链到 GitHub `schemas/reports` 专页等）→ [`report-requests/types/README.md`](report-requests/types/README.md)（按 `reportType` 字母/索引表浏览），或直接打开 [`report-requests/types/<REPORT_TYPE>.md`](report-requests/types)。

---

## 1. Amazon Business 报告

业务相关费用与折扣报告。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `FEE_DISCOUNTS_REPORT` | Amazon Business 费用折扣 | 仅卖家 |

---

## 2. 分析报告

销售、流量和经营分析报告。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_BRAND_ANALYTICS_SEARCH_CATALOG_PERFORMANCE_REPORT` | 搜索目录表现指标 | 仅卖家 |
| `GET_BRAND_ANALYTICS_SEARCH_QUERY_PERFORMANCE_REPORT` | 搜索查询表现数据 | 仅卖家 |
| `GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT` | 经常组合购买的商品 | 卖家与 Vendor |
| `GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT` | 商品热门搜索词 | 卖家与 Vendor |
| `GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT` | 重复购买行为分析 | 卖家与 Vendor |
| `GET_VENDOR_REAL_TIME_INVENTORY_REPORT` | Vendor 实时库存 | 仅 Vendor |
| `GET_VENDOR_REAL_TIME_TRAFFIC_REPORT` | Vendor 实时流量 | 仅 Vendor |
| `GET_VENDOR_REAL_TIME_SALES_REPORT` | Vendor 实时销售 | 仅 Vendor |
| `GET_VENDOR_SALES_REPORT` | Vendor 销售报告 | 仅 Vendor |
| `GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT` | Vendor 商品利润率 | 仅 Vendor |
| `GET_VENDOR_TRAFFIC_REPORT` | Vendor 流量报告 | 仅 Vendor |
| `GET_VENDOR_FORECASTING_REPORT` | Vendor 需求预测 | 仅 Vendor |
| `GET_VENDOR_INVENTORY_REPORT` | Vendor 库存报告 | 仅 Vendor |
| `GET_SALES_AND_TRAFFIC_REPORT` | 按日期汇总的销售与流量 | 仅卖家 |

---

## 3. B2B 商品机会

B2B 商品机会洞察。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_B2B_PRODUCT_OPPORTUNITIES_RECOMMENDED_FOR_YOU` | 个性化 B2B 商品推荐 | 仅卖家 |
| `GET_B2B_PRODUCT_OPPORTUNITIES_NOT_YET_ON_AMAZON` | 尚未在 Amazon 上架的 B2B 机会 | 仅卖家 |

---

## 4. 浏览树报告

商品类目和浏览节点数据。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_XML_BROWSE_TREE_DATA` | 浏览树层级（XML 格式） | 仅卖家 |

---

## 5. Easy Ship 报告

Amazon Easy Ship 计划报告（印度站点）。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_EASYSHIP_DOCUMENTS` | Easy Ship 配送文档 | 仅卖家 |
| `GET_EASYSHIP_PICKEDUP` | Easy Ship 已揽收订单 | 仅卖家 |
| `GET_EASYSHIP_WAITING_FOR_PICKUP` | 等待 Easy Ship 揽收的订单 | 仅卖家 |

---

## 6. FBA（亚马逊配送）报告

FBA 库存、货件、费用和履约数据。

### 6.1 FBA 配送货件

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL` | FBA 配送货件（通用） | 仅卖家 |
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_INVOICING` | FBA 货件开票数据 | 仅卖家 |
| `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_TAX` | FBA 货件税务数据 | 仅卖家 |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_SALES_DATA` | FBA 客户货件销售 | 仅卖家 |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA` | FBA 货件促销数据 | 仅卖家 |
| `GET_FBA_FULFILLMENT_CUSTOMER_TAXES_DATA` | FBA 客户税务数据 | 仅卖家 |

### 6.2 FBA 库存

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_AFN_INVENTORY_DATA` | Amazon 配送网络库存 | 仅卖家 |
| `GET_AFN_INVENTORY_DATA_BY_COUNTRY` | 按国家汇总的 AFN 库存 | 仅卖家 |
| `GET_LEDGER_SUMMARY_VIEW_DATA` | 库存分类账汇总 | 仅卖家 |
| `GET_LEDGER_DETAIL_VIEW_DATA` | 库存分类账明细 | 仅卖家 |
| `GET_RESERVED_INVENTORY_DATA` | 预留库存数据 | 仅卖家 |
| `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA` | FBA 有效库存管理 | 仅卖家 |
| `GET_FBA_MYI_ALL_INVENTORY_DATA` | FBA 全部库存状态 | 仅卖家 |
| `GET_RESTOCK_INVENTORY_RECOMMENDATIONS_REPORT` | FBA 补货建议 | 仅卖家 |
| `GET_STRANDED_INVENTORY_UI_DATA` | 滞留库存（界面格式） | 仅卖家 |
| `GET_STRANDED_INVENTORY_LOADER_DATA` | 滞留库存（批量格式） | 仅卖家 |
| `GET_FBA_INVENTORY_PLANNING_DATA` | FBA 库存规划 | 仅卖家 |
| `GET_REMOTE_FULFILLMENT_ELIGIBILITY` | 远程配送资格 | 仅卖家 |

### 6.3 FBA 费用

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_FBA_STORAGE_FEE_CHARGES_DATA` | FBA 仓储收费 | 仅卖家 |
| `GET_FBA_OVERAGE_FEE_CHARGES_DATA` | FBA 超量仓储收费 | 仅卖家 |
| `GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA` | FBA 费用估算 | 仅卖家 |
| `GET_FBA_FULFILLMENT_LONGTERM_STORAGE_FEE_CHARGES_DATA` | 长期仓储费用 | 仅卖家 |

### 6.4 FBA 退货与赔偿

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` | FBA 客户退货 | 仅卖家 |
| `GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA` | FBA 货件替换商品 | 仅卖家 |
| `GET_FBA_REIMBURSEMENTS_DATA` | FBA 赔偿 | 仅卖家 |

### 6.5 FBA 移除

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_FBA_RECOMMENDED_REMOVAL_DATA` | 建议移除的库存 | 仅卖家 |
| `GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA` | Removal order details | 仅卖家 |
| `GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA` | 移除货件明细 | 仅卖家 |

### 6.6 FBA 合规

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_FBA_FULFILLMENT_INBOUND_NONCOMPLIANCE_DATA` | 入库不合规问题 | 仅卖家 |

---

## 7. 库存报告

刊登与库存管理报告。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_FLAT_FILE_OPEN_LISTINGS_DATA` | 开放刊登（平面文件） | 仅卖家 |
| `GET_MERCHANT_LISTINGS_ALL_DATA` | 全部有效刊登 | 仅卖家 |
| `GET_MERCHANT_LISTINGS_DATA` | 有效刊登（标准） | 仅卖家 |
| `GET_MERCHANT_LISTINGS_INACTIVE_DATA` | 失效刊登 | 仅卖家 |
| `GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT` | 刊登（向后兼容） | 仅卖家 |
| `GET_MERCHANT_LISTINGS_DATA_LITE` | 刊登（精简版） | 仅卖家 |
| `GET_MERCHANT_LISTINGS_DATA_LITER` | 刊登（更精简版） | 仅卖家 |
| `GET_MERCHANT_CANCELLED_LISTINGS_DATA` | 已取消刊登 | 仅卖家 |
| `GET_MERCHANTS_LISTINGS_FYP_REPORT` | 商品问题修复报告 | 仅卖家 |
| `GET_PAN_EU_OFFER_STATUS` | 泛欧报价状态 | 仅卖家 |
| `GET_MFN_PANEU_OFFER_STATUS` | 卖家配送泛欧报价状态 | 仅卖家 |
| `GET_REFERRAL_FEE_PREVIEW_REPORT` | 佣金预览 | 仅卖家 |

---

## 8. 发票报告

用于税务合规的 VAT 发票数据。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_FLAT_FILE_VAT_INVOICE_DATA_REPORT` | VAT 发票数据（平面文件） | 仅卖家 |
| `GET_XML_VAT_INVOICE_DATA_REPORT` | VAT 发票数据（XML） | 仅卖家 |

---

## 9. 订单报告

订单处理与履约数据。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING` | 待处理发货订单 | 仅卖家 |
| `GET_ORDER_REPORT_DATA_INVOICING` | 订单开票数据 | 仅卖家 |
| `GET_ORDER_REPORT_DATA_TAX` | 订单税务数据 | 仅卖家 |
| `GET_ORDER_REPORT_DATA_SHIPPING` | 订单配送数据 | 仅卖家 |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_INVOICING` | 订单开票（平面文件） | 仅卖家 |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_SHIPPING` | 订单配送（平面文件） | 仅卖家 |
| `GET_FLAT_FILE_ORDER_REPORT_DATA_TAX` | 订单税务（平面文件） | 仅卖家 |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | 按最后更新日期的全部订单 | 仅卖家 |
| `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | 按下单日期的全部订单 | 仅卖家 |
| `GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE` | 已归档订单 | 仅卖家 |
| `GET_XML_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL` | 全部订单（XML，按更新日期） | 仅卖家 |
| `GET_XML_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL` | 全部订单（XML，按下单日期） | 仅卖家 |
| `GET_FLAT_FILE_PENDING_ORDERS_DATA` | 待处理订单（平面文件） | 仅卖家 |
| `GET_PENDING_ORDERS_DATA` | 待处理订单 | 仅卖家 |
| `GET_CONVERGED_FLAT_FILE_PENDING_ORDERS_DATA` | 合并的待处理订单 | 仅卖家 |

---

## 10. 支付报告

财务冻结与支付数据。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_DATE_RANGE_FINANCIAL_HOLDS_DATA` | 指定日期范围的财务冻结 | 仅卖家 |

---

## 11. 绩效报告

卖家绩效指标与反馈。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_SELLER_FEEDBACK_DATA` | 客户反馈 | 仅卖家 |
| `GET_V1_SELLER_PERFORMANCE_REPORT` | 卖家绩效 v1 | 仅卖家 |
| `GET_V2_SELLER_PERFORMANCE_REPORT` | 卖家绩效 v2 | 仅卖家 |
| `GET_PROMOTION_PERFORMANCE_REPORT` | 促销表现 | 卖家与 Vendor |
| `GET_COUPON_PERFORMANCE_REPORT` | 优惠券表现 | 卖家与 Vendor |

---

## 12. 监管合规报告

合规与监管报告。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `END_USER_DATA_REPORT` | 终端用户数据报告 | 仅卖家 |
| `FBA_BULK_INVOICE` | FBA 批量发票 | 仅卖家 |
| `MARKETPLACE_ASIN_PAGE_VIEW_METRICS` | ASIN 页面浏览指标 | 仅卖家 |
| `GET_EPR_MONTHLY_REPORTS` | 生产者延伸责任（月度） | 仅卖家 |
| `GET_EPR_QUARTERLY_REPORTS` | EPR 季度报告 | 仅卖家 |
| `GET_EPR_ANNUAL_REPORTS` | EPR 年度报告 | 仅卖家 |

---

## 13. 退货报告

退货与替换订单数据。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_XML_RETURNS_DATA_BY_RETURN_DATE` | 按日期的退货（XML） | 仅卖家 |
| `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE` | 按日期的退货（平面文件） | 仅卖家 |
| `GET_XML_MFN_PRIME_RETURNS_REPORT` | MFN Prime 退货（XML） | 仅卖家 |
| `GET_CSV_MFN_PRIME_RETURNS_REPORT` | MFN Prime 退货（CSV） | 仅卖家 |
| `GET_XML_MFN_SKU_RETURN_ATTRIBUTES_REPORT` | MFN SKU 退货属性（XML） | 仅卖家 |
| `GET_FLAT_FILE_MFN_SKU_RETURN_ATTRIBUTES_REPORT` | MFN SKU 退货属性（平面文件） | 仅卖家 |

---

## 14. 结算与支付报告

财务结算与交易数据。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` | 结算报告 v2（平面文件） | 仅卖家 |
| `GET_V2_SETTLEMENT_REPORT_DATA_XML` | 结算报告 v2（XML） | 仅卖家 |
| `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE_V2` | 增强结算报告 | 仅卖家 |

---

## 15. 税务报告

税务合规与交易数据。

| 报告类型 | 说明 | 可用范围 |
|-------------|-------------|--------------|
| `GST_MTR_STOCK_TRANSFER_REPORT` | GST 库存调拨报告 | 仅卖家 |
| `GST_MTR_B2B` | GST 月度税务报告 B2B | 仅卖家 |
| `GST_MTR_B2C` | GST 月度税务报告 B2C | 仅卖家 |
| `GET_FLAT_FILE_SALES_TAX_DATA` | 销售税收取数据 | 仅卖家 |
| `SC_VAT_TAX_REPORT` | Seller Central VAT 税务报告 | 仅卖家 |
| `GET_VAT_TRANSACTION_DATA` | VAT 交易数据 | 仅卖家 |
| `GET_GST_MTR_B2B_CUSTOM` | 自定义 GST MTR B2B | 仅卖家 |
| `GET_GST_MTR_B2C_CUSTOM` | 自定义 GST MTR B2C | 仅卖家 |
| `GET_GST_STR_ADHOC` | GST 临时报表 | 仅卖家 |

---

## 报告请求建议

1. **请求频率**：多数报告可按需请求，但部分存在频率限制。
2. **日期范围**：通常按 1–90 天合理选择，具体以报告约定为准。
3. **保留期限**：未另行约定时报告保留 90 天。
4. **速率限制**：参考速率约 0.0222 次/秒，实际请求间隔须遵循对应接口配额及响应提示。
5. **站点范围**：部分报告仅在特定站点可用。

## 常用站点 ID

| 区域 | 国家 | 站点 ID |
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

## 按场景速查

**库存管理**:
- `GET_MERCHANT_LISTINGS_ALL_DATA`
- `GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA`
- `GET_STRANDED_INVENTORY_UI_DATA`

**订单处理**:
- `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL`
- `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING`

**财务分析**:
- `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE`
- `GET_SALES_AND_TRAFFIC_REPORT`
- `GET_FBA_STORAGE_FEE_CHARGES_DATA`

**绩效监控**:
- `GET_V2_SELLER_PERFORMANCE_REPORT`
- `GET_SELLER_FEEDBACK_DATA`
- `GET_SALES_AND_TRAFFIC_REPORT`

**退货管理**:
- `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE`
- `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA`

**税务合规**:
- `GET_FLAT_FILE_SALES_TAX_DATA`
- `GET_VAT_TRANSACTION_DATA`
- `GET_GST_MTR_B2B_CUSTOM`

---

**官方文档**： https://developer-docs.amazon.com/sp-api/docs/report-type-values

**文档覆盖时间**：2026 年 4 月；报告类型的可用性与后续变化以对应官方文档为准。
