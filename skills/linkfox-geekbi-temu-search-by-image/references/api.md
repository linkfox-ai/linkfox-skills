# Temu 以图搜同款 接口说明

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

## 接口：获取图片上传预签名

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/oss/file/presignedPut`

### 请求参数

| 参数 | 类型 | 必填 | 默认值 / 约束 / 说明 |
|---|---|---|---|
| contentType | string | 是 | 图片 MIME 类型：`image/jpeg`、`image/png`、`image/gif`、`image/webp`、`image/bmp`；须与后续 OSS PUT 的 Content-Type 和实际图片字节一致。 |
| fileExtension | string | 是 | 不带点的扩展名；脚本支持 `jpg`、`jpeg`、`png`、`gif`、`webp`、`bmp`，从文件名提取并转小写。 |

本地文件须存在且非空，不超过 10,000,000 字节（10 MB）；按实际字节检测 JPEG、PNG、GIF、WebP 或 BMP，扩展名必须与格式匹配。外部 URL 须先下载到本地。脚本仅使用 Python 标准库。

#### 脚本 CLI 与上传约定

| 输入 / 配置 | 类型 | 必填 | 说明 |
|---|---|---|---|
| 本地图片路径 | CLI positional | 是 | `python scripts/upload_image.py <本地图片路径>`；仅接受一个位置参数。 |
| LINKFOX_AGENT_API_KEY | environment | 二选一 | 优先密钥。 |
| LINKFOXAGENT_API_KEY | environment | 二选一 | 兼容密钥，优先密钥为空时使用。 |
| LINKFOX_TOOL_GATEWAY | environment | 否 | 网关基础地址；默认见公共规则，去掉末尾斜杠。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | environment | 否 | 随预签名请求透传；未设置为空串，SESSION_ID 去除首尾空白。 |

预签名接口不扣算力 （限时）。上传脚本不缓存；业务封装始终以 `--no-cache` 调用公共 run，不读取或保存预签名响应缓存，不落盘或打印带签名的原始响应。

### 响应结构

#### 网关响应

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 成功值示例为 200；状态判断按下方基础规则。 |
| errmsg | string | 网关消息或失败原因。 |
| url | string | 预签名 HTTPS PUT URL，包含私密签名查询参数；不得在日志、反馈或面向用户的输出中泄露。 |

#### OSS PUT 与脚本输出

脚本将本地字节 PUT 到返回的 HTTPS 地址，使用相同 `Content-Type` 和 `x-oss-object-acl: public-read`，超时 120s；HTTP 200 或 201 视为上传完成。此步骤是 OSS 素材上传，不是额外的 LinkFox 工具接口。上传失败不自动重试；输出错误，不返回成功地址。

成功后去除预签名 URL 的查询参数和片段，仅输出以下 JSON。脚本错误输出 `error`，扩展名不支持时另有 `supported`；失败退出码 1。

| 字段 | 类型 | 说明 |
|---|---|---|
| url | string | 已去掉查询参数和片段的公开 OSS 图片地址。 |
| contentType | string | 与文件字节和上传一致的 MIME 类型。 |
| path | string | 公开 URL 的路径，去掉开头 `/`，保持 URL 编码。 |
| name | string | 本地文件名。 |
| size | integer | 文件字节数。 |
| ext | string | 小写文件扩展名，不含点。 |
| error | string | 仅失败：文件、格式、预签名或上传错误；不泄露签名查询参数和密钥。 |
| supported | string | 仅不支持的扩展名错误：逗号分隔的支持扩展名。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 基础正常响应仍须含有效 HTTPS `url`，否则报错，不开始上传。
- HTTP 403 为无权限，不按充值处理；错误消息不包含 API Key 或预签名查询参数。
- 预签名地址只供一次上传使用；搜索复用公开地址与 MIME 类型，不反复上传。

### curl 示例

```bash
curl --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/oss/file/presignedPut" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"contentType":"image/jpeg","fileExtension":"jpg"}'
```

## 接口：Temu 图搜同款

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/geekbi/temu/goodsImageSearch`

### 请求参数

POST Body 为 JSON 对象，只包含以下已验证字段：

| 参数 | 类型 | 必填 | 约束 | 说明 |
|---|---|---:|---|---|
| `imageUrl` | string | 是 | 非空；最大 2048 字符；必须是 LinkFox OSS 临时图片目录中的资源 URL | 用于视觉相似商品检索的源图 |
| `contentType` | string | 否 | 最大 100 字符；仅 `image/jpeg`、`image/png`、`image/gif`、`image/webp`、`image/bmp` | 图片 MIME 类型；传入时必须同时与 OSS 响应类型和图片实际字节格式一致 |

服务端下载后的图片不得超过 10 MB，且实际字节必须是 JPEG、PNG、GIF、WebP 或 BMP。省略 `contentType` 时，服务端从 OSS 响应和图片字节识别类型。

以下请求会被拒绝：

- `{}` 或缺少 `imageUrl`：HTTP 400，`imageUrl 为必填参数`
- 任意外部图片 URL（含 Amazon、CDN 直链）、data URI 或 Base64 图片：HTTP 400，要求使用配置好的 LinkFox OSS 资源
- 图片超过 10 MB、格式不受支持，或 `contentType` 与 OSS 响应/实际字节不一致：HTTP 400

该端点的已验证请求契约不包含 Base64、分页、每页数量、排序、筛选、关键词或站点字段。不要从同族商品搜索接口复制这些参数。

#### 脚本 CLI、缓存和认证兼容

| 输入 / 配置 | 类型 | 必填 | 说明 |
|---|---|---|---|
| JSON 参数 | CLI positional | 是 | 顶层必须为对象，内容为上表的图搜参数。 |
| --inline | CLI flag | 否 | 强制全量输出，同时落盘；不绕过缓存。 |
| --no-cache | CLI flag | 否 | 跳过业务缓存的读写，强制请求，可能再次消耗 150 算力。 |
| LINKFOX_AGENT_API_KEY | environment | 二选一 | 优先密钥。 |
| LINKFOXAGENT_API_KEY | environment | 二选一 | 优先密钥为空时使用兼容键。 |
| LINKFOX_TOOL_GATEWAY | environment | 否 | 默认值见公共规则，去掉末尾斜杠。客户端只调用工具网关，不直接调用上游数据服务。 |
| SESSION_ID / MESSAGE_ID / MODE_ID / APP_NAME | environment | 否 | 透传请求头；未设置为空串，SESSION_ID 去掉首尾空白；SESSION_ID 同时聚合会话输出。 |

业务入口仅使用一层 24 小时本地响应缓存，位于 `<cwd>/linkfox/.cache/linkfox-geekbi-temu-search-by-image/`。缓存键包含网关地址、端点、密钥 SHA-256 指纹及排序后的参数，隔离不同账号和网关；仅缓存基础正常且无显式业务失败的响应，成功空结果可缓存，HTTP/业务错误不缓存。过期或损坏缓存不复用。

业务封装调用公共 `call_api.run` 时始终传 `--no-cache`，只关闭公共层缓存；用户是否传此选项仍决定业务缓存的读写。缓存命中也重新保存本次完整响应。大响应摘要忽略 `columns`，展示最大业务列表前 3 条。输出必须写当前工作目录，目录不可写时直接报错，不回退用户目录或系统临时目录。创建会话时写入 `_meta.json` 并向 `index.jsonl` 追加会话索引，保存响应时更新会话元数据。

请求前先检查认证并实际打开目标响应文件；无法创建文件时退出，不产生图搜请求。读取缓存时重新检查业务成功条件，不复用 `errcode=0` 等失败响应。

### 响应结构

| 字段 | 类型 | 真实值 / 说明 |
|---|---|---|
| `errcode` | integer | 成功为 `200` |
| `errmsg` | string | 成功为 `ok` |
| `total` | integer | 返回的相似商品行数；随源图变化，可为 `0` |
| `items` | array | 相似商品行；成功响应也可能为空数组，不得假设固定为 100 行 |
| `columns` | array | 渲染列定义 |
| `title` | string | 实测 `Temu 图搜同款` |
| `sourceType` | string | 实测 `temu` |
| `sourceTool` | string | 实测 `geekbi_temu` |
| `type` | string | 实测 `tableListWorkbenches` |

真实成功响应未包含 `page`、`size` 或 `regionId`；不要在文档中虚构分页字段。

#### items[] 商品字段

业务字段都可能缺失或为 `null`，不得按必填字段解析。类型未声明的字段明确标注“未声明”；示例类型不应当作稳定契约。实测同一商品可能重复、标题与 SKU 文本可能乱码、价格可能互相矛盾，不静默修正、合并或补造。

| 字段 | 类型 | 说明 |
|---|---|---|
| `goodsId` | string（示例） | 商品编号；同一编号可能重复出现，且指标或时间不同。 |
| `mallId` | string（示例） | 店铺编号。 |
| `goodsName` | 未声明 | 商品标题。 |
| `goodsNameCn` | 未声明 | 中文标题，可能乱码。 |
| `goodsNameEn` | string（示例） | 英文标题。 |
| `brand` | 未声明 | 品牌。 |
| `thumbnail` | string（示例） | 商品缩略图 URL。 |
| `catIds` | 未声明 | 品类编号集合；以实际返回为准。 |
| `catItems` | array | 品类对象列表，嵌套字段见下表。 |
| `sold` | number（示例） | 历史销量。 |
| `sales` | 未声明 | 历史销售额。 |
| `quantity` | 未声明 | 库存。 |
| `mallSold` | 未声明 | 店铺销量。 |
| `daySold` | 未声明 | 日销量。 |
| `weekSold` | 未声明 | 周销量。 |
| `monthSold` | number（示例） | 月销量。 |
| `daySoldRate` | 未声明 | 日销量对应比率；单位与计算口径未声明。 |
| `weekSoldRate` | 未声明 | 周销量对应比率；单位与计算口径未声明。 |
| `monthSoldRate` | 未声明 | 月销量对应比率；单位与计算口径未声明。 |
| `daySales` | 未声明 | 日销售额。 |
| `weekSales` | 未声明 | 周销售额。 |
| `monthSales` | 未声明 | 月销售额。 |
| `daySalesRate` | 未声明 | 日销售额对应比率；单位与计算口径未声明。 |
| `weekSalesRate` | 未声明 | 周销售额对应比率；单位与计算口径未声明。 |
| `monthSalesRate` | 未声明 | 月销售额对应比率；单位与计算口径未声明。 |
| `minPrice` | number（示例） | 最低价格，站点当地货币；响应未识别币种时不补造。 |
| `maxPrice` | 未声明 | 最高价格，站点当地货币。 |
| `supplyPrice` | 未声明 | 上游供货价字段；币种未明确，不自行标为 CNY。 |
| `minSupplyPrice` | 未声明 | 上游最低供货价字段。 |
| `medianSupplyPrice` | 未声明 | 上游中位供货价字段。 |
| `maxSupplyPrice` | 未声明 | 上游最高供货价字段。 |
| `goodsScore` | number（示例） | 商品评分。 |
| `reviewNum` | number（示例） | 评论数。 |
| `hostingMode` | integer（示例） | 托管模式：1=全托管，2=半托管。 |
| `status` | integer（示例） | 商品状态：1=正常，2=缺货，3=下架。 |
| `isAd` | 未声明 | 广告标记，保留上游值。 |
| `isCustom` | 未声明 | 定制标记，保留上游值。 |
| `isPresale` | 未声明 | 预售标记，保留上游值。 |
| `onSaleTime` | 未声明 | 上架时间；格式和时区未声明。 |
| `mallOpenTime` | 未声明 | 店铺开业时间；格式和时区未声明。 |
| `createTime` | 未声明 | 创建时间；格式和时区未声明。 |
| `updateTime` | 未声明 | 更新时间；格式和时区未声明。 |
| `similarNum` | 未声明 | 相似商品数量字段。 |
| `sku` | 可能为 JSON 编码字符串 | 不保证为已解析数组；需要时解析，处理畸形内容并保留原值，内部文本可能乱码。 |

#### items[].catItems[] 品类字段

| 字段 | 类型 | 说明 |
|---|---|---|
| catId | 未声明 | 品类编号。 |
| catName | 未声明 | 品类名称。 |
| catLevel | 未声明 | 品类层级。 |
| parentCatId | 未声明 | 父品类编号。 |
| isLeaf | 未声明 | 是否叶子节点标记，以原值为准。 |

#### columns[] 渲染元数据

通常包含下列字段；实测返回 44 个列定义，数量不保证固定。解析以 `items[]` 实际存在字段为准，列中的可排序或可筛选标记不表示图搜请求支持这些参数。

| 字段 | 类型 | 说明 |
|---|---|---|
| field | 未声明 | 列对应字段。 |
| title | 未声明 | 展示标题。 |
| cellType | 未声明 | 单元格渲染类型。 |
| sortable | 未声明 | 渲染排序标记。 |
| filterable | 未声明 | 渲染筛选标记。 |

#### 错误包装

| 字段 | 类型 | 说明 |
|---|---|---|
| error | string | 非 JSON HTTP 错误、连接错误、超时、非法 JSON 或非法 UTF-8 的说明。HTTP JSON 错误体原样保留。 |
| details | string | 非 JSON XML/文本响应内容，最多保留前 500 字符；不以 Python 堆栈代替业务错误。 |

HTTP 错误体含非法 UTF-8 时以替换方式解码，保留 HTTP 状态及可解析的 JSON 业务体；非 JSON 错误的 `error` 保留 HTTP 状态码和原因，`details` 保留响应片段。

### 响应示例

以下示例只展示已由真实响应确认的层级，业务值已简化：

```json
{
  "errcode": 200,
  "errmsg": "ok",
  "total": 100,
  "items": [
    {
      "goodsId": "601100240999226",
      "mallId": "634418220884840",
      "goodsNameEn": "Men's thick-soled hiking shoes",
      "thumbnail": "https://img.kwcdn.com/product/fancy/example.jpg",
      "sold": 53000,
      "monthSold": 1494,
      "minPrice": 22.32,
      "goodsScore": 4.7,
      "reviewNum": 5070,
      "hostingMode": 1,
      "status": 1
    }
  ],
  "columns": [],
  "title": "Temu 图搜同款",
  "sourceType": "temu",
  "sourceTool": "geekbi_temu",
  "type": "tableListWorkbenches"
}
```

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 成功的 `total=0`、`items=[]` 是有效结果；实测也有 100 行，不保证固定条数。
- HTTP 400 表示参数或图片不合规，按请求参数节核对输入，不自动换图重试。
- 已验证非 JSON 错误示例：`<ToolErrorResponse><errcode>400</errcode><errmsg>imageUrl 为必填参数</errmsg></ToolErrorResponse>`。
- HTTP 403 为无权限，停止并联系工具管理员，不按充值处理。429 时停止连续调用，稍后再试。
- 502 / 503 / 504 为网关或上游异常，不自动重试。说明可能再次扣费并取得用户确认后，才可按原参数重试一次；失败、空结果也不得自动换图连续试探。

### curl 示例

先用上传脚本获取公开 OSS 地址与配套 MIME 类型，再替换示例中的 `imageUrl`。

```bash
curl --max-time 150 -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/geekbi/temu/goodsImageSearch" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -H "SESSION_ID: ${SESSION_ID}" \
  -H "MESSAGE_ID: ${MESSAGE_ID}" \
  -H "MODE_ID: ${MODE_ID}" \
  -H "APP_NAME: ${APP_NAME}" \
  -d '{"imageUrl":"https://<LinkFox OSS 主机>/<临时图片路径>/product.jpg","contentType":"image/jpeg"}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-geekbi-temu-search-by-image",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
