# 市场与业务限制

这些条件来自 Amazon Fulfillment Inbound 官方概述、operation 描述和 India 工作流。能否调用最终仍受卖家资格、目标 FC、商品可入库性和 Amazon 实时返回影响。

| 能力 | 限制 |
|---|---|
| v2024 创建入库 shipment | Amazon 当前概述声明支持除 Brazil 外的 Amazon stores |
| Self-ship appointment | `MX`、`BR`、`EG`、`SA`、`AE`、`IN` |
| Item compliance | `listItemComplianceDetails` / `updateItemComplianceDetails` 仅用于 India compliance，IN marketplace ID 为 `A21TJRUUN4KGV` |
| Custom placement | India 工作流可在 `generatePlacementOptions.requestBody.customPlacement` 中指定商品/数量与 FC |
| Delivery challan | 仅 India marketplace 的 Partnered Carrier Program（PCP）shipment |
| Pack Later | 仅 pallet delivery（LTL/FTL）；可用 Amazon Partnered 或自有承运人 |
| Amazon-recommended packing | ES、UK、FR、DE、IT；适用于单件 parcel 小于 15kg 的 SPD，不支持 LTL/FTL |
| US prep/label | 卖家必须在发往 Amazon 履约网络前完成商品预处理和贴标 |

## 预处理信息

- 必须先调用 `setPrepDetails`，才能通过 `listPrepDetails` 取回该 Skill 设置的 prep details。
- 在 Seller Central 中填写的 prep details 不会由 `listPrepDetails` 返回。
- `listPrepDetails` 和 `listItemComplianceDetails` 的 `mskus` 是重复 query key，最多 100 个。MSKU 中 `%`、`+`、`,` 要按 Amazon 要求双重 percent encode。
- `listPrepDetails` 返回的 `prepOwnerConstraint` 和 `labelOwnersConstraint` 决定 `createInboundPlan` 可用的 owner；两者为空时可选 `AMAZON` 或 `SELLER`。`allOwnersConstraint=MUST_MATCH` 时 prep/label owner 必须一致。
- `prepCategory=FC_PROVIDED` 表示 Amazon 已固定该类别，不可修改。如果在创建 plan 后又用 `setPrepDetails` 改了 category，当前 plan 仍使用 `listInboundPlanItems` / `listInboundPlanBoxes` 返回的原 prep/label owner；新设置仅影响后续 plan。
- `ITEM_NO_PREP` 不代表可以省略 prep/label owner；`prepCategory=NONE` 也可能仍需 label owner，应以 `listPrepDetails` 返回的 owner 约束为准。

## 刊登前置条件

- 入库 MSKU 必须已建立 Amazon listing 并设为 FBA fulfillment channel；不在本 Skill 内自动创建 listing 或将 FBM 转换为 FBA。
- 电池、含电池或可能属于危险品的商品，必须先在 listing 中补齐 battery/dangerous-goods 信息，否则转为 FBA 会失败。
- 官方 listing channel code 按区域使用 `AMAZON_NA`、`AMAZON_EU`、`AMAZON_IN` 或 `AMAZON_JP`；这属于 Listings Items / Feeds API，不应拼到 Fulfillment Inbound 请求中。

## 自配送与 India

- Self-ship 四个 operation 的 endpoint 虽列出 BR，不能将此推导为 `createInboundPlan` 在 BR 可用；两项能力限制应独立校验。
- 生成 self-ship slots 前，先用 `getShipment` 确认已存在 `amazonReferenceId`。
- 不传 `desiredStartDate` / `desiredEndDate` 时，Amazon 默认生成未来 42 天的可用 slot。
- `scheduleSelfShipAppointment` 用于重新预约时，`reasonComment` 必须填写。
- India 店铺业务除 Amazon Fulfillment role 外，官方流程还要求 Product Listing role 以及已建立的 listing。

## 时效性

- Packing、placement、transportation、delivery window、content-update preview 和 appointment slot 均可能带有 `validUntil`、`expiration` 或类似字段。确认前必须重新检查。
- 重新生成 option 后，之前的 option ID 不再可信。
- 在 placement / transportation 尚未确认时切换到 Send to Amazon，STA 会重新生成 options，API 中之前的 options 会被丢弃。

## 官方来源

- [Fulfillment Inbound API](https://developer-docs.amazon.com/sp-api/docs/fulfillment-inbound-api)
- [Ship Inventory to Amazon Fulfillment Centers in India](https://developer-docs.amazon.com/sp-api/docs/ship-inventory-to-india-fc)
- [Prep details 发布说明](https://developer-docs.amazon.com/sp-api/changelog/update-fulfillment-inbound-api-v2024-03-20-now-supports-preparation-details)
