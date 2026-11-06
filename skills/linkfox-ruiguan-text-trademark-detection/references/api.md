# 睿观文本商标检测 接口说明

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

## 接口：文本商标检测

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ruiguan/textTrademarkDetection`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| productTitle | string | 是 | 产品标题，用于商标检测（最大1000字符） |
| regions | string | 否 | 国家/地区代码，多个用逗号分隔；用户未指定时使用 US。支持值：US、EM、GB、DE、FR、IT、ES、AU、CA、MX、JP、CN、WO、TR、BX |
| limit | integer | 是 | 返回结果数量限制（默认100，最大500） |
| productText | string | 否 | 产品的其他文本信息，如五点描述或产品描述（最大1000字符） |

#### 地区代码

| 代码 | 国家或地区 |
|------|------------|
| US | 美国 |
| EM | 欧盟 |
| GB | 英国 |
| DE | 德国 |
| FR | 法国 |
| IT | 意大利 |
| ES | 西班牙 |
| AU | 澳大利亚 |
| CA | 加拿大 |
| MX | 墨西哥 |
| JP | 日本 |
| CN | 中国 |
| WO | WIPO（世界知识产权组织） |
| TR | 土耳其 |
| BX | 标注名称为 Bolivia（玻利维亚），名称与代码对应关系未核实；使用代码 BX，不据此推断实际管辖范围。 |

#### 参数约定与使用限制

- 必须提交完整商品标题；标题和附加文本各最多 1000 字符。附加文本可包括五点描述、产品描述和后台关键词；超长时先让用户确定范围，不静默截断。
- `regions` 是逗号分隔的字符串，不是数组；按目标市场选择，未指定时使用 `US`。数据库覆盖上述 15 个国家或地区，其他司法管辖区注册的商标可能无法检测。
- `limit` 为必填参数，默认值为 100；调用方显式传入 100 作为标准检测值，潜在匹配较多时可提高，单次最多 500 条。
- 本接口仅检测文本，不分析 Logo、图片或图形商标；记录为空不等于已经完成全部司法管辖区的商标清查。

#### 脚本选项与运行约定

| 项目 | 约定 |
|------|------|
| 命令 | `python scripts/ruiguan_text_trademark_detection.py '<JSON 参数>' [--inline] [--no-cache]` |
| JSON 参数 | 作为首个位置参数传入上述请求对象；脚本透传，不自动填入地区或返回数量。默认值由调用方按本文准备。 |
| `--inline` | 可选 CLI 开关，默认关闭；开启后强制全量打印，同时仍保存完整响应。 |
| `--no-cache` | 可选 CLI 开关，默认关闭；开启后跳过缓存读取和写入，默认启用 24 小时缓存。 |
| 缓存 | `<cwd>/linkfox/.cache/linkfox-ruiguan-text-trademark-detection/`；参数按键排序序列化后，取 SHA-256 前 16 位作为缓存键；文件名为 `<slug>-<key>.json`，TTL 从文件修改时间起计算。同参缓存跨进程可复用，命中增加 `_cache.hit=true`。缓存由公共调用器统一处理。 |
| 缓存范围 | 保存收到的 JSON，包括错误或空结果；再次付费尝试前遵守成本约束，不因命中缓存而自动重试。 |
| 认证兼容 | 优先 `LINKFOX_AGENT_API_KEY`，回退 `LINKFOXAGENT_API_KEY`；网关使用 `LINKFOX_TOOL_GATEWAY`，未配置则使用公共规则默认地址。 |
| 请求上下文 | 发送 `SESSION_ID`、`MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头，HTTP 超时 150 秒。 |
| 输出 | 完整响应以 UTF-8 保存，按 `SESSION_ID` 聚合会话并维护 `_meta.json` 与 `index.jsonl`；无会话标识时生成同进程稳定标识。输出大小阈值为 8000 UTF-8 字节，超过阈值默认展示最大列表的前 3 条样本。 |
| 目录 | 脚本依次尝试 `ACPX_WORKSPACES` 首个目录、当前工作目录、家目录、系统临时目录下的 `linkfox/`，选定后在进程内复用。调用前按 SKILL.md 检查可写工作目录及 `ACPX_WORKSPACES`，不依赖家目录或临时目录兜底；保存失败会在标准错误中报告，不能认定响应已落盘。 |
| Windows 路径 | 未启用长路径支持时使用较短的工作目录；缓存完整路径过长会导致缓存写入失败；脚本会忽略该写入错误。批量检测前检查缓存文件已生成，不能仅凭进程成功就认定结果已缓存。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 匹配到的商标记录数 |
| data | array | 商标列表（扁平化），每个元素包含以下字段 |
| detectId | string | 接口调用 ID |
| columns | array | 渲染的列定义 |
| blacklistTrademarks | array | 文本中检测到的黑名单商标 |
| whitelistTrademarks | array | 文本中检测到的白名单（安全）商标 |
| textTrademarkRadar | string | 产品风险等级："0" = 低风险，"1" = 待人工核查，"2" = 高风险 |
| costToken | integer | 消耗token |
| type | string | 渲染的样式 |

#### data[] 元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| trademarkName | string | 商标词 |
| region | string | 国家/地区代码 |
| score | integer | 风险分数 |
| highestModeScore | integer | 最高风险分数（范围0-5） |
| trademarksStatus | string | 最高分商标词状态 |
| regionStatus | string | 商标在匹配地区的状态 |
| holder | string | 权利人 |
| applicationNumber | string | 申请号 |
| registrationNumber | string | 注册号 |
| isFamous | boolean | 是否著名商标 |
| isAmazonBrand | boolean | 是否亚马逊热搜品牌 |
| isActiveHolder | boolean | 是否活跃维权人 |
| isCompatibility | boolean | 是否兼容性 |
| isCommonSense | boolean | 是否常用词 |
| niceClass | array | 尼斯分类 |
| originalTextMatches | array | 触发匹配的原词 |

#### blacklistTrademarks[] 和 whitelistTrademarks[] 元素字段

| 字段 | 类型 | 说明 |
|------|------|------|
| trademark | string | 商标名称 |
| region | string | 国家/地区代码 |
| note | string | 备注 |

#### 状态字段与兼容信息

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务响应码，200 表示成功；判断正常响应统一采用公共规则。 |
| errmsg | string | 业务或认证错误信息，例如 `authorized error`；用于解释失败原因。 |
| errorCode | 以实际返回为准 | 200 表示业务成功、其他值表示业务错误。该字段仅用于辅助解释；正常响应判断统一采用公共规则中的 HTTP 状态及 `errcode`。 |
| error | string | 脚本在连接失败或 HTTP 错误无可解析 JSON 时生成的错误说明。 |
| details | string | HTTP 错误正文无法解析为 JSON 时，脚本保留的原始正文。 |
| _cache.hit | boolean | 本地缓存命中时追加为 true；非上游字段。 |

`columns`、`niceClass`、`originalTextMatches` 的元素结构和其他嵌套字段以实际返回为准，原样保留，不推造子字段。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 正常响应后再解读风险结果；风险等级及黑白名单的展示要求见 `../SKILL.md` 的“约束与建议”，不能将低风险或无命中作为请求成功的判断依据。
- HTTP 错误带有 JSON 正文时，脚本保留该正文，不额外注入 HTTP 状态字段；没有 JSON 时输出 `error`，正文解析失败时另带 `details`。直接调用方保留 HTTP 状态并按公共规则处理，脚本结果有错误信息时不得当作“无风险”。

### 响应示例

认证失败响应示例：

```json
{
  "errcode": 401,
  "errmsg": "authorized error"
}
```

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/ruiguan/textTrademarkDetection" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "productTitle": "Portable USB-C Charger Fast Charging Power Bank",
    "productText": "Compatible with iPhone, Samsung Galaxy, supports QC 3.0",
    "regions": "US,EM,GB",
    "limit": 200
  }'
```

#### 其他请求场景（JSON）

美国站耳机标题检测：

```json
{"productTitle":"Wireless Bluetooth Headphones Noise Cancelling Over Ear","regions":"US","limit":100}
```

美国、欧盟和英国的多地区标准检测：

```json
{"productTitle":"Portable USB-C Charger Fast Charging Power Bank","regions":"US,EM,GB","limit":100}
```

美国和日本的完整 Listing 检查：

```json
{"productTitle":"Stainless Steel Vacuum Insulated Water Bottle","productText":"BPA-free, double-wall insulation, keeps drinks cold 24 hours, fits standard cup holders","regions":"US,JP","limit":200}
```

广泛销售地区检查：

```json
{"productTitle":"LED Ring Light with Tripod Stand for Streaming","regions":"US,EM,GB,DE,FR,IT,ES,AU,CA,MX,JP,CN","limit":500}
```

中国市场中文标题检查：

```json
{"productTitle":"智能蓝牙耳机降噪头戴式","regions":"CN","limit":100}
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-ruiguan-text-trademark-detection",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```