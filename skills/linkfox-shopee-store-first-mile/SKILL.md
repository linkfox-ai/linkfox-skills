---
name: linkfox-shopee-store-first-mile
description: 管理已授权 Shopee（虾皮）店铺的跨境头程物流 FirstMile，支持未绑定订单查询、头程运单生成与绑定、指定订单或整票解绑、运单列表及详情、面单、渠道与中转仓查询，并覆盖快递配送头程。适用于头程运单整理和交运准备；不适用于店铺授权、正向物流发货、SBS 仓储库存或通用订单查询。
---
# Shopee 头程 FirstMile

## 适用范围

### 适用

管理已授权 Shopee 店铺的跨境头程运单及面单。用户希望整理未绑定订单、生成并绑定头程运单，或查询渠道、中转仓和快递头程资料时使用。

**场景速查**

| 用户表达 | 查询场景 |
|---|---|
| 找出还没绑定头程运单的订单 | 未绑定订单查询。 |
| 给这些订单生成并绑定头程运单 | 分步生成与绑定，或一步生成并绑定。 |
| 解绑这些订单或整票订单 | 按用户指定范围选择对应解绑操作。 |
| 查看头程运单列表、详情或面单 | 头程查询及交运准备。 |
| 查看可用渠道、中转仓和快递配送头程 | 渠道与仓库查询、快递头程管理。 |

### 边界

店铺授权使用 `linkfox-shopee-store-auth`；正向物流发货使用 `linkfox-shopee-store-logistics`；SBS 仓储库存使用 `linkfox-shopee-store-sbs`；通用订单查询使用 `linkfox-shopee-store-orders`。

## 接口清单

| 接口 | 端点 | 接口文档 | 对应脚本 | 说明 |
|---|---|---|---|---|
| 查询未绑定订单（`get_unbind_order_list`） | POST `/shopee/developerProxy` -> method：`GET`，path：`api/v2/first_mile/get_unbind_order_list` | [references/apis/get-unbind-order-list.md](references/apis/get-unbind-order-list.md) | `scripts/get_unbind_order_list.py` | 查询未绑定订单。 |
| 查询头程详情（`get_detail`） | POST `/shopee/developerProxy` -> method：`GET`，path：`api/v2/first_mile/get_detail` | [references/apis/get-detail.md](references/apis/get-detail.md) | `scripts/get_detail.py` | 查询头程详情。 |
| 生成头程运单号（`generate_first_mile_tracking_number`） | POST `/shopee/developerProxy` -> method：`POST`，path：`api/v2/first_mile/generate_first_mile_tracking_number` | [references/apis/generate-first-mile-tracking-number.md](references/apis/generate-first-mile-tracking-number.md) | `scripts/generate_first_mile_tracking_number.py` | 生成头程运单号。 |
| 绑定头程运单号（`bind_first_mile_tracking_number`） | POST `/shopee/developerProxy` -> method：`POST`，path：`api/v2/first_mile/bind_first_mile_tracking_number` | [references/apis/bind-first-mile-tracking-number.md](references/apis/bind-first-mile-tracking-number.md) | `scripts/bind_first_mile_tracking_number.py` | 绑定头程运单号。 |
| 解绑指定订单的头程运单号（`unbind_first_mile_tracking_number`） | POST `/shopee/developerProxy` -> method：`POST`，path：`api/v2/first_mile/unbind_first_mile_tracking_number` | [references/apis/unbind-first-mile-tracking-number.md](references/apis/unbind-first-mile-tracking-number.md) | `scripts/unbind_first_mile_tracking_number.py` | 解绑指定订单的头程运单号。 |
| 查询头程运单号列表（`get_tracking_number_list`） | POST `/shopee/developerProxy` -> method：`GET`，path：`api/v2/first_mile/get_tracking_number_list` | [references/apis/get-tracking-number-list.md](references/apis/get-tracking-number-list.md) | `scripts/get_tracking_number_list.py` | 查询头程运单号列表。 |
| 获取头程面单（`get_waybill`） | POST `/shopee/developerProxy` -> method：`GET`，path：`api/v2/first_mile/get_waybill` | [references/apis/get-waybill.md](references/apis/get-waybill.md) | `scripts/get_waybill.py` | 获取头程面单。 |
| 查询头程渠道（`get_channel_list`） | POST `/shopee/developerProxy` -> method：`GET`，path：`api/v2/first_mile/get_channel_list` | [references/apis/get-channel-list.md](references/apis/get-channel-list.md) | `scripts/get_channel_list.py` | 查询头程渠道。 |
| 查询快递配送渠道（`get_courier_delivery_channel_list`） | POST `/shopee/developerProxy` -> method：`GET`，path：`api/v2/first_mile/get_courier_delivery_channel_list` | [references/apis/get-courier-delivery-channel-list.md](references/apis/get-courier-delivery-channel-list.md) | `scripts/get_courier_delivery_channel_list.py` | 查询快递配送渠道。 |
| 查询中转仓（`get_transit_warehouse_list`） | POST `/shopee/developerProxy` -> method：`GET`，path：`api/v2/first_mile/get_transit_warehouse_list` | [references/apis/get-transit-warehouse-list.md](references/apis/get-transit-warehouse-list.md) | `scripts/get_transit_warehouse_list.py` | 查询中转仓。 |
| 生成并绑定头程运单号（`generate_and_bind_first_mile_tracking_number`） | POST `/shopee/developerProxy` -> method：`POST`，path：`api/v2/first_mile/generate_and_bind_first_mile_tracking_number` | [references/apis/generate-and-bind-first-mile-tracking-number.md](references/apis/generate-and-bind-first-mile-tracking-number.md) | `scripts/generate_and_bind_first_mile_tracking_number.py` | 生成并绑定头程运单号。 |
| 绑定快递配送头程运单号（`bind_courier_delivery_first_mile_tracking_number`） | POST `/shopee/developerProxy` -> method：`POST`，path：`api/v2/first_mile/bind_courier_delivery_first_mile_tracking_number` | [references/apis/bind-courier-delivery-first-mile-tracking-number.md](references/apis/bind-courier-delivery-first-mile-tracking-number.md) | `scripts/bind_courier_delivery_first_mile_tracking_number.py` | 绑定快递配送头程运单号。 |
| 解绑头程运单号下全部订单（`unbind_first_mile_tracking_number_all`） | POST `/shopee/developerProxy` -> method：`POST`，path：`api/v2/first_mile/unbind_first_mile_tracking_number_all` | [references/apis/unbind-first-mile-tracking-number-all.md](references/apis/unbind-first-mile-tracking-number-all.md) | `scripts/unbind_first_mile_tracking_number_all.py` | 解绑头程运单号下全部订单。 |
| 查询快递头程详情（`get_courier_delivery_detail`） | POST `/shopee/developerProxy` -> method：`GET`，path：`api/v2/first_mile/get_courier_delivery_detail` | [references/apis/get-courier-delivery-detail.md](references/apis/get-courier-delivery-detail.md) | `scripts/get_courier_delivery_detail.py` | 查询快递头程详情。 |
| 获取快递头程面单（`get_courier_delivery_waybill`） | POST `/shopee/developerProxy` -> method：`GET`，path：`api/v2/first_mile/get_courier_delivery_waybill` | [references/apis/get-courier-delivery-waybill.md](references/apis/get-courier-delivery-waybill.md) | `scripts/get_courier_delivery_waybill.py` | 获取快递头程面单。 |
| 查询快递头程运单号列表（`get_courier_delivery_tracking_number_list`） | POST `/shopee/developerProxy` -> method：`GET`，path：`api/v2/first_mile/get_courier_delivery_tracking_number_list` | [references/apis/get-courier-delivery-tracking-number-list.md](references/apis/get-courier-delivery-tracking-number-list.md) | `scripts/get_courier_delivery_tracking_number_list.py` | 查询快递头程运单号列表。 |
| 查询店铺授权状态（兼容辅助） | POST `/shopee/storeTokens` | [references/api.md](references/api.md) | `scripts/_shopee_first_mile_common.py` 中 `resolve_store_tokens` | 返回授权资料，不返回原始令牌；默认头程流程由网关解析令牌，无需额外查询。 |

## 前置条件

**先完成店铺授权并确定操作目标**：依赖 `linkfox-shopee-store-auth` 选店和完成授权。运行 `python scripts/check_auth_dependency.py` 检查依赖；检测为缺失时先安装依赖，再继续本流程。依赖检测约定和完整接口定义见 `references/api.md` 及对应接口文档。

## 头程运单处理流程

以下绑定流程适用于需要生成或绑定运单的任务；仅查询列表、详情、面单、渠道或中转仓时，直接选用对应查询操作。解绑任务按第 4 步选择范围。

1. 确定目标店铺和用户要处理的订单，查询未绑定头程运单的订单。
2. 按用户要求一步生成并绑定，或先生成头程运单号再绑定订单。
3. 获取头程面单，按需读取运单详情、渠道或中转仓；快递配送头程使用对应操作。
4. 需要解绑时，核对用户指定范围，分别使用指定订单解绑或整票解绑，展示实际处理结果。

## 执行方式

- **直接调用接口**：接口端点、完整参数、响应和错误码见 `references/api.md`。
- **脚本调用（推荐）**：`python <脚本路径> '<JSON 参数>' [--inline] [--no-cache]`。
- **调用约束**：同一会话、同一参数组合默认只调用一次。业务封装始终禁用响应缓存，不读取或写入缓存响应。失败或空结果时，不得自动更换关键词、翻页或修改邮编连续试探；需要继续查询时，先说明原因和拟执行的操作。

### 输出策略

- 始终保存完整头程业务响应，目标路径为 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-shopee-store-first-mile-<接口标识>-<timestamp>.json`。`<cwd>` 为脚本运行时的工作目录，`<session>` 优先取环境变量 `SESSION_ID`，用于聚合同一任务的数据。禁止写入 `/tmp`，当前目录不可写时应报错；授权状态兼容辅助函数仅保存脱敏对象，见 `references/api.md`。
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

- **区分物流阶段**：本技能处理跨境头程（First Mile），正向物流发货与面单按边界转交。
- **区分查询与变更**：生成、绑定和解绑会改变头程业务状态，按用户已经明确的店铺、订单与运单范围执行；不能把指定订单解绑扩大为整票解绑。
- **清晰展示数据**：注明店铺与操作名称，用表格展示返回的订单、运单、渠道或仓库资料，并说明面单获取结果。
- **解释多层状态**：区分网关响应、Shopee 上游响应和订单级处理结果；不能仅凭取得响应或取得运单号就声称全部订单已绑定。判断依据见接口定义。
- **保持真实数据**：只展示实际返回字段；空结果和错误先解释原因，保留已取得数据，遵守执行方式中的调用约束。

## 使用示例

### 为订单准备头程交运

用户：找出这家店还没绑定头程运单的订单，按我指定的订单生成并绑定运单，再取面单。

确认店铺和订单范围，依次查询未绑定订单、生成并绑定运单、获取面单，展示每步结果。

### 解绑指定订单

用户：把指定订单从这个头程运单中解绑。

核对目标店铺、订单与运单，使用指定订单解绑操作，说明返回结果。

## 使用反馈

当技能有BUG，或技能描述有错误/疏漏/歧义/表述模糊，或技能结果与用户预期不符，或用户表达不满/赞扬，或发现其他可改进之处时，按 `references/api.md#Feedback` 的指引反馈，不要打断用户当前流程。

---

更多优质、专业的跨境电商技能，请访问 [LinkFox Skill](https://skill.linkfox.com/)。
