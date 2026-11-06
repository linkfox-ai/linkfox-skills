# Temu 美国站合规商品列表接口说明

对应脚本：`scripts/us_manage_compliance_list_query.py`。网关及兼容运行约定见 [api.md](../api.md)。

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

## 接口：合规商品列表（bg.local.compliance.goods.list.query）

> Partner 官方文档：https://partner-us.temu.com/documentation?menu_code=fb16b05f7a904765aac4af3a24b87d4a&sub_menu_code=2a343c65a03d42d380e9ad835aa7b54b

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/temu/proxy`

### 请求参数

**用途说明：**合规商品列表。

#### 网关 POST Body

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| site | string | 是 | 本技能默认 `us`；兼容 `cn`、`partner`、`global`、`eu`，须与令牌来源一致。 |
| managementType | string | 是 | 默认 `semi-managed`，兼容 `full-managed`；区分店铺托管类型。 |
| accessToken | string | 与 storeKey 二选一 | Temu 店铺令牌；传入时优先于本地令牌。 |
| storeKey | string | 脚本兼容 | 本地店铺键，脚本读取令牌后仅发送 accessToken，不将 storeKey 发给网关。 |
| tokenPurpose | string | 否 | 本技能店铺令牌默认用途 `product-inventory`；用于本地定位，不发往网关。 |
| type | string | 是 | 固定为 `bg.local.compliance.goods.list.query`；大小写与原值一致。 |
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

##### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pageNo | INTEGER | **是** | 页码 |
| pageSize | INTEGER | **是** | 每页条数，**默认 25** |
| searchText | STRING | 否 | 支持按 **goodsName** / **goodsId** / **skuId** 搜索 |
| statusList | INTEGER[] | 否 | 合规状态筛选，见下表 |
| optionalConditionList | OBJECT[] | 否 | 合规信息筛选 |

###### `statusList` / 各块 `status` 枚举

| 值 | 说明 |
|----|------|
| `1` | 未提交 |
| `2` | 待审核 |
| `3` | 审核中 |
| `4` | 需处理 |
| `5` | 已通过 |
| `6` | 已拒绝 |
| `7` | 待更新 |

##### `optionalConditionList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| complianceType | INTEGER | 否 | `1` 治理属性；`2` 通用产品安全法规（GPSR） |
| templateId | INTEGER | 否 | 合规模板类型筛选（文档与 `complianceType` 同组说明：`1` 治理属性 / `2` GPSR） |
| repType | INTEGER | 否 | `2` 欧盟负责人；`3` 制造商。**`complianceType=2` 时必填** |
| actualPhotoCheckType | LONG | 否 | 实拍图 checkType。**`complianceType=3` 时必填** |
| certType | LONG | 否 | 资质 checkType。**`complianceType=4` 时填写** |

> 筛选侧 `complianceType` 除 `1`/`2` 外，通过条件字段可推断 **`3`** 实拍、`**4**` 资质等类型（以 Partner 与实网为准）。

> **勿**使用字段 `goodsIdList`、`complianceStatus`；官方为 **`statusList`** + **`optionalConditionList`**。

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
| success | BOOLEAN | 当前请求是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 业务结果 |
| result.total | LONG | 总条数 |
| result.goodsList | OBJECT[] | 商品列表 |

##### `result.goodsList[]`

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

##### `extraTemplateInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| templateId | INTEGER | 治理属性模板 ID |
| status | INTEGER | 合规状态，见 `statusList` 枚举 |

##### `gpsrInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| repType | INTEGER | `2` 欧盟负责人；`3` 制造商 |
| status | INTEGER | 合规状态 |

##### `repInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| repType | INTEGER | `4` 售后负责人 |
| status | INTEGER | 合规状态 |

##### `actualPhotoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| actualPhotoCheckType | LONG | 实拍图检查类型 |
| status | INTEGER | 合规状态 |

##### `certificateInfoList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| certType | LONG | 本证书资质类型 |
| status | INTEGER | 合规状态 |

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
  "type": "bg.local.compliance.goods.list.query",
  "params": {
    "request": {
      "pageNo": 1,
      "pageSize": 25,
      "statusList": [
        4,
        7
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
  "skillName": "linkfox-temu-manage-product-us",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
