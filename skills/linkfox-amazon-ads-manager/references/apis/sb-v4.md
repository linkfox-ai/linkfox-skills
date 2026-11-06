# Sponsored Brands V4 与共享资源 接口说明

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

### 网关错误响应

成功对象与错误对象分别判断。错误对象字段如下；本地调用器记录的传输状态与解析结果见脚本参考。

| 字段 | 类型 | 说明 |
|---|---|---|
| errcode | integer | 网关错误码，HTTP 200 仍可能包含业务错误。 |
| errmsg | string | 错误说明，保留原文。 |

参数异常可返回 HTTP 400、errcode=400；上游连接异常可返回 HTTP 200、errcode=1503。1002用于缺参数、区域或路径不合法，1004用于授权记录不存在或不属于当前成员；1005可能是授权失效，也可能是路径或方法未放行，结合errmsg判断。受保护状态遵循账号保护规则，不连续试探。

代理通过profileId校验当前成员绑定并选择授权令牌。Ads v1的adsApi/v1/路径不发送Amazon-Advertising-API-Scope；其他可用路径以profileId作为该请求头。ClientId由上游代理注入。广告profile的查询与刷新使用授权技能的/amazonAds/profiles接口。

## 接口：SB V4 创建广告组

对应脚本：`scripts/sb/v4/create_ad_groups.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/v4/adGroups`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/v4/adGroups",
  "method": "POST",
  "body": "{}",
  "contentType": "application/vnd.sbadgroupresource.v4+json",
  "accept": "application/vnd.sbadgroupresource.v4+json"
}'
```


## 接口：SB V4 创建广告

对应脚本：`scripts/sb/v4/create_ads.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/v4/ads/{adType}`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- adType 非法时调用前返回 SB_INVALID_AD_TYPE。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/v4/ads/productCollection",
  "method": "POST",
  "body": "{}",
  "contentType": "application/vnd.sbadresource.v4+json",
  "accept": "application/vnd.sbadresource.v4+json"
}'
```


## 接口：SB V4 创建预算规则

对应脚本：`scripts/sb/v4/create_budget_rules.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/budgetRules`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/budgetRules",
  "method": "POST",
  "body": "{\"budgetRules\":[]}",
  "contentType": "application/json",
  "accept": "application/json"
}'
```


## 接口：SB V4 创建广告活动

对应脚本：`scripts/sb/v4/create_campaigns.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/v4/campaigns`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/v4/campaigns",
  "method": "POST",
  "body": "{}",
  "contentType": "application/vnd.sbcampaignresource.v4+json",
  "accept": "application/vnd.sbcampaignresource.v4+json"
}'
```


## 接口：SB V4 创建创意

对应脚本：`scripts/sb/v4/create_creatives.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/ads/creatives/{creativeType}`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- creativeType 非法时调用前返回 SB_INVALID_CREATIVE_TYPE。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/ads/creatives/productCollection",
  "method": "POST",
  "body": "{\"adId\":\"998877\",\"creative\":{\"asins\":[\"B0EXAMPLE\"],\"headline\":\"Example\"}}",
  "contentType": "application/vnd.sbAdCreativeResource.v4+json",
  "accept": "application/vnd.sbAdCreativeResource.v4+json"
}'
```


## 接口：SB V4 创建关键词

对应脚本：`scripts/sb/v4/create_keywords.py`、`scripts/sb/v3/create_keywords.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/keywords`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- V3 入口遇到已知多广告组结构，调用前返回 SB_V4_CAMPAIGN_NOT_SUPPORTED；不得以切版本重试绕过。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/keywords",
  "method": "POST",
  "body": "{}",
  "contentType": "application/json",
  "accept": "application/vnd.sbkeywordresponse.v3+json"
}'
```


## 接口：SB V4 创建商品定向

对应脚本：`scripts/sb/v4/create_targets.py`、`scripts/sb/v3/create_targets.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/targets`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- V3 入口遇到已知多广告组结构，调用前返回 SB_V4_CAMPAIGN_NOT_SUPPORTED；不得以切版本重试绕过。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/targets",
  "method": "POST",
  "body": "{}",
  "contentType": "application/json"
}'
```


## 接口：SB V4 查询广告组

对应脚本：`scripts/sb/v4/list_ad_groups.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/v4/adGroups/list`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- fetchAll 非法时本地返回 SB_INVALID_BOOLEAN，终止调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/v4/adGroups/list",
  "method": "POST",
  "body": "{\"maxResults\":100}",
  "contentType": "application/vnd.sbadgroupresource.v4+json",
  "accept": "application/vnd.sbadgroupresource.v4+json"
}'
```


## 接口：SB V4 查询广告

对应脚本：`scripts/sb/v4/list_ads.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/v4/ads/list`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- fetchAll 非法时本地返回 SB_INVALID_BOOLEAN，终止调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/v4/ads/list",
  "method": "POST",
  "body": "{\"maxResults\":100}",
  "contentType": "application/vnd.sbadresource.v4+json",
  "accept": "application/vnd.sbadresource.v4+json"
}'
```


## 接口：SB V4 查询预算规则

对应脚本：`scripts/sb/v4/list_budget_rules.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/budgetRules`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`GET`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- fetchAll 非法时本地返回 SB_INVALID_BOOLEAN，终止调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/budgetRules",
  "method": "GET",
  "queryString": "pageSize=100",
  "accept": "application/json"
}'
```


## 接口：SB V4 查询广告活动

对应脚本：`scripts/sb/v4/list_campaigns.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/v4/campaigns/list`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- fetchAll 非法时本地返回 SB_INVALID_BOOLEAN，终止调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/v4/campaigns/list",
  "method": "POST",
  "body": "{\"maxResults\":100}",
  "contentType": "application/vnd.sbcampaignresource.v4+json",
  "accept": "application/vnd.sbcampaignresource.v4+json"
}'
```


## 接口：SB V4 查询创意

对应脚本：`scripts/sb/v4/list_creatives.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/ads/creatives/list`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- fetchAll 非法时本地返回 SB_INVALID_BOOLEAN，终止调用。
- 缺少 adId 时调用前返回 SB_CREATIVE_AD_ID_REQUIRED；本接口按 Ad 查询 Creative Version。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/ads/creatives/list",
  "method": "POST",
  "body": "{\"maxResults\":100,\"adId\":\"998877\"}",
  "contentType": "application/vnd.sbAdCreativeResource.v4+json",
  "accept": "application/vnd.sbAdCreativeResource.v4+json"
}'
```


## 接口：SB V4 查询关键词

对应脚本：`scripts/sb/v4/list_keywords.py`、`scripts/sb/v3/list_keywords.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/keywords`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`GET`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- V3 入口遇到已知多广告组结构，调用前返回 SB_V4_CAMPAIGN_NOT_SUPPORTED；不得以切版本重试绕过。
- fetchAll 非法时本地返回 SB_INVALID_BOOLEAN，终止调用。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/keywords",
  "method": "GET",
  "queryString": "startIndex=0&count=100",
  "accept": "application/vnd.sbkeyword.v3+json"
}'
```


## 接口：SB V4 查询商品定向

对应脚本：`scripts/sb/v4/list_targets.py`、`scripts/sb/v3/list_targets.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/targets/list`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`POST`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- V3 入口遇到已知多广告组结构，调用前返回 SB_V4_CAMPAIGN_NOT_SUPPORTED；不得以切版本重试绕过。
- fetchAll 非法时本地返回 SB_INVALID_BOOLEAN，终止调用。
- 原生 filters 不是数组时返回 SB_INVALID_TARGET_FILTERS；同类原生过滤优先，不重复映射顶层过滤。

### curl 示例

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/targets/list",
  "method": "POST",
  "body": "{\"maxResults\":100}",
  "contentType": "application/json"
}'
```


## 接口：SB V4 修改广告组

对应脚本：`scripts/sb/v4/update_ad_groups.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/v4/adGroups`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`PUT`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/v4/adGroups",
  "method": "PUT",
  "body": "{}",
  "contentType": "application/vnd.sbadgroupresource.v4+json",
  "accept": "application/vnd.sbadgroupresource.v4+json"
}'
```


## 接口：SB V4 修改广告

对应脚本：`scripts/sb/v4/update_ads.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/v4/ads`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`PUT`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/v4/ads",
  "method": "PUT",
  "body": "{}",
  "contentType": "application/vnd.sbadresource.v4+json",
  "accept": "application/vnd.sbadresource.v4+json"
}'
```


## 接口：SB V4 修改预算规则

对应脚本：`scripts/sb/v4/update_budget_rules.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/budgetRules`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`PUT`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/budgetRules",
  "method": "PUT",
  "body": "{\"budgetRules\":[]}",
  "contentType": "application/json",
  "accept": "application/json"
}'
```


## 接口：SB V4 修改广告活动

对应脚本：`scripts/sb/v4/update_campaigns.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/v4/campaigns`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`PUT`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/v4/campaigns",
  "method": "PUT",
  "body": "{}",
  "contentType": "application/vnd.sbcampaignresource.v4+json",
  "accept": "application/vnd.sbcampaignresource.v4+json"
}'
```


## 接口：SB V4 修改关键词

对应脚本：`scripts/sb/v4/update_keywords.py`、`scripts/sb/v3/update_keywords.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/keywords`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`PUT`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- V3 入口遇到已知多广告组结构，调用前返回 SB_V4_CAMPAIGN_NOT_SUPPORTED；不得以切版本重试绕过。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/keywords",
  "method": "PUT",
  "body": "{}",
  "contentType": "application/json",
  "accept": "application/vnd.sbkeywordresponse.v3+json"
}'
```


## 接口：SB V4 修改商品定向

对应脚本：`scripts/sb/v4/update_targets.py`、`scripts/sb/v3/update_targets.py`。

### 调用规范

- 基本规则参考 `公共规则` -> `调用规范`
- **请求地址**：`${LINKFOX_TOOL_GATEWAY}/amazonAds/developerProxy`

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| region | string | 是 | 请求区域NA / EU / FE，也支持小写；使用所选profile的区域。 |
| profileId | integer（Long） | 是 | 当前成员已绑定的广告profile；用于权属校验并由服务端选择授权令牌。 |
| path | string | 是 | `sb/targets`；不含域名及ad-proxy/{region}/前缀，最长2048字符。路径占位段分别编码。 |
| method | string | 是 | 本操作上游方法为`PUT`；外层LinkFox请求始终POST。 |
| queryString | string | 否 | 不含问号的查询串，最长4096字符；具体构参见脚本参考。 |
| body | string | 否 | 上游正文字符串，最长1,048,576字符；POST/PUT按操作传入，GET/DELETE不发送正文。 |
| contentType | string | 否 | 上游请求媒体类型，最长128字符，默认application/json；vendor MIME按操作值传入，不附加charset。 |
| accept | string | 否 | 上游Accept，最长128字符；显式传入时优先，未传且path为sp/时取contentType。 |

操作的脚本输入、媒体类型和正文构造见 [sb-v4-script-usage.md](sb-v4-script-usage.md)。

### 响应结构

| 字段 | 类型 | 说明 |
|---|---|---|
| httpStatus | integer | Amazon 上游 HTTP 状态，区别于 LinkFox 外层 HTTP。 |
| contentType | string | 上游响应内容类型，可为空。 |
| body | string | 上游原始正文；可为空字符串。内部业务字段由脚本按实际响应解析。 |

### 响应码规则

#### 基础规则

基本规则参考 `公共规则` -> `响应码基本规则`。

#### 业务规则

- 网关正常后仍须检查 Amazon `httpStatus` 为 2xx；保留原始 body，非 2xx 不自动重试。
- 批量创建/修改需逐项核对成功和失败，不能只依据外层 HTTP 或 success。
- 450 / 453 / 454 / 459 的停止范围、阈值和冷却见 [账号保护与重试](../ads-protection.md)。
- V3 入口遇到已知多广告组结构，调用前返回 SB_V4_CAMPAIGN_NOT_SUPPORTED；不得以切版本重试绕过。

### curl 示例

写入示例只说明形状；需先按已授权任务准备真实原生字段，不能直接执行空批次。

```bash
curl -sS -X POST "${LINKFOX_TOOL_GATEWAY:-https://tool-gateway.linkfox.com}/amazonAds/developerProxy" \
  -H "Authorization: ${LINKFOX_AGENT_API_KEY:-$LINKFOXAGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: LinkFox-Skill/2.0" \
  -d '{
  "region": "NA",
  "profileId": 1234567890,
  "path": "sb/targets",
  "method": "PUT",
  "body": "{}",
  "contentType": "application/json"
}'
```


## Feedback

> 该接口与上方工具接口不同，**请勿混用两个基础地址**。

- **POST** `https://skill-api.linkfox.com/api/v1/public/feedback`
- **请求内容类型**：`Content-Type: application/json`

```json
{
  "skillName": "linkfox-amazon-ads-manager",
  "sentiment": "<可选项: POSITIVE / NEUTRAL / NEGATIVE>",
  "category": "<可选项: BUG / COMPLAINT / SUGGESTION / OTHER>",
  "content": "<反馈内容>"
}
```
