# 类目、属性与规格 API — 参数参考

文档导航：[网关与运行约定](api.md)、[Partner US 目录](partner-us-catalog.md)。

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

## 接口：获取类目属性模板（temu.local.product.attributes.get）

- **Partner 文档分区**：`sub_menu_code=1ecd9ad752a14d5e9f5297edfd6c8848`
- **脚本**：`scripts/us_goods_attrs.py`
- **用途**：按**叶子类目 ID** 获取发品所需属性模板（必填/选填、控件类型、属性值列表等）。发品前必须先调用。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| type | string | 是 | 固定 `temu.local.product.attributes.get`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| catId | integer | 是 | **叶子类目 ID**（须选到最细子类目，与同族 `bg.goods.attrs.get` 一致） |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则；不将 0 或 false 视为空。 |
| errmsg | string | LinkFox 错误消息。 |
| code | integer | 网关错误码（非 Temu 业务码），如 1002 参数或用户 Token 无效、1003 转发失败。 |
| message | string | 网关说明，结合 code 判断。 |
| body | string | Temu 原始 JSON 字符串；脚本尽量解析为 temuBody，并保留原文。 |
| temuBody | object / array / scalar | 脚本成功解析 body 后添加的结果；无有效 JSON 时不添加。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| error | string | 本地网络或非 JSON HTTP 错误说明（出现时）。 |
| details | string | 非 JSON HTTP 错误原文（出现时）。 |

#### Temu 业务信封（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | Temu 业务是否成功。 |
| errorCode | integer | Temu 业务码；1000000 或 0 常表示成功，须结合 success 和实际接口返回，不代替 LinkFox 基础规则。 |
| errorMsg | string | Temu 错误说明，成功时多为空。 |
| requestId | string | 请求追踪 ID。 |
| result | object | 业务数据；部分接口可为空对象，结构依接口而异。 |

#### 本接口 result

与同族 `bg.goods.attrs.get` 返回的类目属性模板一致，顶层字段示例：

| 字段 | 类型 | 说明 |
|------|------|------|
| inputMaxSpecNum | integer | 允许的自定义规格数量上限 |
| chooseAllQualifySpec | boolean | 限定规格是否须全选 |
| singleSpecValueNum | integer | 单个自定义规格值数量上限 |
| properties | array | 属性模板列表，见下表 |

#### `properties[]` 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| pid | integer | 基础属性 ID |
| templatePid | integer | 模板属性 ID |
| refPid | integer | 引用属性 ID |
| name | string | 属性名称 |
| lang2Name | string | 第二语言名称 |
| required | boolean | 是否必填 |
| isSale | boolean | 是否销售属性（规格维度） |
| mainSale | integer | 是否主销售属性 |
| controlType | integer | 控件类型（输入/勾选/时间/尺码选择器等） |
| propertyValueType | integer | 属性值类型（文本/数值/日期等） |
| valueRule | integer | 数值规则 |
| chooseMaxNum | integer | 最大可勾选数 |
| inputMaxNum | integer | 最大可输入数；0 表示不可输入 |
| valuePrecision | integer | 小数精度；0 表示不允许小数 |
| maxValue | string | 输入上限 |
| valueUnit | array | 属性值单位列表 |
| parentSpecId | integer | 父规格 ID（销售属性相关） |
| parentTemplatePid | integer | 模板父属性 ID |
| values | array | 可选属性值，见下表 |
| showCondition | array | 按父属性展示条件 `{ parentRefPid, parentVids[] }` |

#### `properties[].values[]` 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| vid | integer | 属性值 ID（发品时填入 `productPropertyReqs`） |
| value | string | 展示值 |
| specId | integer | 规格 ID（部分销售属性） |
| group | string | 分组 |
| extendInfo | string | 扩展信息 |
| parentVidList | array | 父属性值 ID 列表 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 解析 body 后结合 success、errorCode、errorMsg 判断 Temu 业务结果，不将 HTTP 成功直接当成发品、编辑或库存更新成功；无法确认写入结果时先查当前商品或库存，避免直接重放。

### curl 示例

示例仅展示结构；发品等写操作须按目标类目返回的要求补齐真实资料。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TEMU_PRODUCT_TOKEN",
  "type": "temu.local.product.attributes.get",
  "params": {
    "catId": 12345
  }
}'
```

## 接口：获取商品规格（temu.local.product.variation.get）

- **Partner 文档分区**：`sub_menu_code=d23bfec96065492ebe8290c6fe867a19`
- **脚本**：`scripts/us_goods_variation.py`
- **用途**：获取指定类目支持的 **Variation / 规格维度**（如颜色、尺码）及可选值，供 `temu.local.goods.v2.add` 组装 `productSpecPropertyReqs` / `skuList`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| type | string | 是 | 固定 `temu.local.product.variation.get`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| catId | integer | 是 | 叶子类目 ID |

#### Partner 后台扩展参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| parentSpecId | 以 Partner 后台该接口定义为准 | 按后台文档 | 仅在该接口后台定义支持时追加，不自行假定类型。 |
| siteId | 以 Partner 后台该接口定义为准 | 按后台文档 | 多数场景仅需 catId；仅在该接口后台定义支持时追加，不自行假定类型。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则；不将 0 或 false 视为空。 |
| errmsg | string | LinkFox 错误消息。 |
| code | integer | 网关错误码（非 Temu 业务码），如 1002 参数或用户 Token 无效、1003 转发失败。 |
| message | string | 网关说明，结合 code 判断。 |
| body | string | Temu 原始 JSON 字符串；脚本尽量解析为 temuBody，并保留原文。 |
| temuBody | object / array / scalar | 脚本成功解析 body 后添加的结果；无有效 JSON 时不添加。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| error | string | 本地网络或非 JSON HTTP 错误说明（出现时）。 |
| details | string | 非 JSON HTTP 错误原文（出现时）。 |

#### Temu 业务信封（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | Temu 业务是否成功。 |
| errorCode | integer | Temu 业务码；1000000 或 0 常表示成功，须结合 success 和实际接口返回，不代替 LinkFox 基础规则。 |
| errorMsg | string | Temu 错误说明，成功时多为空。 |
| requestId | string | 请求追踪 ID。 |
| result | object | 业务数据；部分接口可为空对象，结构依接口而异。 |

#### 本接口 result

与同族规格查询接口一致，常见为「父规格 + 子规格值」或「可售规格维度列表」：

| 字段 | 类型 | 说明 |
|------|------|------|
| parentSpecList / variationList / specList | array | 规格维度列表（命名以实网为准） |

#### 规格维度元素（典型）

| 字段 | 类型 | 说明 |
|------|------|------|
| parentSpecId | integer | 父规格 ID |
| parentSpecName | string | 父规格名称（如 Color、Size） |
| specId | integer | 子规格/规格值 ID |
| specName | string | 规格值名称 |
| values | array | 可选规格值列表 `{ specId, specName }` |

多规格发品时，SKU 的 `skuSpecList` 需引用此处返回的 `specId` / `parentSpecId`。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 解析 body 后结合 success、errorCode、errorMsg 判断 Temu 业务结果，不将 HTTP 成功直接当成发品、编辑或库存更新成功；无法确认写入结果时先查当前商品或库存，避免直接重放。

### curl 示例

示例仅展示结构；发品等写操作须按目标类目返回的要求补齐真实资料。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TEMU_PRODUCT_TOKEN",
  "type": "temu.local.product.variation.get",
  "params": {
    "catId": 12345
  }
}'
```

## 接口：商品类目树（bg.goods.cats.get）

- **sub_menu_code**：`7f9ded1bfce7485798c3862467d5c30e`
- **脚本**：`scripts/us_goods_cats.py`

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| type | string | 是 | 固定 `bg.goods.cats.get`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| siteId | integer | 是 | 站点 ID，当前固定传 `1` |
| parentCatId | integer | 否 | 父类目 ID，查顶级类目可不传 |
| showHidden | boolean | 否 | 是否展示隐藏类目，默认 false |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则；不将 0 或 false 视为空。 |
| errmsg | string | LinkFox 错误消息。 |
| code | integer | 网关错误码（非 Temu 业务码），如 1002 参数或用户 Token 无效、1003 转发失败。 |
| message | string | 网关说明，结合 code 判断。 |
| body | string | Temu 原始 JSON 字符串；脚本尽量解析为 temuBody，并保留原文。 |
| temuBody | object / array / scalar | 脚本成功解析 body 后添加的结果；无有效 JSON 时不添加。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| error | string | 本地网络或非 JSON HTTP 错误说明（出现时）。 |
| details | string | 非 JSON HTTP 错误原文（出现时）。 |

#### Temu 业务信封（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | Temu 业务是否成功。 |
| errorCode | integer | Temu 业务码；1000000 或 0 常表示成功，须结合 success 和实际接口返回，不代替 LinkFox 基础规则。 |
| errorMsg | string | Temu 错误说明，成功时多为空。 |
| requestId | string | 请求追踪 ID。 |
| result | object | 业务数据；部分接口可为空对象，结构依接口而异。 |

#### 本接口 result

| 字段 | 类型 | 说明 |
|------|------|------|
| categoryDTOList | array | 类目列表 |

#### `categoryDTOList[]`

| 字段 | 类型 | 说明 |
|------|------|------|
| catId | integer | 类目 ID |
| catName | string | 类目名称 |
| catLevel | integer | 层级 |
| parentCatId | integer | 父类目 ID |
| isLeaf | boolean | 是否叶子类目 |
| catType | integer | 1=服饰，其它=非服饰 |
| isHidden | boolean | 是否隐藏 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 解析 body 后结合 success、errorCode、errorMsg 判断 Temu 业务结果，不将 HTTP 成功直接当成发品、编辑或库存更新成功；无法确认写入结果时先查当前商品或库存，避免直接重放。

### curl 示例

示例仅展示结构；发品等写操作须按目标类目返回的要求补齐真实资料。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TEMU_PRODUCT_TOKEN",
  "type": "bg.goods.cats.get",
  "params": {
    "parentCatId": 0,
    "showHidden": false,
    "siteId": 1
  }
}'
```

## 接口：类目属性模板（跨境 type）（bg.goods.attrs.get）

- **sub_menu_code**：`2b42b46f51c348b69bf8f69c5397279e`
- **脚本**：`scripts/us_goods_attrs_bg.py`
- **说明**：与 `temu.local.product.attributes.get` 返回结构相同，**type 不同**；半托管跨境发品常用此 type。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| type | string | 是 | 固定 `bg.goods.attrs.get`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| catId | integer | 是 | 叶子类目 ID |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则；不将 0 或 false 视为空。 |
| errmsg | string | LinkFox 错误消息。 |
| code | integer | 网关错误码（非 Temu 业务码），如 1002 参数或用户 Token 无效、1003 转发失败。 |
| message | string | 网关说明，结合 code 判断。 |
| body | string | Temu 原始 JSON 字符串；脚本尽量解析为 temuBody，并保留原文。 |
| temuBody | object / array / scalar | 脚本成功解析 body 后添加的结果；无有效 JSON 时不添加。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| error | string | 本地网络或非 JSON HTTP 错误说明（出现时）。 |
| details | string | 非 JSON HTTP 错误原文（出现时）。 |

#### Temu 业务信封（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | Temu 业务是否成功。 |
| errorCode | integer | Temu 业务码；1000000 或 0 常表示成功，须结合 success 和实际接口返回，不代替 LinkFox 基础规则。 |
| errorMsg | string | Temu 错误说明，成功时多为空。 |
| requestId | string | 请求追踪 ID。 |
| result | object | 业务数据；部分接口可为空对象，结构依接口而异。 |

#### 本接口 result

与同族 `bg.goods.attrs.get` 返回的类目属性模板一致，顶层字段示例：

| 字段 | 类型 | 说明 |
|------|------|------|
| inputMaxSpecNum | integer | 允许的自定义规格数量上限 |
| chooseAllQualifySpec | boolean | 限定规格是否须全选 |
| singleSpecValueNum | integer | 单个自定义规格值数量上限 |
| properties | array | 属性模板列表，见下表 |

#### `properties[]` 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| pid | integer | 基础属性 ID |
| templatePid | integer | 模板属性 ID |
| refPid | integer | 引用属性 ID |
| name | string | 属性名称 |
| lang2Name | string | 第二语言名称 |
| required | boolean | 是否必填 |
| isSale | boolean | 是否销售属性（规格维度） |
| mainSale | integer | 是否主销售属性 |
| controlType | integer | 控件类型（输入/勾选/时间/尺码选择器等） |
| propertyValueType | integer | 属性值类型（文本/数值/日期等） |
| valueRule | integer | 数值规则 |
| chooseMaxNum | integer | 最大可勾选数 |
| inputMaxNum | integer | 最大可输入数；0 表示不可输入 |
| valuePrecision | integer | 小数精度；0 表示不允许小数 |
| maxValue | string | 输入上限 |
| valueUnit | array | 属性值单位列表 |
| parentSpecId | integer | 父规格 ID（销售属性相关） |
| parentTemplatePid | integer | 模板父属性 ID |
| values | array | 可选属性值，见下表 |
| showCondition | array | 按父属性展示条件 `{ parentRefPid, parentVids[] }` |

#### `properties[].values[]` 元素

| 字段 | 类型 | 说明 |
|------|------|------|
| vid | integer | 属性值 ID（发品时填入 `productPropertyReqs`） |
| value | string | 展示值 |
| specId | integer | 规格 ID（部分销售属性） |
| group | string | 分组 |
| extendInfo | string | 扩展信息 |
| parentVidList | array | 父属性值 ID 列表 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 解析 body 后结合 success、errorCode、errorMsg 判断 Temu 业务结果，不将 HTTP 成功直接当成发品、编辑或库存更新成功；无法确认写入结果时先查当前商品或库存，避免直接重放。

### curl 示例

示例仅展示结构；发品等写操作须按目标类目返回的要求补齐真实资料。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TEMU_PRODUCT_TOKEN",
  "type": "bg.goods.attrs.get",
  "params": {
    "catId": 12345
  }
}'
```

## 接口：父规格列表（bg.glo.goods.parentspec.get）

- **sub_menu_code**：`8a6a6e8b14814d518fe8f004f35b2192`
- **脚本**：`scripts/us_goods_parent_spec.py`
- **说明**：无业务入参，返回平台支持的父规格维度。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| type | string | 是 | 固定 `bg.glo.goods.parentspec.get`，写入 Body，不是 URL 路径。 |
| params | object | 否 | 无业务参数；可传空对象，US 封装会省略空对象。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

无，传 `{}` 即可。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则；不将 0 或 false 视为空。 |
| errmsg | string | LinkFox 错误消息。 |
| code | integer | 网关错误码（非 Temu 业务码），如 1002 参数或用户 Token 无效、1003 转发失败。 |
| message | string | 网关说明，结合 code 判断。 |
| body | string | Temu 原始 JSON 字符串；脚本尽量解析为 temuBody，并保留原文。 |
| temuBody | object / array / scalar | 脚本成功解析 body 后添加的结果；无有效 JSON 时不添加。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| error | string | 本地网络或非 JSON HTTP 错误说明（出现时）。 |
| details | string | 非 JSON HTTP 错误原文（出现时）。 |

#### Temu 业务信封（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | Temu 业务是否成功。 |
| errorCode | integer | Temu 业务码；1000000 或 0 常表示成功，须结合 success 和实际接口返回，不代替 LinkFox 基础规则。 |
| errorMsg | string | Temu 错误说明，成功时多为空。 |
| requestId | string | 请求追踪 ID。 |
| result | object | 业务数据；部分接口可为空对象，结构依接口而异。 |

#### 本接口 result

| 字段 | 类型 | 说明 |
|------|------|------|
| parentSpecDTOS | array | 父规格列表 |

#### `parentSpecDTOS[]`

| 字段 | 类型 | 说明 |
|------|------|------|
| parentSpecId | integer | 父规格 ID |
| parentSpecName | string | 父规格名称 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 解析 body 后结合 success、errorCode、errorMsg 判断 Temu 业务结果，不将 HTTP 成功直接当成发品、编辑或库存更新成功；无法确认写入结果时先查当前商品或库存，避免直接重放。

### curl 示例

示例仅展示结构；发品等写操作须按目标类目返回的要求补齐真实资料。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TEMU_PRODUCT_TOKEN",
  "type": "bg.glo.goods.parentspec.get",
  "params": {}
}'
```

## 接口：可绑定品牌（bg.glo.goods.brand.get）

- **sub_menu_code**：`f8065a07b2d6441f9f33c2d808dcc593`
- **脚本**：`scripts/us_goods_brand.py`

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| type | string | 是 | 固定 `bg.glo.goods.brand.get`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 是 | 页码 |
| pageSize | integer | 是 | 每页条数 |
| vid | integer | 否 | 搜索的属性 ID |
| BrandName | string | 否 | 品牌名称（注意大小写） |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则；不将 0 或 false 视为空。 |
| errmsg | string | LinkFox 错误消息。 |
| code | integer | 网关错误码（非 Temu 业务码），如 1002 参数或用户 Token 无效、1003 转发失败。 |
| message | string | 网关说明，结合 code 判断。 |
| body | string | Temu 原始 JSON 字符串；脚本尽量解析为 temuBody，并保留原文。 |
| temuBody | object / array / scalar | 脚本成功解析 body 后添加的结果；无有效 JSON 时不添加。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| error | string | 本地网络或非 JSON HTTP 错误说明（出现时）。 |
| details | string | 非 JSON HTTP 错误原文（出现时）。 |

#### Temu 业务信封（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | Temu 业务是否成功。 |
| errorCode | integer | Temu 业务码；1000000 或 0 常表示成功，须结合 success 和实际接口返回，不代替 LinkFox 基础规则。 |
| errorMsg | string | Temu 错误说明，成功时多为空。 |
| requestId | string | 请求追踪 ID。 |
| result | object | 业务数据；部分接口可为空对象，结构依接口而异。 |

#### 本接口 result

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 总数 |
| pageItems | array | 品牌列表 |

#### `pageItems[]`

| 字段 | 类型 | 说明 |
|------|------|------|
| brandId | integer | 品牌 ID |
| brandNameEn | string | 品牌英文名 |
| pid | integer | 基础属性值 ID |
| vid | integer | 属性值 ID |
| regSerialCode | string | 注册序列号 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 解析 body 后结合 success、errorCode、errorMsg 判断 Temu 业务结果，不将 HTTP 成功直接当成发品、编辑或库存更新成功；无法确认写入结果时先查当前商品或库存，避免直接重放。

### curl 示例

示例仅展示结构；发品等写操作须按目标类目返回的要求补齐真实资料。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TEMU_PRODUCT_TOKEN",
  "type": "bg.glo.goods.brand.get",
  "params": {
    "page": 1,
    "pageSize": 20,
    "BrandName": "Nike"
  }
}'
```

## 接口：商品类目映射（bg.goods.category.mapping）

- **sub_menu_code**：`3f15de61844e4a989d042767a385d8f5`
- **脚本**：`scripts/us_goods_category_mapping.py`
- **用途**：根据中英文商品名推荐类目。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | US 封装默认 `us`；兼容 `cn` / `partner` / `global` / `eu`，按目标店铺授权选择。 |
| managementType | string | 是 | US 封装默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌，最长约 8192；直接提供时优先使用。 |
| storeKey | string | 与 accessToken 二选一 | 脚本本地店铺键，解析后发送 accessToken；不发送 storeKey。 |
| tokenPurpose | string | 否 | 本地令牌用途；US 封装默认 `product-inventory`，通用脚本默认 `default`；不发送此字段。 |
| type | string | 是 | 固定 `bg.goods.category.mapping`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsName | string | 是 | 商品中文名 |
| goodsNameEn | string | 是 | 商品英文名 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | LinkFox 响应码，遵循公共规则；不将 0 或 false 视为空。 |
| errmsg | string | LinkFox 错误消息。 |
| code | integer | 网关错误码（非 Temu 业务码），如 1002 参数或用户 Token 无效、1003 转发失败。 |
| message | string | 网关说明，结合 code 判断。 |
| body | string | Temu 原始 JSON 字符串；脚本尽量解析为 temuBody，并保留原文。 |
| temuBody | object / array / scalar | 脚本成功解析 body 后添加的结果；无有效 JSON 时不添加。 |
| transportHttpStatus | integer / null | 脚本记录的 LinkFox 外层 HTTP 状态，连接失败为 null。 |
| error | string | 本地网络或非 JSON HTTP 错误说明（出现时）。 |
| details | string | 非 JSON HTTP 错误原文（出现时）。 |

#### Temu 业务信封（body 解析后）

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | Temu 业务是否成功。 |
| errorCode | integer | Temu 业务码；1000000 或 0 常表示成功，须结合 success 和实际接口返回，不代替 LinkFox 基础规则。 |
| errorMsg | string | Temu 错误说明，成功时多为空。 |
| requestId | string | 请求追踪 ID。 |
| result | object | 业务数据；部分接口可为空对象，结构依接口而异。 |

#### 本接口 result

| 字段 | 类型 | 说明 |
|------|------|------|
| categoryId | integer | 推荐类目 ID（字段名以实网为准，亦可能为 `catId`） |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 外层正常后，再检查网关 code/message；1002 表示参数校验或 LinkFox 用户 Token 问题，修正后再调用；1003 表示转发或上游失败，检查 Temu accessToken、IP 白名单和网络，后续调用遵守调用约束。
- 解析 body 后结合 success、errorCode、errorMsg 判断 Temu 业务结果，不将 HTTP 成功直接当成发品、编辑或库存更新成功；无法确认写入结果时先查当前商品或库存，避免直接重放。

### curl 示例

示例仅展示结构；发品等写操作须按目标类目返回的要求补齐真实资料。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TEMU_PRODUCT_TOKEN",
  "type": "bg.goods.category.mapping",
  "params": {
    "goodsName": "测试商品",
    "goodsNameEn": "Test Product"
  }
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-add-product-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
