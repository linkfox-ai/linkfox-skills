---
name: linkfox-lazada-store-marketing
description: 查询和管理已授权 Lazada 店铺的优惠券、包邮、组合促销与 Sponsored Max 广告，适用于核对活动、维护促销和查看广告表现。
---

# Lazada 店铺营销与广告

## 适用范围

### 适用

管理已授权 Lazada 店铺的促销和 Sponsored Max 广告。

| 用户表达 | 场景 |
| --- | --- |
| 优惠券 | 读取活动、适用商品和优惠规则，按用户确认的范围维护优惠券。 |
| 包邮 | 读取配送选项、适用区域和活动信息，按已确认规则维护活动。 |
| 组合促销 | 查询折扣门槛和适用商品，按已确认的条件维护活动。 |
| Sponsored Max 广告 | 查看活动和报表，按已确认的预算、出价与状态执行变更。 |

### 边界

店铺授权由 `linkfox-lazada-store-auth` 处理。维护原价与可售库存使用 `linkfox-lazada-store-product`。广告操作范围为接口清单中的 Sponsored Max 能力。

## 接口清单

| 操作 | LinkFox 网关与 Lazada 上游 | 对应脚本 | 接口文档 | 性质 |
| --- | --- | --- | --- | --- |
| `listVouchers` | `POST /lazada/marketing` → `GET /promotion/vouchers/get` | `scripts/marketing_api.py listVouchers` | [接口说明](references/api.md#listvouchers) | 只读 |
| `getVoucher` | `POST /lazada/marketing` → `GET /promotion/voucher/get` | `scripts/marketing_api.py getVoucher` | [接口说明](references/api.md#getvoucher) | 只读 |
| `createVoucher` | `POST /lazada/marketing` → `POST /promotion/voucher/create` | `scripts/marketing_api.py createVoucher` | [接口说明](references/api.md#createvoucher) | 写入 |
| `updateVoucher` | `POST /lazada/marketing` → `POST /promotion/voucher/update` | `scripts/marketing_api.py updateVoucher` | [接口说明](references/api.md#updatevoucher) | 写入 |
| `activateVoucher` | `POST /lazada/marketing` → `POST /promotion/voucher/activate` | `scripts/marketing_api.py activateVoucher` | [接口说明](references/api.md#activatevoucher) | 写入 |
| `deactivateVoucher` | `POST /lazada/marketing` → `POST /promotion/voucher/deactivate` | `scripts/marketing_api.py deactivateVoucher` | [接口说明](references/api.md#deactivatevoucher) | 写入 |
| `listVoucherProducts` | `POST /lazada/marketing` → `GET /promotion/voucher/products/get` | `scripts/marketing_api.py listVoucherProducts` | [接口说明](references/api.md#listvoucherproducts) | 只读 |
| `addVoucherSkus` | `POST /lazada/marketing` → `POST /promotion/voucher/product/sku/add` | `scripts/marketing_api.py addVoucherSkus` | [接口说明](references/api.md#addvoucherskus) | 写入 |
| `removeVoucherSkus` | `POST /lazada/marketing` → `POST /promotion/voucher/product/sku/remove` | `scripts/marketing_api.py removeVoucherSkus` | [接口说明](references/api.md#removevoucherskus) | 写入 |
| `listFreeShipping` | `POST /lazada/marketing` → `GET /promotion/freeshippings/get` | `scripts/marketing_api.py listFreeShipping` | [接口说明](references/api.md#listfreeshipping) | 只读 |
| `getFreeShipping` | `POST /lazada/marketing` → `GET /promotion/freeshipping/get` | `scripts/marketing_api.py getFreeShipping` | [接口说明](references/api.md#getfreeshipping) | 只读 |
| `createFreeShipping` | `POST /lazada/marketing` → `POST /promotion/freeshipping/create` | `scripts/marketing_api.py createFreeShipping` | [接口说明](references/api.md#createfreeshipping) | 写入 |
| `updateFreeShipping` | `POST /lazada/marketing` → `POST /promotion/freeshipping/update` | `scripts/marketing_api.py updateFreeShipping` | [接口说明](references/api.md#updatefreeshipping) | 写入 |
| `activateFreeShipping` | `POST /lazada/marketing` → `POST /promotion/freeshipping/activate` | `scripts/marketing_api.py activateFreeShipping` | [接口说明](references/api.md#activatefreeshipping) | 写入 |
| `deactivateFreeShipping` | `POST /lazada/marketing` → `POST /promotion/freeshipping/deactivate` | `scripts/marketing_api.py deactivateFreeShipping` | [接口说明](references/api.md#deactivatefreeshipping) | 写入 |
| `listFreeShippingProducts` | `POST /lazada/marketing` → `GET /promotion/freeshipping/products/get` | `scripts/marketing_api.py listFreeShippingProducts` | [接口说明](references/api.md#listfreeshippingproducts) | 只读 |
| `addFreeShippingSkus` | `POST /lazada/marketing` → `POST /promotion/freeshipping/product/sku/add` | `scripts/marketing_api.py addFreeShippingSkus` | [接口说明](references/api.md#addfreeshippingskus) | 写入 |
| `removeFreeShippingSkus` | `POST /lazada/marketing` → `POST /promotion/freeshipping/product/sku/remove` | `scripts/marketing_api.py removeFreeShippingSkus` | [接口说明](references/api.md#removefreeshippingskus) | 写入 |
| `listFreeShippingRegions` | `POST /lazada/marketing` → `GET /promotion/freeshipping/regions/get` | `scripts/marketing_api.py listFreeShippingRegions` | [接口说明](references/api.md#listfreeshippingregions) | 只读 |
| `listShippingOptions` | `POST /lazada/marketing` → `GET /promotion/freeshipping/deliveryoptions/get` | `scripts/marketing_api.py listShippingOptions` | [接口说明](references/api.md#listshippingoptions) | 只读 |
| `listFlexiCombo` | `POST /lazada/marketing` → `GET /promotion/flexicombo/list` | `scripts/marketing_api.py listFlexiCombo` | [接口说明](references/api.md#listflexicombo) | 只读 |
| `getFlexiCombo` | `POST /lazada/marketing` → `GET /promotion/flexicombo/details` | `scripts/marketing_api.py getFlexiCombo` | [接口说明](references/api.md#getflexicombo) | 只读 |
| `createFlexiCombo` | `POST /lazada/marketing` → `POST /promotion/flexicombo/create` | `scripts/marketing_api.py createFlexiCombo` | [接口说明](references/api.md#createflexicombo) | 写入 |
| `updateFlexiCombo` | `POST /lazada/marketing` → `POST /promotion/flexicombo/update` | `scripts/marketing_api.py updateFlexiCombo` | [接口说明](references/api.md#updateflexicombo) | 写入 |
| `activateFlexiCombo` | `POST /lazada/marketing` → `POST /promotion/flexicombo/activate` | `scripts/marketing_api.py activateFlexiCombo` | [接口说明](references/api.md#activateflexicombo) | 写入 |
| `deactivateFlexiCombo` | `POST /lazada/marketing` → `POST /promotion/flexicombo/deactivate` | `scripts/marketing_api.py deactivateFlexiCombo` | [接口说明](references/api.md#deactivateflexicombo) | 写入 |
| `listFlexiComboProducts` | `POST /lazada/marketing` → `GET /promotion/flexicombo/products/list` | `scripts/marketing_api.py listFlexiComboProducts` | [接口说明](references/api.md#listflexicomboproducts) | 只读 |
| `addFlexiComboSkus` | `POST /lazada/marketing` → `POST /promotion/flexicombo/products/add` | `scripts/marketing_api.py addFlexiComboSkus` | [接口说明](references/api.md#addflexicomboskus) | 写入 |
| `removeFlexiComboSkus` | `POST /lazada/marketing` → `POST /promotion/flexicombo/products/delete` | `scripts/marketing_api.py removeFlexiComboSkus` | [接口说明](references/api.md#removeflexicomboskus) | 写入 |
| `listSponsoredMaxCampaigns` | `POST /lazada/marketing` → `GET /sponsor/solution/smax/searchSmaxCampaign` | `scripts/marketing_api.py listSponsoredMaxCampaigns` | [接口说明](references/api.md#listsponsoredmaxcampaigns) | 只读 |
| `getSponsoredMaxOverview` | `POST /lazada/marketing` → `GET /sponsor/solution/smax/report/getReportOverview` | `scripts/marketing_api.py getSponsoredMaxOverview` | [接口说明](references/api.md#getsponsoredmaxoverview) | 只读 |
| `getSponsoredMaxMetric` | `POST /lazada/marketing` → `GET /sponsor/solution/smax/report/getReportOverviewMetric` | `scripts/marketing_api.py getSponsoredMaxMetric` | [接口说明](references/api.md#getsponsoredmaxmetric) | 只读 |
| `createSponsoredMaxCampaign` | `POST /lazada/marketing` → `POST /sponsor/solution/smax/addSMaxAASolution` | `scripts/marketing_api.py createSponsoredMaxCampaign` | [接口说明](references/api.md#createsponsoredmaxcampaign) | 写入 |
| `updateSponsoredMaxCampaign` | `POST /lazada/marketing` → `POST /sponsor/solution/smax/updateSmaxCampaign` | `scripts/marketing_api.py updateSponsoredMaxCampaign` | [接口说明](references/api.md#updatesponsoredmaxcampaign) | 写入 |
| `setSponsoredMaxCampaignStatus` | `POST /lazada/marketing` → `POST /sponsor/solution/smax/updateSmaxStatusWithoutAd` | `scripts/marketing_api.py setSponsoredMaxCampaignStatus` | [接口说明](references/api.md#setsponsoredmaxcampaignstatus) | 写入 |
| 查询写入状态 `operationStatus` | `POST /lazada/operationStatus` | `scripts/marketing_api.py operationStatus` | [写入与续查](references/api.md#写入与续查) | 只读 |

## 前置条件

从授权 Skill 确认目标店铺、站点和 `connectionId`。按活动类型检查应用权限。核对目标活动、SKU、日期、币种、折扣条件或广告预算后再提交变更。

## 执行方式

- **脚本调用（推荐）**。使用 Python 3.9+，运行 `python scripts/marketing_api.py <操作> '<JSON 参数>' [--inline] [--no-cache]`。也可用 `--params-file <UTF-8 JSON 文件>` 提供参数。
- **接口调用**。请求字段、响应和状态恢复见 [接口参考](references/api.md)。
- **调用约束**。业务脚本通过预检后发起一次实时请求。按用户指定的条件分页，空结果或失败时说明实际情况。

### 输出策略

- 可保存的结果写入 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<技能名>-<操作>-<时间>.json`。会话优先取 `SESSION_ID`。输出或会话元数据不可写时，在发请求前报错。
- 成功结果不超过 8000 字节时，保存后打印完整 JSON。更大的结果打印摘要，主要列表最多展示前三项。`--inline` 可打印全部可保存数据，同时仍保存文件。
- HTTP、网关或响应格式错误时，脚本保存可用的脱敏诊断并以非零状态退出。
- 以 `Saved full response:` 后的实际文件路径为准。需要更多字段时，从保存的 JSON 按需提取。

## 执行规则

### 操作流程

1. 查看当前活动、状态、适用 SKU 和规则。包邮活动按店铺读取区域及配送选项。广告报表先确定日期范围和报表指标。
2. 写入前向用户列明店铺、站点、活动或 SKU、实际变更及折扣或预算影响。取得明确授权后生成 UUID 并提交对应操作。
3. 保存原写入 UUID。超时、部分失败或状态不明时，查询原 `operationStatus` 并核对平台状态。广告或促销的业务生效以平台显示和后续查询为准。

### 算力消耗

本 Skill 的营销查询、写入及写入状态查询均为 0 算力/次。算力消耗以网关实际计费配置为准。广告预算属于店铺广告成本。

### 解决认证和算力问题

LinkFox Key 未配置或确认无效时，按 [认证和算力指引](references/onboarding.md) 检查。活动或广告权限问题按 [错误处理](references/api.md#错误处理) 核对店铺、应用和站点。

发送短信或使用验证码登录前先取得用户同意。创建算力订单前确认套餐、金额和支付方式。下单结果不明时先核对已有订单。安装了 qrcode 和 Pillow 时可生成二维码图片，也可使用支付链接。

### 约束与建议

- 按店铺、站点、活动 ID、币种和时间范围展示结果。报表缺失字段保留为未知。
- 广告预算、出价与活动状态分别确认。查询报表与修改广告属于不同操作。

## 使用示例

查询当前店铺的领取型优惠券。替换店铺连接并按需分页。

```sh
python scripts/marketing_api.py listVouchers '{"connectionId":"11111111-1111-4111-8111-111111111111","params":{"voucher_type":"COLLECTIBLE_VOUCHER","cur_page":1}}'
```

## 使用反馈

技能出现错误、指引不清或结果不符合预期时，可按 [Feedback](references/api.md#feedback) 整理脱敏摘要。用户授权发送后再提交。

---

更多跨境电商技能见 [LinkFox Skill](https://skill.linkfox.com/)。
