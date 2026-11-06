# Temu 全球站商品管理接口说明

[公共运行约定](../api.md#运行约定) · [完整接口索引](README.md)

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

## 接口：商品列表 — `bg.local.goods.list.query`

> Partner 文档：https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=7b50a3af47824c4482c7238c6e11aedc
> 部分 sub_menu_code 使用 US 文档编号；须在 Global Partner 后台按 type 核对，索引链接不代表地址已实时校验。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `global`，全球区（非 US/EU）；由网关选择上游 `https://openapi-b-global.temu.com/openapi/router`。兼容脚本可显式指定 `cn` / `partner` / `us` / `global` / `eu`，须与实际授权区域一致。 |
| managementType | string | 是 | 本技能默认 `semi-managed`；通用脚本支持 `full-managed` / `semi-managed`。 |
| accessToken | string | 是 | Temu 店铺令牌；与 LinkFox 用户密钥不同。使用 `storeKey` 时由业务脚本读取本地令牌并转换为此字段。 |
| type | string | 是 | 本接口固定 `bg.local.goods.list.query`。 |
| params | object | 否 | 本接口业务载荷；通常为 `{"request": {...}}`，具体结构见下文。 |

#### 脚本兼容参数与选项

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | 仅脚本鉴权参数，按所列顺序取首个非空值，优先于环境变量；不转发到 Temu 业务参数。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 无 JSON 密钥时必填 | 优先使用前者，同时支持两个变量；`Authorization` 与 `Token` 请求头同值。 |
| storeKey | string | 与 accessToken 二选一 | 从本地 store 取 Temu 令牌；直接传入 accessToken 时优先使用该值。 |
| tokenPurpose | string | 否 | Global 包装默认 `product-inventory`；与 storeKey、site、managementType 一起精确匹配，不回退到其他区域或用途的令牌。 |
| params | object | 否 | 显式传入时优先使用整个 params；否则将顶层除鉴权、店铺、站点、type、params 外的字段作为业务载荷。 |
| --inline | CLI flag | 否 | 完整打印响应，仍保存文件。 |
| --no-cache | CLI flag | 否 | 本技能不使用响应缓存，业务包装调用 run 时始终添加此选项，不读写响应缓存。 |

Global 脚本自动补全站点、管理模式和令牌用途；`temu_proxy.py` 兼容入口要求显式传 site、managementType 和 type。业务载荷保持原始层级，不自动展平 request。授权步骤和本地令牌 CLI 见 [access-token.md](../access-token.md)。

#### 业务包装

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| params.request | OBJECT | 否 | 业务请求包装为选填，内部必填字段仍按下表执行。 |

```text
params
└── request (OBJECT, 选填)
    ├── pageNo / pageSize              ← 均必填
    ├── orderField / orderType
    ├── goodsSearchType                ← 必填（INTEGER 枚举）
    ├── goodsStatusFilterType          ← 必填（新版）
    ├── goodsSubStatusFilterType       ← 选填（新版）
    ├── searchText / statusFilterType
    ├── crtFrom / crtTo
    ├── goodsIdList / catIdList
    ├── goodsStatusChangeTimeFrom / goodsStatusChangeTimeTo
    └── goodsSearchTags
```

##### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageNo | INTEGER | **是** | 页码，用于分页 |
| pageSize | INTEGER | **是** | 每页条数，**上限 100** |
| orderField | STRING | 否 | 排序字段：`goodsId`、`createTime`、`goodsName`、`outGoodsSn`、`quantity`、`price`；默认按创建时间 |
| orderType | INTEGER | 否 | `0` 降序（默认），`1` 升序 |
| goodsSearchType | INTEGER | **是** | 商品状态筛选，见下表 |
| searchText | STRING | 否 | 搜索文本，支持按 **goodsName** 或 **goodsId** |
| statusFilterType | INTEGER | 否 | 子状态筛选类型，参见 Partner「Goods status description」 |
| crtFrom | LONG | 否 | 创建时间起，13 位毫秒时间戳 |
| crtTo | LONG | 否 | 创建时间止，13 位毫秒时间戳 |
| goodsIdList | LONG[] | 否 | 商品 ID 列表 |
| catIdList | LONG[] | 否 | 类目 ID 列表，支持叶子/非叶子类目，可批量 |
| goodsStatusFilterType | INTEGER | **是** | 商品状态筛选（**新版字段**），具体取值见 Partner 文档 |
| goodsSubStatusFilterType | INTEGER | 否 | 商品子状态筛选（**新版字段**） |
| goodsStatusChangeTimeFrom | LONG | 否 | 商品状态变更时间起（时间戳） |
| goodsStatusChangeTimeTo | LONG | 否 | 商品状态变更时间止（时间戳） |
| goodsSearchTags | INTEGER[] | 否 | `1` 低流量（Low traffic），`4` 限制流量（Restricted traffic） |

###### `goodsSearchType` 枚举

| 值 | 说明 |
|----|------|
| `1` | Available / off the shelf（在售/下架） |
| `4` | Not yet published（尚未发布） |
| `5` | Draft（草稿） |
| `6` | Deleted（已删除） |

> 官方同时标记 **`goodsSearchType`** 与 **`goodsStatusFilterType`** 为必填；调用时需同时传入（`goodsStatusFilterType` 取值以 Partner「Goods status description」为准）。

> **勿**使用字段名 `createTimeFrom`/`createTimeTo`（官方为 **`crtFrom`/`crtTo`**）；**勿**用单值 `catId`（官方为 **`catIdList`**）。

### 响应结构

#### 网关与脚本输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态；按公共规则判断。未出现时仍须结合外层 HTTP 状态与下列业务字段。 |
| errmsg | string | 网关错误或提示消息。 |
| code | integer | 网关错误码：1002 表示参数或 LinkFox Token 无效，1003 表示转发失败；不能替代外层 HTTP/errcode 判断。 |
| body | string | Temu 原始 JSON 字符串；保留原文。 |
| temuBody | object / array / scalar | 脚本附加字段，仅当 body 为可解析 JSON 字符串时生成；解析仅用于展示，不代表业务成功。 |

下面的字段以解析后的 Temu body 为作用域；未展开定义的子对象按实际返回解释，不推测补造字段。

```text
response
├── success
├── errorCode
├── errorMsg
└── result
    ├── pageNo
    ├── total
    └── goodsList[]
        ├── goodsId / goodsName / specName / thumbUrl
        ├── outGoodsSn / status4VO / subStatus4VO
        ├── currency / marketPrice / listPrice / price / retailPrice
        ├── outSkuSnList / skuIdList / skuInfoList
        ├── quantity / crtTime / goodsStatusChangeTime
        ├── catId / brandId / trademarkId
        ├── costTemplateId / shipmentLimitSecond
        ├── goodsShowSubStatus / lowTrafficTag / restrictedTrafficTag
        └── ...
```

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果 |
| result.pageNo | INTEGER | 结果集当前页码 |
| result.total | LONG | 结果集总条数 |
| result.goodsList | OBJECT[] | 商品列表 |

##### `result.goodsList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| goodsId | LONG | 商品唯一 ID |
| goodsName | STRING | 商品标题 |
| specName | STRING | 规格/类型 |
| thumbUrl | STRING | 缩略图 URL |
| outGoodsSn | STRING | 外部商品编码 |
| status4VO | INTEGER | 商品状态（如 `1` 在售、`4` 未发布等） |
| subStatus4VO | INTEGER | 商品子状态（含义依业务） |
| currency | STRING | 价格币种 |
| marketPrice | LONG | 市场价/建议零售价 |
| listPrice | OBJECT | 市场价/建议零售价（结构化，子字段见 Partner 展开） |
| price | STRING | 售价/零售价 |
| retailPrice | OBJECT | 售价/零售价（结构化，子字段见 Partner 展开） |
| outSkuSnList | STRING[] | 外部 SKU 编码列表 |
| skuIdList | LONG[] | SKU ID 列表 |
| quantity | INTEGER | 库存数量 |
| crtTime | LONG | 创建时间，Unix **秒** |
| goodsStatusChangeTime | STRING | 商品状态变更时间（时间戳格式） |
| catId | LONG | 类目 ID |
| brandId | LONG | 品牌 ID |
| trademarkId | LONG | 商标 ID |
| costTemplateId | STRING | 配送选项 ID，逗号分隔 |
| shipmentLimitSecond | LONG | 接单至可发货间隔（秒） |
| skuInfoList | OBJECT[] | SKU 信息列表（子字段见 Partner 展开） |
| goodsShowSubStatus | INTEGER | 商品展示子状态（**新版字段**） |
| lowTrafficTag | INTEGER | `1` 低流量，`2` 非低流量 |
| restrictedTrafficTag | INTEGER | `1` 限制流量，`2` 非限制流量 |

> 响应中状态字段为 **`status4VO` / `subStatus4VO`**，勿写成 `status` / `subStatus`。`listPrice`、`retailPrice`、`skuInfoList` 在 Partner 文档中为可展开对象，子字段以官方为准。

#### 与 `temu.local.goods.list.retrieve` 对比

| 项 | `bg.local.goods.list.query` | `temu.local.goods.list.retrieve` |
|----|----------------------------|----------------------------------|
| 分页 | `pageNo` + `pageSize`（均必填） | `pageToken` + `pageSize` |
| 主状态筛选 | `goodsSearchType`（INTEGER 1/4/5/6） | 游标检索侧字段以 Partner 为准 |
| 新版状态 | `goodsStatusFilterType`（必填） | — |
| 创建时间 | `crtFrom` / `crtTo` | 多为 `goodsCreateTimeFrom` / `To` |
| ID 列表 | `goodsIdList`（LONG[]） | 多为 STRING[] |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 基础规则通过后，核对网关 code，再检查 body 中的 success、errorCode、errorMsg 与 result。仅 body 解析成功不能认定操作成功。
- code=1002 时核对参数与 LinkFox 用户令牌；code=1003 时核对 Temu 店铺令牌、IP 白名单与转发情况。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "global",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.local.goods.list.query",
  "params": {
    "request": {
      "pageNo": 1,
      "pageSize": 20,
      "goodsSearchType": 1,
      "goodsStatusFilterType": 0,
      "searchText": "keyword"
    }
  }
}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-temu-manage-product-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
