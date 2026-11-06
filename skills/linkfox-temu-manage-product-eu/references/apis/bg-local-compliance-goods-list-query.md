# 合规商品列表 接口说明

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

## 接口：合规商品列表（`bg.local.compliance.goods.list.query`）

商品管理属性列表查询（合规待办/属性管理商品列表查询）。

> Partner EU 文档：https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896&sub_menu_code=cf3e1c09736d4f1f96c4b0016b2af52d

对应脚本：`scripts/eu_manage_compliance_list_query.py`；从技能根目录运行。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

转发 path：`/temu/proxy` → 上游 `/openapi/router`，Body `type=bg.local.compliance.goods.list.query`；`type` 不拼入 URL。

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
    ├── pageNo / pageSize
    ├── searchText
    ├── statusList
    └── optionalConditionList[]
        ├── complianceType
        ├── templateId
        ├── repType
        ├── actualPhotoCheckType
        └── certType
```

#### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageNo | INTEGER | **是** | 页码 |
| pageSize | INTEGER | **是** | 每页条数，**默认 25** |
| searchText | STRING | 否 | 支持按 **goodsName** / **goodsId** / **skuId** 搜索 |
| statusList | INTEGER[] | 否 | 合规状态筛选，见下表 |
| optionalConditionList | OBJECT[] | 否 | 合规信息筛选 |

#### `statusList` / 各块 `status` 枚举

| 值 | 说明 |
|----|------|
| `1` | 未提交 |
| `2` | 待审核 |
| `3` | 审核中 |
| `4` | 需处理 |
| `5` | 已通过 |
| `6` | 已拒绝 |
| `7` | 待更新 |

#### `optionalConditionList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| complianceType | INTEGER | 否 | `1` 治理属性；`2` 通用产品安全法规（GPSR） |
| templateId | INTEGER | 否 | 合规模板类型筛选（文档与 `complianceType` 同组说明：`1` 治理属性 / `2` GPSR） |
| repType | INTEGER | 否 | `2` 欧盟责任人；`3` 制造商。**`complianceType=2` 时必填** |
| actualPhotoCheckType | LONG | 否 | 实拍图 checkType。**`complianceType=3` 时必填** |
| certType | LONG | 否 | 资质 checkType。**`complianceType=4` 时填写** |

> 筛选侧 `complianceType` 除 `1`/`2` 外，通过条件字段可推断 **`3`** 实拍、`**4**` 资质等类型（以 Partner 与实网为准）。

> **勿**使用字段 `goodsIdList`、`complianceStatus`；官方为 **`statusList`** + **`optionalConditionList`**。

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
    ├── total
    └── goodsList[]
        ├── goodsId / goodsName / thumbUrl / outGoodsSn / crtTime
        ├── extraTemplateInfoList[]
        ├── gpsrInfoList[]
        ├── repInfoList[]
        ├── actualPhotoList[]
        └── certificateInfoList[]
```

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果 |
| result.total | LONG | 总数 |
| result.goodsList | OBJECT[] | 商品列表 |

#### `result.goodsList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| goodsId | LONG | 商品 ID |
| goodsName | STRING | 商品名称 |
| thumbUrl | STRING | 商品缩略图 URL |
| outGoodsSn | STRING | 外部商品编码 |
| crtTime | LONG | 创建时间，单位 **秒** |
| extraTemplateInfoList | OBJECT[] | 治理属性模板信息列表 |
| gpsrInfoList | OBJECT[] | GPSR 信息列表 |
| repInfoList | OBJECT[] | 责任人信息 |
| actualPhotoList | OBJECT[] | 实拍图列表 |
| certificateInfoList | OBJECT[] | 资质列表 |

#### `extraTemplateInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| templateId | INTEGER | 治理属性模板 ID |
| status | INTEGER | 合规状态，见 `statusList` 枚举 |

#### `gpsrInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| repType | INTEGER | `2` 欧盟责任人；`3` 制造商 |
| status | INTEGER | 合规状态 |

#### `repInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| repType | INTEGER | `4` 售后责任人 |
| status | INTEGER | 合规状态 |

#### `actualPhotoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| actualPhotoCheckType | LONG | 实拍图检查类型 |
| status | INTEGER | 合规状态 |

#### `certificateInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| certType | LONG | 当前证书的资质类型 |
| status | INTEGER | 合规状态 |

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
  "type": "bg.local.compliance.goods.list.query",
  "params": {
    "request": {
      "pageNo": 1,
      "pageSize": 25,
      "statusList": [
        4,
        7
      ],
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
