# Keepa 亚马逊商品历史趋势 接口说明

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

## 接口：商品历史时序数据（productSeries）

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/keepa/productSeries`

### 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| asin | string | 是 | 亚马逊标准识别号(ASIN)，只支持单个ASIN，最大长度1000 |
| domain | string | 是 | 亚马逊域名 ID；完整枚举和默认选择见下方「站点映射与默认选择」。 |
| days | integer | 否 | 限制历史数据天数，范围 `1`–`365` 天，默认 `90` 天 |
| showPrice | integer | 否 | 设为 `1` 返回市场最低新品价曲线 |
| showPriceList | integer | 否 | 设为 `1` 返回划线价/标价曲线 |
| showPriceDeal | integer | 否 | 设为 `1` 返回闪促价格曲线 |
| showPricePrime | integer | 否 | 设为 `1` 返回Prime专属新品价曲线 |
| showPriceFba | integer | 否 | 设为 `1` 返回第三方FBA新品价曲线 |
| showPriceFbm | integer | 否 | 设为 `1` 返回第三方FBM新品价曲线 |
| showPriceCoupon | integer | 否 | 设为 `1` 返回优惠券后买盒价曲线 |
| showBsrMain | integer | 否 | 设为 `1` 返回大类BSR曲线 |
| showSellerCount | integer | 否 | 设为 `1` 返回卖家数曲线 |

#### 站点映射与默认选择

`domain` 是必填字符串。用户未指定站点时由调用方使用 `"1"`（美国），并非省略该字段。脚本透传 JSON 参数，不会将数字站点 ID 自动转换为字符串；准备请求时以字符串字段定义为准。

| domain | 亚马逊站点 |
|--------|------------|
| 1 | 美国 Amazon.com |
| 2 | 英国 Amazon.co.uk |
| 3 | 德国 Amazon.de |
| 4 | 法国 Amazon.fr |
| 5 | 日本 Amazon.co.jp |
| 6 | 加拿大 Amazon.ca |
| 8 | 意大利 Amazon.it |
| 9 | 西班牙 Amazon.es |
| 10 | 印度 Amazon.in |
| 11 | 墨西哥 Amazon.com.mx |
| 12 | 巴西 Amazon.com.br |

#### 参数选择与使用限制

- 每次仅查询一个 ASIN 和一个站点；多个 ASIN 必须拆成多次串行请求，并说明额外消耗。
- 历史数据最多回溯 365 天；短期分析可选 30 天，中期 90 天，长期 365 天。
- 不启用可选开关时，核心系列为 Buy Box 价格、评分、评分数、月销量与小类 BSR；可选系列须将对应 `show*` 参数设为 `1`。其他开关取值及默认数值未定义，不据此推断额外枚举。
- Keepa 在捕获变化时产生观测点，间隔不规则，并非固定每日一条；不要将缺少某日的数据解释为零或自动补齐。
- 消耗算力 = `0.045 × costToken`，其中 `costToken` 为本次 Keepa token 消耗。请求前按 SKILL.md 的算力消耗预估提醒用户。

#### 脚本选项与运行约定

| 参数 / 选项 | 类型 | 必填 | 说明 |
|-------------|------|------|------|
| JSON 参数 | JSON | 是 | 第一个位置参数，JSON 参数原样传入接口。 |
| --inline | CLI flag | 否 | 完整打印响应，同时仍保存文件。 |
| --no-cache | CLI flag | 否 | 绕过本地缓存读取和写入；默认开启 24 小时缓存。 |
| --help / -h | CLI flag | 否 | 仅展示本地帮助，不发请求。 |
| LINKFOX_TOOL_GATEWAY | 环境变量 | 否 | 网关基础地址，缺省为公共规则中的地址。 |
| LINKFOX_AGENT_API_KEY / LINKFOXAGENT_API_KEY | 环境变量 | 是（实际请求时） | 优先读取前者，兼容后者；缓存命中不发请求。 |
| SESSION_ID | 环境变量 | 否 | 聚合同一会话的数据；未设置时生成会话标识。 |
| MESSAGE_ID / MODE_ID / APP_NAME | 环境变量 | 否 | 作为同名请求头传入接口。 |

缓存路径为 `<cwd>/linkfox/.cache/linkfox-keepa-product-series/`，缓存键为排序后的 JSON 参数的 SHA-256 前 16 位；有效期为文件修改时间起 24 小时。仅由公共调用器维护这一层缓存，同参数可复用有效缓存文件，命中时保留 `_cache.hit` 标记。脚本也会缓存接口返回的错误对象；修正问题后需重新查询时，可显式使用 `--no-cache`，不得自动反复重试收费请求。

完整数据保存在 `<cwd>/linkfox/<YYYY-MM-DD>/<session>/data/linkfox-keepa-product-series-<timestamp>.json`，会话 `_meta.json` 与 `linkfox/index.jsonl` 用于登记会话及数据文件。业务脚本在请求前检查当前工作目录中的会话数据目录是否可写；不可写则失败，禁止回退到家目录或 `/tmp`，不采用 `ACPX_WORKSPACES` 替换输出根目录。业务封装限定本技能的输出位置。

### 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| asin | string | ASIN |
| buyboxPrice | array | Buybox价格（time=时间，value=Buybox价格） |
| price | array | 价格（time=时间，value=价格） |
| priceList | array | 划线价（time=时间，value=划线价格） |
| priceDeal | array | Deal价格（time=时间，value=Deal价格） |
| pricePrime | array | Prime价格（time=时间，value=Prime价格） |
| priceFba | array | FBA价格（time=时间，value=FBA价格） |
| priceFbm | array | FBM价格（time=时间，value=FBM价格） |
| priceCoupon | array | coupon价格（time=时间，value=coupon价格） |
| bsrMain | array | 大类BSR，每个元素包含 `categoryName`（类目名称）和 `points`（time=时间，value=排名） |
| bsrSub | array | 小类BSR，每个元素包含 `categoryName`（类目名称）和 `points`（time=时间，value=排名） |
| sellerCount | array | 卖家数（time=时间，value=卖家数） |
| rating | array | 评分（time=时间，value=评分） |
| ratingCount | array | 评分数（time=时间，value=评分数） |
| monthlySold | array | 子体销量（time=时间，value=销量） |
| costToken | integer | 消耗token |

#### 时序观测点

除 BSR 外，上述曲线为 `{time, value}` 对象数组；时间戳单位及各观测值的具体 JSON 类型未限定，应保留实际返回值，不擅自推断单位或倍率。

| 字段 | 类型 | 说明 |
|------|------|------|
| time | 以实际返回为准 | 观测时间戳；根据实际返回格式转换为可读日期。 |
| value | 以实际返回为准（指标值） | 当前系列对应的价格、数量、评分、月销量或排名值。 |
| bsrMain[].categoryName / bsrSub[].categoryName | 以实际返回为准（类目名称） | 该组 BSR 所属类目。 |
| bsrMain[].points / bsrSub[].points | array | 该类目的排名点，元素为 `{time, value}`。 |
| bsrMain[].points[].time / bsrSub[].points[].time | 以实际返回为准 | BSR 观测时间戳。 |
| bsrMain[].points[].value / bsrSub[].points[].value | 以实际返回为准（排名值） | BSR 数值，越小排名越靠前。 |

#### 状态与本地输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | integer / string / null | 如返回，按公共规则判断；`errcode:401` 表示认证失败。 |
| errmsg | string | 实际错误原因，例如 `authorized error`。 |
| errorCode | 以实际返回为准 | 响应以此字段表示业务状态时，`200` 表示成功，其他业务码表示失败；不能仅因缺少 `errcode` 就认定成功。 |
| error | string | 调用器遇到非 JSON HTTP 错误或连接失败时生成的本地错误信息。 |
| details | string | HTTP 错误正文不能解析为 JSON 时保留的原始正文。 |
| _cache.hit | boolean | 本地缓存命中时添加，非服务端业务字段。 |

### 响应码规则

#### 基础规则

- 基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 响应以 `errorCode` 表示业务状态时，`200` 表示成功，其他业务码表示失败；结合 `errmsg` 解释原因，不因 `errcode` 缺省而忽略明确的业务错误。认证或余额错误仍按 `references/onboarding.md` 的指引处理。
- 成功后依据实际返回的曲线分析；缺失系列或空曲线不补造为完整历史。失败时建议核对 ASIN、站点和历史范围，后续请求遵守成本约束。

### curl 示例

```bash
curl -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/keepa/productSeries" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{"asin":"B0DFRJ7WSX","domain":"1","days":90,"showBsrMain":1,"showPrice":1,"showSellerCount":1}'
```

## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-keepa-product-series",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
