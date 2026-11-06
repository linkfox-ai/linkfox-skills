# 脚本输入、构参与本地输出

网关参数与响应定义见 [eligibility.md](eligibility.md)。本文件的本地输入、输出与上游构参不属于网关 DTO；只使用实际响应已有的业务字段。

共享脚本约定适用于本文件各操作；操作差异以对应小节为准。

## 接口：预览商品入仓与混装资格（getItemEligibilityPreview）

### 脚本输入与构参

#### 脚本参数与 CLI 选项

| 字段 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sellerId | string | 是 | 已授权店铺标识。 |
| region | string | 是 | NA / EU / FE。 |
| api | string | 统一入口二选一 | 选择本节 operation；优先于 operation。单操作脚本无需传入。 |
| operation | string | 统一入口二选一 | api 的兼容名称。 |
| requestBody | object / array | 视业务模型 | 优先使用此字段；对象或数组原样序列化。具体嵌套字段须符合本节链接的官方模型；不是任意字段均可被上游接受。 |
| query | object | 否 | 附加查询字段，先加入 query 对象，再加入本操作声明的同级查询字段；同名键可重复，不静默合并。 |
| queryString | string | 否 | 非空时完全覆盖 query 及同级字段构造的查询串；仍执行本地必填校验。 |
| marketplaceId | string / array | 否，或见下表 | marketplaceIds 缺失、空串或空数组时自动提升为 marketplaceIds；原字段保留，不自动删除。 |
| skipDepCheck | boolean | 否 | 默认 false；仅外部已确认依赖时跳过安装检测，不绕过店铺授权。 |
| useAmazonRequestShape | 任意 JSON 值 | 否 | 兼容保留键，不参与平铺 body，不改变请求形状。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 兼容接受；业务封装始终禁用响应缓存。 |

路径字段直接放在同级 JSON；所有占位段经去除首尾空白后分别百分号编码，包括 /、空格和非 ASCII 字符。查询数组生成重复键，布尔标量写为 true / false，空字符串和 None 不进入查询。无值的必填字段（None、空白字符串、空数组）在请求前报错。

有 requestBody 时优先使用；否则本操作启用 body 时，将非保留、非路径、非声明查询字段组成对象。保留键为 sellerId、region、skipDepCheck、api、operation、requestBody、query、queryString、useAmazonRequestShape；自动提升产生的 marketplaceIds 也参与后续组装。没有可组成 body 的字段时不传 body；这不表示上游免除业务必填要求。即使本操作未声明 body，显式 requestBody 仍会发送。

依赖检测返回 42 时先安装 `linkfox-amazon-store-auth`，不在本技能内实现令牌逻辑；网关环境变量、缓存和输出约定见 [运行约定](../api.md#运行约定与使用限制)。

#### HTTP 与方法（Amazon）

- **Method**：`GET`
- **资源路径模板**（写入 `developerProxy.path`）：`fba/inbound/v1/eligibility/itemPreview`
- **当前脚本**：`../../scripts/get_item_eligibility_preview.py`；统一入口 api / operation 取 `getItemEligibilityPreview`。

#### Path 参数

无路径占位参数。

#### Query 参数

| 参数 | 类型（脚本输入） | 必填 | 说明 |
|---|---|---|---|
| asin | string | 是 | 商品 ASIN。 |
| program | string | 是 | INBOUND / COMMINGLING；脚本转为大写，其他值报错。 |
| marketplaceIds | string / array[string] | INBOUND 时是 | 目标站点；也可由 marketplaceId 提升。Eligibility 的 INBOUND 必填，最多 1 个；脚本不会自动截断，调用方应遵守限制。 |

#### Body 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| requestBody | object / array | 通常不传 | 本操作未启用自动组装 body，通常省略；显式提供 requestBody 时仍会序列化发送。对象或数组的嵌套字段须符合本节链接的官方接口模型。 |

### 脚本输出与业务结果

#### 脚本输出字段

| 字段 | 类型 | 说明 |
|---|---|---|
| api | string | Amazon operationId；旧版 getShipmentsV0 输出 getShipments。 |
| developerProxy | object | 网关完整响应；错误和保护码原样保留。 |
| resolvedPath | string | 分段编码后实际使用的资源路径。 |
| method | string | 实际转发的 Amazon HTTP 方法。 |
| queryString | string / null | 实际发送的无 ? 查询串，无查询时为 null。 |
| requestBody | object / array | 仅发送业务 body 时返回，内容与序列化前一致。 |
| transportHttpStatus | integer / null | LinkFox 外层 HTTP 状态；连接失败为 null。 |
| payload | 任意 JSON 值 / null | 网关及外层正常、上游 2xx 后解析的业务数据；204 或空 body 为 null；错误时不将 body 解析为业务成功。兼容旧响应未给 httpStatus 时由成功 errcode 表达上游状态，显式失败的 httpStatus 不被成功 errcode 覆盖。 |
| payloadRaw | string | 仅成功状态下 JSON 解析失败时保留原始 body，同时 payload 为 null。 |
| success | boolean | 上游 204 或成功且空 body 时为 true；有 JSON 数据时不要求出现此字段，不据此认定业务状态机完成。 |


#### 本地调用器补充字段

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误或连接失败的错误说明；完整保留在 developerProxy 中。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始文本。 |
