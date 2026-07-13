---
name: linkfox-lingxing-erp
description: LinkFox 包装的领星（Lingxing）ERP 技能「linkfox-lingxing-erp」：由 LinkFox Skills 仓库收录分发，封装领星官方 OpenAPI 文档与脚本用法，底层仍直连 openapi.lingxing.com（非 LinkFox 自建网关）。覆盖约 373 个接口场景，含广告报表 SP/SB/SD、订单与 Listing、库存仓库、财务与 FBA、源表、采购、客服、多平台广告与订单等。当用户提到领星、Lingxing、领星开放接口、领星 ERP 数据、领星广告报表、领星订单/库存/利润、领星 SID、Lingxing OpenAPI、Lingxing ERP data、LinkFox 领星、linkfox-lingxing-erp 时触发。分模块参数见 references/api.md 及各 references/*.md；需 LINGXING_APP_ID 与 LINGXING_APP_SECRET。
---

# 领星 ERP OpenAPI（LinkFox 包装版）

**本 skill 是 LinkFox 对领星（Lingxing）官方开放能力的包装**：`name` 为 `linkfox-lingxing-erp`，内容与领星侧 OpenAPI 文档及 `scripts/lingxing.py` 保持一致，由 LinkFox 仓库统一版本管理；认证与请求仍发往 **领星官方域名**。速查见 `references/api.md`。

查询领星 ERP 全模块数据，支持 **373 个接口**，覆盖广告、销售、产品、财务、统计、FBA、仓库、采购、客服、多平台等全业务线。

## 环境变量配置

```bash
export LINGXING_APP_ID=your_app_id
export LINGXING_APP_SECRET=your_app_secret

# 可选：设置默认店铺 SID，无需每次在 --params 中传入
export LINGXING_SID=your_sid
```

在领星 ERP -> 开放接口菜单中获取 AppID 和 AppSecret。

## 使用方式

以下命令均在 **本 skill 根目录**（含 `SKILL.md` 与 `scripts/` 的目录）下执行。

```bash
# 列出所有已授权亚马逊店铺，获取 SID
python3 scripts/lingxing.py --list-stores

# 查看所有支持的接口
python3 scripts/lingxing.py --api help

# 基础调用
python3 scripts/lingxing.py --api <接口名> --params '<JSON参数>'

# 自动翻页获取全部数据
python3 scripts/lingxing.py --api <接口名> --params '<JSON参数>' --all

# 自定义翻页大小
python3 scripts/lingxing.py --api <接口名> --params '<JSON参数>' --all --page-size 50
```

输出为 JSON 到 stdout，翻页进度输出到 stderr。

## 调用示例

```bash
# 第一步：查询店铺列表获取 SID
python3 scripts/lingxing.py --list-stores
export LINGXING_SID=813

# 广告报表
python3 scripts/lingxing.py \
  --api spCampaignReports \
  --params '{"report_date": "2024-01-01"}'

# 亚马逊订单（自动翻页）
python3 scripts/lingxing.py \
  --api mwsOrders \
  --params '{"start_date": "2024-01-01", "end_date": "2024-01-31"}' --all

# 亚马逊 Listing
python3 scripts/lingxing.py \
  --api mwsListing \
  --params '{"sid": "813", "is_pair": 1, "is_delete": 0}' --all

# 产品列表
python3 scripts/lingxing.py \
  --api ProductLists --params '{"offset": 0, "length": 20}'

# 利润报表（ASIN维度）
python3 scripts/lingxing.py \
  --api profitAsin \
  --params '{"sids": "813", "start_date": "2024-01-01", "end_date": "2024-01-31"}'

# ASIN日销量
python3 scripts/lingxing.py \
  --api AsinDailyLists \
  --params '{"sid": 813, "start_date": "2024-01-01", "end_date": "2024-01-07"}' --all

# FBA发货单列表
python3 scripts/lingxing.py \
  --api FBAShipmentList \
  --params '{"sid": 813}' --all

# 亚马逊源表-全部订单
python3 scripts/lingxing.py \
  --api AllOrders \
  --params '{"sid": 813, "start_date": "2024-01-01", "end_date": "2024-01-31"}' --all

# 仓库列表
python3 scripts/lingxing.py \
  --api WarehouseLists --params '{"offset": 0, "length": 50}'

# Review列表（v2，支持更多筛选）
python3 scripts/lingxing.py \
  --api reviewV2 --params '{"sid": 813, "offset": 0, "length": 20}'

# 多平台订单（V2）
python3 scripts/lingxing.py \
  --api MultiPlatOrderV2 \
  --params '{"start_date": 1704067200, "end_date": 1706745600}' --all

# TikTok广告主列表
python3 scripts/lingxing.py \
  --api queryAdvertiserList \
  --params '{"length": 100}'

# 补货建议汇总
python3 scripts/lingxing.py \
  --api GetSummaryList \
  --params '{"sid_list": [813]}' --all
```

## 接口总览（373个）

### 新广告报表（37个）
接口详见 `references/newad-report.md`。

| 分组 | 接口 |
|------|------|
| SP报表(8) | spCampaignReports, campaignPlacementReports, spAdGroupReports, spProductAdReports, spKeywordReports, spTargetReports, asinReports, queryWordReports |
| SB报表(8) | hsaCampaignReports, hsaCampaignPlacementReports, hsaAdGroupReports, listHsaTargetingReport, hsaQueryWordReports, hsaPurchasedAsinReports, listHsaProductAdReport, listHsaKeywordPlacementReport |
| SD报表(6) | sdCampaignReports, sdAdGroupReports, sdProductAdReports, sdTargetReports, sdAsinReports, sdMatchTargetReports |
| SP小时(5) | spCampaignHourData, spAdPlacementHourData, spAdGroupHourData, spAdvertiseHourData, spTargetHourData |
| SB小时(4) | sbCampaignHourData, sbAdGroupHourData, sbTargetHourData, sbAdPlacementHourData |
| SD小时(4) | sdCampaignHourData, sdAdGroupHourData, sdAdvertiseHourData, sdTargetHourData |
| 其他(2) | dspReportOrderList, ProductAnalysisList |

### 广告基础数据（21个）
接口详见 `references/basedata.md`。

| 分组 | 接口 |
|------|------|
| 账号(1) | dspAccountList |
| 组合(1) | portfolios |
| SP(6) | spCampaigns, spAdGroups, spProductAds, spKeywords, spTargets, spNegativeTargetsOrKeywords |
| SB(6) | hsaCampaigns, hsaAdGroups, hsaProductAds, sbTargeting, hsaNegativeKeywords, hsaNegativeTargets, sbDivideAsinReports |
| SD(5) | sdCampaigns, sdAdGroups, sdProductAds, sdTargets, sdNegativeTargets |
| 报表下载(1) | abaReport |

### 基础数据（8个）
接口详见 `references/basicdata-full.md`。

AccoutLists(GET), AllMarketplace(GET), AttachmentDownload, ConceptSellerLists(GET), Currency, CustomAttachmentDownload, StateList, WorldStateLists

### 销售（39个）
接口详见 `references/sale-ops.md`（订单/Listing核心4个）+ `references/sale-full.md`（其余35个）。

| 分组 | 接口 |
|------|------|
| 订单(7) | mwsOrders, OrderDetail, FBMOrderList, FBMOrderDetail, MCFOrderList, RefundOrder, afterSaleList |
| Listing(5) | mwsListing, sale_ProductList, QueryProductList, GetPrices, listingOperateLogPageList |
| 退货(3) | orderReturnInformation, ProductInformation, LogisticsInformation |
| 促销(12) | promotionListingList, promotionListingDetailCoupon/Manage/PrimeDiscount/SecKill, promotionalActivitiesCouponList/ManageList/SecKillList/VipDiscountList, promotionCouponAllDetailBatch/ManagementAllDetailBatch/PrimeDiscountAllDetailBatch/SecKillAllDetailBatch |
| 运营(7) | scOrderSetRemark, adjustPriceAdjustPriceManual, fbaFeeDifferenceList/MskuList, globalTagPageList, queryListingRelationTagList, GetFulfillmentResult |
| 刊登(5) | PublishManageCategoryRoot/Children, PublishManageGetProductType, GetMerchantShippingGroup |

### 产品（14个）
接口详见 `references/product.md`。

ProductLists, ProductDetails, Brand, Category, UpcList, GetProductTag(GET), GetPagingLogLists, attributeList, batchGetProductInfo, bundledProductList, getTransparencyProductList, productAuxList, spuInfo, spuList

### 财务（41个）
接口详见 `references/finance.md`。

| 分组 | 接口 |
|------|------|
| 利润报表(7) | profitAsin, profitAsinSon, profitSettlement, FianceProfitMsku, OrderProfitListMSKU, ProfitMsku |
| 结算(6) | SettlementReport, SettlementExportUrlGet, settlementSummaryList, settlementTransactionList, CostStream, summaryQuery |
| BD报表(7) | bdASIN, bdMSKU, bdOrder, bdParentASIN, bdSKU, bdSeller, bdSellerSummary |
| 发票(3) | InvoiceList, InvoiceDetail, InvoiceCampaignList |
| 费用管理(2) | feeManagementList, feeManagementType |
| 资金池(6) | requestFundsPoolCustomFeeList/InboundList/LogisticsList/OtherFeeList/PrepayList/PurchaseList |
| 应收(3) | receivableReportList, reportListDetail, reportListDetailInfo |
| 其他(7) | QueryReceiptFundsList, RequestFundsOrderList, centerOdsDetailQuery, profitReportOrderTranscationList, lazadaPayoutList, lazadaSettlementList, shopeeAdjustmentList/IncomeList/PayoutList |

### 统计（35个）
接口详见 `references/statistics.md`。

| 分组 | 接口 |
|------|------|
| 销量(4) | AsinDailyLists, AsinList, AsinListNew, StoreSales |
| FBA仓储(5) | FBAStorageFeeLongTerm, FBAStorageFeeMonth, FbaStockReportList, FbaStockAggregateListNew, FbaStockDetailListNew |
| 本地仓(4) | LocalAggregateList/New, LocalDetailList/New |
| 海外仓(4) | OverseasAggregateList/New, OverseasDetailList/New |
| 新版统计(4) | statisticsOpenASIN/MSKU/Parent/Seller |
| 其他(14) | MonthRefund, ProfitMsku, ReimbursementList, ReturnOrderAnalysisLists, PurchaseReportBuyerList/ProductList/SupplierList, performanceTrendByHour, operateLogList/V2List, PlatformStatisticsSaleStatPageListV2, AmazonReportExportTask, reportCreate/QueryReportExportTask |

### FBA发货（13个）
接口详见 `references/fba.md`。

FBAShipmentList, FBAReceivedInventory, ShipmentPlanLists, GetFbaProductList, GetInboundShipmentList, GetInboundShipmentListMwsDetailList, ShipFromAddressList, BoxInfo, GetHeadLogisticsFeeTypes, GetSeaTrackSupplierCarriers, QuerySTATaskList, StaTaskDetail, getInboundShipmentListMwsDetail

### 亚马逊源表数据（20个）
接口详见 `references/sourcedata.md`。

AllOrders, FbaOrders, RefundOrders, Transaction, ManageInventory, DailyInventory, AfnFulfillableQuantity, ReservedInventory, RemovalLists, RemovalOrderListNew, RemovalShipmentList, SourceRemovalOrders, AdjustmentList, getAmazonFulfilledShipmentsList, getFbaAgeList, getFbaInventoryEventDetailList, v1getAmazonFulfilledShipmentsList, v1getFbaInventoryEventDetailList, fbaExchangeOrderList, fbmReturnOrderList

### 补货建议（9个）
接口详见 `references/fbasug.md`。

GetSummaryList, ConfigASIN, ConfigMSKU, DailySalesInfoFeatureASIN, DailySalesInfoFeatureMSKU, InfoASIN, InfoMSKU, SourceListASIN, SourceListMSKU

### 补货限制（2个）
接口详见 `references/fbalimit.md`。

GetIpiInfo, replenishmentRestrictionList

### 采购（7个）
接口详见 `references/purchase.md`。

PurchaseOrderList, Supplier, changeOrderList, purchaseGetOrders, getPurchasePlans, getPurchaseReturnOrderList, purchaserLists

### 仓库（32个）
接口详见 `references/warehouse.md`。

| 分组 | 接口 |
|------|------|
| 仓库/库存(11) | WarehouseLists, WarehouseStatement/New, InventoryDetails, inventoryBinDetails, wareHouseBinStatement, warehouseBin, FBAStock, FBAStock_v2, AwdWarehouseDetail |
| 批次(2) | GetBatchDetailList, GetBatchStatementList |
| 收货(4) | GetReceiveGoodRecords, PurchaseReceiptOrderList, ReceiptOrderQcList, getPackingData(GET) |
| WMS(2) | WmsOrderList, WmsOrderDetail |
| 海外仓(2) | OverseaWarehouseMatchList, OverSeasStockDetail |
| 调拨/调整/盘点(3) | getStorageAdjustOrderList, getStorageAllocationList, checkGetOrderList/Detail |
| 入库/出库(4) | inboundgetOrders, outboundgetOrders, listInbound, matchSkuList |
| 其他(4) | getProcessOrderLists, ReturnList, removalInboundList, qualityInspectionOrderDetail |

### 客服（18个）
接口详见 `references/service.md`。

FeedbackList, FeedbackListMws, CustomerList, AfterSalesWorkOrderList, PerformanceNoticeList, PerformanceNoticeDetail, mailDetail, mailLists, review, reviewDetail, reviewLists(GET), reviewV2, feedbackDetail, feedbackLists, customerServiceCrmcustomerIndex, customerServiceRmaManageList, storePerformanceList, voiceOfBuyerList

### 物流（3个）
接口详见 `references/logistics.md`。

ChannelList, QueryHeadLogisticsProvider, transportMethodList

### 工具（4个）
接口详见 `references/tools.md`。

CompetitiveMonitorList, GetKeywordList, warningMessageGoodsList, warningMessageInventoryList

### VC（7个）
接口详见 `references/vc.md`。

vcOrderPageList, vcOrderPoDetail, vcOrderDfDetail, vcDeliverPageList, vcDeliverDetail, listingManageVcListingPageList, platformAuthVcSellerPageList

### 目标管理（2个）
接口详见 `references/targetmanage.md`。

StoreBatchSelect, UserBatchSelect

### 多平台广告（28个）
接口详见 `references/multiplatform-ads.md`。

| 分组 | 接口 |
|------|------|
| TikTok(9) | queryCommonAdvertiserList, queryGmvStoreList, queryTiktokAdGroupList/AdList/CampaignList, queryAdvertiserList, queryGmvAdvertiserReportList/CampaignReportList/ItemGroupReportList |
| Walmart(19) | queryAdGroupSvList, queryCampaignSpList, queryGroupSpList, queryPageTypeSPList, queryReportPageTypeSvList, reportAdGroupSbList, reportAdItemSbList/SpList/SvList, reportCampaignSbList/SvList, reportKeywordSbList/SpList/SvList, reportPageTypeSbList, reportPlatformSbList/SpList/SvList, reportSearchTrendsList |

### 多平台V2（33个）
接口详见 `references/multiplatform-v2.md`。

| 分组 | 接口 |
|------|------|
| 订单(3) | MultiPlatOrderV2, newPlatformOrderList |
| 店铺(1) | StoreInfoV2 |
| Listing(2) | PairListV2, addCargoGoodsList |
| 发货(4) | QueryShippingListV2, QueryShippingListPage, QueryWFSCargoPage/InventionPage |
| 平台订单(8) | AliexpressListV2, aliexpressList, eBayList, walmartList, TemuList, TikTokList, SheinList, ShopifyVariantList |
| 库存(6) | TemuCargo, CoupangStockList, FbsStockList, FbtStockList/Search, FullList, WayfairStockList |
| 利润(4) | profitReportMsku/Order/Seller/Sku |
| 其他(5) | WalmartPaymentQueryPage/Report, WalmartCommentList, LineList, addressReturnAddressList |

## 店铺列表（--list-stores）

调用 `GET /erp/sc/data/seller/lists` 接口，列出所有已授权亚马逊店铺。

> **注意**：此接口需要领星 ERP **全量权限**。如果 AppKey 仅授权了广告数据，会返回 403。
> 解决方法：在领星 ERP -> 开放接口中为该 AppKey 添加「基础数据」权限，或直接设置 `LINGXING_SID=<数字>` 跳过自动发现。

## 注意事项

- **SID 注入优先级**: `--params` 中显式传入 > `LINGXING_SID` 环境变量自动注入
- **sid vs profile_id**: 广告类接口 sid 和 profile_id 二选一必填；dspReportOrderList 仅支持 profile_id
- **GET 接口**: AccoutLists, AllMarketplace, ConceptSellerLists, GetProductTag, reviewLists, getPackingData 使用 GET 方法
- **分页模式**: 大多数接口用 offset/length；WmsOrderList 等用 page/page_size；FBMOrderList 用 page/length
- **响应格式**: `/cost/center/` 路径 API 数据在 `data.records` 或 `data.row_data` 下
- **日期参数**: 报表类接口用 `report_date`（单日）；订单/利润类用 `start_date`/`end_date`（日期范围）；多平台V2用 Unix 时间戳（秒）
- **Token 缓存**: token 自动缓存到 `/tmp/lingxing_token_*.json`，2小时有效
- **限流**: 大多数接口令牌桶容量为 10，ProductAnalysisList 和 mwsOrders 仅为 1
- **依赖**: 需要安装 `pycryptodome` 和 `requests`（`pip install pycryptodome requests`）

## 错误处理

| 场景 | 处理 |
|------|------|
| 环境变量未设置 | 脚本报错退出，提示设置 LINGXING_APP_ID/LINGXING_APP_SECRET |
| Token 获取失败 | 检查 AppID/AppSecret 是否正确，IP 是否在白名单内 |
| API 返回 code != 0 | 检查参数是否正确，参见错误信息 |
| --list-stores 返回 403 | AppKey 仅有广告权限；设置 LINGXING_SID 直接指定店铺 |
| 依赖未安装 | `pip install pycryptodome requests` |

<!-- LF_LARGE_RESPONSE_BLOCK -->
## Handling Large Responses

To avoid overflowing the agent context, persist the response to disk and extract only the fields you need:

```
python scripts/response_io.py run --script scripts/lingxing.py --out-dir <DIR> '<params>'
python scripts/response_io.py read <file> --fields "<paths>"   # or --path "<JMESPath>"
```

> Pick `--out-dir` outside any git working tree (e.g. `/tmp/...` on Unix, `%TEMP%/...` on Windows). Persisted responses may contain PII, pricing, or auth-sensitive data — do not commit them. Files are not auto-deleted; clean up when the task is done.

`run` writes the full response to a file and emits only a schema preview + file path. `read` projects specific fields, with `--limit/--offset` for slicing and `--format json|jsonl|csv|table` for output.

**When to prefer this pattern** — apply your judgment based on the response characteristics, e.g.:
- High field count per record, or fields you don't need
- Batch/paginated results (multiple items per call)
- Long-text fields (descriptions, reviews, HTML, time series)
- Output reused across later steps rather than consumed immediately

For small, single-use responses, calling the main script directly is fine.

⚠️ The preview is a truncated schema + sample, not the full data. Any field-level decision must read from the persisted file via `read`.
<!-- /LF_LARGE_RESPONSE_BLOCK -->

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

不消耗积分。
