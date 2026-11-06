---
name: linkfox-temu-price-global
description: 管理 Temu 全球区（非美国、欧洲）的商品价格与供货价，支持定价单查询、推荐供货价、基础价估算、SKU 供货价列表和批量改价，并支持加签资源下载。适用于全球站定价评估、供货价核对与价格维护；美国站、欧洲站、商品信息编辑、库存和订单履约使用对应技能。
---
# Temu 全球站价格与供货价管理

## 适用范围

### 适用

管理 Temu 全球站商品的定价单、推荐价与 SKU 供货价。用户希望查看平台报价、估算供货价或维护已授权店铺商品价格时，使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看全球站商品的定价单或报价 | 查询定价单与价格审核情况。 |
| 平台建议这些商品卖什么供货价 | 查询已有商品的推荐供货价。 |
| 按类目、规格和站外价估算基础价 | 获取发品或改价前的估算结果。 |
| 核对这些 SKU 的当前供货价 | 查询 SKU 供货价列表。 |
| 按指定金额批量调整 SKU 基础价 | 提交改价并核对逐 SKU 结果。 |

### 边界

美国站与欧洲站价格分别使用 `linkfox-temu-price-us`、`linkfox-temu-price-eu`；商品列表、详情、编辑、库存及上下架使用 `linkfox-temu-manage-product-global`。订单查询、发货与物流使用 `linkfox-temu-order-global`。发品侧半托管供货价查询使用 `linkfox-temu-add-product-us`，与本技能本地仓价格操作区分使用。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 推荐基础价/供货价估算（`temu.local.goods.baseprice.recommend`） | POST `/temu/proxy` → path：`/openapi/router`，Body `type=temu.local.goods.baseprice.recommend` | [接口定义](references/apis/temu-local-goods-baseprice-recommend.md) | `scripts/global_price_baseprice_recommend.py` | 推荐基础价/供货价估算。 |
| 推荐供货价查询（`temu.local.goods.recommendedprice.query`） | POST `/temu/proxy` → path：`/openapi/router`，Body `type=temu.local.goods.recommendedprice.query` | [接口定义](references/apis/temu-local-goods-recommendedprice-query.md) | `scripts/global_price_recommendedprice_query.py` | 推荐供货价查询。 |
| 定价单列表查询（`bg.local.goods.priceorder.query`） | POST `/temu/proxy` → path：`/openapi/router`，Body `type=bg.local.goods.priceorder.query` | [接口定义](references/apis/bg-local-goods-priceorder-query.md) | `scripts/global_price_priceorder_query.py` | 定价单列表查询。 |
| 批量修改 SKU 基础价（`bg.local.goods.priceorder.change.sku.price`） | POST `/temu/proxy` → path：`/openapi/router`，Body `type=bg.local.goods.priceorder.change.sku.price` | [接口定义](references/apis/bg-local-goods-priceorder-change-sku-price.md) | `scripts/global_price_priceorder_change_sku_price.py` | 批量修改 SKU 基础价。 |
| SKU 供货价列表查询（`bg.local.goods.sku.list.price.query`） | POST `/temu/proxy` → path：`/openapi/router`，Body `type=bg.local.goods.sku.list.price.query` | [接口定义](references/apis/bg-local-goods-sku-list-price-query.md) | `scripts/global_price_sku_list_price_query.py` | SKU 供货价列表查询。 |
| 加签文件下载 | POST `/temu/fileDownload` | [接口定义](references/api.md#接口加签文件下载) | `scripts/temu_global_file_download.py` / `scripts/temu_file_download.py` | 获取 Temu 加签资源。 |

## 前置条件

确认目标店铺、区域、商品与操作范围，准备 LinkFox 用户密钥和 Temu 店铺授权。Temu 授权须由用户在卖家后台手动完成，步骤及本地令牌保存见 [授权说明](references/access-token.md) 和 [授权流程](references/authorization-flow.md)。

业务参数、认证兼容与脚本选项见 [接口说明](references/api.md)，按需阅读清单中的独立接口文档。`scripts/temu_global_proxy.py` 提供全球站通用转发，`scripts/temu_proxy.py` 保留多站点兼容入口；二者复用已列端点，不增加新的定价操作。

## 价格管理流程

1. 需要商品标识时，先由商品管理技能的列表、详情或 `spec.info.get` 取得 `goodsId`、`catId` 和 `specIdList`。
2. 根据用户需求查询定价单、已有商品推荐供货价或 SKU 当前供货价；需要发品或改价前估算时，再查询推荐基础价。
3. 用户要求调价时，核对目标店铺、商品、SKU、金额与币种，按已明确范围提交批量改价。
4. 展示成功与失败的 SKU 及原因，再通过定价单查询核对 `priceAuditList` 的审核情况和 `supplierPrice` 最终供货价；不得为确认结果而重复提交改价。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次。本技能不启用业务响应缓存，可按需读取同一任务已保存的响应。失败或空结果时，不得自动更换参数、翻页或连续试探；需要继续查询时，先说明原因和调用范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-temu-price-global-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
- 添加 `--inline` 可强制全量打印到标准输出，同时仍保存文件。

先通过摘要判断数据是否足够。需要具体字段时，优先使用 `jq` 或 `ConvertFrom-Json` 从保存的 JSON 文件按需提取，避免将整份响应载入上下文。

## 执行规则

### 算力消耗预估

不消耗算力 （限时）。

**声明**：算力消耗以实际扣除为准；如因需要调整算力消耗标准，恕不另行通知。最终解释权归 LinkFox 官方所有。

### 解决认证和算力问题

出现以下情况时，按 `references/onboarding.md` 的指引处理：

- 未配置接口密钥：`LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 均为空。
- HTTP 状态码为 `401` 或 `402`。
- 响应提示算力或余额不足、计费不足、配额超限、套餐到期或需要充值。英文错误消息也按其含义判断。

### 约束与建议

- **区分价格含义**：平台推荐价、目标新价、原供货价与最终供货价分别展示，避免将建议值当作已生效价格。
- **清晰展示数据**：注明店铺、区域与返回范围，用表格展示商品、SKU、币种、价格、审核状态和失败原因；状态无已知说明时保留原值，不推断已通过审核。
- **解释写入结果**：整体请求成功不代表所有 SKU 成功，也不代表最终价格已生效；结合逐 SKU 结果与后续定价单说明。
- **响应缓存**：业务脚本关闭响应缓存，具体约定及通用调用器行为见 [脚本运行约定](references/api.md#脚本运行约定)。
- **按需读取文档**：完整嵌套字段、价格单位、白名单、分页及其他限制见各接口定义；Partner 菜单与文档索引见 [全球站目录](references/partner-global-catalog.md)。

## 使用示例

### 查询与核对价格

用户：查看全球站这些商品的推荐供货价，再核对指定 SKU 的当前供货价。

确认店铺与商品范围，分别查询推荐价与当前价，按 SKU 对照展示金额和币种。

### 调整基础价并核对结果

用户：把指定商品的两个 SKU 按我提供的金额调价。

核对商品与 SKU，按用户指定的币种和金额提交，展示逐 SKU 结果，再查询定价单核对审核与最终价格。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
