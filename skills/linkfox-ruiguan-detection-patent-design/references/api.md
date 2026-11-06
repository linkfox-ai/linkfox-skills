# 睿观外观专利检测 接口说明

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

## 接口：外观专利检测

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/ruiguan/detectionPatentDesign`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| imageUrl | string | 是 | - | 产品图片文件URL，用于与专利数据库进行比对（最大1000字符） |
| queryMode | string | 是 | hybrid | 检索模式：`physical`（实物图检索）、`line`（线条图检索）、`hybrid`（混合检索）。最大1000字符 |
| topNumber | integer | 是 | 100 | 召回专利数量（最大100） |
| regions | string | 否 | US | 商品所售卖国家/地区代码，多选时用逗号隔开（如 `US,EU,CN`）。支持：US、EU、CN、JP、KR、DE、GB、FR、IT、AU、CA、BR、MX、IN、TH、SE、CH、IE、IL、DK、NZ、AT、BX、FI、WO。最大1000字符 |
| productTitle | string | 否 | - | 产品标题，用于补充检索上下文（最大1000字符） |
| productDescription | string | 否 | - | 产品描述，用于补充检索上下文（最大1000字符） |
| patentStatus | string | 否 | 1 | 专利有效性筛选：`1`（有效专利）、`0`（失效专利）、`1,0`（全部）。最大1000字符 |
| enableRadar | boolean | 否 | true | 是否启用雷达图（AI侵权判定分析） |
| topLoc | string | 否 | - | 指定检索的一级LOC范围（如 `06,07`）。格式：`^(0[1-9]\|1[0-9]\|2[0-9]\|3[0-2]\|ALL)(,(0[1-9]\|1[0-9]\|2[0-9]\|3[0-2]\|ALL))*$`。不指定时使用模型LOC预测服务的结果 |
| sourceLanguage | string | 否 | - | 原语言代码，需要标记以便统一翻译成英文（如 `zh-CN`）。文本为英语时传空即可。最大1000字符 |


#### 支持的国家和地区

| 代码 | 国家或地区 |
|------|------|
| US | 美国 |
| EU | 欧盟 |
| CN | 中国 |
| JP | 日本 |
| KR | 韩国 |
| DE | 德国 |
| GB | 英国 |
| FR | 法国 |
| IT | 意大利 |
| AU | 澳大利亚 |
| CA | 加拿大 |
| BR | 巴西 |
| MX | 墨西哥 |
| IN | 印度 |
| TH | 泰国 |
| SE | 瑞典 |
| CH | 瑞士 |
| IE | 爱尔兰 |
| IL | 以色列 |
| DK | 丹麦 |
| NZ | 新西兰 |
| AT | 奥地利 |
| BX | 玻利维亚（Bolivia）；代码 BX 的实际地区含义以服务返回为准 |
| FI | 芬兰 |
| WO | 世界知识产权组织（WIPO） |

用户未指定市场时使用 US。

#### LOC 一级分类

| 代码 | 类别 |
|------|------|
| 01 | 食品 |
| 02 | 服装、服饰用品和缝纫用品 |
| 03 | 旅行用品、箱包、阳伞和其他个人用品 |
| 04 | 刷具 |
| 05 | 纺织品、人造和天然片状材料 |
| 06 | 家具和家居用品 |
| 07 | 其他家用物品 |
| 08 | 工具和五金 |
| 09 | 运输或搬运货物用包装和容器 |
| 10 | 钟表、测量、检查和信号仪器 |
| 11 | 装饰品 |
| 12 | 运输或起重工具 |
| 13 | 发电、配电或变电设备 |
| 14 | 录制、通信或数据处理设备 |
| 15 | 其他机械 |
| 16 | 摄影、电影和光学设备 |
| 17 | 乐器 |
| 18 | 印刷和办公机械 |
| 19 | 文具、办公设备、美术和教学用品 |
| 20 | 销售和广告设备、标牌 |
| 21 | 游戏、玩具、帐篷和体育用品 |
| 22 | 武器、烟火、狩猎、捕鱼及灭虫用品 |
| 23 | 流体分配、卫生、供暖、通风、空调设备及固体燃料 |
| 24 | 医疗和实验室设备 |
| 25 | 建筑单元和建筑构件 |
| 26 | 照明设备 |
| 27 | 烟草和吸烟用品 |
| 28 | 医药、化妆品、盥洗用品及器具 |
| 29 | 防火、事故预防和救援设备 |
| 30 | 动物护理和管理用品 |
| 31 | 其他食品或饮料制备机械和设备 |
| 32 | 图形符号、标志、表面图案、装饰及室内外布局 |
| ALL | 全部类别 |

#### 脚本选项与使用限制

| 参数 / 约定 | 类型 | 说明 |
|------|------|------|
| JSON 参数 | object | CLI 的第一个位置参数；字段按上表准备，脚本不自动补造业务参数。 |
| --inline | CLI flag | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 不读取或更新检测响应缓存；默认使用 24 小时缓存。 |
| 缓存键与路径 | 本地约定 | 参数以 ensure_ascii=False、sort_keys=True 序列化，取 SHA-256 前 16 位；缓存路径为 `<cwd>/linkfox/.cache/linkfox-ruiguan-detection-patent-design/linkfox-ruiguan-detection-patent-design-<hash>.json`。缓存包装保存 `_ruiguan_cache_version=1`、`http_status` 和完整响应 `body`；对象响应命中时标记 `_cache.hit=true`。缓存时效依据文件 mtime。 |
| 缓存行为 | 本地约定 | 按参数保存响应，包括错误或空响应；命中不再次请求。确认需要重新调用时可使用 --no-cache。公共调用器始终收到 --no-cache，不另建第二份响应缓存。 |
| HTTP 状态诊断 | stderr | 新请求输出 `HTTP status`；缓存命中输出 `Cached HTTP status`，表示历史状态而非新请求。未记录状态的兼容缓存或连接失败显示 `unknown`，不能据此认定 HTTP 成功，也不自动重新请求。响应数据文件仍保存响应体，HTTP 状态不伪装成服务端业务字段。 |
| 输出目录 | 本地约定 | 完整响应保存到当前工作目录下的 linkfox 会话目录，SESSION_ID 优先；禁止回退到家目录或 /tmp，当前目录不可写时在请求前报错。 |
| 超过 5 次调用 | 费用限制 | 即将进行第 6 次及后续检测调用前，必须二次确认：明确告知用户已消耗算力及继续调用预计消耗，让用户决定是否继续。有 AskUserQuestion 时使用它，否则用当前环境可用的提问方式等待确认。按实际消耗核算，缓存命中不重复计入付费检测。 |

雷达开启每次 106 算力，关闭每次 71 算力，实际扣费为准。失败或空结果不得自动换参数连续试探。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| total | integer | 返回的专利记录总数 |
| data | array | 专利列表（详见下方专利对象） |
| columns | array | 渲染的列定义 |
| costToken | integer | 消耗token |
| type | string | 渲染的样式 |

#### 专利对象（`data` 数组中的每个元素）

| 字段 | 类型 | 说明 |
|------|------|------|
| applicationNumber | string | 专利申请号 |
| publicationNumber | string | 专利公开号 |
| patentProd | string | 专利标题（英文） |
| patentProdCn | string | 专利标题（中文） |
| similarity | string | 专利与产品图片的相似度（0-1） |
| patentImageUrl | string | 与产品图片相似度最高的专利附图URL |
| images | array | 专利图片列表 |
| abstracts | string | 专利摘要 |
| specification | string | 专利说明书 |
| inventors | array | 发明人列表 |
| applicants | array | 申请人列表 |
| applicantAddresses | array | 申请人地址 |
| troCase | boolean | 是否有TRO维权史 |
| troHolder | boolean | 是否是TRO权利人的专利 |
| radarResult | object | 启用雷达（enableRadar=true）时，各专利结果的 AI 雷达分析；未启用时不要求返回此字段。 |
| radarResult.same | boolean | 是否疑似侵权 |
| radarResult.exp | string | 预期描述（雷达判定说明） |
| patentLoc | string | 该专利的LOC分类（多个用逗号隔开） |
| locOneInfo | string | LOC一级详情 |
| locTwoInfo | string | LOC二级详情 |
| patentValidity | string | 专利有效性 |
| applicationDate | string | 专利申请日 |
| publicationDate | string | 专利公开日 |
| grantDate | string | 专利授权日 |
| estimatedDueDate | string | 预估到期日 |
| registrationOfficeCode | string | 专利注册受理局 |
| patentFamily | array | 同族专利列表 |
| globalPatentId | string | 全球专利ID |
| globalImageId | string | 专利图片的ID |
| isSketchText | string | 是否线稿图 |

#### 状态与本地兼容字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 按公共响应码基本规则判断；401 表示认证失败。 |
| errmsg | string | 接口消息，如 authorized error；用于解释异常原因。 |
| errorCode | integer | 状态字段，实际出现时原样保留，不替代公共规则中的 errcode 判断。 |
| error | string | 公共调用器生成的 HTTP 或连接错误说明，实际出现时保留。 |
| details | string | 无法解析为 JSON 的 HTTP 错误原文，实际出现时保留。 |
| _cache.hit | boolean | 本地缓存命中标记，不是服务端字段。 |

`columns`、`images`、`inventors`、`applicants`、`applicantAddresses`、`patentFamily` 数组的元素按实际响应展示；不预设或虚构嵌套结构。

若实际响应为数组、null 或其他非对象 JSON，业务封装仍原样保存并按输出策略展示，不补造专利字段，也不据此认定检测成功。

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 空列表仅表示本次检索未返回专利，不能据此断言产品无侵权风险。后续调用仍遵守使用限制。
- 失败时结合接口消息核查图片链接可访问性和国家或地区代码，保留接口返回的错误信息。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/ruiguan/detectionPatentDesign \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"imageUrl":"https://example.com/product.jpg","queryMode":"physical","topNumber":100,"regions":"US,EU,CN","productTitle":"便携式无线充电支架","productDescription":"一款可折叠的智能手机无线充电支架","patentStatus":"1","enableRadar":true}'
```

## 接口：图片上传预签名

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

POST Body（JSON）；上传脚本显式传入下列字段，不依赖服务端默认值；服务端长度限制以实际响应为准。

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|------|
| contentType | string | 是（脚本始终传入） | 无 | 本地图片 MIME 类型；映射见下表。 |
| fileExtension | string | 是（脚本始终传入） | 无 | 不带点的小写扩展名，由本地文件名提取。 |

#### 本地上传 CLI 与格式

| 参数 / 格式 | 类型 | 说明 |
|------|------|------|
| local_image_path | CLI 位置参数 | `python scripts/upload_image.py <本地图片路径>`；必须是存在的文件，路径含空格时加引号。 |
| jpg / jpeg | MIME | image/jpeg |
| png | MIME | image/png |
| gif | MIME | image/gif |
| webp | MIME | image/webp |
| heic | MIME | image/heic |
| 缓存 | 本地约定 | 不缓存预签名响应；每次预签名均以 --no-cache 调用公共调用器，不复用签名。 |
| 输出目录 | 本地约定 | 预签名完整响应先保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-ruiguan-detection-patent-design-upload-<timestamp>.json`；禁止回退到家目录或 /tmp，当前目录不可写时在请求前报错。stdout 最终仍仅输出公开链接 JSON。 |

#### OSS 文件 PUT（后续存储操作，不是额外的 LinkFox 业务接口）

| 项目 | 类型 | 说明 |
|------|------|------|
| 请求地址 | string | 原样使用预签名响应的 url，保留查询串中的签名和 URL 编码，不自行重建。 |
| 请求方法 | string | PUT，超时 120 秒。 |
| 请求体 | bytes | 本地文件的原始二进制内容。 |
| Content-Type | header | 与预签名时的 contentType 一致。 |
| x-oss-object-acl | header | 固定 public-read。 |
| Authorization | header | OSS PUT 不附带 LinkFox API key。 |
| 成功状态 | integer | 接受 200 或 201；其他状态及连接错误均停止，不继续检测。 |
| 公开图片链接 | string | 上传成功后去掉签名地址的查询串；公开链接有效 24 小时，需在有效期内用于检测。 |

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 按公共响应码基本规则判断；成功响应示例值为 200。 |
| errmsg | string | 接口消息，用于解释失败原因。 |
| url | string | 预签名 PUT 地址，原样用于上传，缺失或为空时停止。 |

非对象 JSON 响应仍原样保存，上传脚本报告预签名失败并停止，不执行 OSS PUT。

#### 脚本最终输出

| 字段 | 类型 | 说明 |
|------|------|------|
| url | string | OSS 上传成功后的公开图片链接，不含签名查询串。CLI 以 JSON 输出。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关未正常响应、响应缺少有效 url、本地文件不存在或格式不支持时，不执行 OSS PUT。
- OSS PUT 的结果独立核验，按上方存储操作规则处理；失败时不返回看似成功的公开链接。

### curl 示例

```bash
curl -X POST https://tool-gateway.linkfox.com/oss/file/presignedPut \
  -H "Authorization: $LINKFOXAGENT_API_KEY" \
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
  "skillName": "linkfox-ruiguan-detection-patent-design",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
