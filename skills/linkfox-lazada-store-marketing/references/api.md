# Lazada 店铺营销与广告接口说明

## 公共规则

### 调用规范

- LinkFox 网关 `POST /lazada/marketing` 使用下列顶层字段。命令行入口从操作名生成 `operation`，JSON 输入包含其余字段。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `connectionId` | 字符串 | 必填 | 按原样传入当前用户已授权店铺的连接 ID，网关上限 36 字符。 |
| `operation` | 字符串 | 必填 | 使用本页列出的固定操作名。 |
| `params` | 对象 | 按操作 | 仅接受当前操作列出的字段。无业务参数时可省略。网关限制序列化后的 UTF-8 大小为 1 MiB。 |
| `requestId` | 字符串 | 写入必填 | 带连字符的 UUID。查询操作省略该字段。 |

- 请求头、网关地址、超时和 LinkFox Key 配置使用 `Content-Type: application/json`、`Accept: application/json`、`User-Agent: LinkFox-Skill/2.0` 及 `Authorization: <LinkFox Key>`。基础地址读取 `LINKFOX_TOOL_GATEWAY`，默认 `https://tool-gateway.linkfox.com`，超时 150 秒。Key 优先取 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`，透传 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME`。`scripts/marketing_api.py` 从命令行选择固定操作，支持内联 JSON 或 `--params-file <UTF-8 JSON 文件>`。每次业务调用均为实时请求。
- `params` 中的对象和数组可按表格使用原生 JSON 值。网关会按紫鸟代理约定把 POST 中的对象和数组编码成 JSON 文本。金额和长 ID 按字段类型传入，避免经浮点数转换。

### 写入与续查

已确认的写动作请求另需 `requestId` UUID。后端按当前用户、店铺连接、UUID 和请求内容识别重复请求。结果不明时执行 `python scripts/marketing_api.py operationStatus '<JSON 参数>'`，输入仅含 `connectionId` 和原 `requestId`。该命令调用 LinkFox `POST /lazada/operationStatus`。

| 响应字段 | 类型 | 含义 |
| --- | --- | --- |
| `data` | 对象、数组、标量或 `null` | 脱敏业务响应，查询写记录或提交重复请求时可能为 `null`。 |
| `requestId` | 字符串或 `null` | Lazada 上游请求标识。 |
| `clientRequestId` | 字符串 | 写动作原 UUID，供状态查询使用。查询业务数据时缺省。 |
| `status` | 字符串 | 写记录状态。查询业务数据时缺省。 |
| `success` | 布尔值 | CLI 调用结果。写入仅 `SUCCEEDED` 视为成功。状态查询成功后仍需读取 `status`。 |

`PENDING` 时按原 UUID 续查。`SUCCEEDED` 表示上游确认写入，仍需结合各项业务结果。`REJECTED` 时核对失败原因。`PARTIAL` 时逐项检查成功与失败范围。`UNKNOWN` 时核对店铺的实际状态。写操作失败或结果不明时保留原 UUID，避免自动重放。部署侧默认关闭写入，需由接入方启用。

`addVoucherSkus`、`addFreeShippingSkus` 和 `addFlexiComboSkus` 的上游 `data` 是以 SKU ID 为键的失败清单。空对象表示没有失败项，部分 SKU 出现在清单中时为 `PARTIAL`，全部出现时为 `REJECTED`。

`LAZADA_WRITES_DISABLED` 表示部署未启用写入。`LAZADA_REQUEST_ID_CONFLICT` 时检查原 UUID 与原请求参数。`LAZADA_OPERATION_NOT_FOUND` 时核对店铺连接和 UUID，并检查目标当前状态。

### 响应结构

下文的 `data.*` 路径从 CLI JSON 的顶层 `data` 开始。网关响应可能有外层 `data` 包装，CLI 会剥去这一层。后端将上游 `request_id` 提到 `requestId`，移除上游传输层 `code`、`type`、`message`、`msg`，并过滤凭据和敏感字段。上游只返回一个业务字段 `data` 时，后端将其内容直接作为结果 `data`。

促销接口的官方示例同时返回 `success`、`error_code`、`error_msg`，因此业务对象通常位于 `data.data`。诊断字段见[促销响应状态](#促销响应状态)。广告响应通常位于 `data.result`，诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。上游 `success` 与 CLI 顶层 `success` 含义不同。

官方响应示例会将部分数字和布尔值序列化成字符串，也会返回空值或字符串 `"null"`。LinkFox 将 `id`、`ids` 或 `idList` 结尾的整数字段转为字符串，其他字段保留上游类型。处理标识时保留整数精度，提交 `sku_ids` 时保持数字数组。

CLI 将完整脱敏结果写入 `linkfox/YYYY-MM-DD/<SESSION_ID>/data/`，并输出保存路径。响应超过 8000 字节时，终端默认仅显示摘要。需要完整业务字段时读取 JSON 文件，也可加 `--inline` 输出完整结果。

`listVouchers` 的空页与 `getSponsoredMaxMetric` 的时间序列分别使用 `data.data` 和 `data.result`。以下为简化后的 CLI 输出示例。

```json
{
  "data": {
    "data": {"data_list": [], "total": "0", "current": "1", "page_size": "10"},
    "success": "true"
  },
  "requestId": null,
  "success": true
}
```

```json
{
  "data": {
    "result": {"dateList": [1680451200000], "hourList": [], "metricList": [0]},
    "success": "true"
  },
  "requestId": null,
  "success": true
}
```

## listVouchers

上游 `GET /promotion/vouchers/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `cur_page` | 数字 | 可选 | 页码。 |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `name` | 字符串 | 可选 | 按活动名称筛选。 |
| `page_size` | 数字 | 可选 | 每页条数。 |
| `status` | 字符串 | 可选 | 活动状态。可选 `NOT_START`、`ONGOING`、`SUSPEND`、`FINISH`。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为[优惠券](#优惠券)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvouchers%2Fget)

## getVoucher

上游 `GET /promotion/voucher/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.data` 为[优惠券](#优惠券)对象。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fget)

## createVoucher

上游 `POST /promotion/voucher/create`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `criteria_over_money` | 字符串 | 必填 | 订单达到该金额后可享受优惠，金额使用十进制文本。 |
| `voucher_type` | 字符串 | 必填 | 只支持 `COLLECTIBLE_VOUCHER`。 |
| `apply` | 字符串 | 必填 | 适用范围。可选 `ENTIRE_SHOP` 或 `SPECIFIC_PRODUCTS`。 |
| `collect_start` | 数字 | 可选 | 开始领券的 Unix 毫秒时间戳。 |
| `display_area` | 字符串 | 必填 | 买家可见渠道。官方创建定义列出 `REGULAR_CHANNEL`、`STORE_FOLLOWER`、`OFFLINE`、`LIVE_STREAM`、`CEM_SELLER`。 |
| `period_end_time` | 数字 | 必填 | 结束时间，Unix 毫秒时间戳，须晚于开始时间。 |
| `voucher_name` | 字符串 | 必填 | 优惠券名称。 |
| `voucher_discount_type` | 字符串 | 必填 | 折扣类型。可选 `MONEY_VALUE_OFF` 或 `PERCENTAGE_DISCOUNT_OFF`。 |
| `offering_money_value_off` | 字符串 | 条件必填 | 固定优惠金额，十进制文本。选择 `MONEY_VALUE_OFF` 时须为正数。 |
| `period_start_time` | 数字 | 必填 | 开始时间，Unix 毫秒时间戳。 |
| `limit` | 数字 | 必填 | 每位买家的领取上限，整数。 |
| `issued` | 数字 | 必填 | 发放数量，整数。 |
| `max_discount_offering_money_value` | 字符串 | 可选 | 单笔订单最高折扣金额，十进制文本，仅适用于比例折扣。 |
| `offering_percentage_discount_off` | 数字 | 条件必填 | 折扣比例。选择 `PERCENTAGE_DISCOUNT_OFF` 时须为正数。 |

`data.data` 为[促销写入返回的活动 ID](#促销写入返回的活动-id)。`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fcreate)

## updateVoucher

上游 `POST /promotion/voucher/update`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `max_discount_offering_money_value` | 字符串 | 可选 | 单笔订单最高折扣金额，十进制文本，仅适用于比例折扣。 |
| `offering_percentage_discount_off` | 数字 | 条件必填 | 折扣比例。选择 `PERCENTAGE_DISCOUNT_OFF` 时须为正数。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `criteria_over_money` | 字符串 | 必填 | 订单达到该金额后可享受优惠，金额使用十进制文本。 |
| `voucher_type` | 字符串 | 必填 | 只支持 `COLLECTIBLE_VOUCHER`。 |
| `apply` | 字符串 | 必填 | 适用范围。可选 `ENTIRE_SHOP` 或 `SPECIFIC_PRODUCTS`。 |
| `collect_start` | 数字 | 可选 | 开始领券的 Unix 毫秒时间戳。 |
| `display_area` | 字符串 | 必填 | 买家可见渠道，按现有优惠券及站点支持值传入。 |
| `period_end_time` | 数字 | 必填 | 结束时间，Unix 毫秒时间戳，须晚于开始时间。 |
| `voucher_name` | 字符串 | 必填 | 优惠券名称。 |
| `voucher_discount_type` | 字符串 | 必填 | 折扣类型。可选 `MONEY_VALUE_OFF` 或 `PERCENTAGE_DISCOUNT_OFF`。 |
| `offering_money_value_off` | 字符串 | 必填 | 固定优惠金额，十进制文本。选择 `MONEY_VALUE_OFF` 时须为正数。 |
| `period_start_time` | 数字 | 必填 | 开始时间，Unix 毫秒时间戳。 |
| `limit` | 数字 | 必填 | 每位买家的领取上限，整数。 |
| `issued` | 数字 | 必填 | 发放数量，整数。更新时按官方要求提供大于原设置的数量。 |

`data.data` 为[促销写入返回的活动 ID](#促销写入返回的活动-id)。`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fupdate)

## activateVoucher

上游 `POST /promotion/voucher/activate`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Factivate)

## deactivateVoucher

上游 `POST /promotion/voucher/deactivate`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fdeactivate)

## listVoucherProducts

上游 `GET /promotion/voucher/products/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `cur_page` | 数字 | 可选 | 页码。 |
| `page_size` | 数字 | 可选 | 每页条数。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为[活动商品](#活动商品)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fproducts%2Fget)

## addVoucherSkus

上游 `POST /promotion/voucher/product/sku/add`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

`data.data` 为[添加 SKU 失败清单](#添加-sku-失败清单)。结果判定见[写入与续查](#写入与续查)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fproduct%2Fsku%2Fadd)

## removeVoucherSkus

上游 `POST /promotion/voucher/product/sku/remove`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fproduct%2Fsku%2Fremove)

## listFreeShipping

上游 `GET /promotion/freeshippings/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `curPage` | 数字 | 可选 | 页码。 |
| `name` | 字符串 | 可选 | 按活动名称筛选。 |
| `pageSize` | 数字 | 可选 | 每页条数。 |
| `status` | 字符串 | 可选 | 活动状态。可选 `NOT_START`、`ONGOING`、`SUSPEND`、`FINISH`。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为[包邮活动](#包邮活动)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshippings%2Fget)

## getFreeShipping

上游 `GET /promotion/freeshipping/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.data` 为[包邮活动](#包邮活动)对象。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fget)

## createFreeShipping

上游 `POST /promotion/freeshipping/create`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `budget_type` | 字符串 | 必填 | 预算类型。可选 `UNLIMITED_BUDGET` 或 `LIMITED_BUDGET`。 |
| `template_type` | 字符串 | 可选 | 模板类型。可选 `MANUALLY`、`CAMPAIGN`、`TEMPLATE`。 |
| `apply` | 字符串 | 必填 | 适用范围。可选 `ENTIRE_SHOP`、`SPECIFIC_PRODUCTS`、`CAMPAIGN_PRODUCTS`。 |
| `period_end_time` | 数字 | 必填 | 结束时间，Unix 毫秒时间戳。选 `SPECIAL_PERIOD` 时须晚于开始时间。 |
| `template_code` | 字符串 | 可选 | 促销模板编码。 |
| `category_name` | 字符串 | 可选 | 商品类目标识，使用字符串。 |
| `budget_value` | 字符串 | 条件必填 | 预算金额，十进制文本。`LIMITED_BUDGET` 时必填且为正数。 |
| `promotion_name` | 字符串 | 必填 | 包邮活动名称。 |
| `period_type` | 字符串 | 必填 | 活动期限。可选 `LONG_TERM` 或 `SPECIAL_PERIOD`。 |
| `region_type` | 字符串 | 必填 | 地区范围。可选 `ALL_REGIONS` 或 `SPECIAL_REGIONS`。区域查询为空时使用 `ALL_REGIONS`。 |
| `period_start_time` | 数字 | 必填 | 开始时间，Unix 毫秒时间戳。LinkFox 要求传入该字段，选 `SPECIAL_PERIOD` 时校验时间顺序。 |
| `campaign_tag` | 字符串 | 条件必填 | 活动标签。模板为 `CAMPAIGN` 且范围为 `CAMPAIGN_PRODUCTS` 时必填。 |
| `region_value` | 字符串数组 | 条件必填 | 地区编码数组。`SPECIAL_REGIONS` 时必填且非空，元素取自 `listFreeShippingRegions` 的 `value`。 |
| `delivery_option` | 字符串 | 必填 | 配送选项编码，取自 `listShippingOptions` 的 `value`。 |
| `tiers` | 对象数组 | 必填 | 非空优惠层级数组。 |
| `tiers[].filter` | 字符串 | 必填 | 该层的门槛值，按 `deal_criteria` 表示金额、件数或无门槛。 |
| `tiers[].result` | 字符串 | 条件必填 | 该层运费补贴值。`PARTIAL_SUBSIDY` 时必填。 |
| `discount_type` | 字符串 | 必填 | 运费补贴类型。可选 `FULL_SUBSIDY` 或 `PARTIAL_SUBSIDY`。 |
| `deal_criteria` | 字符串 | 必填 | 补贴门槛类型。可选 `MONEY_VALUE_FROM_X`、`ITEM_QUANTITY_FROM_X`、`NO_CONDITION`。 |

`data.data` 为[促销写入返回的活动 ID](#促销写入返回的活动-id)。`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fcreate)

## updateFreeShipping

上游 `POST /promotion/freeshipping/update`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `budget_type` | 字符串 | 必填 | 预算类型。可选 `UNLIMITED_BUDGET` 或 `LIMITED_BUDGET`。 |
| `template_type` | 字符串 | 必填 | 模板类型。可选 `MANUALLY`、`CAMPAIGN`、`TEMPLATE`。 |
| `apply` | 字符串 | 必填 | 适用范围。可选 `ENTIRE_SHOP`、`SPECIFIC_PRODUCTS`、`CAMPAIGN_PRODUCTS`。 |
| `period_end_time` | 数字 | 必填 | 结束时间，Unix 毫秒时间戳。选 `SPECIAL_PERIOD` 时须晚于开始时间。 |
| `template_code` | 字符串 | 可选 | 促销模板编码。 |
| `category_name` | 字符串 | 可选 | 商品类目标识，使用字符串。 |
| `budget_value` | 字符串 | 条件必填 | 预算金额，十进制文本。`LIMITED_BUDGET` 时必填且为正数。 |
| `promotion_name` | 字符串 | 必填 | 包邮活动名称。 |
| `period_type` | 字符串 | 必填 | 活动期限。可选 `LONG_TERM` 或 `SPECIAL_PERIOD`。 |
| `region_type` | 字符串 | 必填 | 地区范围。可选 `ALL_REGIONS` 或 `SPECIAL_REGIONS`。区域查询为空时使用 `ALL_REGIONS`。 |
| `period_start_time` | 数字 | 必填 | 开始时间，Unix 毫秒时间戳。LinkFox 要求传入该字段，选 `SPECIAL_PERIOD` 时校验时间顺序。 |
| `campaign_tag` | 字符串 | 条件必填 | 活动标签。模板为 `CAMPAIGN` 且范围为 `CAMPAIGN_PRODUCTS` 时必填。 |
| `region_value` | 字符串数组 | 条件必填 | 地区编码数组。`SPECIAL_REGIONS` 时必填且非空，元素取自 `listFreeShippingRegions` 的 `value`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `delivery_option` | 字符串 | 必填 | 配送选项编码，取自 `listShippingOptions` 的 `value`。 |
| `discount_type` | 字符串 | 必填 | 运费补贴类型。可选 `FULL_SUBSIDY` 或 `PARTIAL_SUBSIDY`。 |
| `deal_criteria` | 字符串 | 必填 | 补贴门槛类型。可选 `MONEY_VALUE_FROM_X`、`ITEM_QUANTITY_FROM_X`、`NO_CONDITION`。 |
| `tiers` | 对象数组 | 必填 | 非空优惠层级数组。 |
| `tiers[].filter` | 字符串 | 必填 | 该层的门槛值，按 `deal_criteria` 表示金额、件数或无门槛。 |
| `tiers[].result` | 字符串 | 条件必填 | 该层运费补贴值。`PARTIAL_SUBSIDY` 时必填。 |

`data.data` 为[促销写入返回的活动 ID](#促销写入返回的活动-id)。`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fupdate)

## activateFreeShipping

上游 `POST /promotion/freeshipping/activate`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Factivate)

## deactivateFreeShipping

上游 `POST /promotion/freeshipping/deactivate`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fdeactivate)

## listFreeShippingProducts

上游 `GET /promotion/freeshipping/products/get`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `curPage` | 数字 | 可选 | 页码。 |
| `pageSize` | 数字 | 可选 | 每页条数。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为[活动商品](#活动商品)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fproducts%2Fget)

## addFreeShippingSkus

上游 `POST /promotion/freeshipping/product/sku/add`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

`data.data` 为[添加 SKU 失败清单](#添加-sku-失败清单)。结果判定见[写入与续查](#写入与续查)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fproduct%2Fsku%2Fadd)

## removeFreeShippingSkus

上游 `POST /promotion/freeshipping/product/sku/remove`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fproduct%2Fsku%2Fremove)

## listFreeShippingRegions

上游 `GET /promotion/freeshipping/regions/get`。只读。

无 `params` 业务字段。

`data.data[]` 的每项为[包邮选项](#包邮选项)，表示地区。数组可能为空。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fregions%2Fget)

## listShippingOptions

上游 `GET /promotion/freeshipping/deliveryoptions/get`。只读。

无 `params` 业务字段。

`data.data[]` 的每项为[包邮选项](#包邮选项)，表示配送方式。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fdeliveryoptions%2Fget)

## listFlexiCombo

上游 `GET /promotion/flexicombo/list`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `cur_page` | 数字 | 必填 | 页码。 |
| `name` | 字符串 | 可选 | 按活动名称筛选。 |
| `page_size` | 数字 | 必填 | 每页条数。 |
| `status` | 字符串 | 可选 | 活动状态。可选 `NOT_START`、`ONGOING`、`SUSPEND`、`FINISH`。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为[组合促销](#组合促销)。 网关亦接受上游兼容形态 `data.data.data.dataList[]`，保留该包装。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Flist)

## getFlexiCombo

上游 `GET /promotion/flexicombo/details`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.data` 为[组合促销](#组合促销)对象。网关亦接受上游兼容形态 `data.data.data.id`，保留该包装。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fdetails)

## createFlexiCombo

上游 `POST /promotion/flexicombo/create`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `apply` | 字符串 | 必填 | 适用范围。创建接口的官方定义为 `ENTIRE_STORE` 或 `SPECIFIC_PRODUCTS`。 |
| `sample_skus` | 对象数组 | 可选 | 试用装商品与 SKU 清单。子字段使用驼峰命名。 |
| `sample_skus[].productId` | 数字 | 可选 | 商品 ID，整数。 |
| `sample_skus[].skuId` | 数字 | 可选 | SKU ID，整数。 |
| `criteria_type` | 字符串 | 必填 | 门槛类型。可选 `AMOUNT` 或 `QUANTITY`。 |
| `criteria_value` | 字符串数组 | 必填 | 各层门槛值，非空字符串数组。 |
| `order_numbers` | 数字 | 必填 | 可使用此组合活动的订单数量，整数。 |
| `name` | 字符串 | 必填 | 组合促销名称。 |
| `platform_channel` | 字符串 | 可选 | 平台渠道标识，使用字符串。官方默认值为 `"1"`。 |
| `gift_skus` | 对象数组 | 可选 | 赠品商品与 SKU 清单。子字段使用驼峰命名。 |
| `gift_skus[].productId` | 数字 | 可选 | 商品 ID，整数。 |
| `gift_skus[].skuId` | 数字 | 可选 | SKU ID，整数。 |
| `start_time` | 数字 | 必填 | 开始时间，Unix 毫秒时间戳。 |
| `discount_type` | 字符串 | 必填 | 折扣类型。可选 `money`、`discount`、`freeGift`、`freeSample`、`discountWithGift`、`moneyWithGift`、`discountWithSample`、`moneyWithSample`。 |
| `end_time` | 数字 | 必填 | 结束时间，Unix 毫秒时间戳，须晚于开始时间。 |
| `discount_value` | 字符串数组 | 必填 | 各层折扣值，非空字符串数组。 |
| `stackable` | 字符串 | 可选 | 是否按档位叠加折扣，官方请求示例使用字符串 `"false"`。 |
| `gift_buy_limit_value` | 字符串数组 | 可选 | 每层买家可选的赠品或试用装数量上限。 |

`data.data` 为[促销写入返回的活动 ID](#促销写入返回的活动-id)。`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fcreate)

## updateFlexiCombo

上游 `POST /promotion/flexicombo/update`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `apply` | 字符串 | 必填 | 适用范围。可选 `ENTIRE_SHOP` 或 `SPECIFIC_PRODUCTS`。 |
| `sample_skus` | 对象数组 | 可选 | 试用装商品与 SKU 清单。子字段使用驼峰命名。 |
| `sample_skus[].productId` | 数字 | 可选 | 商品 ID，整数。 |
| `sample_skus[].skuId` | 数字 | 可选 | SKU ID，整数。 |
| `criteria_type` | 字符串 | 必填 | 门槛类型。可选 `AMOUNT` 或 `QUANTITY`。 |
| `criteria_value` | 字符串数组 | 必填 | 各层门槛值，非空字符串数组。 |
| `order_numbers` | 数字 | 必填 | 可使用此组合活动的订单数量，整数。 |
| `name` | 字符串 | 必填 | 组合促销名称。 |
| `platform_channel` | 字符串 | 可选 | 平台渠道标识，使用字符串。 |
| `gift_skus` | 对象数组 | 可选 | 赠品商品与 SKU 清单。子字段使用驼峰命名。 |
| `gift_skus[].productId` | 数字 | 可选 | 商品 ID，整数。 |
| `gift_skus[].skuId` | 数字 | 可选 | SKU ID，整数。 |
| `start_time` | 数字 | 必填 | 开始时间，Unix 毫秒时间戳。 |
| `discount_type` | 字符串 | 必填 | 折扣类型。可选 `money`、`discount`、`freeGift`、`freeSample`、`discountWithGift`、`moneyWithGift`、`discountWithSample`、`moneyWithSample`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `end_time` | 数字 | 必填 | 结束时间，Unix 毫秒时间戳，须晚于开始时间。 |
| `discount_value` | 字符串数组 | 必填 | 各层折扣值，非空字符串数组。 |
| `stackable` | 字符串 | 可选 | 是否按档位叠加折扣，官方请求示例使用字符串 `"false"`。 |
| `gift_buy_limit_value` | 字符串数组 | 可选 | 每层买家可选的赠品或试用装数量上限。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fupdate)

## activateFlexiCombo

上游 `POST /promotion/flexicombo/activate`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Factivate)

## deactivateFlexiCombo

上游 `POST /promotion/flexicombo/deactivate`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fdeactivate)

## listFlexiComboProducts

上游 `GET /promotion/flexicombo/products/list`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `cur_page` | 数字 | 必填 | 页码。 |
| `page_size` | 数字 | 必填 | 每页条数，官方范围 10–100。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为SKU ID。官方定义为数字数组，空数组表示该页无 SKU。 网关亦接受上游兼容形态 `data.data.data.dataList[]`，保留该包装。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fproducts%2Flist)

## addFlexiComboSkus

上游 `POST /promotion/flexicombo/products/add`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

`data.data` 为[添加 SKU 失败清单](#添加-sku-失败清单)。结果判定见[写入与续查](#写入与续查)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fproducts%2Fadd)

## removeFlexiComboSkus

上游 `POST /promotion/flexicombo/products/delete`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fproducts%2Fdelete)

## listSponsoredMaxCampaigns

上游 `GET /sponsor/solution/smax/searchSmaxCampaign`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `sceneId` | 数字 | 可选 | 广告场景标识。省略时同时查 SMAX 与 SMAX AA，`12021` 仅查 SMAX AA。 |

`data.result[]` 的每项为 [Sponsored Max 活动](#sponsored-max-活动)。诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.totalCount` | 整数或数字字符串 | 符合条件的活动数。 |
| `data.errorCode` | 字符串 | 活动列表接口的错误码，可能缺省。 |

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2FsearchSmaxCampaign)

## getSponsoredMaxOverview

上游 `GET /sponsor/solution/smax/report/getReportOverview`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `useRtTable` | 布尔值 | 必填 | 查询包含当天数据时传 `true`，否则传 `false`。 |
| `startDate` | 字符串 | 必填 | 开始日期，`YYYY-MM-DD`。 |
| `endDate` | 字符串 | 必填 | 结束日期，`YYYY-MM-DD`。 |
| `lastStartDate` | 字符串 | 必填 | 对比时段开始日期，`YYYY-MM-DD`。 |
| `lastEndDate` | 字符串 | 必填 | 对比时段结束日期，`YYYY-MM-DD`。 |

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.reportOverviewDetailDTO` | 对象 | 当前时段的[广告总览指标](#广告总览指标)，可能缺省。 |
| `data.result.lastReportOverviewDetailDTO` | 对象 | 对比时段的[广告总览指标](#广告总览指标)，可能缺省。 |

诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2Freport%2FgetReportOverview)

## getSponsoredMaxMetric

上游 `GET /sponsor/solution/smax/report/getReportOverviewMetric`。只读。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `metricType` | 数字 | 必填 | 指标编号。`1` 花费，`2` 曝光，`3` 点击，`4` 点击率，`5` 销量，`6` 收入，`7` 平均点击成本，`8` ROI，`9` 店铺订单，`10` 店铺加购，`11` 商品订单。 |
| `startDate` | 字符串 | 必填 | 开始日期，`YYYY-MM-DD`。 |
| `endDate` | 字符串 | 必填 | 结束日期，`YYYY-MM-DD`。 |
| `useRtTable` | 布尔值 | 必填 | 查询包含当天数据时传 `true`，否则传 `false`。 |

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.dateList` | 数字数组 | 时间坐标，元素为 Unix 毫秒时间戳。可能缺省。 |
| `data.result.hourList` | 数字数组 | 查询当天时的小时坐标。可能缺省。 |
| `data.result.metricList` | 字符串数组或数字数组 | 与时间坐标对应的指标值。可能缺省。 |

诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2Freport%2FgetReportOverviewMetric)

## createSponsoredMaxCampaign

上游 `POST /sponsor/solution/smax/addSMaxAASolution`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `campaignViewDTO` | 对象 | 必填 | SMAX AA 广告活动设置。 |
| `campaignViewDTO.campaignName` | 字符串 | 必填 | 广告活动名称。 |
| `campaignViewDTO.biddingType` | 字符串 | 必填 | 出价方式。`bcb` 按预算，`mcb` 按最高 CPC，`troi` 按目标 ROI。 |
| `campaignViewDTO.budget` | 字符串 | 必填 | 正数活动预算，使用十进制文本。三种出价方式都必填。 |
| `campaignViewDTO.maxBid` | 字符串 | 条件必填 | 最高点击出价，使用十进制文本。`mcb` 时必填且为正数。官方说明切换到其他出价方式会取消最高出价限制。 |
| `campaignViewDTO.userProperties` | 对象 | 条件必填 | 附加活动设置对象。`troi` 时须提供 `_iop_roas`。 |
| `campaignViewDTO.userProperties._iop_roas` | 十进制字符串 | 条件必填 | `troi` 的正数目标 ROI，例如 `"4"`。 |

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.campaignId` | 字符串 | 新广告活动 ID。 |
| `data.result.adgroupAndCreativeMap` | 对象 | 以广告组 ID 为键、以创意 ID 列表为值。 |

诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2FaddSMaxAASolution)

## updateSponsoredMaxCampaign

上游 `POST /sponsor/solution/smax/updateSmaxCampaign`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `campaignId` | 正整数或数字字符串 | 必填 | 广告活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `campaignName` | 字符串 | 可选 | 广告活动名称。 |
| `startDate` | 字符串 | 可选 | 开始日期，`YYYY-MM-DD`。 |
| `endDate` | 字符串 | 可选 | 结束日期，`YYYY-MM-DD`。 |
| `dayBudget` | 字符串 | 可选 | 正数日预算，使用十进制文本。 |
| `campaignObjective` | 数字 | 可选 | 广告活动目标编码。 |
| `switchStatus` | 数字 | 可选 | 活动开关状态编码，LinkFox 接受非负整数。按已确认的目标状态提交。 |
| `platform` | 数字数组 | 可选 | 投放平台编码的非空非负整数数组。 |
| `biddingType` | 字符串 | 可选 | 出价方式。`bcb` 按预算，`mcb` 按最高 CPC，`troi` 按目标 ROI。 |
| `maxBid` | 字符串 | 条件必填 | 最高点击出价，使用十进制文本。`mcb` 时必填且为正数。官方说明切换到其他出价方式会取消最高出价限制。 |
| `autoCreative` | 数字 | 可选 | 自动创意开关编码。 |
| `userProperties` | 对象 | 条件必填 | 附加活动设置对象。`troi` 时须提供 `_iop_roas`。 |
| `userProperties._iop_roas` | 十进制字符串 | 条件必填 | `troi` 的正数目标 ROI，例如 `"4"`。 |

`data.result` 为更新后的 [Sponsored Max 活动](#sponsored-max-活动)对象。诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2FupdateSmaxCampaign)

## setSponsoredMaxCampaignStatus

上游 `POST /sponsor/solution/smax/updateSmaxStatusWithoutAd`。写入。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `campaignId` | 正整数或数字字符串 | 必填 | 广告活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `switchStatus` | 数字 | 必填 | 活动开关状态编码，LinkFox 接受非负整数。按已确认的目标状态提交。 |

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result` | 整数或数字字符串 | 更新后的开关状态。LinkFox 在上游确认成功且返回值与 `switchStatus` 一致时确认写入。 |

诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2FupdateSmaxStatusWithoutAd)

## 响应对象字段

以下字段与响应路径中的对象或数组元素对应。条件字段以实际回包为准。

### 促销响应状态

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.success` | 布尔值或字符串 | Lazada 促销操作的成功标记。CLI 顶层 `success` 是独立的调用结果。 |
| `data.error_code` | 整数或字符串 | 促销业务错误码，可能为空或缺省。 |
| `data.error_msg` | 字符串 | 促销业务错误说明，可能为空或缺省。 |

### 促销写入返回的活动 ID

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.data` | 整数或数字字符串 | Lazada 返回的活动 ID。LinkFox 使用该 ID 和上游成功标记确认写入。 |

### 添加 SKU 失败清单

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.data` | 对象 | 以 SKU ID 字符串为键，以失败原因为值。没有失败项时返回空对象。 |

### 包邮选项

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | 字符串 | 地区或配送选项的显示名称。 |
| `value` | 字符串 | 用于设置包邮活动的地区或配送选项编码。 |

### Sponsored Max 响应状态

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.success` | 布尔值或字符串 | Lazada 广告接口的结果标记。CLI 顶层 `success` 是独立的调用结果。 |
| `data.analyseTraceId` | 字符串 | 用于排查上游结果的追踪标识，可能缺省。 |
| `data.errorMsg` | 字符串 | 广告接口的错误说明，可能为空或缺省。 |

### 促销分页对象

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `total` | 整数或数字字符串 | 符合条件的记录总数。 |
| `current` | 整数或数字字符串 | 当前页码。 |
| `page_size` | 整数或数字字符串 | 每页条数。 |
| `data_list` | 数组 | 当前页记录，元素类型见操作说明。兼容包装可能用 `dataList`。 |

### 优惠券

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | 字符串 | 活动 ID。 |
| `voucher_type` | 字符串 | 领取型或代码型优惠券。 |
| `voucher_name` | 字符串 | 优惠券名称。 |
| `voucher_code` | 字符串 | 优惠券兑换码，按券类型返回。 |
| `apply` | 字符串 | 适用范围。 |
| `status` | 字符串 | 活动状态。 |
| `collect_start` | 整数或数字字符串 | 开始领券时间，Unix 毫秒。 |
| `period_start_time` | 整数或数字字符串 | 可使用起始时间，Unix 毫秒。 |
| `period_end_time` | 整数或数字字符串 | 可使用结束时间，Unix 毫秒。 |
| `display_area` | 字符串 | 买家可见渠道。 |
| `voucher_discount_type` | 字符串 | 优惠类型。 |
| `criteria_over_money` | 十进制字符串 | 订单门槛金额。 |
| `offering_money_value_off` | 十进制字符串 | 固定优惠金额。 |
| `offering_percentage_discount_off` | 数字或数字字符串 | 比例折扣值。 |
| `max_discount_offering_money_value` | 十进制字符串 | 比例折扣的单笔上限。 |
| `order_used_budget` | 数字或数字字符串 | 已使用金额。 |
| `currency` | 字符串 | 币种。 |
| `limit` | 整数或数字字符串 | 每位买家的上限。 |
| `issued` | 整数或数字字符串 | 发放数量。 |

### 活动商品

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `product_id` | 字符串 | 商品 ID。 |
| `sku_ids` | 字符串数组 | 商品下的 SKU ID。 |

### 包邮活动

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | 字符串 | 活动 ID。 |
| `promotion_name` | 字符串 | 活动名称。 |
| `status` | 字符串 | 活动状态。 |
| `apply` | 字符串 | 适用范围。 |
| `template_type` | 字符串 | 模板类型。 |
| `template_code` | 字符串 | 模板编码，模板活动适用。 |
| `category_name` | 字符串 | 类目字段。 |
| `campaign_tag` | 字符串 | 活动标签。 |
| `budget_type` | 字符串 | 预算类型。 |
| `budget_value` | 十进制字符串 | 预算金额。 |
| `used_budget_value` | 十进制字符串 | 已使用预算。 |
| `currency` | 字符串 | 币种。 |
| `period_type` | 字符串 | 活动期限类型。 |
| `period_start_time` | 整数或数字字符串 | 活动起始时间，Unix 毫秒。 |
| `period_end_time` | 整数或数字字符串 | 活动结束时间，Unix 毫秒。 |
| `region_type` | 字符串 | 地区范围类型。 |
| `region_value` | 字符串数组 | 指定地区的编码。 |
| `platform_channel` | 字符串 | 渠道标识。 |
| `delivery_option` | 字符串 | 配送方式编码。 |
| `promo_tier` | 对象 | 补贴层级配置。 |
| `promo_tier.discount_type` | 字符串 | 补贴类型。 |
| `promo_tier.deal_criteria` | 字符串 | 门槛类型。 |
| `promo_tier.tiers` | 对象数组 | 各层级补贴。 |
| `promo_tier.tiers[].filter` | 字符串 | 该层门槛值。 |
| `promo_tier.tiers[].result` | 字符串 | 该层补贴值，部分补贴时适用。 |

### 组合促销

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | 字符串 | 活动 ID。 |
| `name` | 字符串 | 活动名称。 |
| `type` | 字符串 | 活动类型。 |
| `apply` | 字符串 | 适用范围。 |
| `status` | 字符串 | 活动状态。 |
| `criteria_type` | 字符串 | 金额或件数门槛。 |
| `criteria_value` | 字符串数组 | 各档位门槛。 |
| `discount_type` | 字符串 | 折扣类型。 |
| `discount_value` | 字符串数组 | 各档位折扣值。 |
| `platform_channel` | 字符串 | 平台渠道标识。 |
| `order_numbers` | 整数或数字字符串 | 可用订单数量。 |
| `order_used_numbers` | 整数或数字字符串 | 已使用订单数量，可能缺省。 |
| `start_time` | 整数或数字字符串 | 活动开始时间，Unix 毫秒。 |
| `end_time` | 整数或数字字符串 | 活动结束时间，Unix 毫秒。 |
| `stackable` | 布尔值或布尔字符串 | 是否按档位叠加，可能缺省。 |
| `gift_buy_limit_value` | 字符串数组 | 各档位的赠品或试用装数量上限，可能缺省。 |
| `sample_skus` | 对象数组 | 试用装清单。每项包含 `product_id`、`sku_id`，详情可含 `tier`。 |
| `gift_skus` | 对象数组 | 赠品清单。每项包含 `product_id`、`sku_id`，详情可含 `tier`。 |
| `sample_skus[].product_id`、`gift_skus[].product_id` | 字符串 | 商品 ID。 |
| `sample_skus[].sku_id`、`gift_skus[].sku_id` | 字符串 | SKU ID。 |
| `sample_skus[].tier`、`gift_skus[].tier` | 整数或数字字符串 | 所在层级，可能缺省。 |

### Sponsored Max 活动

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `campaignId` | 字符串 | 广告活动 ID。 |
| `campaignName` | 字符串 | 广告活动名称。 |
| `campaignType` | 整数或数字字符串 | `1` 手动，`2` 自动。 |
| `campaignModel` | 整数或数字字符串 | 广告活动模型编码。 |
| `campaignObjective` | 整数或数字字符串 | 广告活动目标编码。 |
| `onlineStatus` | 整数或数字字符串 | 在线状态。 |
| `switchStatus` | 整数或数字字符串 | 开关状态。 |
| `autoCreative` | 整数或数字字符串 | 自动创意开关。 |
| `sceneId` | 字符串 | 广告场景标识。 |
| `version` | 整数或数字字符串 | 活动版本。 |
| `startDate` | 字符串 | 活动开始日期。 |
| `endDate` | 字符串 | 活动结束日期。 |
| `platform` | 整数数组 | 投放平台列表。 |
| `biddingType` | 字符串 | 出价方式。 |
| `maxBid` | 十进制字符串 | 最高点击出价。 |
| `budget` | 十进制字符串 | 活动预算。 |
| `budgetUsedAmount` | 十进制字符串 | 已使用预算。 |
| `totalCost` | 十进制字符串 | 总花费。 |
| `clicks` | 整数或数字字符串 | 总点击数。 |
| `smaxAaColdStartStatus` | 字符串 | SMAX AA 冷启动状态。 |
| `budgetViewDTO` | 对象 | 预算详情。官方接口未列出子字段。 |
| `userProperties` | 对象 | 附加设置，可能缺省。`_iop_roas` 为目标 ROI 字符串，`"-1"` 表示不适用。 |
| `campaignSettingViewDTO` | 对象 | 更新响应可能返回的活动设置。`iopRoas` 是目标 ROI 字符串，负值表示不适用。 |

### 广告总览指标

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `spend` | 十进制字符串 | 广告花费。 |
| `impressions` | 整数或数字字符串 | 曝光量。 |
| `clicks` | 整数或数字字符串 | 点击量。 |
| `ctr` | 十进制字符串 | 点击率。 |
| `unitsSold` | 整数或数字字符串 | 归因销量。 |
| `revenue` | 十进制字符串 | 归因收入，按买家实付口径含折扣、店铺积分、运费及附加费。 |
| `cpc` | 十进制字符串 | 平均每次点击成本。 |
| `roi` | 十进制字符串 | 广告投资回报。 |

## 错误处理

- HTTP、网关或上游失败时保留可用的错误码与请求标识。确认是 LinkFox Key 或计费问题后再按 [认证和算力指引](onboarding.md) 处理。
- `REAUTHORIZATION_REQUIRED` 时核对当前店铺授权。`LAZADA_PROXY_FORBIDDEN` 时由接入方核查代理出口。其他权限问题核对活动类型、广告账号和应用权限。
- 写入结果不明时保留原 UUID 并核对当前活动状态。


## Feedback

仅在用户同意后向反馈接口提交脱敏摘要。省略店铺标识、广告计划、业务数据及凭据。

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- 请求头 `Content-Type: application/json`

```json
{
  "skillName": "linkfox-lazada-store-marketing",
  "sentiment": "NEUTRAL",
  "category": "SUGGESTION",
  "content": "用户同意发送的脱敏反馈摘要"
}
```
