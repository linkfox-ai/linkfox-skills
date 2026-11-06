---
name: linkfox-shopee-store-add-on-deal
description: 管理已授权 Shopee（虾皮）店铺的加购优惠 Add-On Deal，支持创建、查询、更新、删除和提前结束活动，以及维护主商品与加购商品。适用于主商品加购、满额加购等活动管理；不适用于店铺授权、限时折扣、套装优惠、优惠券或商品刊登维护。
---
# Shopee 加购优惠 Add-On Deal

## 适用范围

### 适用

管理已授权 Shopee 店铺的加购优惠活动及其主商品、加购商品。用户希望查看活动、调整商品组合或结束指定活动时使用本技能。

**场景速查**

| 用户表达 | 查询场景 |
| -------- | -------- |
| 创建加购优惠，设置主商品和加购商品 | 创建活动并维护两类商品。 |
| 查看店铺加购优惠及某个活动详情 | 查询活动列表与详情。 |
| 调整这个活动的主商品或加购商品 | 添加、更新或删除指定类型商品。 |
| 提前结束或删除指定活动 | 根据用户指定的操作维护活动。 |

### 边界

店铺授权交给 `linkfox-shopee-store-auth`；限时折扣、套装优惠、优惠券和商品刊登分别使用 `linkfox-shopee-store-discount`、`linkfox-shopee-store-bundle-deal`、`linkfox-shopee-store-voucher` 和 `linkfox-shopee-store-product`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 创建加购优惠（`add_add_on_deal`） | POST `/shopee/developerProxy` → method：`POST`；path：`api/v2/add_on_deal/add_add_on_deal` | [references/apis/add-add-on-deal.md](references/apis/add-add-on-deal.md) | `scripts/add_add_on_deal.py` | 创建加购优惠。 |
| 添加主商品（`add_add_on_deal_main_item`） | POST `/shopee/developerProxy` → method：`POST`；path：`api/v2/add_on_deal/add_add_on_deal_main_item` | [references/apis/add-add-on-deal-main-item.md](references/apis/add-add-on-deal-main-item.md) | `scripts/add_add_on_deal_main_item.py` | 添加主商品。 |
| 添加加购商品（`add_add_on_deal_sub_item`） | POST `/shopee/developerProxy` → method：`POST`；path：`api/v2/add_on_deal/add_add_on_deal_sub_item` | [references/apis/add-add-on-deal-sub-item.md](references/apis/add-add-on-deal-sub-item.md) | `scripts/add_add_on_deal_sub_item.py` | 添加加购商品。 |
| 删除加购优惠（`delete_add_on_deal`） | POST `/shopee/developerProxy` → method：`POST`；path：`api/v2/add_on_deal/delete_add_on_deal` | [references/apis/delete-add-on-deal.md](references/apis/delete-add-on-deal.md) | `scripts/delete_add_on_deal.py` | 删除加购优惠。 |
| 删除主商品（`delete_add_on_deal_main_item`） | POST `/shopee/developerProxy` → method：`POST`；path：`api/v2/add_on_deal/delete_add_on_deal_main_item` | [references/apis/delete-add-on-deal-main-item.md](references/apis/delete-add-on-deal-main-item.md) | `scripts/delete_add_on_deal_main_item.py` | 删除主商品。 |
| 删除加购商品（`delete_add_on_deal_sub_item`） | POST `/shopee/developerProxy` → method：`POST`；path：`api/v2/add_on_deal/delete_add_on_deal_sub_item` | [references/apis/delete-add-on-deal-sub-item.md](references/apis/delete-add-on-deal-sub-item.md) | `scripts/delete_add_on_deal_sub_item.py` | 删除加购商品。 |
| 查询加购优惠列表（`get_add_on_deal_list`） | POST `/shopee/developerProxy` → method：`GET`；path：`api/v2/add_on_deal/get_add_on_deal_list` | [references/apis/get-add-on-deal-list.md](references/apis/get-add-on-deal-list.md) | `scripts/get_add_on_deal_list.py` | 查询加购优惠列表。 |
| 查询加购优惠详情（`get_add_on_deal`） | POST `/shopee/developerProxy` → method：`GET`；path：`api/v2/add_on_deal/get_add_on_deal` | [references/apis/get-add-on-deal.md](references/apis/get-add-on-deal.md) | `scripts/get_add_on_deal.py` | 查询加购优惠详情。 |
| 查询主商品列表（`get_add_on_deal_main_item`） | POST `/shopee/developerProxy` → method：`GET`；path：`api/v2/add_on_deal/get_add_on_deal_main_item` | [references/apis/get-add-on-deal-main-item.md](references/apis/get-add-on-deal-main-item.md) | `scripts/get_add_on_deal_main_item.py` | 查询主商品列表。 |
| 查询加购商品列表（`get_add_on_deal_sub_item`） | POST `/shopee/developerProxy` → method：`GET`；path：`api/v2/add_on_deal/get_add_on_deal_sub_item` | [references/apis/get-add-on-deal-sub-item.md](references/apis/get-add-on-deal-sub-item.md) | `scripts/get_add_on_deal_sub_item.py` | 查询加购商品列表。 |
| 更新加购优惠（`update_add_on_deal`） | POST `/shopee/developerProxy` → method：`POST`；path：`api/v2/add_on_deal/update_add_on_deal` | [references/apis/update-add-on-deal.md](references/apis/update-add-on-deal.md) | `scripts/update_add_on_deal.py` | 更新加购优惠。 |
| 更新主商品设置（`update_add_on_deal_main_item`） | POST `/shopee/developerProxy` → method：`POST`；path：`api/v2/add_on_deal/update_add_on_deal_main_item` | [references/apis/update-add-on-deal-main-item.md](references/apis/update-add-on-deal-main-item.md) | `scripts/update_add_on_deal_main_item.py` | 更新主商品设置。 |
| 更新加购商品设置（`update_add_on_deal_sub_item`） | POST `/shopee/developerProxy` → method：`POST`；path：`api/v2/add_on_deal/update_add_on_deal_sub_item` | [references/apis/update-add-on-deal-sub-item.md](references/apis/update-add-on-deal-sub-item.md) | `scripts/update_add_on_deal_sub_item.py` | 更新加购商品设置。 |
| 提前结束加购优惠（`end_add_on_deal`） | POST `/shopee/developerProxy` → method：`POST`；path：`api/v2/add_on_deal/end_add_on_deal` | [references/apis/end-add-on-deal.md](references/apis/end-add-on-deal.md) | `scripts/end_add_on_deal.py` | 提前结束加购优惠。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店与完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；缺失时先安装依赖，不在本技能内另行实现授权或令牌逻辑。确认目标店铺、活动和商品；依赖检测约定、完整参数及脚本兼容行为见 [references/api.md](references/api.md) 及接口清单中的文档。

## 加购优惠管理流程

1. 确定用户要创建、查询、更新、删除还是提前结束活动，并核对已授权店铺及目标活动。
2. 创建时先运行 `scripts/add_add_on_deal.py`，再根据返回的活动标识运行 `scripts/add_add_on_deal_main_item.py` 和 `scripts/add_add_on_deal_sub_item.py`，添加主商品与加购商品。
3. 运行 `scripts/get_add_on_deal_list.py` 确认活动状态；需要核对详情或商品时，使用对应查询脚本。
4. 修改、移除商品或结束活动时，按用户明确的目标选择接口，解释返回结果；结果不确定时先保留现有响应，避免重复提交。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次；业务脚本不读取或写入响应缓存。失败或空结果时，保留已有响应，按返回信息处理；后续查询按用户任务范围进行，写入结果不确定时避免重复提交。

### 输出策略

- 始终保存完整响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-add-on-deal-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错。
- 响应体不超过 8000 UTF-8 字节：保存后，将完整 JSON 打印到标准输出。
- 响应体超过 8000 UTF-8 字节：保存后，标准输出仅展示摘要，包括顶层字段、实际存在的常见字段（如 `total`、`costToken`）、最大列表字段的长度和前 3 条样本。
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

- **区分活动与商品**：活动、主商品和加购商品是不同操作对象；添加或删除商品不等同于创建或删除活动。
- **清晰展示数据**：注明店铺、活动及操作类型，用表格展示实际返回的活动状态、主商品、加购商品和操作结果；缺失信息不补造。
- **解释执行结果**：区分网关完成、Shopee 返回和业务结果；判断方法见接口文档。
- **说明查询范围**：列表涉及分页或状态筛选时，说明本次返回范围，不把单页当作全部活动。
- **无响应缓存**：业务脚本始终禁用公共调用器的响应缓存；重复调用会重新发起请求。具体运行约定见 [references/api.md](references/api.md)。

## 使用示例

### 创建加购优惠

用户：为这些主商品创建加购优惠，关联我指定的加购商品。

核对店铺和活动方案，先创建活动，取得活动标识后添加主商品与加购商品，最后查询活动列表确认状态。

### 查询活动及商品

用户：查看店铺的加购优惠，并列出这个活动的主商品和加购商品。

查询活动列表，再按目标活动查询详情及两类商品，展示实际返回的内容和查询范围。

### 修改或结束活动

用户：调整这个活动的加购商品，然后提前结束活动。

核对用户指定的活动及商品，按明确的操作范围更新商品并结束活动，说明每一步返回的结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
