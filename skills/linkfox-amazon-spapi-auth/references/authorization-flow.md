# Amazon SP-API 授权流程详细说明

本文档提供所有授权相关接口的详细说明，包括请求参数、返回值、错误处理等。

---

## 1. 获取授权URL

### 接口信息

- **路径**: `/spApi/authorizeUrl`
- **方法**: POST (RouteMapping)
- **鉴权**: 需要（从 Token 中获取 userId）
- **实现**: `SpApiController.java:52`

### 请求参数 (SpApiAuthorizeUrlReq)

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| region | String | ✅ 是 | 区域代码：NA/EU/FE | "NA" |
| sellerName | String | ✅ **是（必填）** | 店铺名 / 卖家展示名称，用于在已授权店铺列表中区分账号；**调用前必须向用户确认并传入非空字符串**，不可省略 | "My Amazon Store" |
| central | String | ❌ 否 | 中心站点 | - |
| marketplace | String | ❌ 否 | 市场代码 | - |

### 返回结果 (SpApiAuthorizeUrlVo)

```json
{
  "authorizeUrl": "https://sellercentral.amazon.com/..."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| authorizeUrl | String | 亚马逊授权链接，用户需在浏览器中打开 |

### 业务逻辑

1. 校验 region 参数（必须为 NA/EU/FE）；**本 Skill 约定**：`sellerName` 须为非空字符串（与用户在 LinkFox 侧展示、区分店铺一致），AI/脚本在调用前应向用户确认店铺名。
2. 构建 state 参数：
   - 包含 gateway.url + /spApi/oauth/callback
   - 附加 userId, region, sellerName
3. 调用紫鸟代理接口 `/developer-proxy/v1/authorize/url`
4. 返回授权链接给用户

### 错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 1002 | 缺少 region 参数 | 必须提供 region (NA/EU/FE) |
| 1003 | 获取授权地址失败 | 检查网络连接和白名单配置，稍后重试 |

### 使用示例

**请求**:
```json
{
  "region": "NA",
  "sellerName": "MyStore"
}
```

**响应**:
```json
{
  "authorizeUrl": "https://sellercentral.amazon.com/apps/authorize/consent?application_id=xxx&state=xxx"
}
```

**后续操作**:
用户在浏览器中打开 `authorizeUrl`，在亚马逊页面完成授权后，会自动重定向到回调地址。

---

## 2. 授权回调处理（服务端内部）

### 接口信息

- **路径**: 服务端内部回调接口（不对客户端/Agent暴露）
- **方法**: POST (RouteMapping)
- **鉴权**: 不需要（auth=false）
- **实现**: `SpApiController.java:111`

### 请求参数 (SpApiAuthorizeCallbackReq)

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userId | String | ✅ 是 | 用户ID（从 state 中解析） |
| sellingPartnerId | String | ✅ 是 | 亚马逊卖家ID |
| accessToken | String | ✅ 是 | 访问令牌 |
| refreshToken | String | ✅ 是 | 刷新令牌 |
| tokenType | String | ❌ 否 | 令牌类型（默认 bearer） |
| expiresIn | String | ❌ 否 | 过期时间（秒） |
| region | String | ✅ 是 | 区域代码 |
| sellerName | String | ❌ 否 | 卖家名称 |
| mwsAuthToken | String | ❌ 否 | MWS 授权令牌 |

### 返回结果 (SpApiAuthorizeCallbackVo)

```json
{
  "saved": true,
  "authRecordId": 123,
  "bindUserId": 456,
  "message": "已新增授权"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| saved | Boolean | 是否保存成功 |
| authRecordId | Long | 授权记录ID（sp_api_amazon_auth 表） |
| bindUserId | Long | 绑定记录ID（sp_api_bind_user 表） |
| message | String | 处理结果消息 |

### 业务逻辑

1. 检查是否已存在同一店铺的授权（sellingPartnerId + region）
2. 如果存在，更新原有授权记录；否则新增
3. 创建或更新用户与授权的绑定关系
4. 返回保存结果

### 注意事项

- 此接口无需鉴权，因为是亚马逊重定向回调
- userId 从 state 参数中解析，必须在获取授权URL时正确设置
- 同一店铺的授权会更新而非重复创建

---

## 3. 查看已授权店铺列表

### 接口信息

- **路径**: `/spApi/authorizedStores`
- **方法**: POST (RouteMapping)
- **鉴权**: 需要（从 Token 中获取 userId）
- **实现**: `SpApiController.java:126`

### 请求参数

无（从 Token 中自动获取当前用户 userId）

### 返回结果 (SpApiAuthorizedStoresVo)

```json
{
  "stores": [
    {
      "sellerName": "My Store",
      "sellerId": "A1234567890",
      "region": "NA"
    },
    {
      "sellerName": "EU Store",
      "sellerId": "A9876543210",
      "region": "EU"
    }
  ],
  "total": 2
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| stores | Array | 店铺列表 |
| stores[].sellerName | String | 卖家名称 |
| stores[].sellerId | String | 卖家ID |
| stores[].region | String | 区域代码 |
| total | Integer | 店铺总数 |

### 业务逻辑

1. 根据 gatewayUserId 查询 sp_api_bind_user 表
2. 获取所有关联的 amazonAuthId
3. 查询对应的授权记录
4. 去重并按 sellerId 和 region 排序
5. 返回店铺列表

### 错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 1002 | 无法识别当前用户 | 请重新登录 |

---

## 4. 刷新访问令牌

### 接口信息

- **路径**: `/spApi/refreshToken`
- **方法**: POST (RouteMapping)
- **鉴权**: 需要（从 Token 中获取 userId）
- **实现**: `SpApiController.java:134`

### 请求参数 (SpApiRefreshTokenReq)

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| sellerId | String | ✅ 是 | 卖家ID | "A1234567890" |
| region | String | ❌ 否 | 区域代码（用于精确匹配） | "NA" |

### 返回结果 (SpApiRefreshTokenVo)

```json
{
  "authRecordId": 123,
  "accessToken": "Atza|IwEBIA...",
  "refreshToken": "Atzr|IwEBIJ...",
  "tokenType": "bearer",
  "expiresIn": "3600",
  "message": "刷新成功并已更新数据库"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| authRecordId | Long | 授权记录ID |
| accessToken | String | 新的访问令牌 |
| refreshToken | String | 新的刷新令牌（可能更新） |
| tokenType | String | 令牌类型 |
| expiresIn | String | 过期时间（秒） |
| message | String | 处理结果 |

### 业务逻辑

1. 根据 sellerId + region 查询授权记录
2. 校验该授权是否属于当前用户
3. 调用紫鸟代理接口 `/developer-proxy/{region}/auth/o2/token`
4. 使用 refresh_token 换取新的 access_token
5. 更新数据库中的令牌信息
6. 返回新令牌

### 错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 1002 | 请指定 sellerId | 必须提供卖家ID |
| 1004 | 未找到授权记录或不属于当前用户 | 检查 sellerId 是否正确，或重新授权 |
| 1004 | 缺少 refresh_token | 授权记录异常，需重新授权 |
| 1003 | 刷新令牌请求失败 | 检查网络连接，稍后重试 |

### 注意事项

- refresh_token 可能在刷新时更新，需保存新的 refresh_token
- 如果 region 未提供，会匹配该 sellerId 的第一条记录

---

## 5. 查询店铺令牌

### 接口信息

- **路径**: `/spApi/storeTokens`
- **方法**: POST (RouteMapping)
- **鉴权**: 需要（从 Token 中获取 userId）
- **实现**: `SpApiController.java:142`

### 请求参数 (SpApiStoreTokensReq)

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| sellerId | String | ✅ 是 | 卖家ID | "A1234567890" |
| region | String | ✅ 是 | 区域代码 | "NA" |

### 返回结果 (SpApiStoreTokensVo)

```json
{
  "sellerId": "A1234567890",
  "region": "NA",
  "authRecordId": 123,
  "accessToken": "Atza|IwEBIA...",
  "refreshToken": "Atzr|IwEBIJ...",
  "tokenType": "bearer",
  "expiresIn": "3600"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| sellerId | String | 卖家ID |
| region | String | 区域代码 |
| authRecordId | Long | 授权记录ID |
| accessToken | String | 访问令牌 |
| refreshToken | String | 刷新令牌 |
| tokenType | String | 令牌类型 |
| expiresIn | String | 过期时间（秒） |

### 业务逻辑

1. 根据 sellerId + region 查询授权记录
2. 校验该授权是否属于当前用户
3. 直接从数据库读取令牌信息（不调用刷新）
4. 返回令牌数据

### 错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 1002 | 请指定 sellerId 或 region | 必须同时提供卖家ID和区域 |
| 1004 | 未找到授权记录或不属于当前用户 | 检查参数或重新授权 |

### 使用场景

- 在调用 Amazon SP-API 前获取访问令牌
- 检查令牌是否即将过期（根据 expiresIn）
- 如果令牌过期，调用 refreshToken 接口更新

---

## 区域与站点映射

### 北美 (NA)

- 美国: amazon.com
- 加拿大: amazon.ca
- 墨西哥: amazon.com.mx

### 欧洲 (EU)

- 英国: amazon.co.uk
- 德国: amazon.de
- 法国: amazon.fr
- 意大利: amazon.it
- 西班牙: amazon.es
- 荷兰: amazon.nl
- 瑞典: amazon.se
- 波兰: amazon.pl

### 远东 (FE)

- 日本: amazon.co.jp
- 澳大利亚: amazon.com.au
- 新加坡: amazon.sg

---

## 数据库表结构

### sp_api_amazon_auth (授权信息表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 主键 |
| region | String | 区域代码 (NA/EU/FE) |
| accessToken | String | 访问令牌 |
| refreshToken | String | 刷新令牌 |
| tokenType | String | 令牌类型 |
| expiresIn | String | 过期时间（秒） |
| sellingPartnerId | String | 卖家ID |
| sellerName | String | 卖家名称 |
| mwsAuthToken | String | MWS 授权令牌 |
| createDate | Date | 创建时间 |
| createTime | Long | 创建时间戳 |
| lastUpdateDate | Date | 更新时间 |
| lastUpdateTime | Long | 更新时间戳 |

### sp_api_bind_user (用户绑定表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 主键 |
| gatewayUserId | String | 网关用户ID |
| amazonAuthId | Long | 授权记录ID（外键） |
| createDate | Date | 创建时间 |
| createTime | Long | 创建时间戳 |
| lastUpdateDate | Date | 更新时间 |
| lastUpdateTime | Long | 更新时间戳 |

---

## 完整授权示例

### 步骤 1: 获取授权链接

**请求**:
```bash
POST /spApi/authorizeUrl
Headers: Authorization: Bearer <token>
Body: {
  "region": "NA",
  "sellerName": "MyStore"
}
```

**响应**:
```json
{
  "authorizeUrl": "https://sellercentral.amazon.com/apps/authorize/consent?..."
}
```

### 步骤 2: 用户授权

用户在浏览器中打开 `authorizeUrl`，登录亚马逊卖家中心并同意授权。

### 步骤 3: 自动回调

亚马逊重定向到:
```
https://<gateway.url>/spApi/oauth/callback?
  userId=<userId>&
  region=NA&
  sellerName=MyStore&
  selling_partner_id=A1234567890&
  access_token=Atza|...&
  refresh_token=Atzr|...&
  token_type=bearer&
  expires_in=3600
```

系统自动保存授权信息。

### 步骤 4: 查看授权结果

**请求**:
```bash
POST /spApi/authorizedStores
Headers: Authorization: Bearer <token>
```

**响应**:
```json
{
  "stores": [
    {
      "sellerName": "MyStore",
      "sellerId": "A1234567890",
      "region": "NA"
    }
  ],
  "total": 1
}
```

### 步骤 5: 使用令牌调用 SP-API

**请求**:
```bash
POST /spApi/storeTokens
Headers: Authorization: Bearer <token>
Body: {
  "sellerId": "A1234567890",
  "region": "NA"
}
```

**响应**:
```json
{
  "accessToken": "Atza|...",
  "refreshToken": "Atzr|...",
  "expiresIn": "3600"
}
```

使用 `accessToken` 作为 `x-amz-access-token` header 调用 Amazon SP-API。

---

## 故障排查

### 问题 1: 授权链接无法访问

**可能原因**:
- 网络连接问题
- 紫鸟代理服务异常
- 白名单配置错误

**解决方案**:
1. 检查网络连接
2. 确认白名单配置
3. 稍后重试或联系技术支持

### 问题 2: 回调未保存授权信息

**可能原因**:
- state 参数中缺少 userId
- 数据库连接异常

**解决方案**:
1. 确认获取授权URL时正确传入用户信息
2. 检查数据库连接
3. 查看服务日志

### 问题 3: 刷新令牌失败

**可能原因**:
- refresh_token 已过期或失效
- 紫鸟代理服务异常

**解决方案**:
1. 如果 refresh_token 失效，需重新授权
2. 检查紫鸟服务状态
3. 确认白名单配置

### 问题 4: 查询令牌返回 1004 错误

**可能原因**:
- sellerId 或 region 错误
- 授权记录不属于当前用户

**解决方案**:
1. 调用 /spApi/authorizedStores 确认店铺信息
2. 确认 sellerId 和 region 正确
3. 如果确实未授权，需先完成授权流程

---

## 安全最佳实践

1. **令牌存储**:
   - 令牌存储在数据库中，不暴露给前端
   - 仅通过后端接口访问令牌

2. **访问控制**:
   - 所有接口都进行用户鉴权
   - 用户只能访问自己授权的店铺

3. **令牌刷新**:
   - 定期检查令牌是否即将过期
   - 自动刷新即将过期的令牌

4. **日志记录**:
   - 记录所有授权操作
   - 记录令牌刷新操作
   - 不记录令牌明文内容

5. **错误处理**:
   - 不在错误消息中暴露敏感信息
   - 提供清晰的错误码和处理建议
