---
name: linkfox-shopee-store-bundle-deal
description: 管理已授权 Shopee（虾皮）店铺的套装优惠 Bundle Deal，支持创建、查询、修改、提前结束和删除活动，以及添加、查询、更新和移除参与商品。适用于套装优惠、组合促销和满件优惠活动维护；不适用于店铺授权、限时折扣、Add-On Deal、优惠券或商品刊登管理。
---
# Shopee 套装优惠 Bundle Deal

## 适用范围

### 适用

管理已授权 Shopee 店铺的 Bundle Deal 活动和参与商品。用户希望查看、创建或维护套装优惠时使用，无需明确说出 Bundle Deal。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 创建满件优惠或组合促销 | 创建活动，再添加参与商品并查询状态。 |
| 查看店铺有哪些套装优惠 | 查询活动列表及指定活动详情。 |
| 调整套装优惠和参与商品 | 修改活动设置、添加或更新商品。 |
| 提前结束或删除活动 | 按用户指定范围结束、删除活动或移除商品。 |

### 边界

店铺授权和选店使用 `linkfox-shopee-store-auth`；限时折扣使用 `linkfox-shopee-store-discount`，Add-On Deal 使用 `linkfox-shopee-store-add-on-deal`，优惠券使用 `linkfox-shopee-store-voucher`，商品刊登维护使用 `linkfox-shopee-store-product`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建套装优惠（`add_bundle_deal`） | POST `/shopee/developerProxy` -> method：`POST`；path：`api/v2/bundle_deal/add_bundle_deal` | [references/apis/add-bundle-deal.md](references/apis/add-bundle-deal.md) | `scripts/add_bundle_deal.py` | 创建套装优惠。 |
| 添加活动商品（`add_bundle_deal_item`） | POST `/shopee/developerProxy` -> method：`POST`；path：`api/v2/bundle_deal/add_bundle_deal_item` | [references/apis/add-bundle-deal-item.md](references/apis/add-bundle-deal-item.md) | `scripts/add_bundle_deal_item.py` | 添加活动商品。 |
| 查询套装优惠列表（`get_bundle_deal_list`） | POST `/shopee/developerProxy` -> method：`GET`；path：`api/v2/bundle_deal/get_bundle_deal_list` | [references/apis/get-bundle-deal-list.md](references/apis/get-bundle-deal-list.md) | `scripts/get_bundle_deal_list.py` | 查询套装优惠列表。 |
| 查询套装优惠详情（`get_bundle_deal`） | POST `/shopee/developerProxy` -> method：`GET`；path：`api/v2/bundle_deal/get_bundle_deal` | [references/apis/get-bundle-deal.md](references/apis/get-bundle-deal.md) | `scripts/get_bundle_deal.py` | 查询套装优惠详情。 |
| 查询活动商品（`get_bundle_deal_item`） | POST `/shopee/developerProxy` -> method：`GET`；path：`api/v2/bundle_deal/get_bundle_deal_item` | [references/apis/get-bundle-deal-item.md](references/apis/get-bundle-deal-item.md) | `scripts/get_bundle_deal_item.py` | 查询活动商品。 |
| 更新套装优惠（`update_bundle_deal`） | POST `/shopee/developerProxy` -> method：`POST`；path：`api/v2/bundle_deal/update_bundle_deal` | [references/apis/update-bundle-deal.md](references/apis/update-bundle-deal.md) | `scripts/update_bundle_deal.py` | 更新套装优惠。 |
| 更新活动商品（`update_bundle_deal_item`） | POST `/shopee/developerProxy` -> method：`POST`；path：`api/v2/bundle_deal/update_bundle_deal_item` | [references/apis/update-bundle-deal-item.md](references/apis/update-bundle-deal-item.md) | `scripts/update_bundle_deal_item.py` | 更新活动商品。 |
| 提前结束套装优惠（`end_bundle_deal`） | POST `/shopee/developerProxy` -> method：`POST`；path：`api/v2/bundle_deal/end_bundle_deal` | [references/apis/end-bundle-deal.md](references/apis/end-bundle-deal.md) | `scripts/end_bundle_deal.py` | 提前结束套装优惠。 |
| 删除套装优惠（`delete_bundle_deal`） | POST `/shopee/developerProxy` -> method：`POST`；path：`api/v2/bundle_deal/delete_bundle_deal` | [references/apis/delete-bundle-deal.md](references/apis/delete-bundle-deal.md) | `scripts/delete_bundle_deal.py` | 删除套装优惠。 |
| 移除活动商品（`delete_bundle_deal_item`） | POST `/shopee/developerProxy` -> method：`POST`；path：`api/v2/bundle_deal/delete_bundle_deal_item` | [references/apis/delete-bundle-deal-item.md](references/apis/delete-bundle-deal-item.md) | `scripts/delete_bundle_deal_item.py` | 移除活动商品。 |
| 获取店铺令牌（兼容辅助） | POST `/shopee/storeTokens` | [references/api.md](references/api.md) | `scripts/_shopee_bundle_deal_common.py` 的 `resolve_store_tokens` | 提供令牌辅助函数；常规流程由服务端解析令牌。 |

## 前置条件

依赖 `linkfox-shopee-store-auth` 完成授权和选店。先运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能中另行实现授权流程。运行约定及各操作参数见 `references/api.md` 和对应接口文档。

## 套装优惠管理流程

1. 确定已授权店铺及用户希望查看或维护的活动、商品。
2. 创建时先使用 `scripts/add_bundle_deal.py` 提交完整活动资料，再使用 `scripts/add_bundle_deal_item.py` 添加参与商品，最后使用 `scripts/get_bundle_deal_list.py` 确认状态。
3. 查询或维护已有活动时，按用户任务读取活动详情及参与商品，再执行对应更新、结束、删除或移除操作，展示结果。
4. 通用入口为 `scripts/bundle_deal_api.py`；完整参数与运行约定见 `references/api.md`。失败或空结果后的继续调用遵守调用约束。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：本工具不消耗算力 （限时）。同一会话、同一参数组合避免无必要的重复调用；各业务入口关闭响应缓存，不提供 24 小时响应复用。失败或空结果时，先解释已返回的信息，再按用户任务范围决定是否继续查询；写入结果不确定时，不自动重试。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-bundle-deal-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 字节：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的常见计数（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分活动与商品**：Bundle Deal 活动设置和活动内商品分别维护，展示时注明目标店铺、活动及商品，避免把商品操作结果当成活动操作结果。
- **保留用户操作范围**：创建、修改、结束、删除及商品维护会改变店铺促销，按用户明确指定的对象和动作执行。
- **清晰展示数据**：用表格展示实际返回的活动、参与商品和操作结果，说明本次查询范围和后续分页情况；不补造缺失字段。
- **区分各层结果**：分别解释网关请求、上游响应及 Shopee 业务结果；具体判断见接口文档。返回不确定时保留已取得的数据，不直接宣布成功或重复写入。

## 使用示例

### 创建套装优惠

用户：按我提供的优惠规则创建套装活动，并加入指定商品。

确认目标店铺和资料，依次创建活动、添加商品、查询活动状态，展示每步返回结果。

### 查询和维护已有活动

用户：查看这个套装活动中的商品，并移除我指定的商品。

确认活动和商品，读取当前参与商品，按用户范围移除并说明返回结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
