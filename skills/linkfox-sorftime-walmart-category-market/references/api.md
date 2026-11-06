# Walmart 类目市场研究 接口说明

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

## 脚本运行约定

| 项目 | 类型 / 默认值 | 说明 |
|---|---|---|
| JSON 参数 | object，必填 | 首个位置参数；字段扁平放在顶层，不批量包装。 |
| `--inline` | CLI flag，默认关闭 | 强制全量打印，同时保存完整响应。 |
| `--no-cache` | CLI flag，默认关闭 | 跳过业务缓存的读取与写入；公共调用器始终禁用其缓存，避免第二层缓存。 |
| 业务缓存 | 24 小时 | 缓存键为参数排序后 SHA-256 的前 16 位，路径为 `<cwd>/linkfox/.cache/linkfox-sorftime-walmart-category-market/`；以 JSON 保存完整结果（包括错误与空结果），读取时设置 `_cache.hit` 标记。 |
| `LINKFOX_TOOL_GATEWAY` | string，可选 | 优先使用此地址，默认 `https://tool-gateway.linkfox.com`，去除末尾 `/`。 |
| API Key | string | 优先 `LINKFOX_AGENT_API_KEY`，兼容 `LINKFOXAGENT_API_KEY`。 |
| 透传请求头 | string | `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 从同名环境变量读取。 |
| 输出目录 | 当前工作目录 | 请求前检查当前目录可写；响应及会话元数据只写 `<cwd>/linkfox/`，不回退到家目录、ACPX 工作目录或临时目录。 |
| `_cache.hit` | boolean，可选 | 缓存读取时为 `true`；费用字段是原始请求值，不能解释为新增扣费。 |

HTTP 请求构造、认证和发送由 `scripts/call_api.py` 完成。业务封装通过 `call_api.run` 编排，提供业务缓存、XML 解码和费用头注入；响应适配仅包装公共 transport 返回的内容，不另建 HTTP 客户端，不重试。

## 接口：完整类目树（tree）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/categoryMarket`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| operation | string | 是 | 固定为 `tree`，大小写严格匹配，无默认值；一次只执行一个操作。 |

#### 参数约束与使用限制

- 请求为顶层扁平 JSON，仅传本操作所需业务参数；无关参数、空白字符串或格式错误可能被拒绝。
- 固定面向 Walmart 美国站，后端使用 Sorftime `domain=21`，无需也不应自行指定其他站点。
- 本操作文档消耗为 5 个 Sorftime Request；不得批量或自动串行执行多个操作，不得未经用户授权重试或切换操作。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。
- 不需要其他业务参数。

### 响应结构

网关使用 `errcode` / `errmsg` 表示框架层状态，成功体内的 `code` / `msg` 表示业务层状态。通常为 `errcode=200`、`errmsg="ok"`、`code=200`、`msg="success"`；异常时可能只有框架层字段，先按公共基本规则判断。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；`data.value` 按 operation 保留 Sorftime 原始数组、对象、标量或 `null` |
| `operation` | string | 本次实际执行的 `tree` |
| `_http_status` | integer / null | 脚本本地附加字段，非网关字段。实时请求为实际 HTTP 状态，连接失败为 `null`；缓存命中时为原始请求状态，旧缓存未记录则为 `null`，不能据此推断成功，也不代表本次发起了 HTTP 请求。 |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |
| `data.value` | array<object> / null | 本操作的原始结果；元素字段见下表。固定容器也兼容上游对象、标量或 `null`，不强制转换。 |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。

业务结果统一从 `data.value` 读取。网关不会改名、扁平化或补造其中的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

#### `data.value`：完整类目树字段


类目树响应通常超过 10 MB，应使用脚本默认落盘模式，不要频繁 `--inline`。

| 字段 | 类型 | 说明 |
|---|---|---|
| `Id` | integer | 类目 ID |
| `ParentId` | integer | 父类目 ID；`0` 表示顶层 |
| `NodeId` | string | Walmart 类目节点 ID |
| `Name` | string | 英文类目名称 |
| `CNName` | string | 中文类目名称 |
| `URL` | string | 类目 URL |


### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架层正常后检查业务 `code` 与 `msg`；业务 `code=200` 表示成功，无数据可能提示“查询成功，但无数据”，不补造结果。
- Sorftime 明确返回 `Code=11` 时按无数据处理，保持上游零消耗，不按文档消耗补全。


| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`，并确认 operation 大小写及枚举值正确 |
| 4001 | 后端语义校验失败 | 检查无关参数及 `operation` 的值 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换参数连续重试 |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4000,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
curl --max-time 150 -sS -i -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/categoryMarket" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"tree"}'
```

## 接口：类目名称匹配（searchByName）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/categoryMarket`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| operation | string | 是 | 固定为 `searchByName`，大小写严格匹配，无默认值；一次只执行一个操作。 |
| name | string | 是 | 自然语言类目名称，非空，例如 `patio furniture`；对应 Sorftime `CategorySearchFromName`。 |

#### 参数约束与使用限制

- 请求为顶层扁平 JSON，仅传本操作所需业务参数；无关参数、空白字符串或格式错误可能被拒绝。
- 固定面向 Walmart 美国站，后端使用 Sorftime `domain=21`，无需也不应自行指定其他站点。
- 本操作文档消耗为 1 个 Sorftime Request；不得批量或自动串行执行多个操作，不得未经用户授权重试或切换操作。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。
- 最多返回 3 个相关类目，不保证精确分类。返回的 `NodeId` 是完整下划线路径，可作为后续市场报告的 `nodePath`，但不得自动追加请求。

### 响应结构

网关使用 `errcode` / `errmsg` 表示框架层状态，成功体内的 `code` / `msg` 表示业务层状态。通常为 `errcode=200`、`errmsg="ok"`、`code=200`、`msg="success"`；异常时可能只有框架层字段，先按公共基本规则判断。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；`data.value` 按 operation 保留 Sorftime 原始数组、对象、标量或 `null` |
| `operation` | string | 本次实际执行的 `searchByName` |
| `_http_status` | integer / null | 脚本本地附加字段，非网关字段。实时请求为实际 HTTP 状态，连接失败为 `null`；缓存命中时为原始请求状态，旧缓存未记录则为 `null`，不能据此推断成功，也不代表本次发起了 HTTP 请求。 |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |
| `data.value` | array<object> / null | 本操作的原始结果；元素字段见下表。固定容器也兼容上游对象、标量或 `null`，不强制转换。 |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。

业务结果统一从 `data.value` 读取。网关不会改名、扁平化或补造其中的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

#### `data.value`：类目名称匹配字段


| 字段 | 类型 | 说明 |
|---|---|---|
| `NodeId` | string | 下划线分隔的完整类目路径，可直接作为 `marketReport.nodePath` |
| `CategoryName` | string | 类目展示名称 |


### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架层正常后检查业务 `code` 与 `msg`；业务 `code=200` 表示成功，无数据可能提示“查询成功，但无数据”，不补造结果。
- Sorftime 明确返回 `Code=11` 时按无数据处理，保持上游零消耗，不按文档消耗补全。


| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`，并确认 operation 大小写及枚举值正确 |
| 4000 | operation 的条件必填参数缺失 | 补充非空 `name` |
| 4001 | 后端语义校验失败 | 检查无关参数及 `name` 是否为空白字符串 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换参数连续重试 |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4000,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
curl --max-time 150 -sS -i -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/categoryMarket" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"searchByName","name":"patio furniture"}'
```

## 接口：类目市场报告（marketReport）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/sorftime/walmart/categoryMarket`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| operation | string | 是 | 固定为 `marketReport`，大小写严格匹配，无默认值；一次只执行一个操作。 |
| nodePath | string | 是 | 已知的完整数字类目 ID 路径，以下划线分隔，例如 `4044_623679_1032619_5842891_9823303`；从类目树或名称匹配的 `NodeId` 获得，不得凭名称猜测。 |

#### 参数约束与使用限制

- 请求为顶层扁平 JSON，仅传本操作所需业务参数；无关参数、空白字符串或格式错误可能被拒绝。
- 固定面向 Walmart 美国站，后端使用 Sorftime `domain=21`，无需也不应自行指定其他站点。
- 本操作文档消耗为 5 个 Sorftime Request；不得批量或自动串行执行多个操作，不得未经用户授权重试或切换操作。
- 上游普通 JSON 与 Base64/GZip 响应的识别、校验及解码由服务端完成。
- `nodePath` 只接受数字 ID 及下划线组成的完整路径，不接受自由文本名称。返回商品摘要数组，不额外嵌套 `Products`，不代表完整类目目录。

### 响应结构

网关使用 `errcode` / `errmsg` 表示框架层状态，成功体内的 `code` / `msg` 表示业务层状态。通常为 `errcode=200`、`errmsg="ok"`、`code=200`、`msg="success"`；异常时可能只有框架层字段，先按公共基本规则判断。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | 网关框架层状态码；`200` 表示请求成功进入业务响应 |
| `errmsg` | string | 网关框架层状态消息；成功时通常为 `ok` |
| `code` | integer | `200` 表示成功 |
| `msg` | string | 响应消息；无数据时可能为“查询成功，但无数据” |
| `data` | object | 固定响应容器；`data.value` 按 operation 保留 Sorftime 原始数组、对象、标量或 `null` |
| `operation` | string | 本次实际执行的 `marketReport` |
| `_http_status` | integer / null | 脚本本地附加字段，非网关字段。实时请求为实际 HTTP 状态，连接失败为 `null`；缓存命中时为原始请求状态，旧缓存未记录则为 `null`，不能据此推断成功，也不代表本次发起了 HTTP 请求。 |
| `requestConsumed` | integer | 本次上游消耗；上游缺失或返回 0 时按该 operation 的文档消耗补全；Sorftime 明确返回 `Code=11`（无数据）时保持 0 |
| `costTime` | integer | 耗时，毫秒 |
| `costToken` | integer / absent | 生产网关响应头 `X-Cost-Token`；入口脚本会复制到该字段。直接解析 JSON body 时该字段当前缺失 |
| `costCredit` | integer / absent | 生产网关响应头 `X-Cost-Credit`，即本次实际扣除算力；入口脚本会复制到该字段 |
| `sourceType` | string | `sorftime` |
| `data.value` | array<object> / null | 本操作的原始结果；元素字段见下表。固定容器也兼容上游对象、标量或 `null`，不强制转换。 |

Sorftime 明确返回 `Code=11`（无数据）时，网关保持 `requestConsumed=0`、`X-Cost-Token=0`，不按文档消耗补全；`X-Cost-Credit` 此时可能缺失。使用入口脚本时直接读取 `costToken` / `costCredit`；直接使用 curl 时从对应响应头读取。

业务结果统一从 `data.value` 读取。网关不会改名、扁平化或补造其中的 Sorftime 字段，因此下表字段保持上游 PascalCase。无数据时 `data.value` 可能为 `null` 或空数组；有数据但某个指标暂缺时，对应字段可能为 `null` 或不出现。

#### `data.value`：类目市场报告字段


| 字段 | 类型 | 说明 |
|---|---|---|
| `Title` | string | 商品标题 |
| `Photo` | array<string> | 商品图片 URL 数组 |
| `ListingSalesVolumeOfMonth` | integer | Listing 维度近 30 天预估销量，不区分变体 |
| `ListingSalesOfMonth` | integer | Listing 维度近 30 天预估销售额；美国站单位为美分 |
| `ProductId` | string | Walmart ProductId |
| `ParentProductId` | string | 父商品 ProductId |
| `Price` | integer | 售价；美国站单位为美分，如 `1999` 表示 `$19.99` |
| `Brand` | string | 品牌 |
| `Seller` | string | 采集时的卖家名称 |
| `Shipedby` | string | 采集时的配送方式；字段名是上游原始拼写 |
| `WFSFee` | integer | WFS 费用；美国站单位为美分 |
| `Attribute` | array<string> / null | 商品属性，按 `[属性名, 属性值, ...]` 交错编码 |
| `FirstReviewsDate` | string / null | 首条评论日期，`yyyy-MM-dd` |
| `ReviewsCount` | integer | 评论数 |
| `Ratings` | number | 评分，如 `4.8` |
| `NodePath` | array<string\|null> | 类目及排名记录，按 `[类目名, NodeId, 排名日期, 排名, ...]` 分组编码；某日排名缺失时对应位置为 `null` |
| `Label` | array<string> | 商品标签，如 `pickup`、`savewith`、`bestsell` |
| `PopularPick` | integer | Popular Pick 标记；`1` 表示存在 |
| `Clearance` | integer | Clearance 标记；`1` 表示存在 |
| `ReducedPrice` | integer | Reduced Price 标记；`1` 表示存在 |
| `Rollback` | integer | Rollback 标记；`1` 表示存在 |
| `FlashDeal` | integer | Flash Deal 标记；`1` 表示存在 |
| `Size` | array<string> / null | 外包装尺寸 `[最长边, 次长边, 最短边]`，单位 cm |
| `Weight` | number | 商品重量，单位 g |
| `Variants` | array<object> / null | 变体列表，字段见下表 |
| `NumberOfStar` | array<number\|string> / null | 各星级评论数，按 `[星级, 评论数, ...]` 交错编码 |

`Variants` 数组元素：

| 字段 | 类型 | 说明 |
|---|---|---|
| `VariantId` | string | 变体 ProductId |
| `Url` | string | 变体商品 URL |
| `Property` | array<string> | 变体属性，按 `[属性名, 属性值, ...]` 编码 |
| `PriceUpdate` | string / null | 价格更新时间，通常为 `yyyy-MM-dd` |
| `DetailUpdate` | string / null | 详情更新时间，通常为 `yyyy-MM-dd`；无有效日期时可能使用 `--` 等上游占位符 |


### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 框架层正常后检查业务 `code` 与 `msg`；业务 `code=200` 表示成功，无数据可能提示“查询成功，但无数据”，不补造结果。
- Sorftime 明确返回 `Code=11` 时按无数据处理，保持上游零消耗，不按文档消耗补全。


| errcode / HTTP | 含义 | 处理建议 |
|---:|---|---|
| 400 | 网关请求结构校验失败 | 检查全局必填 `operation`，并确认 operation 大小写及枚举值正确 |
| 4000 | operation 的条件必填参数缺失 | 补充有效 `nodePath` |
| 4001 | 后端语义校验失败 | 检查无关参数、空白字符串及 `nodePath` 的数字下划线路径格式 |
| 5101–5103 | 上游 HTTP、响应或解析异常 | 不自动换参数连续重试 |
| 5104–5108 | 上游访问受限、参数、IP 或权限异常 | 核对参数；权限类问题交由服务维护方处理 |
| 5109–5111 | 上游额度或频率限制 | 稍后重试；不要连续请求 |
| 5112 | 其他上游业务异常 | 保留返回信息并反馈 |
| 5901 | 服务内部错误 | 稍后重试或反馈 |

网关参数校验错误可能使用 `application/xml` 返回 `ToolErrorResponse`，HTTP 状态可能为 200 或 400。入口脚本会把该 XML 统一转换成 JSON：`{"errcode":4000,"errmsg":"..."}`；直接使用 curl 时需同时兼容 JSON 与 XML。

### curl 示例

```bash
curl --max-time 150 -sS -i -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/sorftime/walmart/categoryMarket" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: $SESSION_ID" -H "MESSAGE_ID: $MESSAGE_ID" \
  -H "MODE_ID: $MODE_ID" -H "APP_NAME: $APP_NAME" \
  -d '{"operation":"marketReport","nodePath":"4044_623679_1032619_5842891_9823303"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-sorftime-walmart-category-market",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
