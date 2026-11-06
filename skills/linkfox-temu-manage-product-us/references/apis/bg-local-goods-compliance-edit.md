# Temu 美国站合规编辑接口说明

对应脚本：`scripts/us_manage_compliance_edit.py`。网关及兼容运行约定见 [api.md](../api.md)。

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

## 接口：合规编辑（bg.local.goods.compliance.edit）

> Partner 官方文档：https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

**用途说明：**合规编辑。

#### 调用方式说明

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

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `us`；兼容 `cn`、`partner`、`global`、`eu`，须与令牌来源一致。 |
| managementType | string | 是 | 默认 `semi-managed`，兼容 `full-managed`；区分店铺托管类型。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；传入时优先于本地令牌。 |
| storeKey | string | 脚本兼容 | 本地店铺键，脚本读取令牌后仅发送 accessToken，不将 storeKey 发给网关。 |
| tokenPurpose | string | 否 | 本技能店铺令牌默认用途 `product-inventory`；用于本地定位，不发往网关。 |
| type | string | 是 | 固定为 `bg.local.goods.compliance.edit`；大小写与原值一致。 |
| params | object | 否 | Temu 业务参数；本接口的 request 及其子字段见下文。 |

#### 脚本参数与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token / linkfoxToken / linkfox_token | string | 否 | 按此顺序优先于环境变量读取 LinkFox Key；不进入业务参数。 |
| site / managementType / tokenPurpose | string | 否 | 美国站包装器使用上表默认值；通用 temu_proxy.py 要求显式提供 site、managementType，本地令牌用途默认 default。 |
| params | object | 否 | 如为对象，优先作为完整业务参数；否则美国站包装器将顶层非保留字段作为业务参数。 |
| --inline | CLI flag | 否 | 强制全量打印响应，仍保存完整文件。 |
| --no-cache | CLI flag | 否 | 兼容选项；业务封装始终传入，禁用响应缓存。 |

#### Temu 业务参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| request | OBJECT | 否 | 官方业务参数对象；下文子字段必填性、嵌套关系和限制仍须遵守。 |

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
| complianceRepType | INTEGER | 否 | 责任人类型，如 **`4`**：售后代表 |
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
| multiLineInputs | OBJECT[] | 否 | 多行输入（`controlType=17`、`18`） |

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

#### LinkFox 网关与脚本输出

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 如存在，严格按公共响应码基本规则判断。 |
| errmsg | string | 网关错误说明；保留原始内容。 |
| code | integer | 本技能网关业务错误码，1002 表示参数或 Token 问题，1003 表示转发失败；不能用它替代公共 errcode 规则。 |
| body | string | Temu 原始 JSON 字符串；按原始内容保存。 |
| temuBody | object / array / scalar | 仅脚本加工字段：body 为有效 JSON 字符串时解析生成；无效或空字符串不补造。 |
| _httpStatus | integer / null | 仅脚本附加：本次请求网关的实际 HTTP 状态，连接失败为 null；用于判断 HTTP 401/402 等传输结果。完整响应和标准输出均保留，不是网关或 Temu 业务字段。 |

以下表格描述 body 解析后的 Temu 业务对象（脚本输出的 temuBody），不表示网关顶层字段。

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

> 解析顺序见 [../api.md](../api.md)：先校验网关 `code`，再解析 `body` 内 `success` / `errorCode` / `errorMsg`。

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

- 按公共基础规则确认网关正常后，检查本技能 code（1002 / 1003 为失败），再解析 body；Temu success 为 false 时依据 errorCode / errorMsg 解释原因，保留原始响应。
- 仅根据本接口返回的业务字段报告结果；未展开的 result 子字段以实际响应为准，不套用其他接口或补造字段。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/temu/proxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Token: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "site": "us",
  "managementType": "semi-managed",
  "accessToken": "TOKEN",
  "type": "bg.local.goods.compliance.edit",
  "params": {
    "request": {
      "goodsId": 123456789,
      "certificateInfo": {
        "certificateDetailList": [
          {
            "certType": 1,
            "skip": false,
            "authCode": "AUTH-2024-001",
            "certFiles": [
              {
                "fileName": "ce-cert.pdf",
                "fileUrl": "https://cdn.example.com/ce-cert.pdf"
              }
            ]
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
  "skillName": "linkfox-temu-manage-product-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
