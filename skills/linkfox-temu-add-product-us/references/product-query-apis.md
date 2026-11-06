# 商品查询 API — 参数参考

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

## 接口：商品列表查询（temu.goods.list.get）

- **sub_menu_code**：`c313f7e3983f407d82d0f7cd88ab5c62`
- **脚本**：`scripts/us_goods_list.py`

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
| type | string | 是 | 固定 `temu.goods.list.get`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 是 | 页码，从 1 起 |
| pageSize | integer | 是 | 每页条数 |
| productName | string | 否 | 货品名称（模糊） |
| productSkcIds | array | 否 | SKC ID 列表 |
| skcExtCode | string | 否 | SKC 外部编码 |
| skuExtCodes | array | 否 | SKU 货号列表 |
| cat1Id … cat10Id | integer | 否 | 各级类目 ID 筛选 |
| bindSiteIds | array | 否 | 经营站点 ID 列表 |
| skcSiteStatus | integer | 否 | SKC 加站点状态：0 未加入，1 已加入 |
| matchJitMode | boolean | 否 | 是否 JIT 模式 |
| quickSellAgtSignStatus | integer | 否 | 快速售卖协议：0 未签，1 已签 |
| supportPersonalization | integer | 否 | 是否支持定制品 |
| createdAtStart | string | 否 | 创建时间起（`YYYY-MM-DD HH:mm:ss`） |
| createdAtEnd | string | 否 | 创建时间止 |

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
| data | array | 商品列表，元素见 `entity.Goods` |
| totalCount | integer | 总条数 |

#### `data[]` 主要字段

| 字段 | 类型 | 说明 |
|------|------|------|
| productId | integer | 货品 ID |
| productSkcId | integer | SKC ID |
| productName | string | 货品名称 |
| extCode | string | SKC 外部编码 |
| mainImageUrl | string | 主图 |
| leafCat | object | 叶子类目 `{ catId, catName }` |
| skcSiteStatus | integer | 站点上架状态 |
| productSkuSummaries | array | SKU 摘要（库存、规格等） |

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
  "type": "temu.goods.list.get",
  "params": {
    "page": 1,
    "pageSize": 20
  }
}'
```

## 接口：商品详情查询（temu.goods.detail.get）

- **sub_menu_code**：`7ce116fe6b87443ba2a5320b25bf2b20`
- **脚本**：`scripts/us_goods_detail.py`

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
| type | string | 是 | 固定 `temu.goods.detail.get`，写入 Body，不是 URL 路径。 |
| params | object | 是 | 本接口业务参数，须包含下表的必填项；US 脚本省略空对象的行为不免除必填要求。 |

脚本认证别名、CLI、默认值与本地令牌解析见 [运行约定](api.md#运行约定)。

#### 业务参数（`params`）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productId | integer | 是 | 货品 ID |

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
| productId | integer | 货品 ID |
| productName | string | 商品名称 |
| categories | object | 类目树 cat1…cat10、leafCat |
| goodsLayerDecorationList | array | 商详装饰楼层 |
| productWhExtAttr | object | 仓配扩展（如产地 `productOrigin`） |

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
  "type": "temu.goods.detail.get",
  "params": {
    "productId": 604269868588112
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
