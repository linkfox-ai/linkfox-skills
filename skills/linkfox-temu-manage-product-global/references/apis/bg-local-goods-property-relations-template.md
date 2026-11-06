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

## 接口：关系属性值查询 — `bg.local.goods.property.relations.template`

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
| type | string | 是 | 本接口固定 `bg.local.goods.property.relations.template`。 |
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
    ├── catId                         ← 必填
    ├── relationId                    ← 必填
    ├── relationType                  ← 必填，车型库传 1
    └── propertyRelationQueryDTOList[]  ← 选填
        ├── propertyDependencyId
        └── parentPropertyValueDependencyId
```

##### `request` 内字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| catId | LONG | **是** | 商品类目 ID。须为**叶子类目**，且与 `category_version` 所指定类目树类型下的叶子类目一致 |
| relationId | LONG | **是** | 关系库 ID（兼容车型库 ID，通常来自 [level.template](./bg-local-goods-property-relations-level-template.md) 的 `levelPropertyDependencyList[].relationId`） |
| relationType | INTEGER | **是** | 关系类型；查询**兼容车型库**时传 **`1`** |
| propertyRelationQueryDTOList | OBJECT[] | 否 | 查询条件；用于指定 `propertyDependencyId` 与 `parentPropertyValueDependencyId`。**留空或不传时，返回全部 level 1 的 `propertyValueId`** |

###### `relationType`（已知）

| 值 | 说明 |
|----|------|
| `1` | 查询兼容车型数据库 |

##### `propertyRelationQueryDTOList[]`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| propertyDependencyId | LONG | 否 | 属性依赖 ID，对应层级分类名（`propertyName`），表示该 `relationId` 下的当前层级 |
| parentPropertyValueDependencyId | LONG | 否 | 上一级（父级）属性**值**的 dependency id |

> 请求侧为 **`parentPropertyValueDependencyId`**（值级父 ID）；与 [level.template](./bg-local-goods-property-relations-level-template.md) 层级定义中的 **`parentPropertyDependencyId`**（层级结构父 ID）名称不同，勿混用。

> **勿**使用字段 `pid`、`parentVid`、`levelId`。

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
    └── parentPropValDepMapDTOList[]
        ├── parentPropertyValueDependencyId
        └── propValDepDTOList[]
            ├── propertyDependencyId
            ├── propertyValueDependencyId
            ├── parentPropertyValueDependencyId
            ├── propertyValueId
            ├── propertyValue
            └── isLeafProperty
```

| 参数 | 类型 | 说明 |
|------|------|------|
| success | BOOLEAN | 是否成功 |
| errorCode | INTEGER | 错误码 |
| errorMsg | STRING | 错误信息 |
| result | OBJECT | 具体信息 |
| result.parentPropValDepMapDTOList | OBJECT[] | 父属性值与其子属性值列表 |

##### `result.parentPropValDepMapDTOList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| parentPropertyValueDependencyId | LONG | 父级属性值的 dependency id（上一级） |
| propValDepDTOList | OBJECT[] | 该父值下，下一层级的属性值数据列表 |

##### `propValDepDTOList[]`

| 参数 | 类型 | 说明 |
|------|------|------|
| propertyDependencyId | LONG | 用于查询层级之间关系的 dependency id |
| propertyValueDependencyId | LONG | 属性值 dependency id，对应当前层级；与 `propertyName` 对应 |
| parentPropertyValueDependencyId | LONG | 父级属性值的 dependency id |
| propertyValueId | LONG | 属性值 ID；与 `propertyValueDependencyId` **一一对应** |
| propertyValue | STRING | 兼容车型枚举展示值，如品牌/年份/发动机等，例：`Toyota`、`1987`、`Base Convertible 2-Door` |
| isLeafProperty | BOOLEAN | `true`：该属性值为**最末级**；`false`：非最末级，可继续级联查询下一层 |

###### 级联查询示意

```text
1. level.template → 得到 relationId、各层 propertyDependencyId / level / propertyName
2. relations.template（本接口）
   - 首次：propertyRelationQueryDTOList 为空 → 返回 level 1 全部 propertyValueId
   - 用户选中某值后：带上 parentPropertyValueDependencyId + propertyDependencyId 再查下一层
   - isLeafProperty=true 的项可作为叶子，写入 goodsVehiclePropertyRelation.leafPropertyValueDependencyIdList
3. property.relations → 按 goodsId 读取商品已保存关联
```

#### 与同族接口协作

| 步骤 | 接口 | 作用 |
|------|------|------|
| 1 | [level.template](./bg-local-goods-property-relations-level-template.md) | 拉层级定义 `levelPropertyDependencyList[]` |
| 2 | **本接口** | 按 `relationId` + 查询 DTO 拉各层可选 `propertyValue` |
| 3 | [property.relations](./bg-local-goods-property-relations.md) | 读商品已选车型数据 |
| 4 | [partial.update](./bg-local-goods-partial-update.md) | `goodsVehiclePropertyRelation` 写回 |

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
  "type": "bg.local.goods.property.relations.template",
  "params": {
    "request": {
      "catId": 12345,
      "relationId": 10001,
      "relationType": 1
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
