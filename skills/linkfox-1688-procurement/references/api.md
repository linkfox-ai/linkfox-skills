# 1688 采购与订单履约 接口说明

## 公共规则

### 调用规范

- **请求基础地址**：`LINKFOX_TOOL_GATEWAY` 默认 `https://tool-gateway.linkfox.com`
- **请求方式**：POST, HTTP 超时 150s
- **请求头**
  - Content-Type: application/json
  - User-Agent: LinkFox-Skill/2.0
  - Authorization: <api_key> (<api_key> 从环境变量 `LINKFOX_AGENT_API_KEY` 或 `LINKFOXAGENT_API_KEY` 读取，未配置则按 SKILL.md 的 **## 解决认证和算力问题** 处理)

### 响应码基本规则

- **正常响应**: HTTP 状态码为 `200`–`299`，且响应体的 `errcode` 不存在、为 `null`、为空字符串（含纯空白）或为 `200`–`299`（数字或数字字符串）。
- **未正常响应**: HTTP 状态码不属于 `200`–`299`，或响应体的 `errcode` 为非空且不属于 `200`–`299` 的值；`0` 和 `false` 不视为空。
- **认证或用量错误**: HTTP 状态码为 `401` / `402`，按 onboarding.md 的指引处理
- **其他情况**: 依据响应体的 `errmsg` 判断具体原因

## 采购脚本运行约定

以下约定由同一业务封装实现，适用于本文件全部 14 个操作；各操作自己的字段与前检规则在各节定义。

| 选项 / 约定 | 类型 | 说明 |
|---|---|---|
| JSON 位置参数 | object | 直接传 JSON 对象字符串，非对象或无效 JSON 本地拒绝。 |
| --payload-env ENV_NAME | CLI option | 从环境变量读取 JSON，适用于 Windows；缺少变量名或变量未设置退出 1。 |
| --payload-file path.json | CLI option | 从 UTF-8 文件读取 JSON；同时使用时优先于环境变量，环境变量优先于位置参数。 |
| --inline | CLI flag | 强制全量打印脱敏响应，不隐含保存。 |
| --save / LINKFOX_SKILL_SAVE_RESPONSE | CLI flag / env | 强制保存脱敏响应；环境变量 1 / true / yes 生效。 |
| --no-save / LINKFOX_SKILL_NO_SAVE | CLI flag / env | 禁止保存；优先于所有强制保存及自动保存条件。 |
| --help / -h | CLI flag | 只展示帮助，不发请求。 |
| --no-cache | CLI flag | 兼容公共命令示例；无论是否传入，采购业务始终禁用缓存。 |
| 缓存 | 运行约定 | 采购业务不做响应缓存。封装每次调用 call_api.run 均传 --no-cache，授权、价格、库存、订单状态和物流以实时结果为准；写操作不得缓存或自动重放。 |
| 输出 | 运行约定 | 脱敏序列化后不超过 8000 字节默认直接完整输出、不保存；超过则默认保存完整脱敏响应并输出摘要。摘要包括顶层字段、状态/消息/消耗、最大列表长度及前 3 项。 |
| 保存目录 | 运行约定 | <writable-root>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-1688-procurement-<operation>-<timestamp>.json；根目录优先 ACPX_WORKSPACES 第一个工作区，其次 cwd，最后用户目录；均不可写时报错，禁止 /tmp 和系统临时目录。session 优先 SESSION_ID，否则进程内自动生成。 |
| 身份与网关 | 运行约定 | LINKFOX_AGENT_API_KEY 优先，兼容 LINKFOXAGENT_API_KEY；LINKFOX_TOOL_GATEWAY 可覆盖默认网关，移除末尾 /；保留 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 请求头。 |

### 采购脚本本地错误与脱敏

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 本地错误标识，可能为 authorization_required / confirmation_required / invalid_parameter，或连接/HTTP/JSON 错误消息。 |
| operation | string | 当前操作名，存在时保留。 |
| message | string | 本地错误说明，存在时保留。 |
| requiredField | string | 确认缺失字段，仅调试使用。 |
| field | string | 参数错误字段，仅调试使用。 |
| transportHttpStatus | integer / null | 仅 HTTP 非 2xx 或连接失败时附加，分别保留实际 HTTP 状态或 null；不据业务 success 推断传输状态。 |
| details | 原始 JSON / string | 非对象错误响应或无法解析的错误正文，原样保留并脱敏。 |
| authCheck | object | 授权拒绝时的检查结果。 |
| authCheck.endpoint | string | authorizedStores。 |
| authCheck.stores | array<object> | 授权检查的账号摘要列表。 |
| authCheck.stores[].accountName | string | 授权账号展示名。 |
| authCheck.stores[].status | string | 授权状态。 |
| authCheck.stores[].expired | boolean / string | 授权是否失效，保留后端实际返回类型。 |
| authCheck.raw | object | 脱敏后的原始授权检查响应。 |

输出及保存递归脱敏密钥、JWT、访问令牌、刷新令牌、callbackCode 等敏感键；删除 tokenExpiresAt（兼容连字符/下划线/大小写）。不得把这些秘密、完整地址、手机号或支付链接写入反馈。

## 接口：生成授权链接（authorizeUrl）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/authorizeUrl`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `accountName` | string | 是 | 授权账号展示名，用于标识本次 1688 OAuth 授权。 |

#### 脚本选项与运行约定

业务入口：`scripts/authorize_url.py`。本操作免除授权前检。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| authorizeUrl | string | 授权链接，供用户手动打开，不自动打开；不返回 token。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 发起授权不等于授权成功；完成后查询 authorizedStores 验证。不向用户索取 token、refreshToken 或 callback code。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/authorizeUrl" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"accountName": "采购账号"}'
```

## 接口：查询已授权账号（authorizedStores）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/authorizedStores`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| - | 未限定 | 否 | 通常传 `{}`。返回当前 LinkFox 用户的 1688 授权状态，不是全库账号列表。 |

#### 脚本选项与运行约定

业务入口：`scripts/authorized_stores.py`。本操作免除授权前检。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| stores | array<object> | 当前 LinkFox 用户的授权账号；脚本也兼容 data.stores 包装。 |
| stores[].accountName | string | 授权账号展示名。 |
| stores[].status | string | 可采购状态为 ACTIVE。 |
| stores[].expired | boolean / string | 可采购时为 false；true 表示 refreshToken 为空、失效或刷新失败。accessToken 普通过期由后端自动刷新。脚本兼容字符串 true / false。 |
| stores[].tokenExpiresAt | 未限定 | 若上游返回，仅内部处理；业务脚本删除该输出字段，不向用户展示。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 只返回当前 LinkFox 用户授权状态。脚本先按公共基础规则确认 HTTP 与 errcode 正常且无本地 error，再检查 ACTIVE 且 expired 不为 true；兼容状态大小写及 expired 的布尔 true / 字符串 true。无可用账号时返回 authorization_required 并阻止目标调用。accessToken 临期或过期由后端用当前用户自己的 refreshToken 自动刷新；只有 expired=true 所代表的授权不可用才需重新授权。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/authorizedStores" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
```

## 接口：查询收货地址（receiveAddressList）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/receiveAddressList`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| - | 未限定 | 否 | 通常传 `{}`。返回当前用户可用收货地址。 |

#### 脚本选项与运行约定

业务入口：`scripts/receive_address_list.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| items | array<object> | 可用收货地址，多地址由用户明确选择。 |
| items[].addressId | string | 地址标识，供预览和下单使用。 |
| items[].fullName | string | 收货人。 |
| items[].mobile | string | 手机号，展示时减少敏感信息。 |
| items[].provinceText | string | 省。 |
| items[].cityText | string | 市。 |
| items[].areaText | string | 区。 |
| items[].address | string | 详细地址。 |
| items[].isDefault | boolean | 是否默认，以实际返回为准，不猜测。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 多地址时由用户明确选择，不能猜测默认地址。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/receiveAddressList" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{}'
```

## 接口：查询商品规格（sku）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/sku`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `offerId` | string | 是 | 1688 商品 ID，必须用字符串，避免 JS 大数精度丢失。 |

#### 脚本选项与运行约定

业务入口：`scripts/sku.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| offerId | string | 1688 商品编号。 |
| skuList | array<object> | 规格列表，价格与库存仅作选择参考，以订单预览为准。 |
| skuList[].specId | string | 下单使用的规格 ID。 |
| skuList[].skuId | string | SKU 标识。 |
| skuList[].price | number / string | 规格参考价格，按实际返回展示。 |
| skuList[].amountOnSale | number | 可售库存。 |
| skuList[].attributes | 未限定 | 规格属性，保留原结构。 |
| skuList[].skuImageUrl | string | 规格图片 URL。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 价格和库存仅作规格选择参考；最终可购性、价格、运费和优惠以 orderPreview 为准。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/sku" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"offerId": "1234567890123456789"}'
```

## 接口：下单预览（orderPreview）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/orderPreview`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `addressId` | string | 条件必填 | 与 addressParam 二选一，优先使用地址查询返回的 addressId。 |
| `addressParam` | object | 条件必填 | 与 addressId 二选一，至少含 fullName、mobile、address。 |
| `addressParam.fullName` | string | 使用对象时必填 | 收货人。 |
| `addressParam.mobile` | string | 使用对象时必填 | 手机号。 |
| `addressParam.provinceText` | string | 否 | 省。 |
| `addressParam.cityText` | string | 否 | 市。 |
| `addressParam.areaText` | string | 否 | 区。 |
| `addressParam.address` | string | 使用对象时必填 | 详细地址。 |
| `cargoParamList` | array<object> | 是 | 货品列表。 |
| `cargoParamList[].offerId` | string | 是 | 1688 商品 ID，字符串避免大数精度丢失。 |
| `cargoParamList[].specId` | string | 否 | 规格 ID；多 SKU 商品使用 sku 返回的 specId。 |
| `cargoParamList[].quantity` | number | 是 | 至少 1；结合售卖单位和起批量理解，不默认等于件数。 |
| `flow` | string | 是 | 普通采购 general；脚本缺省或空白补 general，合法字符串去首尾空格；直接 API 必须显式传。仅用户明确要求时可透传 fenxiao / boutiquefenxiao，本技能不提供分销专属校验或保障。 |
| `isvBizType` | string | 否 | 默认 cross，仅支持 cross / cross_daigou / cross_distribution。 |

#### 脚本选项与运行约定

业务入口：`scripts/order_preview.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| status | boolean | 业务预览是否通过，收到正常响应不等于可下单。 |
| message | string | 上游业务提示，失败时展示。 |
| sumPayment | number | 订单金额，单位分。 |
| sumCarriage | number | 运费，单位分。 |
| discountFee | number | 优惠金额，单位分。 |
| cargoList | array<object> | 预览商品行，必须有效。 |
| cargoList[].finalUnitPrice | number | 最终单价，单位元。 |
| cargoList[].amount | number | 商品行金额，单位元。 |
| tradeModelList | array | 交易模型，元素内部字段以实际返回为准。 |
| payChannelInfos | array | 支付渠道；有可读名称则展示名称，否则原样展示编码。 |
| shopPromotionList | array | 店铺优惠，元素内部字段以实际返回为准。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 即使 errcode=200，status=false、金额为 0、交易/支付/优惠列表为空也可能是业务失败。必须预览明确通过、金额和商品行有效才可进入创建订单；否则展示 message 并复核规格、起批量、售卖单位、quantity 和地址。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/orderPreview" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"flow": "general", "addressId": "987654321012345678", "cargoParamList": [{"offerId": "1234567890123456789", "specId": "456789012345678901", "quantity": 2}]}'
```

## 接口：创建订单（createOrder）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/createOrder`

### 请求参数

下单参数必须与已通过的预览保持一致；全部已知字段见下表，未限定的上游字段按实际定义透传，不推测默认值。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `confirmCreateOrder` | boolean | 是 | 必须是 JSON boolean `true`。未传或 false 时不会调用 1688 下单。 |
| `useRedEnvelope` | string | 否 | 是否使用红包，仅支持 `y`/`n`；默认 `n`。 脚本将缺省、null 或空白补为 n，合法字符串去首尾空格；其他值本地返回 invalid_parameter，退出码 2。 |
| `addressId` | string | 条件必填 | 与 addressParam 二选一，优先使用地址查询返回的 addressId。 |
| `addressParam` | object | 条件必填 | 与 addressId 二选一，至少含 fullName、mobile、address。 |
| `addressParam.fullName` | string | 使用对象时必填 | 收货人。 |
| `addressParam.mobile` | string | 使用对象时必填 | 手机号。 |
| `addressParam.provinceText` | string | 否 | 省。 |
| `addressParam.cityText` | string | 否 | 市。 |
| `addressParam.areaText` | string | 否 | 区。 |
| `addressParam.address` | string | 使用对象时必填 | 详细地址。 |
| `cargoParamList` | array<object> | 是 | 货品列表。 |
| `cargoParamList[].offerId` | string | 是 | 1688 商品 ID，字符串避免大数精度丢失。 |
| `cargoParamList[].specId` | string | 否 | 规格 ID；多 SKU 商品使用 sku 返回的 specId。 |
| `cargoParamList[].quantity` | number | 是 | 至少 1；结合售卖单位和起批量理解，不默认等于件数。 |
| `flow` | string | 是 | 普通采购 general；脚本缺省或空白补 general，合法字符串去首尾空格；直接 API 必须显式传。仅用户明确要求时可透传 fenxiao / boutiquefenxiao，本技能不提供分销专属校验或保障。 |
| `isvBizType` | string | 否 | 默认 cross，仅支持 cross / cross_daigou / cross_distribution。 |
| `message` | 未限定 | 否 | 买家留言。 |
| `tradeType` | 未限定 | 否 | 交易类型。 |
| `shopPromotionId` | 未限定 | 否 | 店铺优惠标识。 |
| `anonymousBuyer` | 未限定 | 否 | 匿名买家设置。 |
| `outOrderId` | 未限定 | 否 | 外部订单标识。 |

#### 脚本选项与运行约定

业务入口：`scripts/create_order.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。 用户中文独立确认后，由 Agent 填入 `confirmCreateOrder=true`；必须是 JSON boolean true，字符串 "true"、数字 1 或其他变体均本地拒绝，返回 confirmation_required，退出码 2，不调用授权或业务接口。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| success | boolean | 下单业务结果。 |
| orderId | string | 1688 订单号；支付使用 orderIdList，状态、物流、取消和收货使用 aliOrderId。 |
| message | string | 业务消息。 |
| code | string / number | 业务码，与外层 errcode 分开判断。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 须使用与已通过预览一致的商品、规格、数量、地址和 flow。下单不包含发票信息，发票在订单完成后独立申请；结果不确定时禁止自动重放。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

仅在取得本次独立确认后执行；示例不是预先授权。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/createOrder" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"confirmCreateOrder": true, "flow": "general", "addressId": "987654321012345678", "cargoParamList": [{"offerId": "1234567890123456789", "specId": "456789012345678901", "quantity": 2}], "useRedEnvelope": "n"}'
```

## 接口：获取支付链接（paymentUrl）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/paymentUrl`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `confirmGetPaymentUrl` | boolean | 是 | 必须是 JSON boolean `true`。只获取支付链接，不自动打开、不自动支付。 |
| `orderIdList` | array<string> | 是 | 1688 订单 ID 字符串数组。使用 `createOrder` 返回的 `orderId`。 |

#### 脚本选项与运行约定

业务入口：`scripts/payment_url.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。 用户中文独立确认后，由 Agent 填入 `confirmGetPaymentUrl=true`；必须是 JSON boolean true，字符串 "true"、数字 1 或其他变体均本地拒绝，返回 confirmation_required，退出码 2，不调用授权或业务接口。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| success | boolean | 获取支付链接的业务结果。 |
| payUrl | string | 仅展示给用户手动打开，不自动支付、不无必要重复展示。 |
| errorMessage | string | 失败消息。 |
| errorCode | string / number | 失败码。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 只获取支付链接，不自动打开或支付。创建成功不代表用户同意获取支付链接。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

仅在取得本次独立确认后执行；示例不是预先授权。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/paymentUrl" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"confirmGetPaymentUrl": true, "orderIdList": ["1234567890123456789"]}'
```

## 接口：查询订单状态（orderStatus）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/orderStatus`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `aliOrderId` | string | 是 | 1688 订单 ID 字符串；可使用 `createOrder` 返回的 `orderId`。 |

#### 脚本选项与运行约定

业务入口：`scripts/order_status.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| aliOrderId | string | 1688 订单号。 |
| aliStatus | string | 1688 原始订单状态。 |
| normalizedStatus | string | 归一化履约状态，用于确认订单阶段。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 依据 aliStatus 和 normalizedStatus 判断履约阶段；不要主动连续轮询。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/orderStatus" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"aliOrderId": "1234567890123456789"}'
```

## 接口：查询物流（logistics）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/logistics`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `aliOrderId` | string | 是 | 1688 订单 ID 字符串；可使用 `createOrder` 返回的 `orderId`。 |

#### 脚本选项与运行约定

业务入口：`scripts/logistics.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| aliOrderId | string | 1688 订单号。 |
| logisticsOrders | array<object> | 物流单列表。 |
| logisticsOrders[].logisticsId | string | 物流单 ID，可用于轨迹查询。 |
| logisticsOrders[].logisticsBillNo | string | 运单号。 |
| logisticsOrders[].logisticsCompanyName | string | 承运公司名称。 |
| logisticsOrders[].status | string | 物流状态。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 多个物流单时，让用户确定轨迹查询目标，不任意合并不同物流单。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/logistics" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"aliOrderId": "1234567890123456789"}'
```

## 接口：查询物流轨迹（logisticsTrace）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/logisticsTrace`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `aliOrderId` | string | 是 | 1688 订单 ID 字符串；可使用 `createOrder` 返回的 `orderId`。 |
| `logisticsId` | string | 否 | 物流订单 ID；多个物流单时建议从 `logistics` 返回中选择。 |

#### 脚本选项与运行约定

业务入口：`scripts/logistics_trace.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| aliOrderId | string | 1688 订单号。 |
| logisticsId | string | 物流单 ID。 |
| traceList | array<object> | 轨迹列表。 |
| traceList[].traceTime | string | 轨迹时间，按 Asia/Shanghai 展示。 |
| traceList[].location | string | 地点。 |
| traceList[].traceDescription | string | 轨迹描述。 |
| traceList[].traceStatus | string | 轨迹状态。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 时间按 Asia/Shanghai 展示；不主动连续轮询。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/logisticsTrace" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"aliOrderId": "1234567890123456789", "logisticsId": "987654321"}'
```

## 接口：确认收货（confirmReceive）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/confirmReceive`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `aliOrderId` | string | 是 | 1688 订单 ID 字符串；可使用 `createOrder` 返回的 `orderId`。 |
| `confirmReceive` | boolean | 是 | 必须是 JSON boolean `true`。确认收货不可逆，需用户单独中文确认。 |

#### 脚本选项与运行约定

业务入口：`scripts/confirm_receive.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。 用户中文独立确认后，由 Agent 填入 `confirmReceive=true`；必须是 JSON boolean true，字符串 "true"、数字 1 或其他变体均本地拒绝，返回 confirmation_required，退出码 2，不调用授权或业务接口。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| success | boolean | 确认收货业务结果。 |
| aliOrderId | string | 1688 订单号。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 确认收货不可逆；查询物流、看到签收或询问状态不构成确认。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

仅在取得本次独立确认后执行；示例不是预先授权。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/confirmReceive" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"aliOrderId": "1234567890123456789", "confirmReceive": true}'
```

## 接口：取消订单（cancelOrder）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/cancelOrder`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `aliOrderId` | string | 是 | 1688 订单 ID 字符串；可使用 `createOrder` 返回的 `orderId`。 |
| `confirmCancel` | boolean | 是 | 必须是 JSON boolean `true`。取消订单不可逆，需用户单独中文确认。 |
| `cancelReason` | string | 否 | 取消原因，非空时透传。 |
| `remark` | string | 否 | 备注，非空时透传。 |

#### 脚本选项与运行约定

业务入口：`scripts/cancel_order.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。 用户中文独立确认后，由 Agent 填入 `confirmCancel=true`；必须是 JSON boolean true，字符串 "true"、数字 1 或其他变体均本地拒绝，返回 confirmation_required，退出码 2，不调用授权或业务接口。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| success | boolean | 尝试取消订单的业务结果；不是退款或售后，不保证退款，由 1688 按状态判断能否取消。 |
| aliOrderId | string | 1688 订单号。 |
| orderId | string | 兼容出参；后续仍按接口要求使用 aliOrderId 或 orderIdList。 |
| message | string | 取消业务提示。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 仅未付款/待付款订单可进入取消确认；已付款待发货、已发货或已完成订单不得用取消接口代替退款售后，转到 1688 处理；已取消不重复调用。是否允许取消以 1688 状态判断与实际结果为准。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

仅在取得本次独立确认后执行；示例不是预先授权。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/cancelOrder" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"aliOrderId": "1234567890123456789", "confirmCancel": true}'
```

## 接口：查询可开票金额（invoiceAmount）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/invoiceAmount`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `orderIds` | array<string> | 是 | 1688 订单 ID 字符串数组，至少 1 项，每项必须为数字字符串；可使用 `createOrder` 返回的 `orderId`。 |

#### 脚本选项与运行约定

业务入口：`scripts/invoice_amount.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| success | boolean | 查询业务结果，false 也可能是 HTTP 200 的业务结果。 |
| code | string / number | 业务码。 |
| message | string | 业务消息。 |
| subCode | string | 子业务码。 |
| subMessage | string | 子业务消息。 |
| retCodes | array | 逐单返回码，与 orderInvoiceAmountModelList 逐项对应；元素结构以实际返回为准。 |
| orderInvoiceAmountModelList | array<object> | 逐单可开票金额。 |
| orderInvoiceAmountModelList[].orderId | string | 1688 订单号。 |
| orderInvoiceAmountModelList[].amount | number | 可开票金额，单位分；原样传给 invoiceApply，不换算或自行计算。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- success=false（如订单不存在、已取消或不可开票）但 HTTP 200 属业务结果，不直接判传输异常。结合 retCodes 与金额列表逐单判断，无法取得金额的订单不进入申请；amount 为分并原样传递。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/invoiceAmount" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"orderIds": ["1234567890123456789"]}'
```

## 接口：申请开票（invoiceApply）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/invoiceApply`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `confirmApplyInvoice` | boolean | 是 | 必须是 JSON boolean `true`。申请开票高风险且不可逆，需用户单独中文确认。 |
| `invoiceApplyModelList` | array<object> | 是 | 开票申请列表，至少 1 项，每项见下「开票申请逐单模型」。 |
| `invoiceApplyModelList[].orderId` | string | 是 | 1688 订单 ID，数字字符串。 |
| `invoiceApplyModelList[].amount` | number | 是 | 从 invoiceAmount 返回值原样获取，单位分，不换算或计算。 |
| `invoiceApplyModelList[].invoiceType` | string | 是 | VATAX_COMM（增值税普通发票）/ VATAX_SPEC（增值税专用发票）。 |
| `invoiceApplyModelList[].purchaserInvoiceTitleModel` | object | 是 | 买家发票抬头，字段见下表。企业抬头建议经 1688 trade.invoiceTitle.getPageList 查到既有抬头后原样传入，避免手填不一致；本技能不提供该上游接口。 |

#### purchaserInvoiceTitleModel 字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `titleType` | string | 是 | `PERSONAL`（个人和社会组织）/ `COMPANY`（企业） |
| `title` | string | 是 | 发票抬头 |
| `taxpayerIdentify` | string | 条件必填 | 纳税人识别号，**企业开票必填** |
| `bankName` | string | 条件必填 | 开户行，**企业开专票必填** |
| `bankAccountId` | string | 条件必填 | 银行账号，**企业开专票必填** |
| `registerAddress` | string | 条件必填 | 企业注册地址，**企业开专票必填** |
| `registerPhone` | string | 条件必填 | 企业电话，**企业开专票必填** |

上表条件必填规则：COMPANY 不论普票/专票均须填 taxpayerIdentify；COMPANY 且 VATAX_SPEC 还须填 bankName、bankAccountId、registerAddress、registerPhone；PERSONAL 可不填以上条件字段。违反时由服务端返回 1002，且不调用 1688 上游；本地 CLI 仅校验独立确认及采购默认值，不声称已校验发票资料。

#### 脚本选项与运行约定

业务入口：`scripts/invoice_apply.py`。调用目标接口前自动调用 authorizedStores，未发现有效授权则停止。 用户中文独立确认后，由 Agent 填入 `confirmApplyInvoice=true`；必须是 JSON boolean true，字符串 "true"、数字 1 或其他变体均本地拒绝，返回 confirmation_required，退出码 2，不调用授权或业务接口。

公共 CLI、输出路径及缓存约定见本文件“采购脚本运行约定”。

### 响应结构

下表列出关键业务字段及语义类型；未限定的序列化类型和内部结构以实际返回为准，不补造缺失字段。业务字段可能位于顶层或 data 包装，以实际返回为准。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关状态，按公共基础规则判断。 |
| errmsg | string | 网关消息，错误时保留原因。 |
| costToken | number | 若实际返回才报告消耗，不补造。 |
| success | boolean | 批量顶层结果，必须继续遍历逐单列表。 |
| code | string / number | 业务码。 |
| message | string | 业务消息。 |
| subCode | string | 子业务码。 |
| subMessage | string | 子业务消息。 |
| successList | array<object> | 申请成功逐单列表。 |
| failedList | array<object> | 申请失败逐单列表。 |
| successList[].orderId | string | 1688 订单号。 |
| successList[].outBizId | string | 外部业务编号。 |
| successList[].result | 未限定 | 逐单申请结果，保留原类型。 |
| successList[].tradeOrderCompleted | boolean | true 表示交易已完结。 |
| successList[].errorCode | string | 逐单错误码；INVOICE_ALREADY_APPLIED 表示历史已开票。 |
| successList[].errorDesc | string | 逐单错误说明。 |
| failedList[].orderId | string | 1688 订单号。 |
| failedList[].outBizId | string | 外部业务编号。 |
| failedList[].result | 未限定 | 逐单申请结果，保留原类型。 |
| failedList[].tradeOrderCompleted | boolean | true 表示交易已完结。 |
| failedList[].errorCode | string | 逐单错误码；INVOICE_ALREADY_APPLIED 表示历史已开票。 |
| failedList[].errorDesc | string | 逐单错误说明。 |

本地错误字段与脱敏约定见本文件“采购脚本本地错误与脱敏”。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 遍历 successList / failedList，批量逐单成败独立。failedList 中 INVOICE_ALREADY_APPLIED 按“已开票”处理。业务失败 HTTP 仍可为 200；code=1003 或 HTTP 4xx/5xx 表示传输/上游异常，须同时遵守公共基础规则。开票成功不可系统侧回滚，红冲联系商家；不自动重放或自动联动多订单批量申请。
- `1002` 表示参数缺失或不合法；检查必填项、枚举及数字字符串订单号。`1003` 为上游调用或业务失败，不自动重试；`1005` 为 1688 授权缺失或失效，重新走授权检查。
- `authorization_required` 为脚本本地授权拒绝，先发起授权再验证；不以动态数据库查询代替。

### curl 示例

仅在取得本次独立确认后执行；示例不是预先授权。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/invoiceApply" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"confirmApplyInvoice": true, "invoiceApplyModelList": [{"orderId": "1234567890123456789", "amount": 30500, "invoiceType": "VATAX_COMM", "purchaserInvoiceTitleModel": {"titleType": "COMPANY", "title": "深圳某某科技有限公司", "taxpayerIdentify": "91440300MA5XXXXXX"}}]}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-1688-procurement",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```

