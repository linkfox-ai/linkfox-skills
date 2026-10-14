# 卖大律产品侵权 TRO 风险检测能力归档

本 reference 归档 `linkfox-maidalv-product-tro-detection` 的能力说明、参数、响应、错误码、MCP 调用、两阶段本地图片上传与反馈接口。检测 endpoint 为 `/maidalv/checkApiFlash`，预签名 endpoint 为 `/oss/file/presignedPut`。

## 能力说明

该能力检测产品是否存在 TRO（Temporary Restraining Order，临时限制令）或知识产权侵权风险：将产品主图与商标、专利、版权资产及 TRO 案件原告记录匹配，可补充参考图片、产品文字和 IP 关键词。返回总体风险等级、高风险侵权项、低风险/非高风险 IP 项、TRO 原告信息、数值风险分和 AI 生成的法律评估报告。

## 核心概念

TRO 是品牌方常用于针对商标/版权/专利侵权卖家的临时禁令。本能力要求一个主商品图片，可再传相似产品参考图、其他产品图片、IP 相关图片、产品文本和关键词，执行视觉与文本匹配；`language` 仅决定 `report` 的语言。

## 响应结构

响应字段来源：`skills/linkfox-maidalv-product-tro-detection/references/api.md`。

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer | 业务状态码，200 表示成功（其他值见「错误码」） |
| errmsg | string | 状态说明（成功为 `ok`） |
| status | string | 分析的整体状态（成功为 `success`） |
| checkId | string | 本次检测的唯一标识 |
| type | string | 渲染样式（如 `tableListWorkbenches`） |
| costToken | integer | 本次消耗 token |
| total | integer | 高风险侵权项数量（即 `results` 数组长度） |
| riskLevel | string | 总体风险评估（`高风险` / `中风险` / `低风险`，对应 High/Medium/Low Risk） |
| results | array | 高风险潜在侵权项列表，详见下方「侵权项字段」 |
| nonResults | array | 非高风险 / 低相似度 IP 项列表（商标、版权、专利等，含 TRO 原告信息），详见下方「侵权项字段」 |
| columns | array | 渲染列定义（渲染元数据，长度可与数据数组不同，仅供展示） |

来源没有说明 `columns[]` 元素的字段、类型或结构，因此只能保留父数组，不能根据渲染用途补猜子字段。

### `results[]` 高风险侵权项

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `results[]` | object | 高风险潜在侵权项 |
| `results[].ipType` | string | IP 类型，实际返回为大写首字母：`Trademark` / `Copyright` / `Patent` |
| `results[].text` | string | IP 文本内容（商标文字、专利标题或版权标题） |
| `results[].ipOwner` | string | 知识产权权利人 |
| `results[].regNo` | string | 注册号（商标序列号、专利号或版权登记号；可能返回 JSON 字符串形式的数组，如 `["1221667"]`） |
| `results[].riskLevel` | string | 风险级别（High/Medium/Low Risk）；无评分时为 `null` |
| `results[].riskScore` | number | 数值风险分（0-10）；无评分时为 `null` |
| `results[].riskDescription` | string | 风险级别文字说明；无评分时为 `null` |
| `results[].ipAssetUrls` | string[] | 查看 IP 证据图片的 URL 列表 |
| `results[].ipAssetUrls[]` | string | 单个 IP 证据图片 URL |
| `results[].plaintiffId` | integer | 原告 ID，仅当该 IP 出现在 TRO 案件中时存在 |
| `results[].plaintiffName` | string | 原告名称，仅当该 IP 出现在 TRO 案件中时存在 |
| `results[].numberOfCases` | integer | 该原告提起的案件数量，仅当出现在 TRO 案件中时存在 |
| `results[].lastCaseDocket` | string | 最近案件的法院案号，仅当出现在 TRO 案件中时存在 |
| `results[].lastCaseDateFiled` | string | 最近案件的立案日期，仅当出现在 TRO 案件中时存在 |
| `results[].report` | string | AI 生成的法律评估报告（按 `language` 参数输出中文或英文） |

### `nonResults[]` 非高风险或低相似度 IP 项

| 字段路径 | 类型 | 说明 |
|---|---|---|
| `nonResults[]` | object | 非高风险 / 低相似度 IP 项 |
| `nonResults[].ipType` | string | IP 类型，实际返回为大写首字母：`Trademark` / `Copyright` / `Patent` |
| `nonResults[].text` | string | IP 文本内容（商标文字、专利标题或版权标题） |
| `nonResults[].ipOwner` | string | 知识产权权利人 |
| `nonResults[].regNo` | string | 注册号（商标序列号、专利号或版权登记号；可能返回 JSON 字符串形式的数组，如 `["1221667"]`） |
| `nonResults[].riskLevel` | string | 风险级别（High/Medium/Low Risk）；无评分时为 `null` |
| `nonResults[].riskScore` | number | 数值风险分（0-10）；无评分时为 `null` |
| `nonResults[].riskDescription` | string | 风险级别文字说明；无评分时为 `null` |
| `nonResults[].ipAssetUrls` | string[] | 查看 IP 证据图片的 URL 列表 |
| `nonResults[].ipAssetUrls[]` | string | 单个 IP 证据图片 URL |
| `nonResults[].plaintiffId` | integer | 原告 ID，仅当该 IP 出现在 TRO 案件中时存在 |
| `nonResults[].plaintiffName` | string | 原告名称，仅当该 IP 出现在 TRO 案件中时存在 |
| `nonResults[].numberOfCases` | integer | 该原告提起的案件数量，仅当出现在 TRO 案件中时存在 |
| `nonResults[].lastCaseDocket` | string | 最近案件的法院案号，仅当出现在 TRO 案件中时存在 |
| `nonResults[].lastCaseDateFiled` | string | 最近案件的立案日期，仅当出现在 TRO 案件中时存在 |
| `nonResults[].report` | string | AI 生成的法律评估报告（按 `language` 参数输出中文或英文） |

> 字段填充规则：IP 项的字段是**按需出现**的——非 TRO、未评分的项只返回基础字段（`ipType`/`text`/`ipOwner`/`regNo`/`ipAssetUrls`），`plaintiffName`/`plaintiffId`/`numberOfCases`/`lastCaseDocket`/`lastCaseDateFiled` 等字段**不出现**（而非 null）；当该 IP 出现在 TRO 案件中时，`plaintiffName`/`plaintiffId` 带值返回，`numberOfCases`/`lastCaseDocket`/`lastCaseDateFiled` 可能为 `null`（无案件细节）。`riskLevel`/`riskScore`/`riskDescription` 仅在给出评分时出现，否则不出现。高风险项（命中）放入 `results`，其余放入 `nonResults`。

### 图片预签名响应

字段来源：`skills/linkfox-maidalv-product-tro-detection/scripts/upload_image.py`。该来源脚本明确检查或读取以下字段，没有定义其他响应字段或嵌套层级。

| 字段 | 类型 | 说明 |
|---|---|---|
| `errcode` | integer | `200` 表示成功；其他值表示预签名接口错误。 |
| `errmsg` | string | 预签名接口错误说明；来源脚本在缺失时使用 `unknown error`。 |
| `url` | string | 成功时返回的预签名 PUT URL；其查询参数属于敏感签名，不得展示。 |

## 请求参数

检测通过 `LinkFox.proxy_call` 调用，精确 `toolName` 为 `maidalv/checkApiFlash`。下表请求对象直接放入 `proxy_call.arguments`，不得额外包裹 `body`、`params` 或 `data`。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `mainProductImage` | string | 是 | — | 主商品图片 URL，或带 `data:image/...;base64,` 前缀的 Base64 data URI；最大 1000 字符。 |
| `referenceImages` | string[] | 否 | — | 相似产品参考图 URL/data URI，最多 3 张。 |
| `otherProductImages` | string[] | 否 | — | 其他产品图 URL/data URI，最多 5 张。 |
| `ipImages` | string[] | 否 | — | IP 相关图片 URL/data URI，最多 3 张。 |
| `referenceText` | string | 否 | — | 相似产品文字，例如产品标题；最大 1000 字符。 |
| `description` | string | 否 | — | 产品描述，建议使用产品标题；最大 1000 字符。 |
| `ipKeywords` | string[] | 否 | — | IP 相关关键词，最多 20 个。 |
| `language` | string | 否 | `zh` | 法律评估报告语言，只能取 `zh` 或 `en`，只影响 `report`。 |

图片 URL 必须可公开访问。本地图片先用 MCP `toolName=oss/file/presignedPut` 请求预签名地址，再运行 `scripts/upload_image.py <local_image_path>` 并仅通过标准输入提供预签名 URL，完成外部存储 PUT；也可自行转成带完整 MIME 前缀的 data URI。

## MCP 调用

### 风险检测

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 原 endpoint：`/maidalv/checkApiFlash`
- 精确 `toolName`：`maidalv/checkApiFlash`
- `arguments`：直接使用“请求参数”表中的检测对象。
- WorkBuddy 自动注入授权；禁止传 `headers`、Authorization、API Key、token、JWT、手机号或其他凭证。
- 先检查 MCP 连接、schema 和 `isError`，再读取 text/structured content；text JSON 只解析一次，之后检查下游 `errcode`/`errmsg`。
- 同一任务内相同 `toolName + arguments` 不得重复调用。失败、空结果或结果不理想不得自动换图、换词或重试收费检测；MCP 不可用时禁止 HTTP fallback。

```json
{
  "toolName": "maidalv/checkApiFlash",
  "arguments": {
    "mainProductImage": "https://example.com/product.jpg",
    "language": "zh"
  }
}
```

### 本地图片两阶段上传

- MCP server：`LinkFox`
- 唯一工具：`proxy_call`
- 原 endpoint：`/oss/file/presignedPut`
- 精确 `toolName`：`oss/file/presignedPut`
- `arguments`：直接传 `contentType` 和 `fileExtension`；WorkBuddy 自动授权，不传任何凭证。

1. 根据本地扩展名确定 `contentType` 与 `fileExtension`，调用预签名 endpoint：

```json
{
  "toolName": "oss/file/presignedPut",
  "arguments": {
    "contentType": "image/png",
    "fileExtension": "png"
  }
}
```

2. 检查 MCP/下游错误并从成功响应读取 `url`。不要显示或记录带查询参数的预签名 URL。
3. 立即运行 `python scripts/upload_image.py "./product.png"`，把预签名 URL 仅写入该进程的标准输入，不得放入命令行参数、日志或用户可见输出。该本地 helper 只校验文件、读取字节并向绝对 HTTPS 预签名 URL 发送 PUT，不读取 LinkFox 凭证，也不访问工具网关。
4. helper 成功输出不含签名查询参数的 `url` 和 `contentType`；将该公开 URL 用作检测图片参数。预签名过期或 PUT 失败时不得静默申请新地址或重新上传。

支持 `.jpg`、`.jpeg`、`.png`、`.gif`、`.webp`、`.heic`。旧检测脚本的 24 小时缓存、自动响应落盘、会话元数据和 stdout 摘要已移除，MCP 不提供这些本地行为。

## 错误码

代理层成功不等于下游业务成功；业务成功与否通过下游响应体 `errcode` 区分。

| errcode | 含义 | 处理 |
|---|---|---|
| `200` | 成功 | 正常解析业务字段。 |
| `401` | 认证失败 | 按 `references/onboarding.md` 的 WorkBuddy 自动授权异常处理，不传凭证。 |
| `402` | 积分不足 | 按顶层认证/计费流程处理，先让用户决定是否充值和继续。 |
| 其他非 200 | 业务异常 | 读取 `errmsg`，修正具体输入或配置；不要盲目重试。 |

按顺序区分 MCP 连接/schema/`isError`、代理内容解析和下游 `errcode`/`errmsg`。保留脱敏错误信息并给出输入或授权方向的修正建议，不得在错误后自动收费重试。

## MCP 示例

### 基础检测

```json
{
  "toolName": "maidalv/checkApiFlash",
  "arguments": {
    "mainProductImage": "https://m.media-amazon.com/images/I/71jKJgFpg8L._AC_SL1500_.jpg",
    "language": "zh"
  }
}
```

### 带参考图与 IP 关键词

```json
{
  "toolName": "maidalv/checkApiFlash",
  "arguments": {
    "mainProductImage": "https://example.com/product.jpg",
    "referenceImages": ["https://example.com/ref1.jpg"],
    "ipKeywords": ["apple", "iphone"],
    "language": "zh"
  }
}
```

## Feedback API

该接口与检测网关分离，不要混用基础 URL。

- POST `https://skill-api.linkfox.com/api/v1/public/feedback`
- `Content-Type: application/json`

```json
{
  "skillName": "linkfox-maidalv-product-tro-detection",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Detection was accurate, user was satisfied."
}
```

`sentiment` 只能是 `POSITIVE`、`NEUTRAL`、`NEGATIVE`；`category` 只能是 `BUG`、`COMPLAINT`、`SUGGESTION`、`OTHER`。`content` 应说明用户意图、实际结果和问题/表扬，不得写入 API Key、验证码、完整手机号或支付信息。

## 归档的使用限制

- 主图必填；本地图片须先上传或转 data URI。
- 结果是一站式分析，不提供 SQL 或二次查询；不能使用 `_dataQuery_executeDynamicQuery` 做后处理。
- `language` 只改变 `report` 语言，字段值按接口原样返回。
- 条件字段缺失是正常返回形态；`columns` 长度与业务数组可能不同。
- 检测结果不构成法律判定；供应商找货、专利全文检索、Listing 优化和关键词分析应由其他能力处理。
