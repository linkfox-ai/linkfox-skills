---
name: linkfox-shopee-store-shop
description: 查询和维护已授权 Shopee（虾皮）店铺的基本信息、店名、标志、描述、仓库地址、卖家通知、授权品牌、巴西入驻资料和假期模式。适用于店铺资料核对、设置维护及营业状态调整；不适用于店铺授权、商品刊登、订单、物流、售后、商户信息、店铺分类或账户健康管理。
---
# Shopee 店铺信息与设置

## 适用范围

### 适用

查询或维护已授权 Shopee 店铺的信息和设置。用户希望查看店铺状态、核对资料、检查仓库、读取通知或调整假期模式时使用，无需明确提及 Shop 模块。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 看店铺是否正常、授权是否快到期 | 读取店铺基本信息。 |
| 查看或修改店名、标志、简介 | 查询或更新店铺资料。 |
| 查揽收或退货仓地址 | 读取仓库详情。 |
| 看卖家通知或授权品牌 | 读取通知或授权品牌列表。 |
| 查巴西店铺入驻资料 | 核对 KYC、税号与入驻状态。 |
| 查看或开启、关闭假期模式 | 查询当前状态，再按用户要求设置。 |

### 边界

授权与选店依赖 `linkfox-shopee-store-auth`。商户信息、订单、物流发货、退货退款、商品刊登、店铺分类、账户健康和跨境全球商品分别转交 `linkfox-shopee-store-merchant`、`linkfox-shopee-store-orders`、`linkfox-shopee-store-logistics`、`linkfox-shopee-store-returns`、`linkfox-shopee-store-product`、`linkfox-shopee-store-shop-category`、`linkfox-shopee-store-account-health`、`linkfox-shopee-store-global-product`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 获取店铺基本信息（`get_shop_info`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/shop/get_shop_info` | [references/apis/get-shop-info.md](references/apis/get-shop-info.md) | `scripts/get_shop_info.py` | 获取店铺基本信息。 |
| 获取店铺资料（`get_profile`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/shop/get_profile` | [references/apis/get-profile.md](references/apis/get-profile.md) | `scripts/get_profile.py` | 获取店铺资料。 |
| 更新店铺资料（`update_profile`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/shop/update_profile` | [references/apis/update-profile.md](references/apis/update-profile.md) | `scripts/update_profile.py` | 更新店铺资料。 |
| 获取仓库详情（`get_warehouse_detail`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/shop/get_warehouse_detail` | [references/apis/get-warehouse-detail.md](references/apis/get-warehouse-detail.md) | `scripts/get_warehouse_detail.py` | 获取仓库详情。 |
| 获取卖家通知（`get_shop_notification`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/shop/get_shop_notification` | [references/apis/get-shop-notification.md](references/apis/get-shop-notification.md) | `scripts/get_shop_notification.py` | 获取卖家通知。 |
| 获取授权经销品牌（`get_authorised_reseller_brand`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/shop/get_authorised_reseller_brand` | [references/apis/get-authorised-reseller-brand.md](references/apis/get-authorised-reseller-brand.md) | `scripts/get_authorised_reseller_brand.py` | 获取授权经销品牌。 |
| 获取巴西店铺入驻信息（`get_br_shop_onboarding_info`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/shop/get_br_shop_onboarding_info` | [references/apis/get-br-shop-onboarding-info.md](references/apis/get-br-shop-onboarding-info.md) | `scripts/get_br_shop_onboarding_info.py` | 获取巴西店铺入驻信息。 |
| 获取假期模式（`get_shop_holiday_mode`） | POST `/shopee/developerProxy` → 上游 GET，path：`api/v2/shop/get_shop_holiday_mode` | [references/apis/get-shop-holiday-mode.md](references/apis/get-shop-holiday-mode.md) | `scripts/get_shop_holiday_mode.py` | 获取假期模式。 |
| 设置假期模式（`set_shop_holiday_mode`） | POST `/shopee/developerProxy` → 上游 POST，path：`api/v2/shop/set_shop_holiday_mode` | [references/apis/set-shop-holiday-mode.md](references/apis/set-shop-holiday-mode.md) | `scripts/set_shop_holiday_mode.py` | 设置假期模式。 |
| 查询选店授权状态（`storeTokens`） | POST `/shopee/storeTokens` | [references/apis/store-tokens.md](references/apis/store-tokens.md) | `scripts/_shopee_shop_common.py::resolve_store_tokens` | 选店辅助操作，9 个业务 CLI 不会自动调用。 |

通用入口：`scripts/shop_api.py`；接口导航、CLI 与运行约定见 [references/api.md](references/api.md)。

## 前置条件

**先完成店铺授权并确定操作目标**：运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装 `linkfox-shopee-store-auth` 并完成授权，不在本技能内实现授权或令牌逻辑。确定用户指定店铺和操作范围，依赖检查约定见 `references/api.md`。

## 业务流程

1. 通过授权技能确定目标店铺，检查依赖并读取所需接口文档。
2. 查看基本信息时先获取店铺状态、区域及授权情况，按需再获取店名、标志和描述。
3. 更新资料时根据用户指定内容准备修改，先核对现有资料及接口限制，再提交并解释实际返回结果。
4. 调整假期模式时先查询当前状态，再按用户要求开启或关闭；说明开启后买家无法下单。
5. 查询仓库、通知、授权品牌或巴西入驻资料时选择对应操作；展示已返回数据与分页情况，后续请求遵守成本约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **成本约束**：算力规则见下文“算力消耗预估”。同一会话、同一参数组合默认只调用一次，优先复用已保存的数据；业务脚本不读写响应缓存，每次执行都会请求网关。失败或空结果时，不得自动修改查询条件、翻页或连续试探；需要继续查询时，先说明原因和拟调用范围。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-shop-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、可用的常见计数（如 `total`、`costToken`），以及非空最大列表字段的长度和前 3 条样本。
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

- **区分信息与资料**：基本信息用于区域、营业状态、授权有效期与履约能力；资料用于店名、标志和简介。
- **理解转发链路**：网关按店铺或商户解析服务端令牌，经 Shopee 代理转发到 Shopee；不在本地重做授权流程。
- **明确写操作影响**：资料更新和假期模式设置会改变真实店铺，按用户已明确的范围操作；不要把请求完成解释为变更成功。
- **清晰展示结果**：注明店铺与区域，按本次任务展示状态、资料、仓库、通知、品牌或入驻信息；缺失字段不补造。
- **分层解释状态**：按接口文档先判断 LinkFox 响应，再判断上游状态与业务错误，最后读取解析后的业务数据。保留原始响应供核对。

## 使用示例

### 查看基本信息与资料

用户：看看我的店铺状态和简介。

确定店铺后先读取基本信息，再读取资料；展示营业状态、区域、授权有效期及店名、标志、简介。

### 更新店铺资料

用户：把这个店铺的简介改为我提供的内容。

核对目标店铺和现有资料，按接口文档准备指定修改内容，提交并说明返回结果。

### 调整假期模式

用户：开启这家店的假期模式。

读取当前状态，按用户指定目标设置，并说明买家下单受影响及接口返回情况。

### 查询仓库、通知、品牌与巴西入驻资料

用户：查退货仓地址和最新卖家通知。

分别查询对应信息并展示已返回范围；品牌与巴西入驻资料按用户需求单独查询，限制与分页约定见对应接口文档。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
