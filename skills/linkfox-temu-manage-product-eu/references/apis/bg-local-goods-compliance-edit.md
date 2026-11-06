# 合规编辑 接口说明

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

## 接口：合规编辑（`bg.local.goods.compliance.edit`）

编辑商品资质信息（编辑商品合规/资质信息：资质文件、实拍图、责任人、治理属性等）。

> Partner EU 文档：https://partner-eu.temu.com/documentation?menu_code=7289390cfd724be4a196f11ebe45a896&sub_menu_code=4499655e8cb044a0b8a30f9c9994f723

对应脚本：`scripts/eu_manage_compliance_edit.py`；从技能根目录运行。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

转发 path：`/temu/proxy` → 上游 `/openapi/router`，Body `type=bg.local.goods.compliance.edit`；`type` 不拼入 URL。

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

经 **LinkFox 网关** 调用时，使用 `accessToken` + `request` 等业务字段即可，**无需**在 `params` 中自行拼装 `app_key`、`sign`、`timestamp` 等（由网关代签转发）。直连 Temu OpenAPI 时需携带下列通用参数。

#### Temu OpenAPI 通用参数（直连上游）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | STRING | **是** | API 名称，如 `bg.local.goods.compliance.edit` |
| app_key | STRING | **是** | 应用 Key |
| access_token | STRING | **是** | 用于访问控制的安全令牌 |
| sign | STRING | **是** | 请求签名 |
| timestamp | STRING | **是** | UNIX 时间戳（秒），10 位；须在「当前时间 ±300 秒」范围内 |
| data_type | STRING | 否 | 请求/响应数据格式，可选参数固定为 JSON |
| version | STRING | 否 | API 版本，默认 V1；无特殊要求可不传 |

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否 | 官方顶层业务请求包装；子字段的必填要求见下文。 |

```text
params
└── request (OBJECT, 选填)
    ├── language
    ├── goodsId                    ← 必填
    ├── certificateInfo            ← 资质文件
    │   └── certificateDetailList[]
    │       ├── certType
    │       ├── skip
    │       ├── authCode
    │       ├── authCodes[]
    │       │   └── authCode
    │       ├── certFiles[]        ← 最多 6
    │       │   ├── fileName
    │       │   ├── fileUrl
    │       │   └── language
    │       └── inspectReportFiles[]  ← 最多 6
    │           ├── fileName
    │           ├── fileUrl
    │           └── language
    ├── actualPhoto                ← 实拍图
    │   ├── skip
    │   └── actualPhotoInfoList[]
    │       ├── sameSku
    │       ├── position
    │       └── skuPhotoInfoList[]
    │           ├── specIdList[]
    │           └── imageList[]
    │               └── imageUrl
    ├── repInfo                    ← 责任人
    │   └── repDetailList[]
    │       ├── complianceRepType
    │       └── repIdList[]
    └── extraTemplate              ← 治理属性
        └── extraTemplateDetailList[]
            ├── templateId
            ├── properties         ← MAP: propertyId → value id[]
            ├── inputText          ← MAP: propertyId → 输入对象
            └── compliancePropertyList[]  ← SKU 维度合规
                ├── specIdList[]
                └── inputTextList[]
                    ├── properties
                    └── inputText
```

#### `request` 顶层字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| language | STRING | 否 | 语言 |
| goodsId | LONG | **是** | 商品 ID |
| certificateInfo | OBJECT | 否 | 资质文件 |
| actualPhoto | OBJECT | 否 | 实拍图 |
| repInfo | OBJECT | 否 | 责任人信息 |
| extraTemplate | OBJECT | 否 | 治理属性 / 合规模板扩展 |

#### `certificateInfo` — 资质文件

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| certificateDetailList | OBJECT[] | 否 | 资质文件明细列表 |

#### `certificateDetailList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| certType | INTEGER | **是** | 资质类型 |
| skip | BOOLEAN | 否 | 是否跳过；未传时**默认不跳过** |
| authCode | STRING | 否 | 资质编号，**最多 120 字符** |
| authCodes | OBJECT[] | 否 | 资质编号信息列表 |
| certFiles | OBJECT[] | 否 | 资质证书文件列表，**最多 6 个** |
| inspectReportFiles | OBJECT[] | 否 | 检测报告文件列表，**最多 6 个** |

#### `authCodes[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| authCode | STRING | 否 | 资质编号，**最多 120 字符** |

#### `certFiles[]` / `inspectReportFiles[]`（结构相同）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fileName | STRING | **是** | 文件名，**最多 200 字符** |
| fileUrl | STRING | **是** | 文件 URL |
| language | STRING | 否 | 文件语言 |

#### `actualPhoto` — 实拍图

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | BOOLEAN | 否 | 是否跳过；未传时**默认不跳过** |
| actualPhotoInfoList | OBJECT[] | 否 | 实拍图模块信息列表 |

#### `actualPhotoInfoList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sameSku | BOOLEAN | **是** | 各 SKU 是否相同 |
| position | INTEGER | **是** | 实拍图位置 |
| skuPhotoInfoList | OBJECT[] | **是** | SKU 实拍图列表 |

#### `skuPhotoInfoList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| specIdList | LONG[] | 否 | 规格 ID 列表 |
| imageList | OBJECT[] | **是** | 图片 URL 列表 |

#### `imageList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| imageUrl | STRING | **是** | 图片 URL |

#### `repInfo` — 责任人信息

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| repDetailList | OBJECT[] | 否 | 责任人明细列表 |

#### `repDetailList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| complianceRepType | INTEGER | 否 | 责任人类型，如 **`4`**：A/S REP（售后代表） |
| repIdList | LONG[] | 否 | 责任人 ID 列表 |

#### `extraTemplate` — 治理属性

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| extraTemplateDetailList | OBJECT[] | 否 | 属性明细列表 |

#### `extraTemplateDetailList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| templateId | INTEGER | 否 | 模板 ID |
| properties | MAP | 否 | **propertyId → 属性值 ID 列表**。对应控件：`controlType=1` 下拉选择；`controlType=3` 输入或选择 |
| inputText | MAP | 否 | **propertyId → 输入值对象**。对应控件：`0` 输入；`3` 输入或选择；`17` 多行输入；`18` 双值比例 |
| compliancePropertyList | OBJECT[] | 否 | SKU 维度合规信息 |

#### `properties`（MAP 键值）

| 键 / 值 | 类型 | 说明 |
|---------|------|------|
| `$key`（propertyId） | STRING | propertyId（属性 ID） |
| `$value` | LONG[] | 属性值 ID 列表 |

#### `inputText`（MAP 键值）

| 键 / 值 | 类型 | 说明 |
|---------|------|------|
| `$key`（propertyId） | STRING | propertyId（属性 ID） |
| `$value` | OBJECT | 输入值对象，见下表 |

#### `inputText.$value`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | STRING | 否 | 输入文本 |
| multiLineInputs | OBJECT[] | 否 | 多行输入（`controlType=17`、`18`） |

#### `multiLineInputs[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | STRING | 否 | 输入值（`controlType=17`、`18` 时的输入值） |
| vid | LONG | 否 | 属性值（`controlType=18` 时的属性值 ID） |

#### `compliancePropertyList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| specIdList | LONG[] | 否 | 规格 ID 列表 |
| inputTextList | OBJECT[] | 否 | 输入值（SKU 维度输入值列表） |

#### `inputTextList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| properties | MAP | 否 | 属性值，**key 为 property_id** → `LONG[]` 属性值 ID |
| inputText | MAP | 否 | 输入值，**key 为 property_id** → 输入对象（结构同上文 `inputText.$value`） |

> 官方字段名为 **`certificateInfo`**（非 `certificationInfo`）。各合规块是否必填取决于类目与待办类型，可先通过 `bg.local.compliance.goods.list.query` 查询待补项。

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
└── result (OBJECT，可能为空)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功：成功返回 `true`，否则返回 `false` |
| errorCode | INTEGER | 错误码：用于对照错误码表定位解决方案 |
| errorMsg | STRING | 错误信息：与 `errorCode` 对应的反馈内容 |
| result | OBJECT | 业务结果；本接口成功时常见为空对象或仅含简单确认字段，以 Partner 实网返回为准 |

#### 相关接口

| 接口 | 用途 |
|------|------|
| `bg.local.compliance.goods.list.query` | 查询待合规/待更新商品及所需合规类型 |
| `bg.local.goods.property.get` | 查询商品属性（含合规模板参考） |
| `linkfox-temu-add-product-eu` 发品文档 | `certificationInfo` 与本文 `certificateInfo` 等同族结构参考 |

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
  "type": "bg.local.goods.compliance.edit",
  "params": {
    "request": {
      "goodsId": 123456789,
      "language": "en",
      "certificateInfo": {
        "certificateDetailList": [
          {
            "certType": 1,
            "authCode": "CERT-001",
            "certFiles": [
              {
                "fileName": "certificate.pdf",
                "fileUrl": "https://example.com/cert.pdf",
                "language": "en"
              }
            ]
          }
        ]
      },
      "actualPhoto": {
        "actualPhotoInfoList": [
          {
            "sameSku": true,
            "position": 1,
            "skuPhotoInfoList": [
              {
                "specIdList": [
                  10001
                ],
                "imageList": [
                  {
                    "imageUrl": "https://example.com/photo1.jpg"
                  }
                ]
              }
            ]
          }
        ]
      },
      "repInfo": {
        "repDetailList": [
          {
            "complianceRepType": 4,
            "repIdList": [
              90001
            ]
          }
        ]
      },
      "extraTemplate": {
        "extraTemplateDetailList": [
          {
            "templateId": 100,
            "properties": {
              "12345": [
                67890
              ]
            },
            "inputText": {
              "23456": {
                "name": "custom text"
              }
            }
          }
        ]
      }
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
