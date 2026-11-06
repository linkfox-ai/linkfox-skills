# 商品列表 接口说明

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

## 接口：商品列表（`bg.local.goods.list.query`）

分页查询商品列表（页码分页，与 `temu.local.goods.list.retrieve` 的游标分页不同）。

> Partner EU 文档：https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896&sub_menu_code=43baaa509c4b4b419853558a613715de

对应脚本：`scripts/eu_manage_list_query.py`；从技能根目录运行。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

转发 path：`/temu/proxy` → 上游 `/openapi/router`，Body `type=bg.local.goods.list.query`；`type` 不拼入 URL。

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 欧洲站为 `eu`，EU 脚本默认 `eu`；通用脚本须显式传入。兼容 `cn`、`partner`、`us`、`global`。 |
| managementType | string | 是 | EU 脚本默认 `semi-managed`；通用脚本须显式传入。可选 `full-managed`、`semi-managed`。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；脚本优先直接使用，或按本地 storeKey 查出后填入网关 Body。 |
| storeKey | string | 与 accessToken 二选一 | 本地令牌库的店铺键；脚本结合 site、managementType、tokenPurpose 查找，不将 storeKey 发到网关。 |
| tokenPurpose | string | 否 | EU 脚本查找本地令牌时默认 `product-inventory`，通用脚本默认 `default`；建议商品库存使用 `product-inventory`。此项用于本地查找。 |
| type | string | 是 | 本接口的 Temu 操作名，见上方调用规范；不是 URL 路径。专用脚本固定该值。 |
| params | object | 否 | Temu 业务载荷，通常为 `{ "request": { ... } }`，完整字段见下文。 |

#### 脚本参数与兼容约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户密钥，按此顺序优先于环境变量 `LINKFOX_AGENT_API_KEY`、`LINKFOXAGENT_API_KEY`；与 Temu accessToken 分开。不会作为业务字段转发。 |
| request | object | 否 | 专用脚本可在 JSON 顶层传入此业务对象，也可放在 `params.request`；显式 object 类型的 params 优先，支持顶层业务字段透传。官方 request 为选填包装，内部必填项仍按下表执行。 |
| --inline | CLI flag | 否 | 强制全量打印，同时保存完整响应。 |
| --no-cache | CLI flag | 否 | 本技能不启用响应缓存；业务封装始终向公共 run 加入此选项，不读取或写入响应缓存。公共调用器可能创建空缓存目录。 |

兼容请求头 `Authorization` 与 `Token` 同值，以及 SESSION_ID、MESSAGE_ID、MODE_ID、APP_NAME 透传。网关地址依次取 `LINKFOX_TOOL_GATEWAY`、`TEMU_API_BASE_URL`、`STORE_API_BASE_URL`，默认正式网关。HTTP 超时为 150 秒。输出保存在当前工作目录，不可写则在请求前报错，不回退到家目录或临时目录。专用脚本接受 JSON 参数及 `--inline`，兼容 `--no-cache`；通用脚本保留站点与托管类型校验。

#### Temu 业务参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否 | 官方顶层业务请求包装；子字段的必填要求见下文。 |

```text
params
└── request (OBJECT, 选填)
    ├── pageNo / pageSize              ← 均必填
    ├── orderField / orderType
    ├── goodsSearchType                ← 必填（INTEGER 枚举）
    ├── goodsStatusFilterType          ← 必填
    ├── goodsSubStatusFilterType       ← 选填
    ├── searchText / statusFilterType
    ├── crtFrom / crtTo
    ├── goodsIdList / catIdList
    ├── goodsStatusChangeTimeFrom / goodsStatusChangeTimeTo
    └── goodsSearchTags
```

#### `request` 内字段

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
| goodsStatusFilterType | INTEGER | **是** | 商品状态筛选，具体取值见 Partner 文档 |
| goodsSubStatusFilterType | INTEGER | 否 | 商品子状态筛选 |
| goodsStatusChangeTimeFrom | LONG | 否 | 商品状态变更时间起（时间戳） |
| goodsStatusChangeTimeTo | LONG | 否 | 商品状态变更时间止（时间戳） |
| goodsSearchTags | INTEGER[] | 否 | `1` 低流量，`4` 受限流量 |

#### `goodsSearchType` 枚举

| 值 | 说明 |
|----|------|
| `1` | 在售/下架 |
| `4` | 尚未发布 |
| `5` | 草稿 |
| `6` | 已删除 |

> 官方同时标记 **`goodsSearchType`** 与 **`goodsStatusFilterType`** 为必填；调用时需同时传入（`goodsStatusFilterType` 取值以 Partner「Goods status description」为准）。

> **勿**使用字段名 `createTimeFrom`/`createTimeTo`（官方为 **`crtFrom`/`crtTo`**）；**勿**用单值 `catId`（官方为 **`catIdList`**）。

### 响应结构

#### 网关与脚本响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态码，按基础规则判断；不存在或空值不代替业务结果判断。 |
| errmsg | string | 网关错误说明，以实际返回为准。 |
| body | string | Temu 原始 JSON 字符串，保留原文。 |
| code | integer | 网关业务错误码：`1002` 为参数或 LinkFox Token 问题，`1003` 为转发失败；未定义的 code 不擅自推断为成功。 |
| temuBody | object / array / scalar / null | 脚本对非空且合法 JSON 的 body 解析后追加；解析失败保留 body，不添加此字段。下文为 Temu 对象响应的字段。 |
| transportHttpStatus | integer / null | 脚本追加的 LinkFox HTTP 状态；连接失败时为 null。 |
| error | string | 连接失败或无法解析的 HTTP 错误消息，仅出现时返回。 |
| details | string | 无法解析的 HTTP 错误原文，仅出现时返回。 |

#### Temu 业务响应

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

#### `result.goodsList[]`

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
| goodsShowSubStatus | INTEGER | 商品展示子状态 |
| lowTrafficTag | INTEGER | `1` 低流量，`2` 非低流量 |
| restrictedTrafficTag | INTEGER | `1` 受限流量，`2` 非受限流量 |

> 响应中状态字段为 **`status4VO` / `subStatus4VO`**，勿写成 `status` / `subStatus`。`listPrice`、`retailPrice`、`skuInfoList` 在 Partner 文档中为可展开对象，子字段以官方为准。

#### 与 `temu.local.goods.list.retrieve` 对比

| 项 | `bg.local.goods.list.query` | `temu.local.goods.list.retrieve` |
|----|----------------------------|----------------------------------|
| 分页 | `pageNo` + `pageSize`（均必填） | `pageToken` + `pageSize` |
| 主状态筛选 | `goodsSearchType`（INTEGER 1/4/5/6） | 游标检索侧字段以 Partner 为准 |
| 状态筛选 | `goodsStatusFilterType`（必填） | — |
| 创建时间 | `crtFrom` / `crtTo` | 多为 `goodsCreateTimeFrom` / `To` |
| ID 列表 | `goodsIdList`（LONG[]） | 多为 STRING[] |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关基础规则通过后，继续检查网关业务 `code`；`1002` 时修正参数与 LinkFox Token，`1003` 时检查 Temu token、IP 白名单与网络。
- 再解析 `body`，检查 Temu `success`、`errorCode`、`errorMsg` 和 `result`。Temu 的 `errorCode=0` 与网关 `errcode=0` 是不同层级，不能混用；body 无法解析时保留原文，不能宣称操作成功。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "eu",
  "managementType": "semi-managed",
  "accessToken": "TEMU_EU_TOKEN",
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
  "skillName": "linkfox-temu-manage-product-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
