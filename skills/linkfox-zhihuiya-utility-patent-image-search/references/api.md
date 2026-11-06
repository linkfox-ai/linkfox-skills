# 智慧芽实用新型专利图片搜索 接口说明

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

## 接口：实用新型专利图片检索

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/zhihuiya/patentImageSearch`

### 请求参数

POST Body（JSON）：

#### 必填参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 是 | 图像的URL（最大1000字符） |
| patentType | string | 是 | 专利类型：`D`（外观专利）或 `U`（实用新型专利）。底层接口默认：`D`；本技能必须使用 `U`，脚本会强制设为 `U` |
| model | integer | 是 | 图像检索模型。外观专利：`1`（智能联想，推荐）、`2`（搜索此图）；实用新型专利：`3`（匹配形状）、`4`（匹配形状/图案/色彩，推荐）。本技能仅允许 3/4，脚本省略 model 时补为 4 |

#### 可选参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| country | string | 否 | 专利受理局（国家/组织/地区代码），多个用英文逗号隔开。例如：`CN,US,JP`。不传时代表查询全部专利受理局的数据 |
| loc | string | 否 | LOC分类（洛迦诺分类号），多个分类号可以用逻辑符 AND/OR/NOT 连接；仅适用于外观设计，本技能的实用新型检索不使用此条件 |
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

#### 常用国家代码

| 代码 | 国家或组织 |
|------|------------|
| CN | 中国 |
| US | 美国 |
| JP | 日本 |
| KR | 韩国 |
| EP | 欧洲专利局 |
| WO | 世界知识产权组织 |
| DE | 德国 |
| GB | 英国 |
| FR | 法国 |
| AU | 澳大利亚 |

#### 脚本选项与运行约定

| 参数或选项 | 类型 | 必填 | 说明 |
|------------|------|------|------|
| JSON 参数 | object | 是 | 首个位置参数，使用上方字段；强制 patentType=U，未传 model 时补 4，拒绝 3/4 之外的模型。 |
| --inline | CLI flag | 否 | 保存后完整打印响应。 |
| --no-cache | CLI flag | 否 | 跳过业务层缓存的读取和写入。 |

运行 `python scripts/zhihuiya_patent_image_search.py '<JSON 参数>' [--inline] [--no-cache]`。
业务层将标准化参数按键排序后序列化为 JSON，计算 SHA-256 并取前 16 位作为缓存键，缓存位于 `<cwd>/linkfox/.cache/linkfox-zhihuiya-utility-patent-image-search/`，有效期 24 小时；命中时添加 `_cache.hit=true`，CLI 显示实际命中的业务缓存文件路径。缓存内容为带本地 `_http_status` 的响应 JSON，可直接读取；命中时该值表示缓存生成时的 HTTP 状态，不表示本次发生网络请求。历史缓存未记录状态时仍复用，输出 `_http_status=null`，不得假定 HTTP 200 或为补齐状态重新请求。业务层负责缓存读写，公共调用器始终使用 `--no-cache`，不增加第二层响应缓存或为检索另建缓存目录。缓存可包含错误或空结果；有效缓存存在时直接复用，缓存不存在、过期或损坏时才重新请求；不得为失败自动再次请求。
完整检索响应以 `linkfox-zhihuiya-utility-patent-image-search-patent-image-search-<timestamp>.json` 保存。输出根目录限定为当前目录的 `linkfox/`，在请求前验证可写，不回退到家目录或临时目录，也不采用外部工作区重定向；使用 UTF-8。业务封装在调用器结束后核对完整文件内容，保存失败则报错退出，不自动重发请求。8 KB 以 8000 字节计算，超出时展示摘要和最大列表的前三条样本。
两个业务脚本均支持 `LINKFOX_TOOL_GATEWAY`，并兼容 `LINKFOX_AGENT_API_KEY` 和 `LINKFOXAGENT_API_KEY` 环境变量；会话请求头由公共调用器传递。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
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

#### 状态与兼容字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码，按公共规则判断。 |
| errmsg | string | 网关消息或错误原因。 |
| errorCode | integer / string | 业务状态字段；如实际返回，应结合业务错误说明判断，200 表示成功。 |
| _cache.hit | boolean | 仅本地缓存命中时添加的标记，不是服务端字段。 |
| _http_status | integer / null | 业务封装添加的本地 HTTP 状态；连接失败或历史缓存未记录时为 null。缓存命中时为历史状态，不能作为本次请求的成功依据。CLI 也显示该状态。 |
| error | string | 仅调用器诊断输出：连接失败、非 JSON HTTP 错误或接口未返回对象时的说明。 |
| details | string | 仅 HTTP 错误体无法解析为 JSON 时保留的原始响应文本。 |
| response | any | 仅接口返回非对象 JSON 时保留的原始结果；与 error 一起落盘，避免丢失返回内容。 |

`columns` 元素及图片列表、摘要、说明书、IPC/UPC、`radarResult`、规格资料以实际返回的字段和结构为准；展示时依据真实响应，缺失则标明，不编造字段或内容。

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 实际返回 `errorCode` 且其非空值不是 200 时，保留错误信息并根据消息解释，不能因缺少 `errcode` 就忽略已返回的业务错误。
- 有效模型必须对应专利类型；底层接口的模型 1/2 对应 D，3/4 对应 U。本技能只使用 U 和 3/4。
- `total` 表示本次返回数量，`allRecordsCount` 表示匹配总量；成功返回空列表时说明本次条件下未找到候选，不解释为“没有侵权风险”。
- 图片必须可公开访问，不能把本地路径直接传给检索接口；上传链接有效期为 24 小时，失效后需重新上传。
- `score` 仅在 field=SCORE 时有效；日期排序不能假定响应有可用相似度。`locMatch` 的 model=1 条件不在本技能使用范围内，保留其字段定义供识别响应。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/zhihuiya/patentImageSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"url":"https://example.com/product-image.jpg","patentType":"U","model":4,"country":"CN,US","limit":20,"lang":"cn"}'
```

## 接口：申请图片上传预签名

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| contentType | string | 是 | 图片 MIME 类型；由脚本根据扩展名确定，映射见下表。 |
| fileExtension | string | 是 | 小写文件扩展名，不含点；来自本地文件名。 |

#### 图片格式映射

| 扩展名 | contentType |
|--------|-------------|
| jpg / jpeg | image/jpeg |
| png | image/png |
| gif | image/gif |
| webp | image/webp |
| heic | image/heic |

#### 脚本 CLI 与上传约定

| 参数或选项 | 类型 | 必填 | 说明 |
|------------|------|------|------|
| local_image_path | string | 是 | `python scripts/upload_image.py <local_image_path>` 的位置参数；必须是存在的本地文件，扩展名不区分大小写，格式不支持时在请求前报错。 |

预签名不缓存：业务封装调用 `call_api.run` 时固定加 `--no-cache`。完整预签名响应保存为 `linkfox-zhihuiya-utility-patent-image-search-upload-presign-<timestamp>.json`，并在当前目录不可写时于请求前报错；调用结束后核对完整文件内容，保存失败则停止，不继续上传。不在 stdout 展示带签名的上传地址，stdout 仅输出含公开链接的 JSON。
取得预签名地址后，通过该地址直接 HTTP PUT 上传原始文件字节（不再请求 LinkFox 业务接口），超时 120 秒，请求头包含 `Content-Type: <contentType>` 与 `x-oss-object-acl: public-read`。仅接受上传状态 200/201；异常或其他状态报错退出，不重试。去掉签名地址问号及其后的查询串，获得公开图片 URL，有效期 24 小时。
公共调用器仅负责 LinkFox 预签名 POST，OSS 文件 PUT 使用独立 HTTP 实现。上传前不向 OSS 发送 API Key 或会话请求头。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态码；200 表示成功，正常响应按公共规则判断。 |
| errmsg | string | 网关消息或错误原因。 |
| url | string | 预签名 PUT 地址，包含上传授权查询串；必须非空才继续上传。 |
| _http_status | integer / null | 仅业务封装保存文件中的本地 HTTP 状态，连接失败时为 null；不属于网关响应字段。 |

#### 上传脚本标准输出

| 字段 | 类型 | 说明 |
|------|------|------|
| url | string | 上传完成后的公开图片 URL，已去掉签名查询串，可用作专利图片检索的 url。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 预签名失败、未返回可用 url 或文件上传失败时停止，不用不完整链接发起检索。
- OSS 文件 PUT 不适用 LinkFox 业务响应判断，仅以上传 HTTP 200/201 表示完成；其他状态与连接错误均保留原因并退出。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/file/presignedPut" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"contentType":"image/png","fileExtension":"png"}'
```

---

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-zhihuiya-utility-patent-image-search",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
