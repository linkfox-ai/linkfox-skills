# Lazada 店铺营销与广告接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`。
- **请求方式**：POST JSON，HTTP 超时 150 秒。上游 method/path 见各操作；外层 POST 不表示业务写入。
- **请求头**：`Content-Type: application/json`、`Accept: application/json`、`User-Agent: LinkFox-Skill/2.0`、`Authorization: <api_key>`。
- Key 优先取 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`。`SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 原样透传，缺省为空字符串。
- 店铺令牌由后端管理。`connectionId` 必须属于当前 LinkFox 用户，站点由该连接确定。CLI 输入和保存结果见 [script-usage.md](script-usage.md)，不属于额外网关字段。

### 响应码基本规则

- **正常响应**：HTTP 200–299，且 `errcode` 缺失、为 null、为空字符串或纯空白，或为 200–299 的整数／数字字符串；再按各接口检查业务结果。
- **未正常响应**：HTTP 非 2xx 或 `errcode` 为其他非空值。`0`、`false` 不视为空；HTTP 200 的 XML `ToolErrorResponse` 或非 JSON 正文不作为业务成功。
- **认证或用量错误**：401／402 结合 `errmsg` 定位；确认是 LinkFox Key 或计费问题后，按 [onboarding.md](onboarding.md) 处理。店铺授权、应用权限、站点和代理限制分别核查，不引导重复注册充值。
- 上游 HTTP 和业务码由后端判定；网关不返回独立 `httpStatus`，不要把 CLI 诊断字段当作上游 HTTP 状态。合法空数组／空页可成功，缺失结构不擅自当空结果。

### 网关错误响应

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | 整数或数字字符串 | 网关错误码，HTTP 200 也可能为业务失败。 |
| `errmsg` | 字符串 | 网关或经后端处理的上游错误说明。CLI 只输出可安全保留的诊断，见脚本参考。 |

`1002` 表示身份或参数问题，`1004` 表示当前用户未拥有对应申请／连接；结合消息确认具体对象。原始错误正文不进入报告或反馈。

### 业务操作请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 当前用户的店铺连接 ID，最长 36 字符。 |
| `operation` | 字符串 | 是 | 对应操作名称，最长 64 字符；不能传任意上游路径。 |
| `params` | 对象 | 按操作 | 仅传当前操作列出的字段；无参数时可省略，按 `{}` 处理。对象、数组和字符串化 JSON 的类型按下表保留。 |
| `requestId` | UUID 字符串 | 写入必填 | 带连字符，最长 36 字符；只读操作不传。与响应中的上游 `requestId` 不同。 |

对象、数组在紫鸟 POST 代理参数中按约定编码成 JSON 文本；接口要求的 XML／JSON 文本放在字符串字段中，不提前编码普通对象。普通 `params` 序列化大小上限为 1 MiB；素材接口限制见各操作。

### 网关成功响应

成功响应为下表对象；网关部署可能将该对象放在外层 `data` 中。下文 `data.*` 从本表的业务 `data` 开始，外层包装单独判断。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data` | 对象、数组或操作定义的标量／null | 业务结果。写记录续查／重复提交可能为 null，不能据此推断未执行。 |
| `requestId` | 字符串或 null | Lazada 上游请求标识。 |
| `clientRequestId` | 字符串，可缺省 | 写操作原 UUID；只读代理查询不返回此字段。 |
| `status` | 字符串，可缺省 | 写记录状态；只读代理查询不返回此字段。 |

仅含业务 `data` 的上游响应由后端去除该层；仍含 `success`、`result`、`_trace_id_` 等独立字段时保留原业务层次。后端去除传输层 `code`、`type`、`message`、`msg` 及敏感字段。各操作的字段表注明实际路径；上游业务 `success` 与本地 CLI 顶层 `success` 含义不同，网关没有额外的 CLI 成功字段。

官方示例中的数字、布尔值可能为字符串，也可能返回 null 或字符串 `"null"`；保留实际类型，不把缺失值补成 0。LinkFox 将 `id`、`ids` 或 `idList` 结尾的整数字段转为字符串，其他字段按合同处理，避免损失长 ID 精度。

### 写入与续查

后端按当前用户、连接、原 `requestId` UUID 和请求内容识别重复提交。`PENDING` 按原 UUID 续查，`SUCCEEDED` 结合具体业务结果确认生效，`REJECTED` 核对拒绝原因，`PARTIAL` 逐项核对，`UNKNOWN` 核对店铺实际状态。结果不明时不自动重放，也不换 UUID 重试。

`requestId` 已用于不同操作／参数时为冲突；查不到写记录时核对当前用户、原连接和 UUID，并检查目标状态。状态查询的 HTTP 成功不等于原写入成功。

`addVoucherSkus`、`addFreeShippingSkus` 和 `addFlexiComboSkus` 的上游 `data` 是以 SKU ID 为键的失败清单。空对象表示没有失败项，部分 SKU 出现在清单中时为 `PARTIAL`，全部出现时为 `REJECTED`。

错误码须结合具体操作解释。`createVoucher` 的 `23` 是业务校验失败；`createFlexiCombo`、`updateFlexiCombo` 的 `22` 是参数无效。组合促销的 `21` 是内部错误，`23` 仅说明创建或更新失败，保留 `UNKNOWN` 并用原请求编号核实，不自动重试。其他营销操作没有明确错误码定义时，不借用这些含义。[优惠券错误码](https://open.lazada.com/apps/doc/api?path=%2Fpromotion%2Fvoucher%2Fcreate) · [组合促销错误码](https://open.lazada.com/apps/doc/api?path=%2Fpromotion%2Fflexicombo%2Fcreate)

`LAZADA_REQUEST_ID_CONFLICT` 时检查原 UUID 与原请求参数。`LAZADA_OPERATION_NOT_FOUND` 时核对店铺连接和 UUID，并检查目标当前状态。

## 接口：listVouchers

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/vouchers/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listVouchers`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `cur_page` | 数字 | 可选 | 页码。 |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `name` | 字符串 | 可选 | 按活动名称筛选。 |
| `page_size` | 数字 | 可选 | 每页条数。 |
| `status` | 字符串 | 可选 | 活动状态。可选 `NOT_START`、`ONGOING`、`SUSPEND`、`FINISH`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为[优惠券](#优惠券)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvouchers%2Fget)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。
- 上游仅返回 `code=0`、`data={}`，缺少分页对象和列表时，不能证明是合法空页；网关返回结构异常，保留请求标识供核对，不补造活动列表或分页值。

## 接口：getVoucher

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/voucher/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getVoucher`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[优惠券](#优惠券)对象。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fget)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：createVoucher

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/voucher/create`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=createVoucher`；下表列出 `params` 内部字段。

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

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 字符串 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销写入返回的活动 ID](#促销写入返回的活动-id)。`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fcreate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：updateVoucher

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/voucher/update`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=updateVoucher`；下表列出 `params` 内部字段。

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

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 字符串 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销写入返回的活动 ID](#促销写入返回的活动-id)。`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fupdate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：activateVoucher

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/voucher/activate`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=activateVoucher`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.success` | 布尔值或字符串 | 上游成功标记，见 [促销响应状态](#促销响应状态)。 |
| `data.error_code`、`data.error_msg` | 字符串 | 上游诊断，可能缺省。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Factivate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：deactivateVoucher

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/voucher/deactivate`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=deactivateVoucher`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.success` | 布尔值或字符串 | 上游成功标记，见 [促销响应状态](#促销响应状态)。 |
| `data.error_code`、`data.error_msg` | 字符串 | 上游诊断，可能缺省。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fdeactivate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：listVoucherProducts

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/voucher/products/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listVoucherProducts`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `cur_page` | 数字 | 可选 | 页码。 |
| `page_size` | 数字 | 可选 | 每页条数。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为[活动商品](#活动商品)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fproducts%2Fget)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：addVoucherSkus

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/voucher/product/sku/add`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=addVoucherSkus`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[添加 SKU 失败清单](#添加-sku-失败清单)。结果判定见[写入与续查](#接口查询写入状态operationstatus)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fproduct%2Fsku%2Fadd)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：removeVoucherSkus

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/voucher/product/sku/remove`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=removeVoucherSkus`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `voucher_type` | 字符串 | 必填 | 优惠券类型。可选 `COLLECTIBLE_VOUCHER` 或 `CODE_VOUCHER`。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.success` | 布尔值或字符串 | 上游成功标记，见 [促销响应状态](#促销响应状态)。 |
| `data.error_code`、`data.error_msg` | 字符串 | 上游诊断，可能缺省。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fvoucher%2Fproduct%2Fsku%2Fremove)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：listFreeShipping

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/freeshippings/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listFreeShipping`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `curPage` | 数字 | 可选 | 页码。 |
| `name` | 字符串 | 可选 | 按活动名称筛选。 |
| `pageSize` | 数字 | 可选 | 每页条数。 |
| `status` | 字符串 | 可选 | 活动状态。可选 `NOT_START`、`ONGOING`、`SUSPEND`、`FINISH`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为[包邮活动](#包邮活动)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshippings%2Fget)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：getFreeShipping

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/freeshipping/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getFreeShipping`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[包邮活动](#包邮活动)对象。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fget)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：createFreeShipping

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/freeshipping/create`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=createFreeShipping`；下表列出 `params` 内部字段。

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

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 字符串 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销写入返回的活动 ID](#促销写入返回的活动-id)。`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fcreate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：updateFreeShipping

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/freeshipping/update`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=updateFreeShipping`；下表列出 `params` 内部字段。

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

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 字符串 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销写入返回的活动 ID](#促销写入返回的活动-id)。`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fupdate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：activateFreeShipping

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/freeshipping/activate`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=activateFreeShipping`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.success` | 布尔值或字符串 | 上游成功标记，见 [促销响应状态](#促销响应状态)。 |
| `data.error_code`、`data.error_msg` | 字符串 | 上游诊断，可能缺省。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Factivate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：deactivateFreeShipping

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/freeshipping/deactivate`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=deactivateFreeShipping`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.success` | 布尔值或字符串 | 上游成功标记，见 [促销响应状态](#促销响应状态)。 |
| `data.error_code`、`data.error_msg` | 字符串 | 上游诊断，可能缺省。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fdeactivate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：listFreeShippingProducts

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/freeshipping/products/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listFreeShippingProducts`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `curPage` | 数字 | 可选 | 页码。 |
| `pageSize` | 数字 | 可选 | 每页条数。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为[活动商品](#活动商品)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fproducts%2Fget)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：addFreeShippingSkus

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/freeshipping/product/sku/add`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=addFreeShippingSkus`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[添加 SKU 失败清单](#添加-sku-失败清单)。结果判定见[写入与续查](#接口查询写入状态operationstatus)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fproduct%2Fsku%2Fadd)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：removeFreeShippingSkus

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/freeshipping/product/sku/remove`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=removeFreeShippingSkus`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.success` | 布尔值或字符串 | 上游成功标记，见 [促销响应状态](#促销响应状态)。 |
| `data.error_code`、`data.error_msg` | 字符串 | 上游诊断，可能缺省。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fproduct%2Fsku%2Fremove)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：listFreeShippingRegions

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/freeshipping/regions/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listFreeShippingRegions`；下表列出 `params` 内部字段。

无 `params` 业务字段。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `params` | 对象 | 否 | 本操作无业务参数，可省略或传 `{}`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象数组 | 业务结果，完整模型和字段见下方链接。 |

`data.data[]` 的每项为[包邮选项](#包邮选项)，表示地区。数组可能为空。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fregions%2Fget)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：listShippingOptions

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/freeshipping/deliveryoptions/get`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listShippingOptions`；下表列出 `params` 内部字段。

无 `params` 业务字段。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `params` | 对象 | 否 | 本操作无业务参数，可省略或传 `{}`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象数组 | 业务结果，完整模型和字段见下方链接。 |

`data.data[]` 的每项为[包邮选项](#包邮选项)，表示配送方式。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Ffreeshipping%2Fdeliveryoptions%2Fget)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：listFlexiCombo

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/flexicombo/list`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listFlexiCombo`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `cur_page` | 数字 | 必填 | 页码。 |
| `name` | 字符串 | 可选 | 按活动名称筛选。 |
| `page_size` | 数字 | 必填 | 每页条数。 |
| `status` | 字符串 | 可选 | 活动状态。可选 `NOT_START`、`ONGOING`、`SUSPEND`、`FINISH`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为[组合促销](#组合促销)。 网关亦接受上游兼容形态 `data.data.data.dataList[]`，保留该包装。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Flist)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：getFlexiCombo

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/flexicombo/details`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getFlexiCombo`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[组合促销](#组合促销)对象。网关亦接受上游兼容形态 `data.data.data.id`，保留该包装。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fdetails)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：createFlexiCombo

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/flexicombo/create`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=createFlexiCombo`；下表列出 `params` 内部字段。

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

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 字符串 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销写入返回的活动 ID](#促销写入返回的活动-id)。`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fcreate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：updateFlexiCombo

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/flexicombo/update`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=updateFlexiCombo`；下表列出 `params` 内部字段。

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

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.success` | 布尔值或字符串 | 上游成功标记，见 [促销响应状态](#促销响应状态)。 |
| `data.error_code`、`data.error_msg` | 字符串 | 上游诊断，可能缺省。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fupdate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：activateFlexiCombo

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/flexicombo/activate`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=activateFlexiCombo`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.success` | 布尔值或字符串 | 上游成功标记，见 [促销响应状态](#促销响应状态)。 |
| `data.error_code`、`data.error_msg` | 字符串 | 上游诊断，可能缺省。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Factivate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：deactivateFlexiCombo

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/flexicombo/deactivate`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=deactivateFlexiCombo`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.success` | 布尔值或字符串 | 上游成功标记，见 [促销响应状态](#促销响应状态)。 |
| `data.error_code`、`data.error_msg` | 字符串 | 上游诊断，可能缺省。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fdeactivate)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：listFlexiComboProducts

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /promotion/flexicombo/products/list`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listFlexiComboProducts`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `cur_page` | 数字 | 必填 | 页码。 |
| `page_size` | 数字 | 必填 | 每页条数，官方范围 10–100。 |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[促销分页对象](#促销分页对象)，其中 `data_list[]` 为SKU ID。官方定义为数字数组，空数组表示该页无 SKU。 网关亦接受上游兼容形态 `data.data.data.dataList[]`，保留该包装。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fproducts%2Flist)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：addFlexiComboSkus

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/flexicombo/products/add`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=addFlexiComboSkus`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.data` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.data` 为[添加 SKU 失败清单](#添加-sku-失败清单)。结果判定见[写入与续查](#接口查询写入状态operationstatus)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fproducts%2Fadd)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：removeFlexiComboSkus

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /promotion/flexicombo/products/delete`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=removeFlexiComboSkus`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | 正整数或数字字符串 | 必填 | 从当前店铺查询取得的活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `sku_ids` | 整数数组 | 必填 | 当前店铺实际 SKU ID 的非空正整数数组，保留原整数精度。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.success` | 布尔值或字符串 | 上游成功标记，见 [促销响应状态](#促销响应状态)。 |
| `data.error_code`、`data.error_msg` | 字符串 | 上游诊断，可能缺省。 |

`data.success`、`data.error_code` 和 `data.error_msg` 的类型见[促销响应状态](#促销响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fpromotion%2Fflexicombo%2Fproducts%2Fdelete)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：listSponsoredMaxCampaigns

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /sponsor/solution/smax/searchSmaxCampaign`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=listSponsoredMaxCampaigns`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `sceneId` | 数字 | 可选 | 广告场景标识。省略时同时查 SMAX 与 SMAX AA，`12021` 仅查 SMAX AA。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

`data.result[]` 的每项为 [Sponsored Max 活动](#sponsored-max-活动)。诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.totalCount` | 整数或数字字符串 | 符合条件的活动数。 |
| `data.errorCode` | 字符串 | 活动列表接口的错误码，可能缺省。 |

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2FsearchSmaxCampaign)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：getSponsoredMaxOverview

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /sponsor/solution/smax/report/getReportOverview`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getSponsoredMaxOverview`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `useRtTable` | 布尔值 | 必填 | 查询包含当天数据时传 `true`，否则传 `false`。 |
| `startDate` | 字符串 | 必填 | 开始日期，`YYYY-MM-DD`。 |
| `endDate` | 字符串 | 必填 | 结束日期，`YYYY-MM-DD`。 |
| `lastStartDate` | 字符串 | 必填 | 对比时段开始日期，`YYYY-MM-DD`。 |
| `lastEndDate` | 字符串 | 必填 | 对比时段结束日期，`YYYY-MM-DD`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.reportOverviewDetailDTO` | 对象 | 当前时段的[广告总览指标](#广告总览指标)，可能缺省。 |
| `data.result.lastReportOverviewDetailDTO` | 对象 | 对比时段的[广告总览指标](#广告总览指标)，可能缺省。 |

诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2Freport%2FgetReportOverview)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：getSponsoredMaxMetric

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`GET /sponsor/solution/smax/report/getReportOverviewMetric`。本操作为只读。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=getSponsoredMaxMetric`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `metricType` | 数字 | 必填 | 指标编号。`1` 花费，`2` 曝光，`3` 点击，`4` 点击率，`5` 销量，`6` 收入，`7` 平均点击成本，`8` ROI，`9` 店铺订单，`10` 店铺加购，`11` 商品订单。 |
| `startDate` | 字符串 | 必填 | 开始日期，`YYYY-MM-DD`。 |
| `endDate` | 字符串 | 必填 | 结束日期，`YYYY-MM-DD`。 |
| `useRtTable` | 布尔值 | 必填 | 查询包含当天数据时传 `true`，否则传 `false`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.dateList` | 数字数组 | 时间坐标，元素为 Unix 毫秒时间戳。可能缺省。 |
| `data.result.hourList` | 数字数组 | 查询当天时的小时坐标。可能缺省。 |
| `data.result.metricList` | 字符串数组或数字数组 | 与时间坐标对应的指标值。可能缺省。 |

诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2Freport%2FgetReportOverviewMetric)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 正常响应后仍按本节响应结构判断业务结果；格式缺失不补造数据。

## 接口：createSponsoredMaxCampaign

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /sponsor/solution/smax/addSMaxAASolution`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=createSponsoredMaxCampaign`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `campaignViewDTO` | 对象 | 必填 | SMAX AA 广告活动设置。 |
| `campaignViewDTO.campaignName` | 字符串 | 必填 | 广告活动名称。 |
| `campaignViewDTO.biddingType` | 字符串 | 必填 | 出价方式。`bcb` 按预算，`mcb` 按最高 CPC，`troi` 按目标 ROI。 |
| `campaignViewDTO.budget` | 字符串 | 必填 | 正数活动预算，使用十进制文本。三种出价方式都必填。 |
| `campaignViewDTO.maxBid` | 字符串 | 条件必填 | 最高点击出价，使用十进制文本。`mcb` 时必填且为正数。官方说明切换到其他出价方式会取消最高出价限制。 |
| `campaignViewDTO.userProperties` | 对象 | 条件必填 | 附加活动设置对象。`troi` 时须提供 `_iop_roas`。 |
| `campaignViewDTO.userProperties._iop_roas` | 十进制字符串 | 条件必填 | `troi` 的正数目标 ROI，例如 `"4"`。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result.campaignId` | 字符串 | 新广告活动 ID。 |
| `data.result.adgroupAndCreativeMap` | 对象 | 以广告组 ID 为键、以创意 ID 列表为值。 |

诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2FaddSMaxAASolution)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：updateSponsoredMaxCampaign

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /sponsor/solution/smax/updateSmaxCampaign`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=updateSponsoredMaxCampaign`；下表列出 `params` 内部字段。

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

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.result` | 对象 | 业务结果，完整模型和字段见下方链接。 |

`data.result` 为更新后的 [Sponsored Max 活动](#sponsored-max-活动)对象。诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2FupdateSmaxCampaign)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 接口：setSponsoredMaxCampaignStatus

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/marketing`。
- **上游方法与路径**：`POST /sponsor/solution/smax/updateSmaxStatusWithoutAd`。本操作为写入。

### 请求参数

公共顶层字段见 [业务操作请求字段](api.md#业务操作请求字段)。本操作 `operation=setSponsoredMaxCampaignStatus`；下表列出 `params` 内部字段。

| `params` 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `campaignId` | 正整数或数字字符串 | 必填 | 广告活动 ID。LinkFox 接受正整数或 1–20 位数字字符串。 |
| `switchStatus` | 数字 | 必填 | 活动开关状态编码，LinkFox 接受非负整数。按已确认的目标状态提交。 |

### 响应结构

公共响应 envelope 见 [网关成功响应](api.md#网关成功响应)。以下为该业务结果的字段与含义。

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.result` | 整数或数字字符串 | 更新后的开关状态。LinkFox 在上游确认成功且返回值与 `switchStatus` 一致时确认写入。 |

诊断字段见 [Sponsored Max 响应状态](#sponsored-max-响应状态)。

[Lazada 官方接口定义](https://isvconsole.lazada.com/handler/share/apidoc/getApi.json?path=%2Fsponsor%2Fsolution%2Fsmax%2FupdateSmaxStatusWithoutAd)

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 按 [写入与续查](api.md#接口查询写入状态operationstatus) 核对原写记录及本节业务字段，不以 HTTP 200 单独判断业务完成。

## 响应对象字段

以下字段与响应路径中的对象或数组元素对应。条件字段以实际回包为准。

### 促销响应状态

| 响应字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.success` | 布尔值或字符串 | Lazada 促销操作的成功标记。本字段为上游业务标记。 |
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
| `data.success` | 布尔值或字符串 | Lazada 广告接口的结果标记。本字段为上游业务标记。 |
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
- Sponsored Max 返回 `seller did not sign` 时，提示在 Lazada 卖家中心开通并同意对应广告服务协议；这不表示店铺 OAuth 授权失效。
- 写入结果不明时保留原 UUID 并核对当前活动状态。

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。仅发送用户授权的脱敏摘要，不含凭据或原始业务数据。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-lazada-store-marketing",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```


## 接口：查询写入状态（operationStatus）

### 调用规范

- 基本规则参考 [公共规则](api.md#公共规则) → 调用规范。
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/lazada/operationStatus`。读取 LinkFox 已有写记录，不重新调用上游写接口。

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `connectionId` | 字符串 | 是 | 原写入的店铺连接，最长 36 字符。 |
| `requestId` | UUID 字符串 | 是 | 原写入 UUID，最长 36 字符。 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `data` | null | 查询已存写记录不重取业务结果。 |
| `requestId` | 字符串或 null | 已存上游请求标识。 |
| `clientRequestId` | 字符串 | 原写入 UUID。 |
| `status` | 字符串 | `PENDING`、`SUCCEEDED`、`REJECTED`、`PARTIAL` 或 `UNKNOWN`。 |

### 响应码规则

- 基本规则参考 [公共规则](api.md#响应码基本规则) → 响应码基本规则。
- 查询成功不等于写入成功。按 [写入与续查](api.md#接口查询写入状态operationstatus) 处理原状态；记录不存在时核对原用户、连接及 UUID，不换 UUID 自动重放。
