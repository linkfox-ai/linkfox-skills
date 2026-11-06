---
name: linkfox-shopee-store-merchant
description: 查询已授权 Shopee（虾皮）跨境商户的资料、下属店铺、仓库及位置、可使用仓库的店铺和预付账户。适用于核对商户区域与币种、授权期限，以及 CNSC/CBSC 跨境卖家的商户资源；不适用于店铺授权、单店资料、商品刊登或订单管理。
---
# Shopee 商户信息与资源查询

## 适用范围

### 适用

查询已授权 Shopee 跨境商户的资料及商户资源。用户提到商户、跨境卖家、CNSC/CBSC、商户下属店铺、商户仓库或预付账户时使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
| -------- | -------- |
| 查我的商户名称、区域和币种 | 商户资料：核对身份、授权期限及跨境类型。 |
| 看这个商户绑定了哪些店铺 | 下属店铺：展示店铺与分页情况。 |
| 查商户仓库、仓库位置及适用店铺 | 仓库资源：按任务选择对应查询。 |
| 看商户的预付账户 | 账户信息：展示实际返回的预付账户资料。 |

### 边界

授权与选店依赖 `linkfox-shopee-store-auth`；单店资料使用 `linkfox-shopee-store-shop`，全球商品使用 `linkfox-shopee-store-global-product`，单店刊登使用 `linkfox-shopee-store-product`，订单使用 `linkfox-shopee-store-orders`。Public 模块（如 `get_merchants_by_partner`）不属于本技能。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 查询商户资料（`get_merchant_info`） | POST `/shopee/developerProxy` → GET path：`api/v2/merchant/get_merchant_info` | [references/apis/get-merchant-info.md](references/apis/get-merchant-info.md) | `scripts/get_merchant_info.py` | 查询商户资料。 |
| 查询商户下属店铺（`get_shop_list_by_merchant`） | POST `/shopee/developerProxy` → GET path：`api/v2/merchant/get_shop_list_by_merchant` | [references/apis/get-shop-list-by-merchant.md](references/apis/get-shop-list-by-merchant.md) | `scripts/get_shop_list_by_merchant.py` | 查询商户下属店铺。 |
| 查询商户仓库位置（`get_merchant_warehouse_location_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/merchant/get_merchant_warehouse_location_list` | [references/apis/get-merchant-warehouse-location-list.md](references/apis/get-merchant-warehouse-location-list.md) | `scripts/get_merchant_warehouse_location_list.py` | 查询商户仓库位置。 |
| 查询商户仓库列表（`get_merchant_warehouse_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/merchant/get_merchant_warehouse_list` | [references/apis/get-merchant-warehouse-list.md](references/apis/get-merchant-warehouse-list.md) | `scripts/get_merchant_warehouse_list.py` | 查询商户仓库列表。 |
| 查询可使用仓库的店铺（`get_warehouse_eligible_shop_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/merchant/get_warehouse_eligible_shop_list` | [references/apis/get-warehouse-eligible-shop-list.md](references/apis/get-warehouse-eligible-shop-list.md) | `scripts/get_warehouse_eligible_shop_list.py` | 查询可使用仓库的店铺。 |
| 查询商户预付账户（`get_merchant_prepaid_account_list`） | POST `/shopee/developerProxy` → GET path：`api/v2/merchant/get_merchant_prepaid_account_list` | [references/apis/get-merchant-prepaid-account-list.md](references/apis/get-merchant-prepaid-account-list.md) | `scripts/get_merchant_prepaid_account_list.py` | 查询商户预付账户。 |
| 查询已授权店铺或商户状态（兼容辅助接口） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](references/apis/store-tokens.md) | `scripts/_shopee_merchant_common.py` 的 `resolve_store_tokens` | 返回授权状态；常规 Merchant 查询不调用。 |

通用命令入口为 `scripts/merchant_api.py`；具体选项与兼容约定见 [references/api.md](references/api.md)。

## 前置条件

先完成商户授权并取得目标 `merchantId`；Merchant 查询应明确传入该值，网关不会仅根据 `shopId` 自动补出上游 `merchant_id`。运行 `python scripts/check_auth_dependency.py` 检查 `linkfox-shopee-store-auth`；缺失时先安装并完成授权，不在本技能内另行实现授权或令牌逻辑。依赖检测与标识选择规则见 [references/api.md](references/api.md)。

## 查询流程

1. 通过授权技能确定目标商户，并检查本地认证依赖。
2. 查询商户及下属店铺时，先读取商户资料，核对区域、币种和授权期限，再按用户需求读取下属店铺；分页参数见对应接口定义。
3. 查询仓库及账户时，仅选择任务需要的仓库列表、仓库位置、可用店铺或预付账户操作。
4. 按接口定义检查网关与上游结果后提取数据，展示本次范围；失败或空结果不自动连续试探。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：本工具不消耗算力 （限时）。同一会话、同一参数组合默认只调用一次，优先复用已保存的响应。业务封装始终禁用响应缓存；公共调用器可能创建空 `.cache` 目录。失败或空结果时，不得自动更换商户、翻页或修改参数连续试探；需要继续查询时，按用户明确的任务范围执行。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-merchant-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8 KB：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8 KB：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的顶层状态与计数字段（如 `total`、`costToken`）、非空最大列表字段的长度和前 3 条样本。
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

- **商户与店铺分工**：Merchant 面向商户级资源，主要用于跨境卖家；单店资料和全球商品由对应技能处理。
- **转发链路**：`developerProxy` 根据已授权标识解析令牌，再经紫鸟 `shopee-proxy` 转发至 Shopee API；不在当前技能内刷新或创建授权。
- **清晰展示数据**：商户资料优先展示名称、区域、币种和授权期限；店铺、仓库、预付账户用表格展示实际返回字段，并标明目标商户。
- **区分各层结果**：LinkFox 请求成功不代表 Shopee 业务成功；按对应接口的响应码规则解释错误，保留原始返回，不补造缺失字段。
- **说明分页情况**：展示本次店铺列表和是否还有后续数据；继续读取遵守调用约束。
- **按需读取文件**：先看摘要，再从落盘 JSON 提取任务所需字段。

## 使用示例

### 核对商户并查看下属店铺

用户：查这个商户的区域、币种，再看看绑定了哪些店铺。

先通过授权技能定位商户，读取资料，再读取下属店铺，展示实际返回的授权期限和分页情况。

### 查询仓库资源

用户：查这个商户的仓库位置，以及哪些店铺能使用仓库。

按目标商户分别读取仓库位置和可用店铺，按返回数据展示关联关系。

### 查看预付账户

用户：看看这个跨境商户的预付账户。

核对商户后查询账户资料，解释实际返回的账户信息与错误。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
