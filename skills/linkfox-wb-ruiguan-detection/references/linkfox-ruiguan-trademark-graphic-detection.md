---
name: linkfox-ruiguan-trademark-graphic-detection
description: 产品图片的图形商标检测与相似度搜索。当用户提到商标检测、图形商标搜索、Logo侵权检查、商标相似度分析、图片商标风险评估、产品图片商标筛查、graphic trademark detection, logo infringement, trademark similarity, trademark risk, image trademark screening, Ruiguan时触发此技能。即使用户未明确说"商标检测"，只要其需求涉及将产品图片与已注册的图形商标进行比对或评估商标侵权风险，也应触发此技能。
---

# Ruiguan Graphic Trademark Detection

This skill guides you on how to detect graphic trademarks in product images, helping e-commerce sellers and brand owners identify potential trademark infringement risks before listing products.

## Core Concepts

Graphic trademark detection analyzes a product image to find visually similar registered trademarks across multiple countries and regions. The tool uses YOLO-based object detection to locate logo-like regions in the image, then compares them against trademark databases worldwide.

**Similarity score**: A higher `similarity` value means the detected graphic is more visually similar to the registered trademark. Values closer to 1.0 indicate near-identical matches and higher infringement risk.

**Trademark status meanings**:
| Status | Meaning |
|--------|---------|
| registered | Trademark is actively registered |
| act | Trademark is active |
| pend | Trademark application is pending |
| filed | Trademark application has been filed |
| ended | Trademark has expired |
| DEL | Trademark has been deleted/cancelled |

## Parameter Guide

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| imageUrl | Yes | Product image URL or base64-encoded image data | - |
| topNumber | Yes | Maximum number of detection results to return (1-100) | 5 |
| productTitle | No | Product title, helps improve detection accuracy | - |
| trademarkName | No | Suspected logo name, helps narrow down results | - |
| regions | No | Country/region codes to check, comma-separated. If omitted, all countries are searched | All |
| enableLocalizing | No | Whether to enable image cropping for detected regions | false |
| enableRadar | No | Whether to enable radar monitoring | true |

### Supported Regions

US (United States), WO (WIPO), ES (Spain), GB (United Kingdom), DE (Germany), IT (Italy), CA (Canada), MX (Mexico), EM (European Union), AU (Australia), FR (France), JP (Japan), TR (Turkey), BX (Benelux), CN (China)

When the user does not specify a region, omit the `regions` parameter so all countries are searched by default.

## Local Image Upload

本接口需要公开图片 URL。本地图片采用两阶段流程：

1. 运行 `python scripts/upload_image.py inspect <local_image_path>`，只在本地检查格式并得到 `contentType` 和 `fileExtension`。
2. 调用 `proxy_call`：`{"toolName":"oss/file/presignedPut","arguments":{"contentType":"<MIME>","fileExtension":"<扩展名>"}}`。
3. 从响应读取 `url` 后，运行 `python scripts/upload_image.py put '<presigned_url>' <local_image_path>`。脚本只向该预签名 URL 上传，不访问工具网关、不读取凭证。
4. 使用脚本输出的去查询参数公开 URL 作为图片参数。原流程约 24 小时有效，过期后需重新获取预签名 URL；不得复用失败或过期 URL。
## Usage Examples

**1. Basic image trademark check**
Detect trademarks in a product image across all regions, returning up to 10 results:
```
imageUrl: "https://example.com/product-image.jpg"
topNumber: 10
```

**2. Region-specific trademark check**
Check a product image against US and EU trademark databases only:
```
imageUrl: "https://example.com/product-image.jpg"
topNumber: 5
regions: "US,EM"
```

**3. Detailed check with product context**
Provide product title and suspected logo name for more accurate detection:
```
imageUrl: "https://example.com/product-image.jpg"
topNumber: 10
productTitle: "Wireless Bluetooth Headphones with Noise Cancellation"
trademarkName: "SonicWave"
regions: "US,GB,DE"
```

**4. Full detection with image cropping**
Enable localizing to get cropped images of detected logo regions:
```
imageUrl: "https://example.com/product-image.jpg"
topNumber: 20
enableLocalizing: true
regions: "US"
```

## MCP 调用

| 项 | 固定值 |
|---|---|
| MCP server | `LinkFox` |
| 唯一工具 | `proxy_call` |
| `toolName` | `ruiguan/trademarkGraphicDetection` |
| `arguments` | 直接使用本 reference 的请求参数对象；不得包裹 `body`、`params`、`data` 或另一层 `arguments` |
| 响应字段来源 | `skills/linkfox-ruiguan-trademark-graphic-detection/references/api.md`；仅按该来源的响应字段契约核对 |

```json
{
  "toolName": "ruiguan/trademarkGraphicDetection",
  "arguments": {
    "imageUrl": "https://example.com/product-image.jpg",
    "topNumber": 5,
    "productTitle": "无线蓝牙耳机",
    "regions": "US,EM"
  }
}
```

- `toolName` 精确匹配且区分大小写；MCP 缺失时停止，不得使用 HTTP fallback。
- WorkBuddy 自动注入 MCP Authorization；不得在配置或 `arguments` 中传 `headers`、API Key、token、JWT、手机号或其他凭证。
- 同一任务内相同 `toolName + arguments` 不重复调用；收费调用失败、空结果或结果不理想时不自动重试。
- 先检查 MCP/schema/`isError`，再读取 text/structured content；text JSON 只解析一次，随后检查下游 `errcode`/`errorCode`/`code`/`errmsg`/`msg`，最后读取业务字段。

## 解决认证和积分问题

- MCP 缺失、MCP 连接 401、下游 401/402/403 或积分不足按 `references/onboarding.md` 分层处理。
- 不要求用户填写 Authorization 或 API Key；不自动选套餐、下单、支付或轮询。
## Display Rules

1. **Present results clearly**: Show detection results in a well-structured table including trademark image, similarity score, trademark name, status, registration office, Nice classification, applicant name, and key dates
2. **Highlight high-risk matches**: When similarity is above 0.8, explicitly warn the user about high infringement risk
3. **Explain trademark status**: When showing results, clarify what each trademark status means for the user's risk assessment
4. **Radar results**: If `radarResult` is present in the response, display it prominently as it contains aggregated risk assessment
5. **Sub-radar results**: If individual items contain `subRadarResult`, include this information alongside each match
6. **Region context**: Always indicate which regions were searched so the user understands the scope of the check
7. **Error handling**: When a detection fails, explain the reason based on the response and suggest adjustments (e.g., using a clearer image, specifying regions, adjusting topNumber)
## Important Limitations

- **Image requirement**: The `imageUrl` parameter is mandatory; the tool cannot perform detection without an image
- **Result cap**: The `topNumber` parameter caps at 100 results per request
- **Image quality**: Detection accuracy depends on image resolution and clarity; higher quality images yield better results
- **Region coverage**: Not all countries are covered; the supported list includes 15 major trademark offices

## User Expression & Scenario Quick Reference

**Applicable** -- Graphic trademark detection tasks:

| User Says | Scenario |
|-----------|----------|
| "Check if this image has trademark issues" | Basic trademark detection |
| "Is this logo registered anywhere" | Multi-region trademark search |
| "Trademark risk for my product image" | Product listing risk assessment |
| "Find similar trademarks to this graphic" | Similarity search |
| "Check this image against US trademarks" | Region-specific detection |
| "Does this design infringe any trademark" | Infringement risk check |
| "Scan my product photo for logos" | Logo detection in product images |

**Not applicable** -- Needs beyond graphic trademark detection:
- Text/word trademark search (no image involved)
- Trademark registration or filing
- Patent or copyright checks
- Legal advice on trademark disputes
- Product listing optimization

**Boundary judgment**: When users say "check my product" or "is this safe to sell", if the concern relates to graphic elements or logos in product images potentially infringing registered trademarks, this skill applies. If they are asking about text trademarks, patent issues, or general legal compliance, it does not apply.

## 积分消耗规则

按动态规则计费：消耗积分 = 雷达检测开启 ? 86.4 : 58.05。

> **重要**：本技能的服务按倍数动态计算，可能一次性消耗大量积分，必须提醒用户，由用户决定是否继续。

**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.


---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*


---

# API 参考

# 睿观-图形商标检测 API 参考

## MCP 调用（API 契约）

本 reference 的业务调用仅使用上方 `proxy_call` 契约；请求参数表中的 JSON 对象直接作为 `arguments`。禁止工具网关 HTTP fallback。
## 请求参数

POST Body（JSON）：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| imageUrl | string | 是 | 产品图片URL或base64编码的图片数据（最大1000字符） |
| topNumber | integer | 是 | 返回YOLO坐标的最大数量，默认 `5`，最大 `100`。实际返回数量可能少于传参数量 |
| productTitle | string | 否 | 产品标题，用于上下文感知检测（最大1000字符） |
| trademarkName | string | 否 | 可能的图形logo名称，用于缩小检索范围（最大1000字符） |
| regions | string | 否 | 需要检测的国家/地区代码，多个时使用逗号隔开，不传默认全部国家。可选值：US（美国）、WO（世界知识产权）、ES（西班牙）、GB（英国）、DE（德国）、IT（意大利）、CA（加拿大）、MX（墨西哥）、EM（欧盟）、AU（澳大利亚）、FR（法国）、JP（日本）、TR（土耳其）、BX（玻利维亚）、CN（中国） |
| enableLocalizing | boolean | 否 | 是否开启切图，默认 `false` |
| enableRadar | boolean | 否 | 是否开启雷达监测，默认 `true` |


## 响应结构

| 字段 | 类型 | 说明 |
|------|------|------|
| boundingBoxCount | integer | 检测结果数量 |
| radarResult | string | 雷达检测结果 |
| total | integer | 记录数 |
| data | array | 检测结果列表（详见下方） |
| detectId | string | 检测ID |
| columns | array | 渲染的列定义 |
| costToken | integer | 消耗token |
| type | string | 渲染的样式 |

### data 数组项字段

`data` 数组中每个对象包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| image | string | 匹配的商标图片地址 |
| boundingBox | string | YOLO坐标（逗号隔开） |
| subRadarResult | string | 子雷达检测结果 |
| applicationNumber | string | 申请号 |
| niceClassName | string | 尼斯分类名称（逗号隔开） |
| applicantName | string | 权利人（逗号隔开） |
| tradeMarkStatus | string | 商标状态，枚举值：`"DEL"`、`"ended"`、`"registered"`、`"act"`、`"pend"`、`"filed"`、`""` |
| niceClass | array | 尼斯分类详情 |
| similarity | number | 相似度（0到1，值越高越相似） |
| registrationNumber | string | 注册号 |
| registrationOfficeCode | string | 商标受理局 |
| registrationDate | string | 注册日期 |
| bid | string | logo标识 |
| trademarkName | string | 图片中的文字商标名称 |
| applicationDate | string | 申请日期 |

## 错误码

正常情况下，接口的 HTTP 状态码均为 200，业务的成功与否通过响应体中的 errorCode 字段区分（errorCode = 200 表示成功，其他值表示业务错误）。当遇到未授权等情况时，HTTP 状态码为 401，且对应的 errorCode 也是 401。

| errcode | 含义 | 处理建议 |
|---------|------|----------|
| 200 | 成功 | 正常解析业务字段 |
| 401 | 认证失败 | HTTP 401 或 authorized error：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 402 | 积分或余额不足 | HTTP 402：按 SKILL.md 的 **## 解决认证和积分问题** 处理。 |
| 其他非200值 | 业务异常 | 参考 `errmsg` 字段获取具体错误原因 |

错误响应示例：

```json
{
    "errcode": 401,
    "errmsg": "authorized error"
}
```

## MCP 示例

```json
{
  "toolName": "ruiguan/trademarkGraphicDetection",
  "arguments": {
    "imageUrl": "https://example.com/product-image.jpg",
    "topNumber": 5,
    "productTitle": "无线蓝牙耳机",
    "regions": "US,EM"
  }
}
```

---

## Feedback API

> This endpoint is **separate** from the tool API above. Do not mix the two base URLs.

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **Content-Type:** `application/json`

```json
{
  "skillName": "linkfox-xxx-xxx",
  "sentiment": "POSITIVE",
  "category": "OTHER",
  "content": "Results were accurate, user was satisfied."
}
```

**Field rules:**
- `skillName`: Use this skill's `name` from the YAML frontmatter
- `sentiment`: Choose ONE — `POSITIVE` (praise), `NEUTRAL` (suggestion without emotion), `NEGATIVE` (complaint or error)
- `category`: Choose ONE — `BUG` (malfunction or wrong data), `COMPLAINT` (user dissatisfaction), `SUGGESTION` (improvement idea), `OTHER`
- `content`: Include what the user said or intended, what actually happened, and why it is a problem or praise
