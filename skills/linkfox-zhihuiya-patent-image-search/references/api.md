# 智慧芽外观专利图片检索 接口说明

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

## 接口：外观专利图片检索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/patentImageSearch`

### 请求参数

POST Body（JSON）：

#### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 图像的URL（最大1000字符） |
| patentType | string | 是 | 专利类型：`D`（外观专利）或 `U`（实用新型专利）。默认：`D` |
| model | integer | 是 | 图像检索模型。外观专利：`1`（智能联想，推荐）、`2`（搜索此图）；实用新型专利：`3`（匹配形状）、`4`（匹配形状/图案/色彩，推荐） |

#### 可选参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| country | string | 否 | 专利受理局（国家/组织/地区代码），多个用英文逗号隔开。例如：`CN,US,JP`。不传时代表查询全部专利受理局的数据 |
| loc | string | 否 | LOC分类（洛迦诺分类号），多个分类号可以用逻辑符 AND/OR/NOT 连接 |
| legalStatus | string | 否 | 专利的法律状态，多个用英文逗号隔开。可选值：`1`（公开）、`2`（实质审查）、`3`（授权）、`8`（避免重复授权）、`11`（撤回）、`12`（撤回-未指定类型）、`17`（撤回-视为撤回）、`18`（撤回-主动撤回）、`13`（驳回）、`14`（全部撤销）、`15`（期限届满）、`16`（未缴年费）、`21`（权利恢复）、`22`（权利终止）、`23`（部分无效）、`24`（申请终止）、`30`（放弃）、`19`（放弃-视为放弃）、`20`（放弃-主动放弃）、`25`（放弃-未指定类型）、`222`（PCT未进入指定国-指定期内）、`223`（PCT进入指定国-指定期内）、`224`（PCT进入指定国-指定期满）、`225`（PCT未进入指定国-指定期满） |
| simpleLegalStatus | string | 否 | 专利的简单法律状态，多个用英文逗号隔开。可选值：`0`（失效）、`1`（有效）、`2`（审中）、`220`（PCT指定期满）、`221`（PCT指定期内）、`999`（未确认） |
| assignees | string | 否 | 申请（专利权）人（最大1000字符） |
| applyStartTime | string | 否 | 专利申请起始时间，格式：`yyyyMMdd` |
| applyEndTime | string | 否 | 专利申请截止时间，格式：`yyyyMMdd` |
| publicStartTime | string | 否 | 专利公开起始时间，格式：`yyyyMMdd` |
| publicEndTime | string | 否 | 专利公开截止时间，格式：`yyyyMMdd` |
| limit | integer | 否 | 返回专利条数，1-100。默认：`10` |
| offset | integer | 否 | 偏移量，0-1000。默认：`0` |
| field | string | 否 | 返回结果排序字段：`SCORE`（按照最相关排序）、`APD`（按照申请日排序）、`PBD`（按照公开日排序）、`ISD`（按照授权日排序）。默认：`SCORE` |
| order | string | 否 | 当 field 选择 APD/PBD/ISD 时有效：`desc`（降序）或 `asc`（升序）。默认：`desc` |
| lang | string | 否 | 设置标题的语言优先选择：`original`（专利原文标题）、`cn`（专利中文翻译标题）、`en`（专利英文翻译标题）。默认：`original` |
| preFilter | integer | 否 | 是否开启前置国家/LOC过滤：`1`（开启）、`0`（关闭）。默认：`1` |
| stemming | integer | 否 | 是否开启截词功能：`1`（开启）、`0`（关闭）。默认：`0` |
| mainField | string | 否 | 专利主要字段，包括标题、摘要、权利要求、说明书、公开号、申请号、申请人、发明人和IPC/UPC/LOC分类号（最大1000字符） |
| includeMachineTranslation | boolean | 否 | 搜索包含机器翻译数据 |
| scoreExpansion | boolean | 否 | 分数拓展 |
| isHttps | integer | 否 | 选择是否返回https域名图片：`1`（返回https）、`0`（返回http）。默认：`0` |
| returnImgId | boolean | 否 | 是否返回img_id。默认：`false` |

**注意**：
- `model` 参数须与 `patentType` 匹配：模型1-2用于外观专利（`D`），模型3-4用于实用新型专利（`U`）

本技能仅使用 `patentType=D`；脚本会强制将传入值纠正为 `D`，缺省 `model` 为 `1`，仅接受整数 `1` 或 `2`。模型 `1` 为智能联想（推荐），模型 `2` 为搜索此图、用于精确视觉匹配；上表保留通用接口的 `U` 和模型 `3`/`4` 定义，但本技能不使用这些取值。实用新型检索应使用对应技能。

图片 `url` 必须可公开访问；本地文件先使用下方预签名上传流程。国家、LOC、法律状态、日期等可选筛选项无另行声明默认值时不传。

#### 常用专利受理局代码

| 代码 | 国家、组织或地区 |
|------|------|
| CN | 中国 |
| US | 美国 |
| JP | 日本 |
| KR | 韩国 |
| EP | 欧洲专利局 |
| WO | 世界知识产权组织（WIPO） |
| DE | 德国 |
| GB | 英国 |
| FR | 法国 |
| AU | 澳大利亚 |

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| JSON 参数 | object | 是 | CLI 接受一个 JSON 对象；除脚本归一化 `patentType` 和默认 `model` 外，其他字段透传。 |
| --inline | CLI flag | 否 | 强制全量打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 禁止读取、写入业务响应缓存；不改变完整响应落盘。 |
| SESSION_ID | 环境变量 string | 否 | 聚合同一任务数据；未设置则自动生成会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 string | 否 | 随公共调用器透传对应请求头，未配置为空字符串。 |

检索脚本提供一层 24 小时本地缓存：目录为 `<cwd>/linkfox/.cache/linkfox-zhihuiya-patent-image-search/`，键为归一化后参数排序 JSON 的 SHA-256 前 16 位，文件名为 `linkfox-zhihuiya-patent-image-search-<key>.json`。同参数不同键序共用缓存；到期或损坏则视为未命中；缓存直接保存响应体，命中时添加 `_cache.hit=true` 标识。错误或空响应也会缓存，缓存命中不证明业务成功；缓存未记录 HTTP 状态，不能据此推断当时 HTTP 正常。需要重新请求时由用户决定并传 `--no-cache`。业务封装调用公共 `call_api.run` 时始终追加 `--no-cache`，不启用第二层缓存。

检索 CLI 将实时请求的实际 HTTP 状态（如 `HTTP 401`、`HTTP 402`）写入标准错误流，连接失败时说明未收到 HTTP 响应；响应体与落盘 JSON 保持原始内容。缓存命中时仅说明历史 HTTP 状态未知，内部状态返回 `None`，不补成 `200`，也不能将此 `None` 当作本次连接失败。HTTP 状态是脚本本地诊断信息，不是网关响应体字段。

完整响应始终以 UTF-8 写入当前工作目录会话数据，文件名前缀为 `linkfox-zhihuiya-patent-image-search-`；使用微秒时间戳避免同秒覆盖。请求前检查当前目录及目标文件可写，不回退家目录或临时目录，不使用 `ACPX_WORKSPACES` 重定向。小于等于 8000 字节全量打印，否则输出摘要及最大列表前 3 项；`--inline` 强制全量打印。缓存命中也会保存响应。错误、空结果均不自动重试或修改参数连续试探。

缓存中的 `_cache` 必须为对象；损坏的元数据与损坏 JSON 一样视为未命中。实时响应即使为非对象 JSON，或携带非对象 `_cache`，也按原始内容保存和输出；不因此改写响应、重试或推断业务成功。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态码，是否正常按公共规则判断。 |
| errmsg | string | 网关错误或提示信息，保留原始内容。 |
| errorCode | 未单独声明 | 错误响应中如出现此字段应原样保留，不代替公共规则中的 `errcode` 判断。 |
| error / details | string | 公共调用器在 HTTP 错误非 JSON 或连接失败时可能输出的错误和原始详情。 |
| total | integer | 本次返回的记录数 |
| allRecordsCount | integer | 数据库中匹配的总记录数 |
| data | array | 匹配的专利记录列表 |
| columns | array | 渲染的列定义 |
| type | string | 渲染的样式 |
| costToken | integer | 消耗token |

#### 专利记录字段（`data` 中的每条记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| patentId | string | 相似专利ID |
| patentPn | string | 相似专利号 |
| apno | string | 申请号 |
| title | string | 专利名称 |
| inventor | string | 发明人 |
| originalAssignee | string | 原始申请人 |
| currentAssignee | string | 当前申请人 |
| authority | string | 受理局（国家代码） |
| url | string | 相似的专利附图URL |
| score | number | 相似度分数（分数越高越相似；仅当 field 为 `SCORE` 时有效） |
| loc | array | LOC分类（洛迦诺分类号） |
| locMatch | integer | 是否命中高权重LOC：`1`（命中）、`0`（未命中）。仅当 model=1 且 field=SCORE 时有效 |
| apdt | integer | 申请日（时间戳） |
| pbdt | integer | 公开日（时间戳） |
| imgId | string | 专利附图img_id（仅当 `returnImgId` 为 true 时返回） |

上述表格列出明确的响应字段。图片列表、摘要、描述、`radarResult`、说明书的实际字段名、类型及嵌套结构未声明，不能自行补造；实际返回时完整保留并按展示规则呈现，未返回则说明缺失。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 相似度 `score` 仅在 `field=SCORE` 时有效；`locMatch` 仅在 `model=1` 且 `field=SCORE` 时有效，不满足条件时不能据这些字段评估匹配。
- `total` 是本次返回数，`allRecordsCount` 才是数据库匹配总数。分页使用 `offset` 和 `limit`，范围见参数表；不能只看 `total` 判断是否还有结果。
- `imgId` 仅在 `returnImgId=true` 时返回。未返回摘要、完整图片列表等扩展资料不能解释为这些资料不存在。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/patentImageSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
    "url": "https://example.com/product-image.jpg",
    "patentType": "D",
    "model": 1,
    "country": "CN,US",
    "limit": 20,
    "lang": "cn"
  }'
```

### 响应示例

```json
{
  "total": 20,
  "allRecordsCount": 1523,
  "data": [
    {
      "patentId": "abcdef123456",
      "patentPn": "CN305123456S",
      "apno": "CN202130123456.7",
      "title": "台灯",
      "inventor": "张三",
      "originalAssignee": "示例公司",
      "currentAssignee": "示例公司",
      "authority": "CN",
      "url": "http://images.zhihuiya.com/patent/12345.jpg",
      "score": 0.95,
      "loc": ["26-05"],
      "locMatch": 1,
      "apdt": 1640995200000,
      "pbdt": 1656633600000
    }
  ],
  "columns": [],
  "type": "patent_image",
  "costToken": 100
}
```

## 接口：获取图片上传预签名地址

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| contentType | string | 是 | 文件 MIME 类型，由扩展名映射，见下表；无默认值。 |
| fileExtension | string | 是 | 不含点的小写图片扩展名，脚本从本地路径提取；无默认值。 |

#### 图片格式映射

| fileExtension | contentType |
|------|------|
| jpg / jpeg | image/jpeg |
| png | image/png |
| gif | image/gif |
| webp | image/webp |
| heic | image/heic |

#### 脚本 CLI 与上传步骤

| 参数 / 选项 | 类型 | 必填 | 说明 |
|------|------|------|------|
| local_image_path | CLI string | 是 | `python scripts/upload_image.py '<本地图片路径>'`；必须是已有文件，支持上表格式，扩展名大小写归一化；路径含空格时加引号。 |
| --help / -h | CLI flag | 否 | 输出帮助，不发起请求。 |

1. 请求预签名地址。本操作不缓存响应，公共 `call_api.run` 始终传 `--no-cache`，不复用过期签名。
2. 读取本地文件二进制，向返回的完整签名 URL 执行 OSS `PUT`，超时 120 秒；请求头为对应 `Content-Type` 与 `x-oss-object-acl: public-read`，不携带 LinkFox API Key。该素材上传 HTTP 不属于 LinkFox 网关接口。
3. OSS 上传状态必须为 `200` 或 `201`。成功后移除签名 URL 的查询串，输出公开图片 URL；URL 有效期为 24 小时，后续检索使用该 URL。保留签名查询串直至 PUT 完成，不能提前剥离签名。

文件不存在或格式不支持时在请求前退出。文件大小限制未单独声明，不自行臆造。LinkFox 预签名请求使用公共认证与 150 秒超时，OSS PUT 处理 HTTPError / URLError；均不自动重试。当前工作目录不可写时，在申请预签名前报错。

### 响应结构

#### LinkFox 预签名响应

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关状态码；按公共规则判断，正常值不限于数值 200。 |
| errmsg | string | 网关提示或错误消息，异常时完整保留。 |
| url | string | 带签名查询串的 PUT 地址；用于 OSS 上传，正常响应也必须检查该字段非空。 |
| error / details | string | 公共调用器在连接或 HTTP 错误时可能返回的错误及原始详情。 |

#### CLI 最终输出

| 字段 | 类型 | 说明 |
|------|------|------|
| url | string | OSS 上传完成后去掉查询串的公开图片 URL；标准输出仅为此 JSON 对象。 |

完整 LinkFox 预签名响应保存在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-zhihuiya-patent-image-search-upload-<timestamp>.json`；上传封装捕获公共调用器的打印，CLI 输出单一 JSON 对象，错误写入标准错误流并非零退出。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关响应正常但缺少非空 `url` 时不能继续上传；给出缺失字段原因。
- OSS PUT 的 `200` / `201` 表示文件上传完成；取得签名地址本身不表示已完成上传。素材上传错误须保留其状态及原始原因，不输出成功 URL。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/file/presignedPut" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"contentType":"image/png","fileExtension":"png"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-patent-image-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
