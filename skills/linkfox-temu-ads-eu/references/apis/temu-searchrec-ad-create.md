# 创建广告 接口说明

[接口索引](README.md) · [网关与运行约定](../api.md)

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

## 接口：创建广告（temu.searchrec.ad.create）

> Partner EU 文档：https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896 。按 type 打开对应条目；sub_menu_code 尚未收录，见 [Partner 目录](../partner-eu-catalog.md)。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| site | string | 是 | 本技能默认 `eu`，欧洲站；由网关解析对应 Temu 上游。 |
| managementType | string | 是 | 本技能默认 `semi-managed`。 |
| accessToken | string | 是 | Temu 店铺令牌；脚本支持从本地 `storeKey` 解析后写入本字段。 |
| type | string | 是 | 当前操作的完整 Temu 接口名，见下方。放在 Body，不放到 URL。 |
| params | object | 否 | 业务参数对象；本接口的字段在 `params.request` 下。 |

#### 脚本 JSON 参数与兼容行为

| 参数 | 类型 | 必填 | 默认 / 说明 |
|---|---|---|---|
| accessToken | string | 与 storeKey 二选一 | 直接传入时优先于本地存储。 |
| storeKey | string | 与 accessToken 二选一 | 本地店铺键；连同 site、managementType、tokenPurpose 精确查找令牌。 |
| site | string | 否 | EU 入口默认 `eu`；通用入口 `temu_proxy.py` 必填，支持 `cn` / `partner` / `us` / `global` / `eu`。 |
| managementType | string | 否 | EU 入口默认 `semi-managed`；通用入口必填，支持 `full-managed` / `semi-managed`。 |
| tokenPurpose | string | 否 | EU 入口建议 `product-inventory`，仅传 storeKey 且未传 accessToken 时默认此值；显式指定其他用途时按该值查找。该字段仅供本地令牌选择，不转发。 |
| token / linkfoxToken / linkfox_token | string | 否 | LinkFox 用户密钥兼容参数，按此顺序选首个非空值，优先于两个密钥环境变量；不作为 Temu 业务参数转发。 |
| type | string | 通用代理必填 | 专用业务脚本固定当前操作；EU 通用脚本为 `temu_eu_proxy.py`。 |
| params | object | 否 | 提供对象时优先使用该对象；否则 EU 业务脚本将剔除认证与路由字段后的顶层业务字段作为 params。因此顶层 request 等价于 params.request，不把 request 的子字段自动提升。 |
| request | OBJECT | 官方标为选填（False） | 放于 params 内；其中标为必填的业务字段仍必须在 params.request 提供。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 业务封装始终向公共调用器传入 --no-cache，不读写响应缓存。 |

Temu 字段名、类型与大小写保持原值。通用代理只转发显式 params 对象；完整运行约定见 [网关与运行约定](../api.md#网关与运行约定)。

本接口固定 `type=temu.searchrec.ad.create`，对应 `scripts/eu_ads_searchrec_ad_create.py`；上游 path 为 `/openapi/router`，无需传入 path 字段。

#### params.request 业务字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| createAdReqs | OBJECT[] | **是** | 创建广告参数 |

##### `createAdReqs[]`（元素字段）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goodsId | LONG | 是 | 商品 ID |
| budget | LONG | 是 | 广告预算 |
| roas | LONG/INTEGER | 是 | 目标 ROAS |
| roasType | INTEGER | 是 | ROAS 类型；具体枚举以 Partner 文档为准 |

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| transportHttpStatus | integer / null | 脚本补充的 LinkFox 外层 HTTP 状态；连接失败时为 null。与网关 code、Temu errorCode 分层判断，401/402 按 onboarding 指引处理。 |
| errcode | integer / string / null | 若返回，按公共响应码基本规则判断外层状态。 |
| errmsg | string | 若返回，保留网关消息。 |
| code | integer | 网关业务错误码：1002 表示参数或 Token 问题，1003 表示转发失败。 |
| body | string | Temu 原始 JSON 字符串，保持原样。 |
| temuBody | JSON 值 | 脚本在 body 为合法 JSON 字符串时补充的解析值；解析失败时不新增此字段。 |

以下按响应层级列出 body 解析后的 Temu 字段；真实结构以返回为准，不补造缺失数据。

#### Temu 顶层字段

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 业务错误码 |
| errorMsg | STRING | 业务错误消息 |
| result | OBJECT 或 OBJECT[] | 业务结果（见下表） |

#### `result`

| 参数 | 类型 | 说明 |
|------|------|------|
| alreadyCreatedGoodsNum | INTEGER | 已创建过广告的商品数 |
| successCreateProductNum | INTEGER | 成功创建广告的商品数 |
| successGoodsIdLists | LONG[] | 成功创建广告的商品 ID 列表 |
| createGoodsFailMap | OBJECT | 失败映射；示例键 `$key` / `$value` 表示失败 goodsId → 原因 |
| createGoodsFailObjList | OBJECT[] | 失败详情列表 |

##### `createGoodsFailObjList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| goodsId | LONG | 商品 ID |
| reason | STRING | 失败原因 |
| success | BOOLEAN | 是否成功；以实际返回为准 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 先依据公共规则判断 LinkFox 外层响应，再检查网关 code；1002 为参数或 LinkFox Token 问题，1003 为转发失败，应核对 Temu token、tokenPurpose、IP 白名单及网络。
- body 可解析后仍须检查 Temu success / errorCode / errorMsg，不能仅凭外层正常响应判断业务成功。解析不成功时保留原始 body。
- 创建可能部分成功，应结合成功列表、已创建计数、失败映射及失败详情逐商品核对，不将已存在广告计为本次新建成功。

| errorCode | errorMsg | 处理建议 |
|-----------|----------|----------------------|
| 230012000 | bad query params | 见 Partner 文档；修正入参或权限后重试 |
| 230012003 | unmatch mall and goods | 见 Partner 文档；修正入参或权限后重试 |
| 230013000 | business exception | 见 Partner 文档；修正入参或权限后重试 |
| 230014000 | system exception | 见 Partner 文档；修正入参或权限后重试 |
| 230016701 | has no permission | 见 Partner 文档；修正入参或权限后重试 |
| 230016103 | not signed because of not main account | 见 Partner 文档；修正入参或权限后重试 |

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
  "accessToken": "TOKEN",
  "type": "temu.searchrec.ad.create",
  "params": {
    "request": {
      "createAdReqs": [
        {
          "goodsId": 100001,
          "budget": 5000,
          "roas": 350,
          "roasType": 1
        }
      ]
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
  "skillName": "linkfox-temu-ads-eu",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
