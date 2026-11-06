# 推荐基础价与供货价估算 接口说明

脚本：`scripts/eu_price_baseprice_recommend.py`；网关总说明见 [../api.md](../api.md)，目录及 Partner 文档标识见 [../partner-eu-catalog.md](../partner-eu-catalog.md)。

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

## 接口：推荐基础价与供货价估算（temu.local.goods.baseprice.recommend）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body 与脚本认证参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | `eu`；EU 脚本默认 eu，通用多站点脚本须显式指定；兼容 cn / partner / us / global / eu。 |
| managementType | string | 是 | 价格接口为 `semi-managed`；EU 脚本默认此值；通用脚本兼容 full-managed / semi-managed。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；实际网关请求必须传 accessToken。 |
| storeKey | string | 与 accessToken 二选一 | 仅本地脚本参数；按 site + managementType + tokenPurpose 解析本地令牌后转为 accessToken，不直接发送此键。 |
| tokenPurpose | string | 否 | 仅本地令牌选择参数；EU 脚本默认 product-inventory，通用脚本默认 default。 |
| type | string | 是 | 固定 `temu.local.goods.baseprice.recommend`；由专用脚本填入。 |
| params | object | 否 | 业务参数；四项价格接口的业务块位于 `params.request`。 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户密钥的 JSON 别名，按左至右取首个非空值，优先于环境变量；不得与 Temu accessToken 混淆，也不进入业务 params。 |
| --inline | CLI flag | 否 | 保存完整响应并强制完整输出。 |
| --no-cache | CLI flag | 否 | 可显式传入此选项；业务入口始终向 run 传入该选项，不读写响应缓存。公共调用器可能创建空缓存目录。 |

脚本调用格式为 `python scripts/<脚本名>.py '<JSON 参数>' [--inline] [--no-cache]`。EU 入口允许把业务字段放顶层，或整体放入 `params`；若有 `request` 则保留整层作为 `params.request`，不自动再包一层。`params` 为对象时优先于顶层业务字段；通用多站点 `temu_proxy.py` 只接受对象形式的 `params`。

基础地址优先级为 LINKFOX_TOOL_GATEWAY → TEMU_API_BASE_URL → STORE_API_BASE_URL → https://tool-gateway.linkfox.com；末尾斜杠会移除。JSON 密钥别名优先于 LINKFOX_AGENT_API_KEY，再优先于 LINKFOXAGENT_API_KEY。在 Authorization 之外额外发送同值 Token 头，并保留 SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME。

请求前检查当前工作目录可写，响应只写当前目录的 linkfox 会话数据目录，禁止回退到 /tmp、其他临时目录或家目录。同一秒多次调用仍保留独立数据文件。认证探测复用同一传输并保存响应，但标准输出保持原探测结果 JSON。公共认证引导资源另见 [onboarding.md](../onboarding.md)。

#### 业务参数（`params` 内）

| 参数路径 | 类型 | 必填 | 说明 |
|---|---|---|---|
| request | OBJECT | 否 | 官方业务请求对象；存在时完整放在 params.request。 |
| request.language | STRING | 否 | 语言。 |
| request.supplierPriceEstimateQry | OBJECT | 是 | 供货价估算查询资料。 |
| request.supplierPriceEstimateQry.trademarkInfo | OBJECT | 否 | 品牌信息；有助于更准确地推荐价格。 |
| request.supplierPriceEstimateQry.trademarkInfo.brandId | LONG | 否 | 品牌 ID。 |
| request.supplierPriceEstimateQry.trademarkInfo.trademarkId | LONG | 否 | 商标 ID。 |
| request.supplierPriceEstimateQry.goodsBasicInfo | OBJECT | 是 | 商品基本信息。 |
| request.supplierPriceEstimateQry.goodsBasicInfo.catId | LONG | 是 | 商品叶子类目 ID，须对应 category_version 指定类目树；category_version 用于说明类目树上下文，不属于此接口已定义的请求字段，不自行新增。 |
| request.supplierPriceEstimateQry.goodsBasicInfo.taxCode | STRING | 否 | 商品税码。 |
| request.supplierPriceEstimateQry.goodsBasicInfo.costTemplateId | STRING | 否 | 商品可用配送配置 ID，多个以逗号分隔。卖家可按业务创建配送配置，上架报价时选择一个配置；网站据此取得有效配送选项。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList | OBJECT[] | 是 | 按 SKU / 规格提供估算资料。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].specIdList | LONG[] | 是 | 规格 ID 列表。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].externPlatformPriceInfo | OBJECT | 是 | 其他平台的商品售价。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].externPlatformPriceInfo.amount | STRING | 否 | 其他平台销售金额。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].externPlatformPriceInfo.currency | STRING | 否 | 币种代码。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo | OBJECT | 否 | 商品重量、尺寸信息。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.weight | STRING | 否 | 商品重量；通用字段说明中巴西站必填。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.weightUnit | STRING | 否 | 重量单位；通用说明为美国 lb、其他国家 kg；巴西站必填。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.length | STRING | 否 | 长度，保留两位小数；巴西站必填。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.width | STRING | 否 | 宽度，保留两位小数；巴西站必填。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.height | STRING | 否 | 高度，保留两位小数；巴西站必填。 |
| request.supplierPriceEstimateQry.supplierPriceEstimateSkuQryList[].productDimensionsInfo.dimensionUnit | STRING | 否 | 尺寸单位；通用说明为美国 inch、其他国家 cm；巴西站必填。 |

网关处理 `type`、`app_key`、`access_token`、`sign`、`timestamp` 等上游鉴权字段，不要把这些字段塞进业务 `params`。

欧洲站单位建议为 weightUnit=lb、dimensionUnit=inch；通用字段说明则为美国使用 lb/inch、其他国家使用 kg/cm，两项说明存在冲突。实际调用前按目标店铺/接口已确认约定提供单位，不自动换算或猜测。

### 响应结构

#### 网关与脚本输出

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | LinkFox 外层状态码；按公共规则判断，不与 Temu errorCode 混淆。 |
| errmsg | string | LinkFox 外层错误说明。 |
| code | integer | 网关业务错误码；1002 为参数或 Token 问题，1003 为转发失败。 |
| body | string | Temu 原始 JSON 字符串，保留原文；代理脚本另解析为 temuBody。 |
| temuBody | object / 任意 JSON 值 | 代理脚本额外解析的 body；无法解析时不添加，不把解析成功当作业务成功。 |
| transportHttpStatus | integer / null | 脚本保留的 LinkFox HTTP 状态；网络失败时为 null。 |
| error | string | 连接失败或非 JSON HTTP 错误时的原始传输错误说明。 |
| details | string | 非 JSON HTTP 错误响应原文（如存在）。 |

#### Temu `body` 解析后的字段

| 字段路径 | 类型 | 说明 |
|---|---|---|
| success | BOOLEAN | Temu 当前请求是否成功。 |
| errorCode | INTEGER | Temu 业务错误码；成功响应示例值为 0，不套用 LinkFox errcode 的 2xx 规则。 |
| errorMsg | STRING | Temu 业务错误说明。 |
| result | OBJECT | Temu 业务结果。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 在公共规则成立后再检查网关 `code`；1002 表示参数或 Token 问题，1003 表示转发失败。修正参数、核对 Temu token、白名单和网络，不自动重试。
- 解析 `body` 后根据 Temu `success`、`errorCode`、`errorMsg` 和 `result` 判断业务结果；解析失败保留原文，不宣称操作成功。
- 官方尚未提供完整推荐结果字段表，`result` 的子字段以实际返回及 Partner 文档为准；不补造字段或推荐金额。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"site": "eu", "managementType": "semi-managed", "accessToken": "TOKEN", "type": "temu.local.goods.baseprice.recommend", "params": {"request": {"supplierPriceEstimateQry": {"goodsBasicInfo": {"catId": 12345}, "supplierPriceEstimateSkuQryList": [{"specIdList": [9001], "externPlatformPriceInfo": {"amount": "19.99", "currency": "EUR"}}]}}}}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-price-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
