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

## 接口：合规编辑 — `bg.local.goods.compliance.edit`

> Partner 文档：https://partner-global.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b
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
| type | string | 是 | 本接口固定 `bg.local.goods.compliance.edit`。 |
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

###### 网关代签与上游兼容参数

经 **LinkFox 网关** 调用时，使用 `accessToken` + `request` 等业务字段即可，**无需**在 `params` 中自行拼装 `app_key`、`sign`、`timestamp` 等（由网关代签转发）。直连 Temu OpenAPI 时需携带下列通用参数。

##### Temu OpenAPI 通用参数（直连上游）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | STRING | **是** | API 名称，如 `bg.local.goods.compliance.edit` |
| app_key | STRING | **是** | 应用 Key |
| access_token | STRING | **是** | 访问控制用安全令牌 |
| sign | STRING | **是** | 请求签名 |
| timestamp | STRING | **是** | UNIX 时间戳（秒），10 位；须在「当前时间 ±300 秒」范围内 |
| data_type | STRING | 否 | 请求/响应数据格式，可选参数固定为 JSON |
| version | STRING | 否 | API 版本，默认 V1；无特殊要求可不传 |

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

##### `request` 顶层字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| language | STRING | 否 | 语言 |
| goodsId | LONG | **是** | 商品 ID |
| certificateInfo | OBJECT | 否 | 资质文件 |
| actualPhoto | OBJECT | 否 | 实拍图 |
| repInfo | OBJECT | 否 | 责任人信息 |
| extraTemplate | OBJECT | 否 | 治理属性 / 合规模板扩展 |

##### `certificateInfo` — 资质文件

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| certificateDetailList | OBJECT[] | 否 | 资质文件明细列表 |

###### `certificateDetailList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| certType | INTEGER | **是** | 资质类型 |
| skip | BOOLEAN | 否 | 是否跳过；未传时**默认不跳过** |
| authCode | STRING | 否 | 资质编号，**最多 120 字符** |
| authCodes | OBJECT[] | 否 | 资质编号信息列表 |
| certFiles | OBJECT[] | 否 | 资质证书文件列表，**最多 6 个** |
| inspectReportFiles | OBJECT[] | 否 | 检测报告文件列表，**最多 6 个** |

###### `authCodes[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| authCode | STRING | 否 | 资质编号，**最多 120 字符** |

###### `certFiles[]` / `inspectReportFiles[]`（结构相同）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| fileName | STRING | **是** | 文件名，**最多 200 字符** |
| fileUrl | STRING | **是** | 文件 URL |
| language | STRING | 否 | 文件语言 |

##### `actualPhoto` — 实拍图

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| skip | BOOLEAN | 否 | 是否跳过；未传时**默认不跳过** |
| actualPhotoInfoList | OBJECT[] | 否 | 实拍图模块信息列表 |

###### `actualPhotoInfoList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sameSku | BOOLEAN | **是** | 各 SKU 是否相同 |
| position | INTEGER | **是** | 实拍图位置 |
| skuPhotoInfoList | OBJECT[] | **是** | SKU 实拍图列表 |

###### `skuPhotoInfoList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| specIdList | LONG[] | 否 | 规格 ID 列表 |
| imageList | OBJECT[] | **是** | 图片 URL 列表 |

###### `imageList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| imageUrl | STRING | **是** | 图片 URL |

##### `repInfo` — 责任人信息

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| repDetailList | OBJECT[] | 否 | 责任人明细列表 |

###### `repDetailList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| complianceRepType | INTEGER | 否 | 责任人类型，如 **`4`**：A/S REP（售后代表） |
| repIdList | LONG[] | 否 | 责任人 ID 列表 |

##### `extraTemplate` — 治理属性

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| extraTemplateDetailList | OBJECT[] | 否 | 属性明细列表 |

###### `extraTemplateDetailList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| templateId | INTEGER | 否 | 模板 ID |
| properties | MAP | 否 | **propertyId → 属性值 ID 列表**。对应控件：`controlType=1` 下拉选择；`controlType=3` 输入或选择 |
| inputText | MAP | 否 | **propertyId → 输入值对象**。对应控件：`0` 输入；`3` 输入或选择；`17` 多行输入；`18` 双值比例 |
| compliancePropertyList | OBJECT[] | 否 | SKU 维度合规信息 |

###### `properties`（MAP 键值）

| 键 / 值 | 类型 | 说明 |
|---------|------|------|
| `$key`（propertyId） | STRING | propertyId（属性 ID） |
| `$value` | LONG[] | 属性值 ID 列表 |

###### `inputText`（MAP 键值）

| 键 / 值 | 类型 | 说明 |
|---------|------|------|
| `$key`（propertyId） | STRING | propertyId（属性 ID） |
| `$value` | OBJECT | 输入值对象，见下表 |

###### `inputText.$value`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | STRING | 否 | 输入文本 |
| multiLineInputs | OBJECT[] | 否 | 多行输入，`controlType=17`、`18` |

###### `multiLineInputs[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | STRING | 否 | `controlType=17`、`18` 时的输入值 |
| vid | LONG | 否 | `controlType=18` 时的属性值 ID |

###### `compliancePropertyList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| specIdList | LONG[] | 否 | 规格 ID 列表 |
| inputTextList | OBJECT[] | 否 | SKU 维度输入值列表 |

###### `inputTextList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| properties | MAP | 否 | 属性值，**key 为 property_id** → `LONG[]` 属性值 ID |
| inputText | MAP | 否 | 输入值，**键为 property_id** → 输入对象（结构同上文 `inputText.$value`） |

> 官方字段名为 **`certificateInfo`**（非 `certificationInfo`）。各合规块是否必填取决于类目与待办类型，可先通过 `bg.local.compliance.goods.list.query` 查询待补项。

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
└── result (OBJECT，可能为空)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 当前请求是否成功：成功返回 `true`，否则返回 `false` |
| errorCode | INTEGER | 错误码：用于对照错误码表定位解决方案 |
| errorMsg | STRING | 错误信息：与 `errorCode` 对应的反馈内容 |
| result | OBJECT | 业务结果；本接口成功时常见为空对象或仅含简单确认字段，以 Partner 实网返回为准 |

> 解析顺序见 [../api.md](../api.md)：先按基础规则检查 HTTP/errcode，再校验网关 `code`，然后解析 `body` 内 `success` / `errorCode` / `errorMsg`。

#### 相关接口

| 接口 | 用途 |
|------|------|
| `bg.local.compliance.goods.list.query` | 查询待合规/待更新商品及所需合规类型 |
| `bg.local.goods.property.get` | 查询商品属性（含合规模板参考） |
| `linkfox-temu-add-product-us` 发品文档 | `certificationInfo` 与本文 `certificateInfo` 等同族结构参考 |

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
  "skillName": "linkfox-temu-manage-product-global",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
