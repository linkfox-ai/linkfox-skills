# 商品详情 接口说明

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

## 接口：商品详情（`bg.local.goods.detail.query`）

查询商品详情。

> Partner EU 文档：https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896&sub_menu_code=50a6dd012fcd41149a2d8ef2cdc58b69

对应脚本：`scripts/eu_manage_detail_query.py`；从技能根目录运行。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

转发 path：`/temu/proxy` → 上游 `/openapi/router`，Body `type=bg.local.goods.detail.query`；`type` 不拼入 URL。

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
    ├── language
    ├── goodsId              ← 必填
    └── versionQueryType     ← 查哪一版商品信息
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| language | STRING | 否 | 语言 |
| goodsId | LONG | **是** | 商品 ID |
| versionQueryType | INTEGER | 否 | 拉取哪一版商品信息，默认 **`2`** |

#### `versionQueryType` 枚举

| 值 | 说明 |
|----|------|
| `1` | 拉取**当前审核中**的最新版本商品信息 |
| `2` | 拉取**线上在售**快照（编辑前的 live 版本），**默认** |

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
    ├── goodsId
    ├── catId
    ├── subStatus
    ├── goodsName
    ├── goodsDesc
    ├── bulletPoints
    ├── customized
    ├── productType
    ├── sourceSiteInfo
    ├── targetSiteInfo[]
    ├── goodsGallery
    ├── importDesignation
    ├── outGoodsSn
    ├── goodsServicePromise
    ├── goodsProperties[]
    ├── goodsTrademark
    ├── goodsSizeChartList
    ├── goodsSizeImage
    ├── goodsOriginInfo
    ├── secondHand
    ├── itemTaxCode
    ├── skuList[]
    └── saveModeStatus
```

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 商品详情 |

#### `result` 顶层字段（官方）

> **注意**：详情 **响应** 的 `result` 为**扁平结构**（字段直接在 `result` 下），与 **update 请求** 中包在 `request.goodsBasic` 内的层级**不同**。改商品时请按 [partial.update](./bg-local-goods-partial-update.md) / [update](./bg-local-goods-update.md) 的 **请求** 结构组装。

| 参数 | 类型 | 说明 |
|------|------|------|
| goodsId | LONG | 商品 ID |
| catId | LONG | 叶子类目 ID（须与类目版本对应的类目树一致） |
| subStatus | INTEGER | 商品草稿状态 |
| goodsName | STRING | 商品名称 |
| goodsDesc | STRING | 商品描述 |
| bulletPoints | STRING[] | 商品卖点 |
| customized | BOOLEAN | 是否为定制商品 |
| productType | INTEGER | `1` 普通，`2` 定制，`3` 按单生产 |
| sourceSiteInfo | OBJECT | 来源站点商品 ID（子字段见 Partner 展开） |
| targetSiteInfo | OBJECT[] | 目标站点商品 ID（子字段见 Partner 展开） |
| goodsGallery | OBJECT | 图库/视频；最多 49 张图 URI、1 个视频 URI，顺序即 Temu 展示顺序，视频在画廊顶部 |
| importDesignation | STRING | 仅 USA：`Imported` / `Made in the USA` / `Made in the USA and Imported` / `Made in the USA or Imported` |
| outGoodsSn | STRING | 外部商品编码，店内唯一，最长 40 字符，勿首尾空格 |
| goodsServicePromise | OBJECT | 商家服务信息 → 结构同 [partial.update §goodsServicePromise](./bg-local-goods-partial-update.md#requestgoodsservicepromise) |
| goodsProperties | OBJECT[] | 商品通用属性（**非** `goodsProperty.goodsProperties`）→ 元素结构同 [partial.update §goodsProperties](./bg-local-goods-partial-update.md#requestgoodsproperty) |
| goodsTrademark | OBJECT | 商标信息 → 同 [partial.update §goodsTrademark](./bg-local-goods-partial-update.md#requestgoodstrademark) |
| goodsSizeChartList | OBJECT | 尺码表（套装可多套）→ 同 [partial.update §goodsSizeChartList](./bg-local-goods-partial-update.md#requestgoodssizechartlist) |
| goodsSizeImage | STRING[] | 尺码表图片 URL |
| goodsOriginInfo | OBJECT | 商品产地信息 → 同 [partial.update §goodsOriginInfo](./bg-local-goods-partial-update.md#requestgoodsorigininfo) |
| secondHand | OBJECT | 二手信息 → 同 [partial.update §secondHand](./bg-local-goods-partial-update.md#requestsecondhand) |
| itemTaxCode | STRING | 税码 |
| skuList | OBJECT[] | SKU 提交查询列表 → SKU 元素结构同 [partial.update §skuList](./bg-local-goods-partial-update.md#requestskulist) |
| saveModeStatus | INTEGER | 自动发布到 Temu 商品的卖家审核状态 |

#### result.goodsGallery 子字段

| 字段 | 类型 | 说明 |
|------|------|------|
| detailVideo | OBJECT | 详情视频，包含 vid 与 videoUrl。 |
| goodsCarouselImage | STRING[] | 商品轮播图 URL 列表。 |
| detailImage | STRING[] | 详情图 URL 列表。 |
| carouselVideo | OBJECT | 轮播视频，包含 vid 与 videoUrl。 |
| detailVideo.vid / carouselVideo.vid | 未限定 | 视频标识。 |
| detailVideo.videoUrl / carouselVideo.videoUrl | 未限定 | 视频 URL。 |

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
  "type": "bg.local.goods.detail.query",
  "params": {
    "request": {
      "goodsId": 123456,
      "versionQueryType": 2
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
