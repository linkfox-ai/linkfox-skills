---
name: linkfox-lazada-store-marketing
description: 查询和管理已授权 Lazada 店铺的优惠券、包邮、组合促销与 Sponsored Max 广告，适用于核对活动、维护促销和查看广告表现。
---

# Lazada 店铺营销与广告

## 适用范围

### 适用

管理已授权 Lazada 店铺的促销和 Sponsored Max 广告。

**场景速查**

| 用户表达 | 场景 |
| --- | --- |
| 优惠券 | 读取活动、适用商品和优惠规则，按用户确认的范围维护优惠券。 |
| 包邮 | 读取配送选项、适用区域和活动信息，按已确认规则维护活动。 |
| 组合促销 | 查询折扣门槛和适用商品，按已确认的条件维护活动。 |
| Sponsored Max 广告 | 查看活动和报表，按已确认的预算、出价与状态执行变更。 |

### 边界

店铺授权由 `linkfox-lazada-store-auth` 处理。维护原价与可售库存使用 `linkfox-lazada-store-product`。广告操作范围为接口清单中的 Sponsored Max 能力。

## 接口清单

| 操作 | LinkFox 网关与 Lazada 上游 | 接口文档 | 对应脚本 | 性质 |
| --- | --- | --- | --- | --- |
| `listVouchers` | `POST /lazada/marketing` → `GET /promotion/vouchers/get` | [接口说明](references/api.md#接口listvouchers) | `scripts/marketing_api.py listVouchers` | 只读 |
| `getVoucher` | `POST /lazada/marketing` → `GET /promotion/voucher/get` | [接口说明](references/api.md#接口getvoucher) | `scripts/marketing_api.py getVoucher` | 只读 |
| `createVoucher` | `POST /lazada/marketing` → `POST /promotion/voucher/create` | [接口说明](references/api.md#接口createvoucher) | `scripts/marketing_api.py createVoucher` | 写入 |
| `updateVoucher` | `POST /lazada/marketing` → `POST /promotion/voucher/update` | [接口说明](references/api.md#接口updatevoucher) | `scripts/marketing_api.py updateVoucher` | 写入 |
| `activateVoucher` | `POST /lazada/marketing` → `POST /promotion/voucher/activate` | [接口说明](references/api.md#接口activatevoucher) | `scripts/marketing_api.py activateVoucher` | 写入 |
| `deactivateVoucher` | `POST /lazada/marketing` → `POST /promotion/voucher/deactivate` | [接口说明](references/api.md#接口deactivatevoucher) | `scripts/marketing_api.py deactivateVoucher` | 写入 |
| `listVoucherProducts` | `POST /lazada/marketing` → `GET /promotion/voucher/products/get` | [接口说明](references/api.md#接口listvoucherproducts) | `scripts/marketing_api.py listVoucherProducts` | 只读 |
| `addVoucherSkus` | `POST /lazada/marketing` → `POST /promotion/voucher/product/sku/add` | [接口说明](references/api.md#接口addvoucherskus) | `scripts/marketing_api.py addVoucherSkus` | 写入 |
| `removeVoucherSkus` | `POST /lazada/marketing` → `POST /promotion/voucher/product/sku/remove` | [接口说明](references/api.md#接口removevoucherskus) | `scripts/marketing_api.py removeVoucherSkus` | 写入 |
| `listFreeShipping` | `POST /lazada/marketing` → `GET /promotion/freeshippings/get` | [接口说明](references/api.md#接口listfreeshipping) | `scripts/marketing_api.py listFreeShipping` | 只读 |
| `getFreeShipping` | `POST /lazada/marketing` → `GET /promotion/freeshipping/get` | [接口说明](references/api.md#接口getfreeshipping) | `scripts/marketing_api.py getFreeShipping` | 只读 |
| `createFreeShipping` | `POST /lazada/marketing` → `POST /promotion/freeshipping/create` | [接口说明](references/api.md#接口createfreeshipping) | `scripts/marketing_api.py createFreeShipping` | 写入 |
| `updateFreeShipping` | `POST /lazada/marketing` → `POST /promotion/freeshipping/update` | [接口说明](references/api.md#接口updatefreeshipping) | `scripts/marketing_api.py updateFreeShipping` | 写入 |
| `activateFreeShipping` | `POST /lazada/marketing` → `POST /promotion/freeshipping/activate` | [接口说明](references/api.md#接口activatefreeshipping) | `scripts/marketing_api.py activateFreeShipping` | 写入 |
| `deactivateFreeShipping` | `POST /lazada/marketing` → `POST /promotion/freeshipping/deactivate` | [接口说明](references/api.md#接口deactivatefreeshipping) | `scripts/marketing_api.py deactivateFreeShipping` | 写入 |
| `listFreeShippingProducts` | `POST /lazada/marketing` → `GET /promotion/freeshipping/products/get` | [接口说明](references/api.md#接口listfreeshippingproducts) | `scripts/marketing_api.py listFreeShippingProducts` | 只读 |
| `addFreeShippingSkus` | `POST /lazada/marketing` → `POST /promotion/freeshipping/product/sku/add` | [接口说明](references/api.md#接口addfreeshippingskus) | `scripts/marketing_api.py addFreeShippingSkus` | 写入 |
| `removeFreeShippingSkus` | `POST /lazada/marketing` → `POST /promotion/freeshipping/product/sku/remove` | [接口说明](references/api.md#接口removefreeshippingskus) | `scripts/marketing_api.py removeFreeShippingSkus` | 写入 |
| `listFreeShippingRegions` | `POST /lazada/marketing` → `GET /promotion/freeshipping/regions/get` | [接口说明](references/api.md#接口listfreeshippingregions) | `scripts/marketing_api.py listFreeShippingRegions` | 只读 |
| `listShippingOptions` | `POST /lazada/marketing` → `GET /promotion/freeshipping/deliveryoptions/get` | [接口说明](references/api.md#接口listshippingoptions) | `scripts/marketing_api.py listShippingOptions` | 只读 |
| `listFlexiCombo` | `POST /lazada/marketing` → `GET /promotion/flexicombo/list` | [接口说明](references/api.md#接口listflexicombo) | `scripts/marketing_api.py listFlexiCombo` | 只读 |
| `getFlexiCombo` | `POST /lazada/marketing` → `GET /promotion/flexicombo/details` | [接口说明](references/api.md#接口getflexicombo) | `scripts/marketing_api.py getFlexiCombo` | 只读 |
| `createFlexiCombo` | `POST /lazada/marketing` → `POST /promotion/flexicombo/create` | [接口说明](references/api.md#接口createflexicombo) | `scripts/marketing_api.py createFlexiCombo` | 写入 |
| `updateFlexiCombo` | `POST /lazada/marketing` → `POST /promotion/flexicombo/update` | [接口说明](references/api.md#接口updateflexicombo) | `scripts/marketing_api.py updateFlexiCombo` | 写入 |
| `activateFlexiCombo` | `POST /lazada/marketing` → `POST /promotion/flexicombo/activate` | [接口说明](references/api.md#接口activateflexicombo) | `scripts/marketing_api.py activateFlexiCombo` | 写入 |
| `deactivateFlexiCombo` | `POST /lazada/marketing` → `POST /promotion/flexicombo/deactivate` | [接口说明](references/api.md#接口deactivateflexicombo) | `scripts/marketing_api.py deactivateFlexiCombo` | 写入 |
| `listFlexiComboProducts` | `POST /lazada/marketing` → `GET /promotion/flexicombo/products/list` | [接口说明](references/api.md#接口listflexicomboproducts) | `scripts/marketing_api.py listFlexiComboProducts` | 只读 |
| `addFlexiComboSkus` | `POST /lazada/marketing` → `POST /promotion/flexicombo/products/add` | [接口说明](references/api.md#接口addflexicomboskus) | `scripts/marketing_api.py addFlexiComboSkus` | 写入 |
| `removeFlexiComboSkus` | `POST /lazada/marketing` → `POST /promotion/flexicombo/products/delete` | [接口说明](references/api.md#接口removeflexicomboskus) | `scripts/marketing_api.py removeFlexiComboSkus` | 写入 |
| `listSponsoredMaxCampaigns` | `POST /lazada/marketing` → `GET /sponsor/solution/smax/searchSmaxCampaign` | [接口说明](references/api.md#接口listsponsoredmaxcampaigns) | `scripts/marketing_api.py listSponsoredMaxCampaigns` | 只读 |
| `getSponsoredMaxOverview` | `POST /lazada/marketing` → `GET /sponsor/solution/smax/report/getReportOverview` | [接口说明](references/api.md#接口getsponsoredmaxoverview) | `scripts/marketing_api.py getSponsoredMaxOverview` | 只读 |
| `getSponsoredMaxMetric` | `POST /lazada/marketing` → `GET /sponsor/solution/smax/report/getReportOverviewMetric` | [接口说明](references/api.md#接口getsponsoredmaxmetric) | `scripts/marketing_api.py getSponsoredMaxMetric` | 只读 |
| `createSponsoredMaxCampaign` | `POST /lazada/marketing` → `POST /sponsor/solution/smax/addSMaxAASolution` | [接口说明](references/api.md#接口createsponsoredmaxcampaign) | `scripts/marketing_api.py createSponsoredMaxCampaign` | 写入 |
| `updateSponsoredMaxCampaign` | `POST /lazada/marketing` → `POST /sponsor/solution/smax/updateSmaxCampaign` | [接口说明](references/api.md#接口updatesponsoredmaxcampaign) | `scripts/marketing_api.py updateSponsoredMaxCampaign` | 写入 |
| `setSponsoredMaxCampaignStatus` | `POST /lazada/marketing` → `POST /sponsor/solution/smax/updateSmaxStatusWithoutAd` | [接口说明](references/api.md#接口setsponsoredmaxcampaignstatus) | `scripts/marketing_api.py setSponsoredMaxCampaignStatus` | 写入 |
| 查询写入状态 `operationStatus` | `POST /lazada/operationStatus` | [写入与续查](references/api.md#接口查询写入状态operationstatus) | `scripts/marketing_api.py operationStatus` | 只读 |

## 前置条件

从授权 Skill 确认目标店铺、站点和 `connectionId`。按活动类型检查应用权限。核对目标活动、SKU、日期、币种、折扣条件或广告预算后再提交变更。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md` 及接口清单中的对应文档。
- **脚本调用（推荐）**：使用 Python 3.9+，`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **业务操作入口**：`python scripts/marketing_api.py <操作> '<JSON 参数>' [--inline] [--no-cache]`，也可用 `--params-file <UTF-8 JSON 文件>` 提供参数。
- **成本约束**：本技能不消耗算力，业务调用通过输出预检后实时请求一次，不启用 24 小时响应缓存。按用户任务范围分页或查询原申请／写记录，不因失败或空结果自动扩大范围或重放写入。

本地输入、默认值、构参映射及保存结果见 [脚本使用说明](references/script-usage.md)。

### 输出策略

- 始终保存可保存的完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/<技能名>-<操作>-<时间>.json`。会话优先取 `SESSION_ID`。输出或会话元数据不可写时，在发请求前报错。
- 响应体不超过 8000 字节：保存后，将完整脱敏 JSON 打印到标准输出。
- 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、可用诊断、最大列表字段的长度和最多前三项样本。
- 添加 `--inline` 可强制全量打印可保存数据，同时仍保存文件。
- HTTP、网关或响应格式错误时，脚本保存可用的脱敏诊断并以非零状态退出。

先通过摘要判断数据是否足够。以 `Saved full response:` 后的实际文件路径为准；需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 操作流程

1. 查看当前活动、状态、适用 SKU 和规则。包邮活动按店铺读取区域及配送选项。广告报表先确定日期范围和报表指标。
2. 写入前向用户列明店铺、站点、活动或 SKU、实际变更及折扣或预算影响。取得明确授权后生成 UUID 并提交对应操作。
3. 保存原写入 UUID。超时、部分失败或状态不明时，查询原 `operationStatus` 并核对平台状态。广告或促销的业务生效以平台显示和后续查询为准。

### 算力消耗

本 Skill 的营销查询、写入及写入状态查询均为 0 算力/次。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。广告预算属于店铺广告成本。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`；先结合接口诊断确认是 LinkFox 用户认证或计费问题。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

Lazada 店铺授权失效、卖家未验证、应用权限或代理限制按接口参考处理。短信、登录和算力订单按用户已授权范围执行；订单结果不明先核对原订单。可选二维码依赖为 qrcode 和 Pillow，未安装时使用支付链接，不静默安装。

### 约束与建议

- 按店铺、站点、活动 ID、币种和时间范围展示结果。报表缺失字段保留为未知。
- 广告预算、出价与活动状态分别确认。查询报表与修改广告属于不同操作。

## 使用示例

查询当前店铺的领取型优惠券。替换店铺连接并按需分页。

```sh
python scripts/marketing_api.py listVouchers '{"connectionId":"11111111-1111-4111-8111-111111111111","params":{"voucher_type":"COLLECTIBLE_VOUCHER","cur_page":1}}'
```

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引整理脱敏反馈，不要打断用户当前流程。仅在用户授权发送后提交。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
