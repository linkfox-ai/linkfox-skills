# 1688 以图搜图 接口说明

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

## 接口：以图搜图

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/alibaba1688/imageSearch`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| imageUrl | string | 条件必填 | - | 直接 API 要求 URL 实际返回 JPEG/PNG；最大长度 1000。Skill 脚本保持 JPEG/PNG 不变，并自动转换 WebP。imageUrl/imageBase64/imageId 三选一必填 |
| imageBase64 | string | 条件必填 | - | 纯 Base64，不含 data URL 前缀。Skill 脚本保持 JPEG/PNG 不变，并自动将 WebP Base64 转成 JPEG Base64 |
| imageId | string | 条件必填 | - | 图片ID（1688图片ID），以图搜图查询结果中也会返回，建议当分页 page>1 查询时带 imageId，加快响应速度 |
| page | int | 否 | 1 | 页码，从1开始 |
| pageSize | int | 否 | 20 | 每页返回的商品数量，范围 1–50，最大不超过50 |
| priceStart | string | 否 | - | 价格筛选起始值（人民币），如 10 |
| priceEnd | string | 否 | - | 价格筛选结束值（人民币），如 100 |
| filter | string | 否 | - | 过滤条件，多个条件用逗号分隔。有效值见下方「支持的过滤条件」 |
| sort | string | 否 | {"monthSold":"desc"} | 排序条件，JSON格式 {排序字段: 排序方式}。有效字段：price、rePurchaseRate、monthSold；方式：asc/desc |
| keyword | string | 否 | - | 关键词，在结果中搜索 |
| productCollectionId | string | 否 | - | 货盘ID，单选。有效值见下方「支持的货盘ID」 |

#### 支持的过滤条件

多个条件用逗号分隔，如 `1688Selection,totalEpScoreLv1,qrr0`。

| 值 | 说明 |
|----|------|
| 1688Selection | 1688严选 |
| certifiedFactory | 认证工厂 |
| totalEpScoreLv1 | 综合体验分5星 |
| totalEpScoreLv2 | 综合体验分4星 |
| totalEpScoreLv3 | 综合体验分3星 |
| totalEpScoreLv4 | 综合体验分2星 |
| qrr0 | 无品质退款 |
| qrr1 | 品质退款率<1% |
| qrr5 | 品质退款率<5% |
| qrr10 | 品质退款率<10% |
| shipInToday | 当日发货 |
| shipIn24Hours | 24小时发货 |
| shipIn48Hours | 48小时发货 |
| noReason7DReturn | 7天无理由退货 |
| isOnePsale | 一件代发 |
| isOnePsaleFreePost | 一件代发包邮 |
| new7 | 7天内新品 |
| new30 | 30天内新品 |
| isQqyx | 全球严选 |
| JPFL | 日本专线 |
| USFL | 美国专线 |
| KRFL | 韩国专线 |
| VNFL | 越南专线 |
| SAFL | 沙特专线 |
| RUFL | 俄罗斯专线 |
| KZFL | 哈萨克斯坦专线 |
| HKFL | 香港专线 |
| MOFL | 澳门专线 |
| TWFL | 台湾专线 |

#### 支持的排序字段

| 字段 | 说明 |
|------|------|
| price | 价格 |
| monthSold | 月销量 |
| rePurchaseRate | 复购率 |

排序方式：`asc`（升序）、`desc`（降序）。格式示例：`{"price":"asc"}`

#### 支持的货盘ID

| ID | 说明 |
|----|------|
| 262105288 | 跨境货盘 |
| 262105286 | 跨境货盘 |
| 262105253 | 跨境货盘 |
| 262105281 | 跨境货盘 |
| 262105280 | 跨境货盘 |
| 262105277 | 跨境货盘 |
| 262105276 | 跨境货盘 |
| 262105274 | 跨境货盘 |
| 262105269 | 跨境货盘 |
| 262185282 | 跨境货盘 |

#### 图片与接口使用限制

- `imageUrl`、`imageBase64`、`imageId` 至少提供一个；`page>1` 时优先使用首轮返回的 `imageId` 加快查询。
- Base64 必须是纯编码内容，不含 `data:image/jpeg;base64,` 等前缀。
- JPEG/PNG 原样传递。1688 上传链路不接受 WebP；业务脚本依据实际文件字节识别并自动转 JPEG。GIF 和其他未识别为 WebP 的格式原样传递，不承诺图搜支持；无法解码的 Base64 也原样传递，由接口判断有效性。
- 图片 URL 先以 Range 读取前 64 字节，失败后仅回退一次普通读取；链接读取、WebP 下载或转换失败时停止，不进入收费图搜。
- WebP URL 转换后重新上传；WebP Base64 直接转换为 JPEG Base64；已有非空 `imageId` 时跳过预处理。
- 同时提供多个图片来源时预处理优先级为：`imageId` → 非空 `imageBase64` → `imageUrl`，不擅自删除其他输入字段。
- 支持的过滤、排序和货盘枚举仅以上表为准；不支持的条件不得通过其他工具或逻辑变通，应向用户说明可用选项。
- 结果来自实时检索，不存储在可查询的数据库，不支持二次 SQL 或 `_dataQuery_executeDynamicQuery` 加工。保存 JSON 供查看字段，不扩大接口筛选能力。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| JSON 参数 | object | 是 | - | 第一个位置参数，字段见上述请求表。 |
| --inline | CLI flag | 否 | 关闭 | 强制完整打印，仍保存完整响应。 |
| --no-cache | CLI flag | 否 | 关闭 | 跳过图搜缓存的读取和写入。 |

图搜缓存位于 `<cwd>/linkfox/.cache/linkfox-1688-search-by-image/`，按原始 JSON 参数排序后取 SHA-256 前 16 位作为键，TTL 为 24 小时；缓存文件直接保存响应体，命中时添加 `_cache.hit` 标记。缓存命中时跳过认证检查、图片读取、转换和上传凭证请求；缓存也可能包含失败响应，且不保存 HTTP 状态，须结合响应体中的 `errcode`、`errorCode` 及错误信息判断，不能仅凭命中推断业务成功。没有可用缓存（缺失、过期或损坏）时才重新调用。业务封装调用公共 `call_api.run` 时始终加 `--no-cache`，避免第二层响应缓存。

响应保存到当前工作目录的会话数据目录，禁止回退到 `/tmp` 或家目录；在图片预处理和接口请求前预留完整输出文件，会话数据目录不可写时立即报错；请求后完整响应保存失败也报错。使用 `SESSION_ID` 聚合及 `MESSAGE_ID`、`MODE_ID`、`APP_NAME` 请求头。上传凭证的独立输出规则见下方接口。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 网关业务状态；按公共规则判断。认证错误示例为 401。 |
| errmsg | string | 业务错误原因，如 authorized error。 |
| errorCode | integer | 兼容业务码；存在时 200 表示业务成功，其他值表示业务错误。 |
| imageId | string | 上传后的图片ID（分页查询时回传可加速） |
| total | integer | 本页商品数量 |
| totalPage | integer | 总页数 |
| sourceType | string | 来源类型（固定值 "1688"） |
| type | string | 渲染样式（固定值 "productWorkbenches"） |
| columns | array | 渲染列定义 |
| costToken | integer | 消耗 token |
| products | array | 商品列表（详见下方商品字段） |

#### 商品字段

| 字段 | 类型 | 说明 |
|------|------|------|
| offerId | string | 商品ID |
| asin | string | 商品编号（同 offerId） |
| imageUrl | string | 商品图片 |
| title | string | 商品标题 |
| price | number | 批发价（元） |
| consignPrice | number | 一件代发价（元） |
| salesQuantity | integer | 月销售件数 |
| estimatedSalesAmount | number | 预估月销售额 |
| asinUrl | string | 商品链接 |
| isOnePsale | string | 是否一件代发（是/否） |
| isJxhy | string | 是否精选货源（是/否） |
| sellerIdentities | string | 商家身份（超级工厂/实力商家/诚信通会员） |
| offerIdentities | string | 商品标（严选） |
| repurchaseRate | string | 复购率 |
| tradeScore | string | 商品交易评分 |
| compositeServiceScore | string | 综合服务体验分 |
| sendGoodsAddressText | string | 发货地 |
| deliveryTime | string | 发货时间（24/48小时） |
| quantityBegin | integer | 起批量 |
| hasPromotion | string | 是否有营销活动（是/否） |
| promotionType | string | 营销类型 |
| isPatentProduct | string | 是否专利商品（是/否） |
| isSelect | string | 跨境select货盘标识 |
| currency | string | 币种（固定值 "¥"） |
| sourceType | string | 来源类型（固定值 "1688"） |
| sourceTool | string | 来源工具（固定值 "1688以图搜图"） |
| dataType | string | 数据类型（固定值 "monthlyData"） |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- `errorCode` 存在时，`200` 表示业务成功，其他值为业务错误；这是额外业务判断，不替代公共规则对 HTTP 与 `errcode` 的判断。
- `total` 是本页商品数量，`totalPage` 才是总页数。空列表不触发自动翻页或更换参数重试。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/alibaba1688/imageSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"imageUrl":"https://example.com/product.jpg","page":1,"pageSize":20,"filter":"1688Selection,totalEpScoreLv1,qrr0","sort":"{\"price\":\"desc\"}"}'
```

## 接口：获取图片上传凭证

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| contentType | string | 是 | - | 文件 MIME 类型，由本地文件扩展名映射，见下表。 |
| fileExtension | string | 是 | - | 不带点的小写扩展名；脚本支持 jpg、jpeg、png、gif、webp、heic。 |

#### 文件类型映射

| fileExtension | contentType |
|---|---|
| jpg / jpeg | image/jpeg |
| png | image/png |
| gif | image/gif |
| webp | image/webp |
| heic | image/heic |

#### 脚本选项与上传约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|---|---|---|---|
| local_image_path | CLI 路径 | 是 | `upload_image.py` 第一个位置参数；必须是存在的本地文件，含空格时引用整个路径。 |

- 本接口脚本不启用缓存，公共执行器始终使用 `--no-cache`，不得复用预签名 URL。
- 凭证响应完整保存到 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-1688-search-by-image-upload-<timestamp>.json`；脚本标准输出仍只返回最终公开链接 JSON，不夹杂凭证摘要。
- 获取凭证后对返回的签名 URL 发起 OSS `PUT`，发送原始文件字节，`Content-Type` 与申请凭证时一致，并设置 `x-oss-object-acl: public-read`；超时 120s，仅 HTTP 200/201 视为上传完成。此 PUT 用于素材上传。
- 上传 HTTP 失败或连接失败时停止并报告；不自动重试。通过去掉签名 URL 的查询参数得到公开 URL，公开链接有效期 24 小时。
- 上传支持的文件扩展名不代表图搜均支持；WebP 图搜转换规则见上方接口。

### 响应结构

上传脚本读取以下响应字段。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer / string / null | 网关业务状态，按公共规则判断；成功值示例为 200。 |
| errmsg | string | 网关错误说明。 |
| url | string | 可用于 OSS PUT 的预签名 URL；正常响应仍须存在非空 URL 才能上传。 |

#### 脚本最终输出

| 字段 | 类型 | 说明 |
|---|---|---|
| url | string | 上传完成后的公开图片链接，移除预签名 URL 的查询参数。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 返回正常响应但缺少非空 `url` 时停止，不进入 OSS 上传或后续图搜。
- 取得凭证仅表示可以开始上传，须 OSS PUT 完成后才返回公开链接。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/file/presignedPut" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"contentType":"image/jpeg","fileExtension":"jpg"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-1688-search-by-image",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```

